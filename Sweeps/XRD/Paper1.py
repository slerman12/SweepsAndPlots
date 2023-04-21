from Sweeps.Templates import template


# Note: norm may have not worked because "low" was set to "low" not "low_" in classify
runs = template()

runs.sweep = [
    # Large + RRUFF, No-Pool-CNN
    """task=npcnn
    task_name='${num_classes}-Way_ICSD-true_Open-Access-false_RRUFF-true_Soup-true'
    num_classes=7,230
    train_steps=5e5
    +'dataset.roots=["/gpfs/fs2/scratch/public/jsalgad2/icsd1.2m_large/","/scratch/slerman/XRDs_backup/icsd_Datasets/rruff/XY_DIF_noiseAll/"]'
    +'dataset.train_eval_splits=[1, 0.5]'
    stream=false
    num_gpus=1
    mem=200
    reservation_id=20230321""",
]

runs.plots = [
    ['NPCNN'],
]

runs.title = 'RRUFF'
runs.sftp = True
runs.lab = False
