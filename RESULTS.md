# Results

The selected protocol is RHCNet Official Released-Code Reproduction. Full experiments remain pending. The one-epoch DUO smoke is running; its current status and final gate are recorded in `reproduction_logs/benchmark_duo.txt` and `reproduction_logs/duo_results.md`. The post-smoke auto-launch watcher has been disabled. No 35-epoch run will start without an explicit user instruction. UTDAC uses the complete standard public 6,461-entry protocol; it is not claimed to match the paper's 5,643-image split.

| Experiment | Paper AP | Reproduced AP | Difference | GPU setup | Effective batch | Iterations / epochs | Config | Checkpoint | Notes |
|---|---:|---:|---:|---|---:|---|---|---|---|
| DUO released-code baseline | 70.53 (paper reference only) | Pending | Pending | 1 x RTX 2080 Ti | 2 | 35 epochs; ~3,309 train iterations/epoch | `configs/reproduction/rhcnet_duo_official_release.py` | Pending | Smoke pending evaluation; supplied archive has train/test only. Full training awaits explicit instruction. |
| UTDAC2020 released-code baseline | 53.35 (paper reference only) | Pending | Pending | 1 x RTX 2080 Ti | 2 | 35 epochs; ~2,584 train iterations/epoch | `configs/reproduction/rhcnet_utdac_official_release.py` | Pending | Standard public protocol (5,168 train + 1,293 val); full training deferred. |

Full metric breakdowns, runtime, and deviations belong in `reproduction_logs/duo_results.md` and `reproduction_logs/utdac_results.md` after training.
