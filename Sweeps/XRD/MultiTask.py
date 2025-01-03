from Sweeps.Templates import template


runs = template()

runs.sweep = [
    # Large + RRUFF, No-Pool-CNN
    """task=npcnn
    task_name='${num_classes}-Way_ICSD-True_Open-Access-False_RRUFF-True_Soup-True'
    num_classes=7,230
    train_steps=5e5
    save_per_steps=1e5
    +'dataset.roots=["/gpfs/fs2/scratch/public/jsalgad2/icsd1.2m_large/","./Data/Generated/XRDs_RRUFF/"]'
    +'dataset.train_eval_splits=[1, 0.5]'
    num_workers=1
    mem=5""",
]

runs.plots = [
    ['NPCNN'],
]

runs.app = 'XRDs'
runs.branch = 'main'
runs.remote_name = 'bluehive_acmml'
runs.title = 'Disjoint 50% RRUFF - NPCNN - Trained on synthetic + 50% RRUFF'
