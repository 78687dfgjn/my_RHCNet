#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

config="configs/reproduction/rhcnet_utdac_official_release.py"
work_dir="work_dirs/rhcnet_utdac_official_release"
mkdir -p "$work_dir"

resume_args=()
if [[ -f "$work_dir/latest.pth" ]]; then
  resume_args=(--resume-from "$work_dir/latest.pth")
fi

exec python tools/train.py "$config" --work-dir "$work_dir" "${resume_args[@]}" "$@"
