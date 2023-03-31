# Copyright (c) AGI.__init__. All Rights Reserved.
#
# This source code is licensed under the MIT license found in the
# MIT_LICENSE file in the root directory of this source tree.
from Sweeps.Templates import template, atari


def join(atari_tasks):
    return f'atari/{",atari/".join([a.lower() for a in atari_tasks])}'


runs = template()

runs.sweep = [
    # Less Exploration
    f"""
    task={join(atari[-3:])}
    train_steps=1000000
    save_per_steps=200000
    replay.save=true
    'stddev_schedule="linear(1.0,0.1,20000)"'
    Agent=Agents.AC2Agent
    experiment=Atari26-LessExplore
    mem=50
    autocast=true
    """,  # Note: Manually set "pseudonym" to task_name in sbatch.yaml
]


runs.plots = [
    ['Atari26-LessExplore']
]

runs.sftp = True
runs.lab = False
runs.title = 'Atari-26'
runs.steps = 1e6
runs.write_tabular = True
