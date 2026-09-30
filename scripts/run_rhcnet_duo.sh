#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

config="configs/reproduction/rhcnet_duo_paper.py"
work_dir="work_dirs/rhcnet_duo_paper"
mkdir -p "$work_dir"

resume_args=()
if [[ -f "$work_dir/latest.pth" ]]; then
  resume_args=(--resume-from "$work_dir/latest.pth")
fi

exec python tools/train.py "$config" --work-dir "$work_dir" "${resume_args[@]}" "$@"
