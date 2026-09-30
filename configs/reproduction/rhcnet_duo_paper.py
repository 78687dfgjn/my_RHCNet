"""Paper-parameter run using the repository's actual RHCNet implementation.

The source implementation selects anchor-based TOOD, not the AutoAssign head
shown in the paper. See reproduction_logs/code_audit.md; this config does not
silently replace or claim to repair those architecture differences.
"""

_base_ = '../rhcnet/rhcnet_tood_r50_fpn_anchor_based_2x_duo.py'

classes = ('holothurian', 'echinus', 'scallop', 'starfish')
data_root = 'data/DUO/'

# Paper §4.1 values. Optimizer matches the source config; the milestones restore
# the paper's epoch 27/32 schedule instead of the repository's 24/30 values.
optimizer = dict(type='SGD', lr=0.001, momentum=0.9, weight_decay=0.0001)
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=0.001,
    step=[27, 32])
runner = dict(type='EpochBasedRunner', max_epochs=35)

# The supplied DUO archive has train/test only; it has no separate validation
# split. Use the test annotations only for the final epoch evaluation. During
# the one-epoch smoke run, evaluation is enabled once to verify the metric path.
data = dict(
    train=dict(
        ann_file=data_root + 'annotations/instances_train.json',
        img_prefix=data_root + 'images/train/',
        classes=classes),
    val=dict(
        ann_file=data_root + 'annotations/instances_test.json',
        img_prefix=data_root + 'images/test/',
        classes=classes),
    test=dict(
        ann_file=data_root + 'annotations/instances_test.json',
        img_prefix=data_root + 'images/test/',
        classes=classes))

# Do not select checkpoints on the test split. Evaluate it only at completion.
evaluation = dict(interval=35, metric='bbox')
checkpoint_config = dict(interval=1)
