#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 CONFIG CHECKPOINT [tools/test.py options...]" >&2
  exit 2
fi

cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
config="$1"
checkpoint="$2"
shift 2

exec python tools/test.py "$config" "$checkpoint" --eval bbox "$@"
