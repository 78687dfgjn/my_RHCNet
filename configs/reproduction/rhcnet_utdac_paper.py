"""Paper-parameter run using the repository's actual RHCNet implementation.

The source implementation selects anchor-based TOOD, not the AutoAssign head
shown in the paper. See reproduction_logs/code_audit.md for the full audit.
"""

_base_ = '../rhcnet/rhcnet_tood_r50_fpn_anchor_based_2x_duo.py'

# The standard UTDAC files contain these four names in an annotation-specific
# category ID order. CocoDataset maps by category name using this class order.
classes = ('holothurian', 'echinus', 'scallop', 'starfish')
data_root = 'data/UTDAC/'

# Paper §4.1 values. Optimizer matches the source config; milestones match the
# paper rather than the source schedule's 24/30 values.
optimizer = dict(type='SGD', lr=0.001, momentum=0.9, weight_decay=0.0001)
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=0.001,
    step=[27, 32])
runner = dict(type='EpochBasedRunner', max_epochs=35)

data = dict(
    train=dict(
        ann_file=data_root + 'annotations_reproduction/instances_train2017.json',
        img_prefix=data_root + 'train2017/',
        classes=classes),
    val=dict(
        ann_file=data_root + 'annotations_reproduction/instances_val2017.json',
        img_prefix=data_root + 'val2017/',
        classes=classes),
    test=dict(
        ann_file=data_root + 'annotations_reproduction/instances_val2017.json',
        img_prefix=data_root + 'val2017/',
        classes=classes))

# A real validation split is available, so best bbox mAP can be selected there.
evaluation = dict(interval=1, metric='bbox', save_best='bbox_mAP')
checkpoint_config = dict(interval=1)
