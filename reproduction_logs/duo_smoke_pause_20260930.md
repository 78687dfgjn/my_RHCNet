# DUO smoke pause state — 2026-09-30

The 1-epoch DUO smoke was suspended on the server after its progress log reached iteration 2,450 of 3,309 (74.0%). This is a mid-epoch process suspension, not a completed run.

- Latest log time: 2026-09-30 19:37:13 server time.
- Latest losses: classification 0.25789, bbox 0.41200, total 0.66989 (finite).
- Latest 50-iteration window: 3.94487 s/iter; the logger estimated 1:00:11 remaining at that point.
- Elapsed from smoke launch (16:45:16) to the last log: approximately 2 h 52 min.
- Memory: MMCV log 7,768 MiB; `nvidia-smi` reported 10,245 MiB used after suspension. GPU utilization was 0% in that paused sample.
- No epoch checkpoint exists yet (`epoch_1.pth` absent). Train-side evaluation and the standalone `tools/test.py` evaluation are pending. AP values must not be reported.
- The smoke training Python process (PID 5659) and its four data-loader workers (PIDs 5800, 5832, 5864, 5896) were confirmed in stopped state (`T`). Its wrapper shell remains waiting. The evaluation-only tmux watcher was stopped. The full-training auto-launch watcher remains disabled.
- The raw text/JSON logs remain under `/hy-tmp/RHCNet/RHCNet/work_dirs/rhcnet_duo_smoke/` and are excluded from Git; this tracked file records the reproducible progress snapshot.

## Resume in place

Do not shut down or recreate the server if the intent is to continue this exact in-memory run; stopping the instance loses the unsaved 2,450 iterations because no checkpoint has been written. On the same live instance, first verify that these PIDs still refer to this smoke command and remain stopped, then restart the evaluation-only watcher and continue the stopped training processes:

```bash
cd /hy-tmp/RHCNet/RHCNet
tmux new-session -d -s rhcnet_duo_smoke_eval 'cd /hy-tmp/RHCNet/RHCNet && bash scripts/eval_duo_smoke_after_train.sh'
ps -o pid,stat,args -p 5659,5800,5832,5864,5896
kill -CONT 5659 5800 5832 5864 5896
```

If those processes no longer exist, the in-memory run cannot be resumed; use the saved dataset/config and start a fresh smoke. Do not start 35-epoch training without explicit user instruction.
