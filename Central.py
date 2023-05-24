# Copyright (c) AGI.__init__. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# MIT_LICENSE file in the root directory of this source tree.
"""
Selecting sweep, UnifiedML local path, and configurations for remote servers.
Modify this file with your info.
"""

from SafePass import safe_pass
from VPN import connect_vpn

# Example sweep in Sweeps/XRD/Paper1.py
sweep_path = 'XRD/Paper1'  # Note to self: can make this a sys arg

# Make sure to define the path to your local UnifiedML for plotting - later can use import pip package
UnifiedML_local_path = '../UnifiedML'

"""
For server configurations
"""

# The username hosting your copy of this repo - GitHub is how this repo syncs across local machine and remote
github_username = 'slerman12'

remote_app_run_files = {'UnifiedML': 'Run.py',
                        'XRDs': 'XRD.py'}  # Names of run files for each UnifiedML app you use

# Support for wandb live-plotting (if so, will have to enter wandb login key into console on first run)
wandb = True


# Server-specific configs
def get_remote(remote_name, local=True):
    """
    Define your own remote server(s) here according to any chosen unique name(s).

    inputs:
        remote_name (str)
    outputs:
        server (str)
        username (str)
        password (str)
            Note: just use get_pass() which will encrypt your entered password locally or an empty string if no password
        vpn: (func)
            A function that connects to VPN if needed, can be None
        remote_app_paths (dict)
            For example: {'UnifiedML': '~/UnifiedML', 'SweepsAndPlots': '~/SweepsAndPlots', 'App2': '/Path/To/App2'}
            Must include UnifiedML and SweepsAndPlots
        remote_app_run_files (dict)
            For example: {'UnifiedML': 'Run.py', 'App2': 'run_app.py'}
        conda (str)
            The command to activate your remote server conda env
        sbatch (str)
            Any additional commands to be passed to slurm/sbatch, can be None

    How to use:
        In sweeps, specify the "runs.remote_name=" variable to define which remote server should be used for that sweep.
    """

    # Config examples for 3 remote names across 2 servers

    # Example 1
    if remote_name == 'iris/retina':
        server, username, password = 'slurm', 'slerman', ''
        vpn = None
        remote_path = f'/home/cxu-serve/u1/{username}'
        remote_app_paths = {'UnifiedML': f"{remote_path}/UnifiedML",
                            'SweepsAndPlots': f"{remote_path}/SweepsAndPlots",
                            'XRDs': f"{remote_path}/XRDs"}
        conda = 'conda activate AGI'
        sbatch = None
    # Examples 2 & 3
    elif remote_name in ['bluehive_csxu', 'bluehive_acmml']:
        server = 'bluehive.circ.rochester.edu'
        username, password = 'slerman', safe_pass('bluehive') if local else ''
        vpn = connect_vpn(username)
        remote_path = f'/scratch/{username}'
        remote_app_paths = {'UnifiedML': f"{remote_path}/UnifiedML",
                            'SweepsAndPlots': f"{remote_path}/SweepsAndPlots",
                            'XRDs': f"{remote_path}/XRDs"}
        conda = f'source /home/{username}/miniconda3/bin/activate'
        conda = ''.join([f'*"{gpu}"*)\n{conda} {env}\n;;\n'
                         for gpu, env in [('K80', 'CUDA10.2'),  # Conda envs w.r.t. GPU
                                          ('', 'AGI')]])  # Default: AGI
        conda = f'GPU_TYPE' \
                f'=$(nvidia-smi --query-gpu=gpu_name --format=csv | tail  -1)\ncase $GPU_TYPE in\n{conda}esac'

        sbatch = '#SBATCH -p csxu -A cxu22_lab\nmodule load gcc' if remote_name == 'bluehive_csxu' \
            else '#SBATCH -p acmml -A cxu22_lab\nmodule load gcc'
    else:
        assert False, 'Invalid remote name.'

    return server, username, password, vpn, remote_app_paths, conda, sbatch


"""
Notes for self: Ways to simplify further: 
1. Clone this repo and UnifiedML on server automatically at ../app_path
2. If UnifiedML not available, automatically do pip install via conda env
3. Only request app-relevant path and run file
4. Request GitHub pass for push/pull, automatically clone SweepsAndPlots in a private repo
5. Can even create the conda env automatically
Then the only server-specific requirement would be conda support and everything could be configured locally 
in this file.
"""
