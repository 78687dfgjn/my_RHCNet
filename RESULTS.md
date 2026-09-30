# Results

The full experiment results remain pending. As of 2026-09-30, a one-epoch DUO smoke run is in progress (800 of approximately 3,309 train iterations); no final metric is claimed. A watcher will start the 35-epoch DUO run only after the smoke run exits successfully with its checkpoint and evaluation. UTDAC training is deferred until the DUO result is reviewed. The first fifteen single-GPU timing windows average 5.11 s/iter, while the latest seven average 7.05 s/iter; at the recent rate the training-only projections are roughly 9.5 days for DUO and 7.4 days for UTDAC before evaluation overhead.

| Experiment | Paper AP | Reproduced AP | Difference | GPU setup | Effective batch | Iterations / epochs | Config | Checkpoint | Notes |
|---|---:|---:|---:|---|---:|---|---|---|---|
| DUO | 70.53 | Pending | Pending | 1 x RTX 2080 Ti | 2 | 35 epochs; ~3,309 train iterations/epoch | `configs/reproduction/rhcnet_duo_paper.py` | Pending | Smoke at 800/~3,309 iterations; supplied archive has train/test only; final test evaluation only. |
| UTDAC2020 | 53.35 | Pending | Pending | 1 x RTX 2080 Ti | 2 | 35 epochs; ~2,584 train iterations/epoch | `configs/reproduction/rhcnet_utdac_paper.py` | Pending | Dataset prepared; deferred until DUO result; supplied archive differs from paper count. |

Full metric breakdowns, runtime, and deviations belong in `reproduction_logs/duo_results.md` and `reproduction_logs/utdac_results.md` after training.
