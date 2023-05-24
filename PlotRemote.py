# Copyright (c) AGI.__init__. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# MIT_LICENSE file in the root directory of this source tree.
import os
from importlib.machinery import SourceFileLoader
from pathlib import Path

from pexpect import spawn

import numpy as np

from Central import UnifiedML_local_path, sweep_path, get_remote


runs = SourceFileLoader(sweep_path, f'Sweeps/{sweep_path}.py').load_module().runs
name = '/'.join(sweep_path.split('/')[:-1])

_, username, password, vpn, remote_app_paths, _, _ = get_remote(runs.remote_name)

vpn()

# TODO Generalize
if runs.sftp:
    cwd = os.getcwd()
    local_path = f"./Benchmarking"

    Path(local_path).mkdir(parents=True, exist_ok=True)
    os.chdir(local_path)

    experiments = set().union(*runs.plots)

    if 'bluehive' in runs.remote_name:
        # SFTP
        print(f'SFTP\'ing: {", ".join(experiments)}')
        if len(runs.tasks):
            print(f'plotting for tasks: {", ".join(runs.tasks)}')
        if runs.steps:
            print(f'up to steps: {runs.steps:.0f}')

        print('\nConnecting to Bluehive', end=" ")
        p = spawn(f'sftp {username}@bluehive.circ.rochester.edu')
        p.expect('Password: ', timeout=None)
        p.sendline(password)
        p.expect('sftp> ', timeout=None)
        print('- Connected! ✓\n')
        p.sendline(f"lcd {local_path}")
        p.expect('sftp> ', timeout=None)
        p.sendline(f"cd {remote_app_paths[runs.app]}")
        p.expect('sftp> ', timeout=None)
        for i, experiment in enumerate(experiments):
            print(f'{i + 1}/{len(experiments)} [bluehive] SFTP\'ing "{experiment}"')
            p.sendline(f"get -r ./Benchmarking/{experiment.replace('.*', '*')}")  # Some regex compatibility
            p.expect('sftp> ', timeout=None)
        print()

    if runs.remote_name == 'iris/retina':
        print('Connecting to lab', end=" ")
        p = spawn(f'sftp macula')
        p.expect('sftp> ')
        print('- Connected! ✓\n')
        p.sendline(f"lcd {local_path}")
        p.expect('sftp> ')
        # SFTP can't access ~/, so need full path
        lab_paths = ['/localdisk2/sam', '/home/vax10/u38/slerman', '/cxu-serve/u1/slerman']
        for i, path in enumerate(lab_paths):  # Note: latest one overrides
            p.sendline(f'cd {remote_app_paths[runs.app]}')
            p.expect('sftp> ')
            for j, experiment in enumerate(experiments):
                if experiment not in runs.bluehive_only:
                    print(f'{i * len(experiments) + j + 1}/{len(lab_paths) * len(experiments)} '
                          f'[lab - {path}] SFTP\'ing "{experiment}"')
                    p.sendline(f"get -r ./Benchmarking/{experiment.replace('.*', '*')}")  # Some regex compatibility
                    p.expect('sftp> ', timeout=None)

    print('\nPlotting results...')

    os.chdir(cwd)


plot = SourceFileLoader("Plot", UnifiedML_local_path + '/Plot.py').load_module().plot

for plot_train in [False, True]:

    print(f'\n Plotting {"train" if plot_train else "eval"}...')

    for plot_experiments in runs.plots:

        plot(path=f"./Benchmarking/{name if name else ''}/{'_'.join(plot_experiments).strip('.')}/Plots/",
             plot_experiments=plot_experiments if len(plot_experiments) else None,
             plot_agents=runs.agents if len(runs.agents) else None,
             plot_suites=runs.suites if len(runs.suites) else None,
             plot_tasks=runs.tasks if len(runs.tasks) else None,
             steps=runs.steps if runs.steps else np.inf,
             write_tabular=runs.write_tabular, plot_train=plot_train,
             title=runs.title, x_axis=runs.x_axis,
             verbose=True
             )

print(f'\nPlots saved to Benchmarking/{sweep_path.rsplit("/", 1)[0]}.')
