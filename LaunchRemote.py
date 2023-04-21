# Copyright (c) AGI.__init__. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# MIT_LICENSE file in the root directory of this source tree.
from importlib.machinery import SourceFileLoader

from pexpect import pxssh

from VPN import get_pass, connect_vpn, username

sweep_path = 'UnifiedML/Atari'  # TODO Central
branch = 'UnifiedML-V1'  # TODO runs
remote_name = 'bluehive'  # TODO All of these should be pulled from the Sweeps file specified via sysarg or central
app = 'UnifiedML'  # TODO runs

# TODO Central
if 'iris/retina' in remote_name:
    server = 'slurm'

    username, password = username, ''
    remote_path = f'/cxu-serve/u1/{username}'
    conda = f'conda activate AGI'
elif 'bluehive' in remote_name:
    server = 'bluehive.circ.rochester.edu'
    connect_vpn()

    username, password = username, get_pass()
    remote_path = f'/scratch/{username}'
    conda = f'source /home/{username}/miniconda3/bin/activate AGI'
else:
    assert False, 'Invalid remote name.'

runs = SourceFileLoader(sweep_path, f'Sweeps/{sweep_path}.py').load_module().runs

# Launch
try:
    s = pxssh.pxssh()
    s.login(server, username, password)
    s.sendline(f'cd {remote_path}/SweepsAndPlots')
    s.prompt()
    print(s.before.decode("utf-8"))
    s.sendline(f'git pull')
    s.prompt()
    print(s.before.decode("utf-8"))
    s.sendline(f'cd {remote_path}/{app}')  # Run a command
    s.prompt()  # Match the prompt
    print(s.before.decode("utf-8"))  # Print everything before the prompt.
    s.sendline(f'git fetch origin')
    s.prompt()
    print(s.before.decode("utf-8"))
    s.sendline(f'git checkout -b {branch} origin/{branch or "master"}')
    s.prompt()
    prompt = s.before.decode("utf-8")
    if f"fatal: A branch named '{branch}' already exists." in prompt:
        s.sendline(f'git checkout {branch}')
        s.prompt()
        prompt = s.before.decode("utf-8")
    print(prompt)
    assert 'error' not in prompt
    s.sendline(f'git pull origin {branch}')
    s.prompt()
    print(s.before.decode("utf-8"))
    s.sendline(conda)
    s.prompt()
    print(s.before.decode("utf-8"))
    for i, hyperparams in enumerate(runs.sweep):
        hyperparams = "\t".join(hyperparams.splitlines())
        print(f'Set: {i + 1}')
        print(f'python {remote_path}/SweepsAndPlots/Remote/sbatch.py -m {hyperparams}   remote_name={remote_name}"\n')
        s.sendline(f'python {remote_path}/SweepsAndPlots/Remote/sbatch.py -m {hyperparams}   remote_name={remote_name}')
        s.prompt()
        print(s.before.decode("utf-8"))
    s.logout()
except pxssh.ExceptionPxssh as e:
    print("pxssh failed on login.")
    print(e)
