# Copyright (c) AGI.__init__. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# MIT_LICENSE file in the root directory of this source tree.
import os
from importlib.machinery import SourceFileLoader
from pathlib import Path

from pexpect import spawn

import numpy as np

from VPN import get_pass, connect_vpn, username


sweep_path = 'UnifiedML/Atari'
UnifiedML_local_path = '../UnifiedML'


"""
Example of how to plot independent from any specified run specs:
    plot_group = 'Independent'
    runs.update(dict(plots=[['Exp']], sftp=False))
"""
runs = SourceFileLoader(sweep_path, f'Sweeps/{sweep_path}.py').load_module().runs
plot_group = sweep_path.split('/')[0]
# plot_group = 'Independent'
# runs.update(dict(plots=[['Exp']], sftp=False))


# SFTP experiment results
if runs.sftp:
    cwd = os.getcwd()
    local_path = f"./Benchmarking"

    Path(local_path).mkdir(parents=True, exist_ok=True)
    os.chdir(local_path)

    experiments = set().union(*runs.plots)

    if runs.bluehive:
        password = get_pass()
        connect_vpn()

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
        p.sendline(f"cd /scratch/{username}/UnifiedML")
        p.expect('sftp> ', timeout=None)
        for i, experiment in enumerate(experiments):
            print(f'{i + 1}/{len(experiments)} [bluehive] SFTP\'ing "{experiment}"')
            p.sendline(f"get -r ./Benchmarking/{experiment.replace('.*', '*')}")  # Some regex compatibility
            p.expect('sftp> ', timeout=None)
        print()

    if runs.lab:
        print('Connecting to lab', end=" ")
        p = spawn(f'sftp macula')
        p.expect('sftp> ')
        print('- Connected! ✓\n')
        p.sendline(f"lcd {local_path}")
        p.expect('sftp> ')
        # SFTP can't access ~/, so need full path
        lab_paths = ['/localdisk2/sam', '/home/vax10/u38/slerman', '/home/cxu-serve/u1/slerman/']
        for i, path in enumerate(lab_paths):  # Note: latest one overrides
            p.sendline(f'cd {path}/UnifiedML')
            p.expect('sftp> ')
            for j, experiment in enumerate(experiments):
                if experiment not in runs.bluehive_only:
                    print(f'{i * len(experiments) + j + 1}/{len(lab_paths) * len(experiments)} '
                          f'[lab - {path}] SFTP\'ing "{experiment}"')
                    p.sendline(f"get -r ./Benchmarking/{experiment.replace('.*', '*')}")  # Some regex compatibility
                    p.expect('sftp> ', timeout=None)

    print('\nPlotting results...')

    os.chdir(cwd)


plot = SourceFileLoader("UnifiedML", UnifiedML_local_path).load_module().Plot.plot

# Generate each plot
for plot_train in [False, True]:

    print(f'\n Plotting {"train" if plot_train else "eval"}...')

    for plot_experiments in runs.plots:

        plot(path=f"./Benchmarking/{plot_group if plot_group else ''}/{'_'.join(plot_experiments).strip('.')}/Plots/",
             plot_experiments=plot_experiments if len(plot_experiments) else None,
             plot_agents=runs.agents if len(runs.agents) else None,
             plot_suites=runs.suites if len(runs.suites) else None,
             plot_tasks=runs.tasks if len(runs.tasks) else None,
             steps=runs.steps if runs.steps else np.inf,
             write_tabular=runs.write_tabular, plot_train=plot_train,
             title=runs.title, x_axis=runs.x_axis,
             verbose=True
             )
