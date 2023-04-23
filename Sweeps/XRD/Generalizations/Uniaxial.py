from Sweeps.Templates import template


runs = template()

runs.sweep = [
    # Large + RRUFF, No-Pool-CNN
    f"""task=npcnn
    experiment={experiment}
    num_classes=230
    task_name='${{num_classes}}-Way_ICSD-true_Open-Access-false_RRUFF-true_Soup-true'
    load=true
    load_path='/scratch/slerman/XRDs/Checkpoints/NPCNN/AC2Agent/classify/${{task_name}}_1.pt'
    train_steps=0
    +'dataset.roots=["/gpfs/fs2/scratch/public/jsalgad2/icsd1.2m_large/","/scratch/slerman/XRDs_backup/icsd_Datasets/rruff/XY_DIF_noiseAll/"]'
    +'dataset.train_eval_splits=[1, 0.5]'
    TestDataset=XRD.XRD
    +'test_dataset.roots=["/gpfs/fs2/scratch/public/jsalgad2/Uniaxial/{experiment}/"]'
    +'test_dataset.train_eval_splits=[0]'
    +test_dataset.num_classes=${{num_classes}}
    mem=80
    reservation_id=20230321""" for experiment in ['090', '095', '099']
]

runs.plots = [
    ['090', '095', '099'],
]

runs.title = 'Uniaxial - NPCNN - Trained on synthetic + 50% RRUFF'
runs.sftp = True
runs.lab = False
