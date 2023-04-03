# Copyright (c) AGI.__init__. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# MIT_LICENSE file in the root directory of this source tree.
import os
import subprocess
import sys
from pathlib import Path

import hydra
from omegaconf import OmegaConf


username = 'slerman'
remote_name = 'iris/retina'  # TODO This can be a sysarg. Just extract it manually.
app = 'UnifiedML'
run = 'Run.py'

path = f'/scratch/{username}/{app}' if 'bluehive' in remote_name \
    else f'/home/cxu-serve/u1/{username}/{app}'
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

os.chdir(path)

# Format path names
# e.g. Checkpoints/Agents.DQNAgent -> Checkpoints/DQNAgent
OmegaConf.register_new_resolver("format", lambda name: name.split('.')[-1])

# Allow recipes config to accept objects as args
OmegaConf.register_new_resolver("allow_objects", lambda config: config._set_flag("allow_objects", True))

# A boolean "not" operation for config
OmegaConf.register_new_resolver("not", lambda bool: not bool)


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
        args.task = args.task.lower()

        if 'task=classify/custom' in sys.argv[1:]:
            args.task = 'classify/custom'

        if 'task=supermario/mario' in sys.argv[1:]:
            args.task = 'mario'  # Careful, custom suites/tasks might break

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
{'#SBATCH -p csxu -A cxu22_lab' if remote_name == 'bluehive_cxu' else ''}
{f'#SBATCH -p reserved --reservation={username}-{args.reservation_id}' if args.reservation_id else ''}
#SBATCH -t {args.time} -o {args.logger.path}{args.task_name}_{args.seed}.log -J {args.pseudonym}
#SBATCH --mem={args.mem}gb 
{f'#SBATCH -C {args.gpu}' if args.num_gpus and 'bluehive' in remote_name else ''}
{cuda}
{'module load gcc' if 'bluehive' in remote_name else ''}
wandb login {wandb_login_key}
python3 {run} {" ".join([f"'{key}={getattr_recursive(args, key.strip('+'))}'" for key in sys_args - meta])}
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
