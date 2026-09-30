# RHCNet Reproduction

This project reproduces the **official released-code baseline** on DUO and standard public UTDAC2020. The audited architecture is TOOD -> ResNet -> HFCP -> TOODHead; it is not the paper's exact architecture. Differences are documented in [`reproduction_logs/code_audit.md`](reproduction_logs/code_audit.md) and [`REPRODUCTION_DEVIATIONS.md`](REPRODUCTION_DEVIATIONS.md). `*_official_release.py` preserves the released `[24, 30]` LR schedule. Separate `*_paper_hparam.py` files record paper settings `[27, 32]`; they are not the selected baseline.

## Server layout

Keep archives, extracted images, checkpoints, and work directories on the server's large temporary volume:

```text
/hy-tmp/RHCNet/
├── datasets/                 # extracted datasets; source ZIPs remain at /hy-tmp root
└── RHCNet/                   # this repository
    ├── data/DUO -> /hy-tmp/RHCNet/datasets/DUO
    └── data/UTDAC -> /hy-tmp/RHCNet/datasets/UTDAC2020
```

Do not copy images into the Git checkout. Once both user-provided archives have uploaded and their SHA256 values match `reproduction_logs/dataset_audit.md`, extract and link them:

```bash
cd /hy-tmp/RHCNet
unzip -q /hy-tmp/DUO.zip -d datasets
unzip -q /hy-tmp/UTDAC2020.zip -d datasets
cd /hy-tmp/RHCNet/RHCNet
mkdir -p data
ln -s /hy-tmp/RHCNet/datasets/DUO data/DUO
ln -s /hy-tmp/RHCNet/datasets/UTDAC2020 data/UTDAC
```

Confirm the extracted tree and annotation filenames before training. Use the original UTDAC standard train/val JSONs unchanged. A previous `annotations_reproduction/` folder may exist from earlier preparation; it deduplicates/filters data and is explicitly unselected.

## Environment

The audited server uses Python 3.8.10, PyTorch 1.9.0+cu111, CUDA 11.1, MMCV 1.4.0, and MMDetection 2.22.0 on one NVIDIA RTX 2080 Ti. The setup used the server's existing Python/PyTorch/CUDA and installed only missing compatible MMCV and runtime dependencies. See [`reproduction_logs/environment.txt`](reproduction_logs/environment.txt) for the complete environment snapshot and `pip freeze`.

For a compatible clean Linux machine, use Python 3.8 and a Torch/CUDA wheel matching the installed NVIDIA driver. The audited wheel commands are:

```bash
python -m pip install 'torch==1.9.0+cu111' 'torchvision==0.10.0+cu111' \
  -f https://download.pytorch.org/whl/torch_stable.html
python -m pip install --no-deps \
  https://download.openmmlab.com/mmcv/dist/cu111/torch1.9.0/mmcv_full-1.4.0-cp38-cp38-manylinux1_x86_64.whl
python -m pip install --no-deps -r requirements-reproduction.txt
sudo apt-get install libglib2.0-0 libglib2.0-data shared-mime-info xdg-user-dirs
```

Run these only in a separate clean environment. On the active server the commands above are already reflected in the captured environment; do not replace its existing Torch stack. Keep the repository root on `PYTHONPATH` instead of installing a second MMDetection package.

Run the environment check from the repository root:

```bash
bash scripts/check_environment.sh
PYTHONPATH="$PWD" python tools/train.py --help
PYTHONPATH="$PWD" python -c "import torch,mmcv,mmdet; from mmcv.ops import nms; print(torch.__version__,mmcv.__version__,mmdet.__version__)"
```

The backbone config requests `torchvision://resnet50` pretrained weights. The smoke log records the checkpoint loading path; do not substitute random initialization.

## Smoke run

The active one-epoch smoke was started before the released-code/paper-hparam config split, using the legacy config alias (same model and first-epoch schedule). It is allowed to finish and will be evaluated separately. Its post-smoke auto-launch watcher is disabled. Do not start full training until the user reviews the smoke gate and explicitly instructs to proceed.

For a fresh run, start the smoke manually with the official-release config:

```bash
cd /hy-tmp/RHCNet/RHCNet
bash scripts/smoke_rhcnet_duo.sh
```

Record full epoch wall time, mean/median iteration time, peak GPU memory, and GPU/CPU samples. The active HFCP code runs sklearn KMeans on CPU in each forward, so iteration speed varies. The smoke score verifies the path; it is not a training result.

The active smoke's separate evaluation command (run only after `epoch_1.pth` exists):

```bash
PYTHONPATH="$PWD" python tools/test.py \
  configs/reproduction/rhcnet_duo_paper_hparam.py \
  work_dirs/rhcnet_duo_smoke/epoch_1.pth \
  --eval bbox \
  --out work_dirs/rhcnet_duo_smoke/epoch_1_predictions.pkl
```

For the currently running smoke, `scripts/eval_duo_smoke_after_train.sh` is an evaluation-only tmux watcher. It waits for the smoke exit marker and checkpoint, then runs the command above and records its exit status. It cannot launch training.

## DUO released-code training and final evaluation (requires explicit user go-ahead)

The supplied DUO archive has train and test splits but no validation split. The config therefore evaluates the test set only at the final epoch; it does not choose a best checkpoint from test results.

```bash
cd /hy-tmp/RHCNet/RHCNet
bash scripts/run_rhcnet_duo.sh
```

The script uses `configs/reproduction/rhcnet_duo_official_release.py` and resumes from `work_dirs/rhcnet_duo_official_release/latest.pth` when present. After all 35 epochs, evaluate the final checkpoint:

```bash
bash scripts/eval_rhcnet.sh \
  configs/reproduction/rhcnet_duo_official_release.py \
  work_dirs/rhcnet_duo_official_release/epoch_35.pth \
  --eval-options classwise=True
```

## UTDAC2020 training and evaluation

UTDAC uses **standard public UTDAC2020 protocol**: 5,168 train + 1,293 val = 6,461 image entries. The RHCNet paper states 5,643; do not claim these are the same split. The exact-content image duplicate and five negative-dimension boxes are recorded and left unchanged. The configs point to original `annotations/instances_train2017.json` and `instances_val2017.json`; no derived-clean JSON is used. `_waterweeds` and unavailable `testA`/`testB` image sets are excluded.

After DUO is reviewed and the user explicitly approves continuing, run:

```bash
cd /hy-tmp/RHCNet/RHCNet
bash scripts/run_rhcnet_utdac.sh
```

This config evaluates the available validation split each epoch. Report epoch 35; do not cherry-pick a checkpoint by validation AP:

```bash
bash scripts/eval_rhcnet.sh \
  configs/reproduction/rhcnet_utdac_official_release.py \
  work_dirs/rhcnet_utdac_official_release/epoch_35.pth
```

## Results and reproducibility records

Record AP, AP50, AP75, APS, APM, APL, training time, seconds per iteration, peak GPU memory, checkpoint path, and differences from the paper in `reproduction_logs/duo_results.md`, `reproduction_logs/utdac_results.md`, and `RESULTS.md`. Keep full training logs, checkpoints, extracted data, and work directories under `/hy-tmp/RHCNet`; `.gitignore` excludes them from Git.
