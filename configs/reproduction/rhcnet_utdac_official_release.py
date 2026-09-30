"""Released-code RHCNet baseline on the full public UTDAC2020 split.

The repository does not provide an explicit UTDAC config. The released
anchor-based TOOD model and [24, 30] schedule are reused, with only dataset
paths/classes adapted. Original public train/val annotations are used intact.
"""

_base_ = '../rhcnet/rhcnet_tood_r50_fpn_anchor_based_2x_duo.py'

classes = ('holothurian', 'echinus', 'scallop', 'starfish')
data_root = 'data/UTDAC/'

data = dict(
    train=dict(
        ann_file=data_root + 'annotations/instances_train2017.json',
        img_prefix=data_root + 'train2017/',
        classes=classes),
    val=dict(
        ann_file=data_root + 'annotations/instances_val2017.json',
        img_prefix=data_root + 'val2017/',
        classes=classes),
    test=dict(
        ann_file=data_root + 'annotations/instances_val2017.json',
        img_prefix=data_root + 'val2017/',
        classes=classes))

# Evaluate every epoch on the public validation split; report epoch 35 rather
# than cherry-picking a checkpoint by validation AP.
evaluation = dict(interval=1, metric='bbox')
checkpoint_config = dict(interval=1)
