from Sweeps.Templates import template


runs = template()

runs.sweep = [
    # Large + RRUFF, No-Pool-CNN
    f"""task=npcnn
    train_steps=0
    experiment={experiment}
    num_classes=7,230
    load=true
    task_name='${{num_classes}}-Way_ICSD-true_Open-Access-false_RRUFF-true_Soup-true'
    +'dataset.roots=["/gpfs/fs2/scratch/public/jsalgad2/icsd1.2m_large/","/scratch/slerman/XRDs_backup/icsd_Datasets/rruff/XY_DIF_noiseAll/"]'
    +'dataset.train_eval_splits=[1, 0.5]'
    TestDataset=XRD.XRD
    +'test_dataset.roots=["/gpfs/fs2/scratch/public/jsalgad2/Uniaxial/{experiment}/"]'
    +'test_dataset.train_eval_splits=[0]'
    +'test_dataset.num_classes=${{num_classes}}'
    mem=80
    reservation_id=20230321""" for experiment in ['090', '095', '099']
]
# Note: I think test_dataset is only needed because it tries to load a training dataset TODO
# The task_name is only needed here because I mistakenly trained with lowercase booleans


runs.plots = [
    ['090', '095', '099'],
]

runs.title = 'Uniaxial - NPCNN - Trained on synthetic + 50% RRUFF'
runs.sftp = True
runs.lab = False
