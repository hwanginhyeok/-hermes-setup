# Be:A Studio Segfault Issue

## Issue Summary

The Be:A Studio daily content collection cron job (`scripts/run_daily.sh`) intermittently crashes with a segmentation fault during the `enrich_news.py` execution phase.

## Error Pattern

```
scripts/run_daily.sh: line 23: 72435 Segmentation fault (core dumped) python3 scripts/enrich_news.py --raw content_queue/daily_raw/$DATE.json
```

## Execution Context

- **Crontab schedule:** 05:30 KST daily (`30 5 * * *`)
- **Script location:** `/home/window11/be-a-studio/scripts/run_daily.sh`
- **Log location:** `~/.pm_logs/be_a_studio_daily.log`

## Typical Successful Run (pre-crash)

The script typically processes these steps successfully before the crash:

1. YouTube transcript enrichment (94 total items)
2. Transcript extraction (46/49 successful, 3 description fallback)
3. Content parsing and classification

## Recovery Procedure

```bash
cd /home/window11/be-a-studio
bash scripts/run_daily.sh
```

Manual re-execution completes the remaining tasks and produces expected output.

## Known Characteristics

- **Intermittent:** Not every daily run crashes
- **Phase-specific:** Occurs during `enrich_news.py`, not during earlier phases
- **Manual recovery works:** Re-running the script completes successfully
- **No data loss:** Content collection completes before crash point

## Investigation Notes

- The crash happens at line 23 of `run_daily.sh`
- Process ID varies (e.g., 72435 in last incident)
- Core dump is generated but not typically analyzed
- No root cause identified yet (memory, library conflict, or data issue possible)

## Related Information

- **Memory note (2026-05-14):** be-a-studio cron(05:30) enrich_news.py 간헐적 Segfault → 수동 bash scripts/run_daily.sh 재실행으로 복구
