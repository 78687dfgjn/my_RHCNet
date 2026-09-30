#!/usr/bin/env bash
# Evaluation-only follow-up for the already-running one-epoch DUO smoke.
# This script never launches training.
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

while [[ ! -s reproduction_logs/duo_smoke.exit ]]; do
  sleep 30
done

train_rc=$(cat reproduction_logs/duo_smoke.exit)
checkpoint=work_dirs/rhcnet_duo_smoke/epoch_1.pth
if [[ "$train_rc" != "0" || ! -s "$checkpoint" ]]; then
  printf '%s\n' "smoke_train_exit=$train_rc checkpoint_present=$([[ -s $checkpoint ]] && echo yes || echo no)" \
    > reproduction_logs/duo_smoke_standalone_eval.exit
  exit 1
fi

set +e
python tools/test.py \
  configs/reproduction/rhcnet_duo_paper_hparam.py \
  "$checkpoint" \
  --eval bbox \
  --out work_dirs/rhcnet_duo_smoke/epoch_1_predictions.pkl \
  > reproduction_logs/duo_smoke_standalone_eval.log 2>&1
eval_rc=$?
set -e
printf '%s\n' "$eval_rc" > reproduction_logs/duo_smoke_standalone_eval.exit
exit "$eval_rc"
