from Sweeps.Templates import template


runs = template()

runs.sweep = [
    # Large + RRUFF, No-Pool-CNN
    """task=npcnn
    task_name='${num_classes}-Way_ICSD-true_Open-Access-false_RRUFF-true_Soup-true'
    num_classes=7
    train_steps=5e5
    save_per_steps=1e5
    +'dataset.roots=["/gpfs/fs2/scratch/public/jsalgad2/icsd1.2m_large/","/scratch/slerman/XRDs_backup/icsd_Datasets/rruff/XY_DIF_noiseAll/"]'
    +'dataset.train_eval_splits=[1, 0.5]'
    stream=false
    num_workers=6
    num_gpus=1
    mem=80""",
]

runs.plots = [
    ['NPCNN'],
]


runs.app = 'XRDs'
runs.branch = 'main'
runs.remote_name = 'bluehive_acmml'
runs.title = 'Disjoint 50% RRUFF - NPCNN - Trained on synthetic + 50% RRUFF'
