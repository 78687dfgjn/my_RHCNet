# Reproduction notes

## Repository and audit state

- Official repository: `https://github.com/YitengGuo/RHCNet`
- Audited commit: `27253dce2d70875cfc5983bfa3ad194583eb58ee`
- Target repository: `git@github.com:78687dfgjn/my_RHCNet.git`
- Official source files have not been modified. The selected definition is **RHCNet Official Released-Code Reproduction**: use the actual TOOD/ResNet/HFCP/TOODHead path without paper-derived architecture edits. Official-release and paper-hparam configurations are separated under `configs/reproduction/`.
- Both uploaded archives passed remote SHA256 and ZIP CRC checks and are extracted to `/hy-tmp/RHCNet/datasets/`; source archives, images, and annotations remain intact. A prior UTDAC derived-clean folder exists from earlier preparation but is now explicitly unselected; all benchmark configs point to the original public annotations.
- The one-epoch DUO smoke is running in tmux as `rhcnet_duo_smoke`; latest verified progress was 1,550 / approximately 3,309 iterations with finite losses. Its originally started config has paper-hparam milestones, but this is an epoch-1 smoke only. The automatic full-training watcher has been stopped and its script now waits without launching training. Full training awaits explicit user instruction.
- The smoke log confirms that the configured `torchvision://resnet50` ImageNet checkpoint (`resnet50-0676ba61.pth`, 102,530,333 bytes) was downloaded and used, not random initialization. See the benchmark log for all finite logged losses and timing samples.

## Environment before changes

Server Python was `/usr/bin/python`, Python 3.8.10; PyTorch 1.9.0+cu111, Torch CUDA 11.1, torchvision 0.10.0+cu111, NumPy 1.22.3, scikit-learn 1.0.2, OpenCV contrib 4.5.5.64. CUDA was available on one NVIDIA RTX 2080 Ti (22,528 MiB; driver 535.216.03; CUDA toolkit 11.1). The environment had no importable MMCV/MMDetection, `mmcv.ops.nms` was unavailable, and `python tools/train.py --help` failed because MMCV was missing. The complete before-change snapshot and `pip freeze` are in `reproduction_logs/environment.txt`.

## Minimal compatibility changes actually made

| Change | Reason / evidence | Scope |
|---|---|---|
| Installed `mmcv-full==1.4.0` from the official CUDA 11.1 / Torch 1.9.0 / CPython 3.8 wheel | `tools/train.py --help` failed with `ModuleNotFoundError: mmcv`; the wheel was confirmed available and its ops match the existing Torch/CUDA ABI. | Did not alter Torch, torchvision, CUDA, or Python. |
| Installed `addict==2.4.0`, `yapf==0.31.0`, `PyYAML==6.0.3`, `terminaltables==3.1.10`, `pycocotools==2.0.7` | These imports were missing one-by-one from the actual MMCV/MMDetection startup trace; these are small direct runtime dependencies already expected by the repository. | No requirements-wide install; all added with `--no-deps`. `yapf` is pinned to a 2021-era API-compatible release after latest YAPF pulled in extra dependencies that MMDetection 2.22 does not need. |
| Installed Ubuntu `libglib2.0-0` plus its small runtime packages | Existing `opencv-contrib-python==4.5.5.64` could not import because `libgthread-2.0.so.0` was absent. | No OpenCV wheel replacement. The `pip check` warning that MMCV requests the distribution named `opencv-python` remains: this server has the functionally equivalent `opencv-contrib-python` wheel. |
| Used `PYTHONPATH=$PWD` to run repository tools | The repository's local `mmdet` is not installed into site-packages; without this path, `tools/train.py --help` could not import `mmdet`. | Avoided editable-installing the whole repo or allowing pip to resolve/replace dependencies. |

One failed `apt-get update` used the default unprivileged apt sandbox, which could not create temp files because server `/tmp` is mode `1755`. Re-running with `APT::Sandbox::User=root` succeeded. No `/tmp` permission change was made. A trial `yapf 0.43.0`/`tomli` install was removed before selecting `yapf==0.31.0`; no `tomli` remains. An attempted duplicate `opencv-python` wheel installation was cancelled before installation; the original `opencv-contrib-python` remains.

## Paper versus repository facts to preserve

- Paper §4.1: 35 epochs, LR 0.001, SGD momentum 0.9, weight decay 0.0001, LR steps 27/32. The selected official-release configs preserve repository steps 24/30. Separate paper-hparam configs document 27/32 and inherited code-sourced warmup (500 iterations, ratio 0.001).
- README train command names a nonexistent `..._duoc.py`; an anchor-based wrapper with the likely intended name `..._duo.py` exists. The parent RHCNet config defaults to anchor-free. This distinction needs to be recorded in the experiment config/report.
- Current config is TOOD/TOODHead with ATSS for its first four epochs and TaskAlignedAssigner thereafter; paper Figure 2 shows a dual-task head with AutoAssign. Repository AutoAssign code exists but is not selected by RHCNet configs.
- LAM/RGFE and top-down Focus are not active in the current forward. PAM/CGCA are active. CGCA performs CPU KMeans and clusters channel maps by its current reshape, unlike the paper's stated pixel-feature prototypes.
- Paper defines a custom IoU/centerness quality target; current TOOD code uses its alignment metric with standard QualityFocalLoss after the initial phase.
- Paper Table 1: UTDAC AP 53.35. README: 50.8. Do not merge these references.
- Local UTDAC follows standard public UTDAC2020: 5,168 train + 1,293 val = 6,461 entries, versus 5,643 in the paper. There is one identical-content cross-split image pair and five negative-dimension boxes. The complete original entries are retained; earlier derived-clean JSONs are unselected and unused. DUO has train/test but no distinct validation split.

## Commands verified so far

```bash
python -c "import torch,mmcv,mmdet; from mmcv.ops import nms; print(torch.__version__,mmcv.__version__,mmdet.__version__)"
PYTHONPATH=$PWD python tools/train.py --help
```

Both imports and CLI help passed after the initial environment setup. A dynamic model build/forward from the source and anchor-based wrapper completed on CUDA; CUDA NMS passed. The official-release and paper-hparam configs are being validated against the selected original data annotations. The one-epoch DUO smoke is the active validation gate; its checkpoint, standalone evaluation, and final status are pending.

All four explicit official-release/paper-hparam configs loaded with MMDetection. Official-release schedules resolve to `[24, 30]`; paper-hparam schedules resolve to `[27, 32]`. The UTDAC official-release dataset built directly from original JSONs with 5,168 train / 1,293 val images and parsed 37,192 / 9,488 boxes. No full run is being started. The one-epoch DUO smoke must complete and pass its standalone evaluation before the gate is reported; it will then pause for explicit user instruction.

## GitHub Deploy Key

A dedicated ED25519 key was created on the reproduction server at `/root/.ssh/id_ed25519_my_RHCNet_deploy` and registered on `78687dfgjn/my_RHCNet` as a write-enabled repository Deploy Key (`read_only=false`). Its fingerprint is `SHA256:dK0I0DUrmNW+iLMOcVc1POnrBdkslOb6OYnPcf8+H7Y`. The server has an SSH host entry for GitHub and the known GitHub ED25519 host key. `ssh -T git@github.com` from the server returned GitHub's successful-authentication banner for `78687dfgjn/my_RHCNet`. The private key is only on the server and was not copied into this repository.
