"""Released-code RHCNet baseline adapted only to the supplied DUO paths.

The model, optimizer and [24, 30] LR milestones are inherited from the
authors' anchor-based TOOD config and schedule_2x.py. This remains the
released-code architecture, not an exact reconstruction of the paper figure.
"""

_base_ = '../rhcnet/rhcnet_tood_r50_fpn_anchor_based_2x_duo.py'

classes = ('holothurian', 'echinus', 'scallop', 'starfish')
data_root = 'data/DUO/'

# The provided DUO archive contains train/test only. Reserve test evaluation
# for the final epoch and do not select a checkpoint on the test set.
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

evaluation = dict(interval=35, metric='bbox')
checkpoint_config = dict(interval=1)
