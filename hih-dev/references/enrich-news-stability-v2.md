# enrich_news.py Stability Improvements (2026-05-17)

## Context

**be-a-studio enrich_news.py Cron Issues:**
- Problem: Cron not registered, Segfault risks with ThreadPoolExecutor
- Impact: Daily news enrichment not running, data pipeline broken

## Solutions Implemented

### 1. Cron Registration Fixed
```bash
# Original issue: No cron entry
# Solution: Registered with proper permissions
chmod +x scripts/enrich_news.py
(crontab -l; echo "30 5 * * * cd ~/be-a-studio && python3 scripts/enrich_news_v2.py ...") | crontab -
```

### 2. Segfault Prevention (V2)
**Root cause:** lxml thread-safety issues with ThreadPoolExecutor (workers=3)

**V2 improvements:**
```python
# Resource monitoring
import psutil
log_resource_usage(stage)  # CPU/RAM logging every batch

# Segfault detection
signal.signal(signal.SIGSEGV, signal_handler)  # Flag on crash

# Batch processing (100-item chunks)
for i in range(0, total_rss, batch_size):
    batch = rss_items[i:i + batch_size]
    ok, fail = enrich_batch(batch, i, workers=2)  # Reduced from 3
```

**Key changes:**
- workers: 3→2 (reduces Segfault risk)
- batch_size: 100 (memory management)
- timeout: 600s global + 30s per item
- psutil integration: CPU/RAM monitoring
- Intermediate saves: Prevent data loss on crash

### 3. Logging Enhancement
```python
# Daily split files (not appending)
log_file = log_dir / f"enrich_news_v2_{datetime.now().strftime('%Y%m%d')}.log"

# Structured logging
logger.info(f"[배치 완료] {batch_start}-{end}: ok={ok}, fail={fail}")
log_resource_usage(f"batch_{batch_start}")
```

## Test Results

**V2 Test (5 items):**
- Elapsed: 0.3s
- Full texts extracted: 5/5 (100%)
- Memory usage: 55.5MB (stable)
- CPU usage: 0.0% (idle)

## Best Practices for Cron Scripts

1. **Error handling wrapper:**
   ```python
   try:
       summary = enrich_raw_file(raw_path, max_items=max_items, workers=workers)
       if SIGSEGV_RECEIVED:
           sys.exit(2)  # Special exit code for crash detection
   except KeyboardInterrupt:
       sys.exit(130)
   except Exception as e:
       logger.error(f"[치명적 에러] {e}")
       sys.exit(1)
   ```

2. **Resource limits:**
   - psutil monitoring (warn at 4GB RAM)
   - Timeout per item (prevent infinite loops)
   - Batch size limits (memory management)

3. **Data safety:**
   - Intermediate saves after each batch
   - Atomic file writes (rename on completion)
   - Exit codes for different failure modes

## Session Context

**2026-05-17 PM Session:**
- 1단계: Cron registration (permission fix)
- 2단계: V2 stability improvements (Segfault prevention)
- Test: 5 items, 0.3s, 100% success
- Status: ✅ Cron registered, V2 deployed