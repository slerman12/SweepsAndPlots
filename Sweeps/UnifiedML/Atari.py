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
    # f"""
    # task={join(atari)}
    # train_steps=1000000
    # save_per_steps=200000
    # replay.save=true
    # 'stddev_schedule="linear(1.0,0.1,20000)"'
    # Agent=Agents.AC2Agent
    # experiment=Atari26-LessExplore
    # mem=50
    # autocast=true
    # """,  # Note: Manually set "pseudonym" to task_name in sbatch.yaml
    # Less Exploration
    f"""
    task={join(atari)}
    train_steps=1000000
    save_per_steps=200000
    replay.save=true
    'stddev_schedule="linear(1.0,0.1,20000)"'
    experiment=Atari26-Test
    mem=50
    autocast=true
    reservation_id=20230321
    """,  # Note: Manually set "pseudonym" to task_name in sbatch.yaml. Autocast throws error
    # Traceback (most recent call last):
    # File "/scratch/slerman/UnifiedML/Run.py", line 85, in main
    # logs = agent.learn(replay)  # Learn
    # File "/gpfs/fs2/scratch/slerman/UnifiedML/Agents/DQN.py", line 108, in learn
    # critic_loss = QLearning.ensembleQLearning(self.critic, self.actor,
    #                                           File "/gpfs/fs2/scratch/slerman/UnifiedML/Losses/QLearning.py", line 36, in ensembleQLearning
    # next_action_prob = next_q.size(1) < 2 or next_Pi.log_prob(next_action).softmax(-1)  # Action probability
    # File "/gpfs/fs2/scratch/slerman/UnifiedML/Agents/HardDQN.py", line 31, in log_prob
    # log_prob = one_hot(self.best.squeeze(-1), num_actions, null_value=-inf)  # Learn exploitative Q-value-target
    # File "/gpfs/fs2/scratch/slerman/UnifiedML/Utils.py", line 302, in one_hot
    # nulls = torch.full([*shape, num_classes], null_value, dtype=x.dtype, device=x.device)
    # RuntimeError: value cannot be converted to type int64_t without overflow
]

runs.plots = [
    ['Atari26-LessExplore']
]

runs.sftp = False
runs.lab = True
runs.title = 'Atari-26'
runs.steps = 1e6
runs.write_tabular = True
