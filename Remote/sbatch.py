# Copyright (c) AGI.__init__. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# MIT_LICENSE file in the root directory of this source tree.
import shutil
import subprocess
import sys
from pathlib import Path

import hydra
from omegaconf import OmegaConf


username = 'slerman'
remote_name = 'bluehive'  # TODO This can be a sysarg. Just extract it manually.
app = 'UnifiedML'
run = 'Run.py'

remote_path = f'/scratch/{username}' if 'bluehive' in remote_name else f'/cxu-serve/u1/{username}'
path = f'{remote_path}/{app}'
conda_activate = f'source /home/{username}/miniconda3/bin/activate' if 'bluehive' in remote_name \
    else 'conda activate'
conda = ''.join([f'*"{gpu}"*)\n{conda_activate} {env}\n;;\n'
                 for gpu, env in [('K80', 'CUDA10.2'), ('', 'AGI')]])  # Conda envs w.r.t. GPU, '' means else
cuda = f'GPU_TYPE' \
       f'=$(nvidia-smi --query-gpu=gpu_name --format=csv | tail  -1)\ncase $GPU_TYPE in\n{conda}esac'
# cuda = f'source /home/{username}/miniconda3/bin/activate AGI'  # One Conda env for any GPU
wandb_login_key = '55c12bece18d43a51c2fcbcb5b7203c395f9bc40'


sys_args = {arg.split('=')[0].strip('"').strip("'") for arg in sys.argv[1:]}
meta = {'num_gpus', 'gpu', 'mem', 'time', 'reservation_id', '-m', 'task_dir', 'pseudonym', 'remote_name'}
sys.argv.extend(['-cd', path + '/Hyperparams'])  # Adds Hyperparams to Hydra's .yaml search path

# Format path names
# e.g. Checkpoints/Agents.DQNAgent -> Checkpoints/DQNAgent
OmegaConf.register_new_resolver("format", lambda name: name.split('.')[-1])

# Allow recipes config to accept objects as args
OmegaConf.register_new_resolver("allow_objects", lambda config: config._set_flag("allow_objects", True))

# A boolean "not" operation for config
OmegaConf.register_new_resolver("not", lambda bool: not bool)

# Copy UnifiedML Hyperparams to any derivative apps
if app != 'UnifiedML':
    shutil.copytree(remote_path + '/UnifiedML/Hyperparams/', path + '/Hyperparams/', dirs_exist_ok=True)

# Import app-specific task
# if 'task' in sys_args:
#     task = [arg.split('=')[1] for arg in sys.argv if 'task' in arg][0]
#     for line in fileinput.input(os.path.dirname(__file__) + '/sbatch.yaml', inplace=True):
#         if 'task@_global_: atari/pong' in line:
#             line = line.replace('atari/pong', task)
#         sys.stdout.write(line)


def getattr_recursive(__o, name):
    for key in name.split('.'):
        __o = getattr(__o, key)
    if __o is None:
        return 'null'
    if isinstance(__o, str) and '(' in __o:
        __o = '"' + __o.strip('"') + '"'
    return __o


@hydra.main(config_path='./', config_name='sbatch')
def main(args):
    Path(path + '/' + args.logger.path).mkdir(parents=True, exist_ok=True)

    if 'task' in sys_args:
        # args.task = args.task.lower()
        #
        # classify_tasks = [Path(file).stem for file in os.listdir(path + '/Hyperparams/task/classify/')]
        # if 'classify' in args.task and args.task.split('/')[1] not in classify_tasks:
        #     args.task = [arg.split('=')[1] for arg in sys.argv if 'task' in arg][0]

        # if 'task=supermario/mario' in sys.argv[1:]:
        #     args.task = 'mario'  # Careful, custom suites/tasks might break

        # In case "suite/task_name" doesn't describe task
        tasks = [arg.split('=')[1] for arg in sys.argv if 'task' in arg][0]
        print(args.task, tasks)
        if args.task not in tasks:
            args.task = tasks  # Can break if multiple comma-separated tasks

    if 'transform' in sys_args:
        args.transform = f'"{args.transform}"'.replace("'", '')

    if 'stddev_schedule' in sys_args:
        args.stddev_schedule = f'"{args.stddev_schedule}"'

    if 'experiment' in sys_args:
        args.experiment = f'"{args.experiment}"'

    # gpu = '$GPU_TYPE'  # Can add to python script e.g. experiment='name_{gpu}'

    script = f"""#!/bin/bash
#SBATCH -c {args.num_workers + 1}
{f'#SBATCH -p gpu --gres=gpu:{args.num_gpus}' if args.num_gpus else ''}
{'#SBATCH -p csxu -A cxu22_lab' if remote_name == 'bluehive_csxu' 
    else '#SBATCH -p acmml -A cxu22_lab' if remote_name == 'bluehive_acmml' else ''}
{f'#SBATCH -p reserved --reservation={username}-{args.reservation_id}' if args.reservation_id else ''}
#SBATCH -t {args.time} -o {args.logger.path}{args.task_name}_{args.seed}.log -J {args.pseudonym}
#SBATCH --mem={args.mem}gb 
{f'#SBATCH -C {args.gpu}' if args.num_gpus and 'bluehive' in remote_name else ''}
{cuda}
{'module load gcc' if 'bluehive' in remote_name else ''}
wandb login {wandb_login_key}
python {path}/{run} {" ".join([f"'{key}={getattr_recursive(args, key.strip('+'))}'" for key in sys_args - meta])}
"""

    # Write script
    with open('./sbatch_script', 'w') as file:
        file.write(script)

    # Launch script (with error checking / re-launching)
    while True:
        try:
            success = str(subprocess.check_output([f'sbatch ./sbatch_script'], shell=True))
            print(success[2:][:-3])
            if "error" not in success:
                break
        except Exception:
            pass
        print("Errored... trying again")
    print("Success!")


if __name__ == '__main__':
    main()
