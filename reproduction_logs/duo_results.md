# DUO results

Status: data transfer, checksum/CRC verification, extraction, dataset build, and pretrained initialization are verified. The one-epoch smoke has not completed (latest verified log: 2,450 / 3,309 train iterations as of 2026-09-30; SIGSTOP-suspended mid-epoch). The automatic 35-epoch watcher has been stopped and its script no longer launches training. Full training awaits explicit user instruction.

Paper reference (AP / AP50 / AP75 / APS / APM / APL): 70.53 / 87.56 / 77.29 / 56.63 / 71.70 / 69.94.

| Metric | Paper | Reproduced | Difference |
|---|---:|---:|---:|
| AP | 70.53 | Pending | Pending |
| AP50 | 87.56 | Pending | Pending |
| AP75 | 77.29 | Pending | Pending |
| APS | 56.63 | Pending | Pending |
| APM | 71.70 | Pending | Pending |
| APL | 69.94 | Pending | Pending |

At the pause, the latest finite total loss is 0.66989 at iter 2,450; latest window time 3.94487 s/iter; MMCV-reported memory 7,768 MiB; `nvidia-smi` reports 10,245 MiB device memory in use. No epoch checkpoint was written, and neither in-run nor standalone evaluation completed. AP metrics and completed-epoch runtime remain pending; no test mAP is claimed from this partial run. The Python training process and data-loader workers are SIGSTOP-suspended in memory. Keep the same server instance running to preserve that state; a shutdown/restart would lose it.
