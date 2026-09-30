#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

exec python tools/train.py \
  configs/reproduction/rhcnet_duo_paper.py \
  --work-dir work_dirs/rhcnet_duo_smoke \
  --cfg-options runner.max_epochs=1 evaluation.interval=1
