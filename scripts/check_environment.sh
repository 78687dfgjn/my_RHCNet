#!/usr/bin/env bash
set -uo pipefail

cd "$(dirname "$0")/.."
mkdir -p reproduction_logs
output="reproduction_logs/environment.txt"
exec > >(tee -a "$output") 2>&1

echo "=== Environment audit: $(date --iso-8601=seconds) ==="
echo "PWD=$PWD"
echo "Python executable: $(command -v python || true)"
python --version 2>&1 || true
python - <<'PY' || true
import torch
print('PyTorch:', torch.__version__)
print('Torch CUDA:', torch.version.cuda)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
PY
nvidia-smi 2>&1 || true
nvcc --version 2>&1 || true
python -c "import mmcv; print('MMCV:', mmcv.__version__)" 2>&1 || true
PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}" python -c "import mmdet; print('MMDetection:', mmdet.__version__)" 2>&1 || true
python -c "import sklearn; print('scikit-learn:', sklearn.__version__)" 2>&1 || true
python -c "from mmcv.ops import nms; print('MMCV ops OK')" 2>&1 || true
pip show torch torchvision mmcv-full mmdet numpy scikit-learn opencv-contrib-python 2>&1 || true
pip check 2>&1 || true
pip freeze 2>&1 || true
