# Copyright (c) AGI.__init__. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# MIT_LICENSE file in the root directory of this source tree.
import os
import sys
import shutil
import subprocess
import importlib
from importlib.machinery import SourceFileLoader
from pathlib import Path

import hydra
from omegaconf import OmegaConf


root = os.path.dirname(__file__) + '/..'

sys.path.append(root)
Central = importlib.import_module('Central')

runs = SourceFileLoader(Central.sweep_path, f'{root}/Sweeps/{Central.sweep_path}.py').load_module().runs

_, username, _, _, remote_app_paths, conda, sbatch = Central.get_remote(runs.remote_name, local=False)

path = remote_app_paths[runs.app]
run = Central.remote_app_run_files[runs.app]

sys_args = {arg.split('=')[0].strip('"').strip("'") for arg in sys.argv[1:]}
meta = {'num_gpus', 'gpu', 'mem', 'time', 'reservation_id', '-m', 'task_dir', 'pseudonym', 'remote_name', 'wandb_key'}
sys.argv.extend(['-cd', path + '/Hyperparams'])  # Adds Hyperparams to Hydra's .yaml search path

# Format path names
# e.g. Checkpoints/Agents.DQNAgent -> Checkpoints/DQNAgent
OmegaConf.register_new_resolver("format", lambda name: name.split('.')[-1])

# Allow recipes config to accept objects as args
OmegaConf.register_new_resolver("allow_objects", lambda config: config._set_flag("allow_objects", True))

# A boolean "not" operation for config
OmegaConf.register_new_resolver("not", lambda bool: not bool)

# Copy UnifiedML Hyperparams to any derivative apps  TODO Just add 'hydra.searchpath=[pkg://additional_conf]' to sys arg
if runs.app != 'UnifiedML':
    shutil.copytree(f'{remote_app_paths["UnifiedML"]}/Hyperparams/', path + '/Hyperparams/', dirs_exist_ok=True)


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

        # if 'task=supermario/mario' in sys.argv[1:]:
        #     args.task = 'mario'  # Careful, custom suites/tasks might break

        # In case "suite/task_name" doesn't describe task
        tasks = [arg.split('=')[1] for arg in sys.argv if 'task' in arg][0]
        if args.task not in tasks:
            args.task = tasks  # Can break if multiple comma-separated tasks

    if 'transform' in sys_args:
        args.transform = f'"{args.transform}"'.replace("'", '')

    if 'stddev_schedule' in sys_args:
        args.stddev_schedule = f'"{args.stddev_schedule}"'

    if 'experiment' in sys_args:
        args.experiment = f'"{args.experiment}"'

    # gpu = '$GPU_TYPE'  # Can add to python script e.g. experiment='name_{gpu}'

    # Note: specifying GPU type via args.gpu seems to work on Bluehive but not all clusters, leaving it
    # bluehive-specific for now, but should work in the general case
    extra = f'#SBATCH -C {args.gpu}' if args.num_gpus and 'bluehive' in runs.remote_name else ''

    script = f"""#!/bin/bash
#SBATCH -c {args.num_workers + 1}
{f'#SBATCH -p gpu --gres=gpu:{args.num_gpus}' if args.num_gpus else ''}
{f'#SBATCH -p reserved --reservation={username}-{args.reservation_id}' if args.reservation_id else ''}
#SBATCH -t {args.time} -o {args.logger.path}{args.task_name}_{args.seed}.log -J {args.pseudonym}
#SBATCH --mem={args.mem}gb 
{extra}
{sbatch if sbatch else ''}
{conda if conda else ''}
{"wandb login " + args.wandb_key if args.wandb_key else ''}
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
