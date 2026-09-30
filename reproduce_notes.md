# Reproduction notes

## Repository and audit state

- Official repository: `https://github.com/YitengGuo/RHCNet`
- Audited commit: `27253dce2d70875cfc5983bfa3ad194583eb58ee`
- Target repository: `git@github.com:78687dfgjn/my_RHCNet.git`
- Official source files have not been modified. Paper-specific changes belong in `configs/reproduction/` and independent dataset scripts.
- The official model passed construction and a random CUDA feature/head forward. Following the user's instruction to continue, training uses the repository's actual implementation, with paper/source mismatches reported rather than patched into a different algorithm. Both uploaded archives passed remote SHA256 and ZIP CRC checks, have been extracted to `/hy-tmp/RHCNet/datasets/`, and project data symlinks are active. UTDAC derived annotations were generated without changing the originals; both DUO and UTDAC configs successfully built their train/validation datasets. The one-epoch DUO smoke test is running in tmux as `rhcnet_duo_smoke`; it reached 1,000/approximately 3,309 iterations with finite losses. See `reproduction_logs/dataset_audit.md` and `reproduction_logs/benchmark_duo.txt`.
- The smoke log confirms that the configured `torchvision://resnet50` ImageNet checkpoint (`resnet50-0676ba61.pth`, 102,530,333 bytes) was downloaded and used, not random initialization. Total loss was finite at all logged windows through iter 1,000 (1.96 at iter 50; 0.88 at iter 1,000).

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

- Paper §4.1: 35 epochs, LR 0.001, SGD momentum 0.9, weight decay 0.0001, LR steps 27/32. Repo's 2x-derived config uses steps 24/30. A reproduction config should override only the paper-explicit steps and preserve the code-sourced warmup (500 iterations, ratio 0.001) with that provenance stated.
- README train command names a nonexistent `..._duoc.py`; an anchor-based wrapper with the likely intended name `..._duo.py` exists. The parent RHCNet config defaults to anchor-free. This distinction needs to be recorded in the experiment config/report.
- Current config is TOOD/TOODHead with ATSS for its first four epochs and TaskAlignedAssigner thereafter; paper Figure 2 shows a dual-task head with AutoAssign. Repository AutoAssign code exists but is not selected by RHCNet configs.
- LAM/RGFE and top-down Focus are not active in the current forward. PAM/CGCA are active. CGCA performs CPU KMeans and clusters channel maps by its current reshape, unlike the paper's stated pixel-feature prototypes.
- Paper defines a custom IoU/centerness quality target; current TOOD code uses its alignment metric with standard QualityFocalLoss after the initial phase.
- Paper Table 1: UTDAC AP 53.35. README: 50.8. Do not merge these references.
- Local UTDAC archive has 6,461 standard four-class split entries versus 5,643 in the paper, one identical-content train/val image pair, and five negative-dimension boxes. A converter writes derived clean JSON under the data symlink, retains the validation copy, and preserves the originals. DUO has train/test but no distinct validation split. See the dataset audit for the evaluation/checkpoint policy.

## Commands verified so far

```bash
python -c "import torch,mmcv,mmdet; from mmcv.ops import nms; print(torch.__version__,mmcv.__version__,mmdet.__version__)"
PYTHONPATH=$PWD python tools/train.py --help
```

Both imports and CLI help passed after the changes above. A dynamic model build/forward from both the source config and README-indicated anchor-based wrapper completed on CUDA using a 640x640 random input; a CUDA NMS check kept the expected boxes. Dataset builds passed after extraction. The one-epoch DUO smoke is now the active validation gate; at the latest check it reached 1,000 / approximately 3,309 with finite losses. Its checkpoint/evaluation and final status are pending.

The two reproduction configs load on the server with 35 epochs and paper LR milestones `[27, 32]`; all shell scripts pass `bash -n`, and the UTDAC annotation converter passes Python compilation. Both datasets have since built successfully; the one-epoch DUO smoke test is in progress as described above.

## GitHub Deploy Key

A dedicated ED25519 key was created on the reproduction server at `/root/.ssh/id_ed25519_my_RHCNet_deploy` and registered on `78687dfgjn/my_RHCNet` as a write-enabled repository Deploy Key (`read_only=false`). Its fingerprint is `SHA256:dK0I0DUrmNW+iLMOcVc1POnrBdkslOb6OYnPcf8+H7Y`. The server has an SSH host entry for GitHub and the known GitHub ED25519 host key. `ssh -T git@github.com` from the server returned GitHub's successful-authentication banner for `78687dfgjn/my_RHCNet`. The private key is only on the server and was not copied into this repository.
