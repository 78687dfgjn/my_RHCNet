# RHCNet code audit

Audit date: 2026-09-30
Official source: `YitengGuo/RHCNet`, commit `27253dce2d70875cfc5983bfa3ad194583eb58ee`.

## Actual configured model and call path

The README's training command contains a typo (`rhcnet_tood_r50_fpn_anchor_based_2x_duoc.py`). The corresponding checked-in config is `configs/rhcnet/rhcnet_tood_r50_fpn_anchor_based_2x_duo.py`; it inherits `rhcnet_tood_r50_fpn_2x_duo.py` and sets `bbox_head.anchor_type='anchor_based'`. The inherited config itself defaults to `anchor_free`, so these are distinct runs. The user selected the README-indicated anchor-based config as the released-code baseline; this selection is explicit and is not a claim about which config produced the paper table.

The actual path in the README-indicated config is:

```text
image
  -> ResNet-50 (ordinary stem and residual stages; no active LAM or RGFE)
  -> HFCP (Positioning, CGCA and PAM active; Focus instances bypassed)
  -> TOODHead (anchor-based wrapper; ATSS for the first 4 epochs,
               TaskAlignedAssigner afterwards)
  -> class scores and box regression
```

`AutoAssign` and `AutoAssignHead` exist in the broader MMDetection source tree, but the RHCNet config does not select them. The RHCNet config selects detector type `TOOD` and head type `TOODHead`.

## Component-by-component findings

| Paper component | Source location | Actual use in configured forward |
|---|---|---|
| LAM | Paper §3.1; source has `LocalAdaptiveContrastEnhancement` in `mmdet/models/backbones/resnet.py` | Not instantiated. ResNet appends a plugin config, then overwrites `self.plugins` with the original `plugins` argument. RHCNet config passes no plugins. The helper class is not evidence of a paper-equivalent LAM, and its plugin is not registered through the usual plugin registry. Dynamic module enumeration found no instance. |
| RGFE | Paper §3.1, equations (1)–(3) | No RGFE class or forward call exists in the repository. Dynamic module enumeration found none. |
| HFCP | `mmdet/models/necks/hfcp.py`, registered and selected by config | Active; dynamic feature extraction produced 5 pyramid levels with shapes `(1,256,80,80)`, `(1,256,40,40)`, `(1,256,20,20)`, `(1,256,10,10)`, `(1,256,5,5)` for a 640-square input. |
| PAM | `mmdet/models/necks/hfcp.py` | Active; forward hook observed 3 calls per image (P6/P5/P4). |
| CGCA | `mmdet/models/necks/hfcp.py` | Active; forward hook observed 4 calls (P6/P5/P4/P3). It calls `.cpu().detach().numpy()` and sklearn KMeans inside each forward. The input is reshaped to `(C,H*W)`, so KMeans treats each channel's spatial map as a sample; the paper describes clustering pixel features. This is a substantive axis/algorithm difference, not just a performance issue. |
| HFCP top-down Focus path | `Focus` is defined and `focus1/2/3` are constructed in `hfcp.py` | Not executed. Hooks observed zero calls. The implemented forward instead uses interpolation, convolutions and residual additions. |

## Dynamic build/forward evidence

On the server, the model was built first from the checked-in base RHCNet config and then from the README-indicated anchor-based wrapper using the existing CUDA environment. The wrapper reported detector `TOOD`, backbone `ResNet`, neck `HFCP`, head `TOODHead`, `anchor_type=anchor_based`. A random `1x3x640x640` CUDA input completed backbone/neck/head forward without error and returned the five feature shapes listed above. Forward hooks on the base config observed `Positioning: 1`, `CGCA: 4`, `PAM: 3`, `Focus: 0`, and `LocalAdaptiveContrastEnhancement: 0`. A small CUDA NMS call returned the expected retained indices `[0,2]`. The dynamic hook test did not call `init_weights()` and is not a training smoke test.

## Head, assignment and loss

- Paper Figure 2 labels a dual-task head with AutoAssign. RHCNet's README points at a TOOD config; the actual detector/head are `TOOD`/`TOODHead`, not AutoAssign.
- The configured RHCNet head starts with `ATSSAssigner(topk=9)` for epochs 0–3 and switches to `TaskAlignedAssigner(topk=13)` from epoch 4. This is TOOD's staged target assignment.
- The configured classification loss is Focal Loss during the initial phase, then standard MMDetection `QualityFocalLoss` using TOOD alignment metrics. Box loss is GIoU with weight 2. The paper defines a task-adaptive quality label from `IoU^rho * centerness^(1-rho)` with `rho=0.5`; current code does not explicitly implement that formula. Treat this as a method-level discrepancy pending a decision, not as a paper-matched loss.

## Schedule and source inconsistencies

The inherited RHCNet 2x schedule sets 35 epochs, SGD, initial LR `0.001`, momentum `0.9`, weight decay `0.0001`, linear warmup (500 iterations, ratio `0.001`) and LR steps `[24,30]`. Paper §4.1 specifies 35 epochs, LR `0.001`, SGD/momentum `0.9`, and steps `[27,32]`. The selected `official_release` baseline preserves `[24,30]`; separate `paper_hparam` configs record `[27,32]` without changing the architecture.

The README reports UTDAC AP 50.8, while the paper's Table 1 reports 53.35. These values must remain separate reference points.

## Reproduction definition and training gate

The user selected **RHCNet Official Released-Code Reproduction**. No RGFE, LAM, AutoAssign, or other paper-derived module will be guessed or added; the architecture remains the dynamically verified `TOOD -> ResNet -> HFCP -> TOODHead` path, with PAM/CGCA active and Focus bypassed. No algorithm source has been modified. The current one-epoch DUO smoke is allowed to finish and will be evaluated independently. Its post-smoke watcher was disabled before it could start full training. Full training is held until the smoke gate is reported and the user explicitly instructs whether to proceed.
