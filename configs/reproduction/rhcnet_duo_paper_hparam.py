"""Paper hyperparameters over the actual released RHCNet architecture.

This is a record/reference config, not the selected released-code baseline.
The head/backbone/neck/assigner remain the repository's anchor-based TOOD.
"""

_base_ = './rhcnet_duo_official_release.py'

# Paper §4.1; warmup settings are inherited from the official schedule because
# the paper does not specify them.
optimizer = dict(type='SGD', lr=0.001, momentum=0.9, weight_decay=0.0001)
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=0.001,
    step=[27, 32])
runner = dict(type='EpochBasedRunner', max_epochs=35)
