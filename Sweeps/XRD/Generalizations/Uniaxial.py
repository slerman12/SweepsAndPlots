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
    load_path='/scratch/slerman/XRDs/Checkpoints/NPCNN/AC2Agent/classify/${{task_name}}_1.pt'
    +'dataset.roots=["/gpfs/fs2/scratch/public/jsalgad2/icsd1.2m_large/","/scratch/slerman/XRDs_backup/icsd_Datasets/rruff/XY_DIF_noiseAll/"]'
    +'dataset.train_eval_splits=[1, 0.5]'
    TestDataset=XRD.XRD
    +'test_dataset.roots=["/gpfs/fs2/scratch/public/jsalgad2/Uniaxial/{experiment}/"]'
    +'test_dataset.train_eval_splits=[0]'
    +'test_dataset.num_classes=${{num_classes}}'
    mem=80
    reservation_id=20230321""" for experiment in ['090', '095', '099']
]
# Note: I think test_dataset is only needed because it tries to load a training dataset TODO - if train=false
#                                                                                           or eval=true
# The task_name is only needed here because I mistakenly trained with lowercase booleans
# Can use test_dataset and not dataset? When test dataset present, create separate Test benchmarking dir?
# test_name can substitutes task_name in benchmarking csv, otherwise :format{TestDataset} or :format{TestEnv}?
# Datasets should support not just pytorch datasets but arbitrary iterables like a numpy array or datapoint
# __init__ should have a load_agent method for calling act() with manually - can pass in nothing, experiment, task_name,
# or just a path to a checkpoint
# Just like detach should be an option, so should making parts of agents not savable (loaded from scratch upon load)


runs.plots = [
    ['090', '095', '099'],
]

runs.remote_name = 'bluehive_acmml'
runs.title = 'Uniaxial - NPCNN - Trained on synthetic + 50% RRUFF'
