# RHCNet Reproduction

This project runs the repository's RHCNet implementation on DUO and UTDAC2020. The paper/source architecture differences are documented in [`reproduction_logs/code_audit.md`](reproduction_logs/code_audit.md) and [`REPRODUCTION_DEVIATIONS.md`](REPRODUCTION_DEVIATIONS.md). The reproduction configs restore the paper's explicit 35-epoch schedule and LR milestones; they do not add missing paper modules or replace the configured detector head.

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
python tools/dataset_converters/prepare_utdac_annotations.py \
  --train-json data/UTDAC/annotations/instances_train2017.json \
  --val-json data/UTDAC/annotations/instances_val2017.json \
  --train-images data/UTDAC/train2017 \
  --val-images data/UTDAC/val2017 \
  --out-dir data/UTDAC/annotations_reproduction
```

Confirm the actual extracted tree and annotation filenames before training. The expected paths are listed in each reproduction config and were based on inspection of the supplied archives.

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

Run one DUO epoch before a full experiment. This uses the supplied test split once to verify the evaluation path; do not use its score to select training settings or checkpoints.

```bash
cd /hy-tmp/RHCNet/RHCNet
mkdir -p reproduction_logs
nohup bash scripts/smoke_rhcnet_duo.sh > reproduction_logs/duo_smoke.log 2>&1 &
echo $! > reproduction_logs/duo_smoke.pid
```

Check the process, recent log, GPU use, checkpoint, and evaluation output before starting 35 epochs:

```bash
cat reproduction_logs/duo_smoke.pid
ps -fp "$(cat reproduction_logs/duo_smoke.pid)"
nvidia-smi
tail -n 80 reproduction_logs/duo_smoke.log
```

Record 50-iteration timing, data time, GPU memory, and utilization in `reproduction_logs/benchmark_duo.txt`. The first available DUO smoke window measured 3.81 s/iteration and 0.071 s data time; the full 1-epoch smoke remains the gate before the 35-epoch run. The active HFCP code runs sklearn KMeans on CPU in each forward, so the single-window estimate is only approximate.

## DUO training and final evaluation

The supplied DUO archive has train and test splits but no validation split. The config therefore evaluates the test set only at the final epoch; it does not choose a best checkpoint from test results.

```bash
cd /hy-tmp/RHCNet/RHCNet
nohup bash scripts/run_rhcnet_duo.sh >> reproduction_logs/duo_train.log 2>&1 &
echo $! > reproduction_logs/duo_train.pid
```

The script resumes from `work_dirs/rhcnet_duo_paper/latest.pth` when present. The config saves an epoch checkpoint. After all 35 epochs, evaluate the final checkpoint:

```bash
bash scripts/eval_rhcnet.sh \
  configs/reproduction/rhcnet_duo_paper.py \
  work_dirs/rhcnet_duo_paper/epoch_35.pth \
  --eval-options classwise=True
```

## UTDAC2020 training and evaluation

After DUO smoke and training behavior are validated, run UTDAC2020. The standard four-class `train2017`/`val2017` files are used; `_waterweeds` annotation variants and unavailable `testA`/`testB` image sets are excluded. The preparation script writes derived JSON files that remove the exact-content train/val duplicate (`train2017/000004.jpg` duplicates `val2017/000001.jpg`) from train and drops five negative-dimension boxes; it never overwrites the source JSON. The derived files contain 5,167 train images / 37,186 annotations and 1,293 validation images / 9,488 annotations.

```bash
cd /hy-tmp/RHCNet/RHCNet
nohup bash scripts/run_rhcnet_utdac.sh >> reproduction_logs/utdac_train.log 2>&1 &
echo $! > reproduction_logs/utdac_train.pid
```

This config evaluates the available validation split each epoch and keeps the best validation mAP. Evaluate the final checkpoint and best checkpoint separately, and report which result is used for comparison:

```bash
bash scripts/eval_rhcnet.sh \
  configs/reproduction/rhcnet_utdac_paper.py \
  work_dirs/rhcnet_utdac_paper/best_bbox_mAP_epoch_*.pth
```

## Results and reproducibility records

Record AP, AP50, AP75, APS, APM, APL, training time, seconds per iteration, peak GPU memory, checkpoint path, and differences from the paper in `reproduction_logs/duo_results.md`, `reproduction_logs/utdac_results.md`, and `RESULTS.md`. Keep full training logs, checkpoints, extracted data, and work directories under `/hy-tmp/RHCNet`; `.gitignore` excludes them from Git.
