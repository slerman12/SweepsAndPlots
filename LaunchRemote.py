# Copyright (c) AGI.__init__. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# MIT_LICENSE file in the root directory of this source tree.
from importlib.machinery import SourceFileLoader

from pexpect import pxssh

from git import Repo

from SafePass import get_pass
from Central import sweep_path, get_remote, wandb, github_username

runs = SourceFileLoader(sweep_path, f'Sweeps/{sweep_path}.py').load_module().runs

server, username, password, vpn, remote_app_paths, conda, _ = get_remote(runs.remote_name)

vpn()

wandb_key = get_pass('wandb') if wandb else ''  # Optional wandb login, can be None or empty string

# Launch
try:
    repo = Repo('.')
    repo.git.add(update=True)
    repo.index.commit('Launch')
    origin = repo.remote(name='origin')
    origin.push()
    s = pxssh.pxssh()
    s.login(server, username, password)
    s.sendline(f'cd {remote_app_paths["SweepsAndPlots"]}')
    s.prompt()
    print(s.before.decode("utf-8"))
    s.sendline(f'git pull')
    s.prompt()
    print(s.before.decode("utf-8"))
    s.sendline(f'cd {remote_app_paths[runs.app]}')  # Run a command
    s.prompt()  # Match the prompt
    print(s.before.decode("utf-8"))  # Print everything before the prompt.
    s.sendline(f'git fetch origin')
    s.prompt()
    print(s.before.decode("utf-8"))
    s.sendline(f'git checkout -b {runs.branch} origin/{runs.branch}')
    s.prompt()
    prompt = s.before.decode("utf-8")
    if f"fatal: A branch named '{runs.branch}' already exists." in prompt:
        s.sendline(f'git checkout {runs.branch}')
        s.prompt()
        prompt = s.before.decode("utf-8")
    print(prompt)
    assert 'error' not in prompt
    s.sendline(f'git pull origin {runs.branch}')
    s.prompt()
    print(s.before.decode("utf-8"))
    s.sendline(conda)
    s.prompt()
    print(s.before.decode("utf-8"))
    for i, hyperparams in enumerate(runs.sweep):
        hyperparams = "\t".join(hyperparams.splitlines())
        print(f'Set: {i + 1}')
        print(f'python {remote_app_paths["SweepsAndPlots"]}/Remote/sbatch.py -m {hyperparams}   '
              f'remote_name={runs.remote_name}   wandb_key={wandb_key}\n')
        s.sendline(f'python {remote_app_paths["SweepsAndPlots"]}/Remote/sbatch.py -m {hyperparams}   '
                   f'remote_name={runs.remote_name}   wandb_key={wandb_key}')
        s.prompt()
        print(s.before.decode("utf-8"))
    s.logout()
except pxssh.ExceptionPxssh as e:
    print("pxssh failed on login.")
    print(e)
