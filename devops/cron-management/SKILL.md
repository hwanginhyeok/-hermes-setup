---
name: cron-management
title: Cron Job Management & Monitoring
description: Manage, monitor, and debug cron jobs across multiple infrastructure types (Hermes cron, crontab, systemd) with standardized verification procedures.
tags: [cron, automation, devops, monitoring]
---

# Cron Job Management

User has a **hybrid cron infrastructure** with three execution mechanisms. Always check all three when reviewing scheduled automation.

## Infrastructure Overview

| Type | Purpose | Status Check | Log Location |
|------|----------|--------------|--------------|
| **Hermes cron** | AI-driven scheduled tasks (via `cronjob` tool) | `cronjob action=list` | Delivered to target (local/email) |
| **crontab** | Traditional Unix scheduled jobs | `crontab -l` | `~/.pm_logs/<name>.log` |
| **systemd timers** | Service-level recurring tasks | `systemctl --user list-units --type=service` | `journalctl -u <service>` |

---

## Quick Verification Workflow

When asked to verify cron execution status:

1. **List all Hermes cron jobs**
   ```bash
   cronjob action=list
   ```
   Check: `next_run_at`, `last_run_at`, `last_status`

2. **List traditional crontab**
   ```bash
   crontab -l
   ```
   Look for: scheduled commands, log file paths

3. **Check crontab logs** (log pattern: `~/.pm_logs/<name>.log`)
   ```bash
   tail -50 ~/.pm_logs/be_a_studio_daily.log
   # or search by date
   grep "2026051[0-9]" ~/.pm_logs/be_a_studio_daily.log
   ```

4. **Check systemd services** (if applicable)
   ```bash
   systemctl --user list-units --type=service
   systemctl --user status <service-name>
   ```

---

## Current Cron Inventory

### Hermes Cron (1 job)
- **gstack 자동 업데이트** (0346a5f2559c)
  - Schedule: Daily 06:00
  - Script: `bash ~/.hermes/skills/gstack-update.sh`
  - Mode: no_agent=true (script only, no LLM)
  - Status: Active, never executed yet

### Crontab Jobs (20+ jobs)

#### Project Manager
- Daily report: 07:00 (`daily_report.py`)
- Weekly report: Sunday 22:00 (`weekly_report.py`)
- Overnight tasks: 00:00 (`overnight_runner.py`)
- Service health check: Hourly (`service_health.py`)
- Log rotation: Sunday 03:00 (`log_rotate.sh`)

#### Stock Analysis
- Morning briefing: 06:00 KST (21:00 UTC) (`run_briefing.sh morning`)
- Evening briefing: 18:00 KST (09:00 UTC) (`run_briefing.sh evening`)
- News collection: Hourly (`collect_and_classify.py`)
- GeoInvest update: :10 hourly (`update_geoinvest.py`)
- StockInvest update: :05 hourly (`update_stockinvest.py`)
- Deep analysis: 05:30 & 17:30 KST (`deep_analysis.py`)
- PM weekly analysis: Sunday 08:00 KST (tmux send-keys)

#### Be:A Studio
- **Daily content collection**: 05:30 KST (`scripts/run_daily.sh`)
  - Log: `~/.pm_logs/be_a_studio_daily.log`
  - Known issue: Segfault in `enrich_news.py` (see Pitfalls)
- Feed health check: 06:00 KST (`scripts/feed_health_check.py`)
- Artifact cleanup: 03:30 KST (`scripts/cleanup_pipeline_artifacts.py`)

#### 인성이 블로그 (insung_blog)
- Nightly healthcheck: 05:00 KST (`nightly_healthcheck.py`)
- Prod server health: */5 min (`server_health.sh --quiet`)
- Prod regression check: Hourly (`regression_cron.sh --quiet`)
- Scraper run: */6 hours (`run_all_scrapers.py`)
- Monitor bot run log: :05 hourly (`monitor_bot_run_log.py`)
- Webstore status: */30 min (`webstore_status_check.sh`)
- Photo pipeline plan: 09:00 KST (`photo_pipeline.py plan`)

#### Supabase Retention
- Expired campaigns cleanup: :15 hourly
- bot_run_log cleanup: Daily 03:00
- comment_activity cleanup: Sunday 04:00
- rejected comments cleanup: Sunday 04:30
- DB usage monitoring: Daily 06:00

#### Other
- Silence watch: 07:00-23:00 hourly (`silence_watch.py`)
- Music Lab token guard: 09:01 KST (`token_guard.py`)

---

## Known Issues & Recovery

### Be:A Studio Segfault (CRITICAL)
**Symptom:** `enrich_news.py` crashes with segmentation fault during daily execution

**Error pattern in log:**
```
scripts/run_daily.sh: line 23: 72435 Segmentation fault (core dumped) python3 scripts/enrich_news.py --raw content_queue/daily_raw/$DATE.json
```

**Recovery:**
```bash
cd /home/window11/be-a-studio
bash scripts/run_daily.sh  # Re-run manually to complete
```

**Context:** This is an **intermittent issue** that occurs during `enrich_news.py` execution. The script typically processes content collection successfully before hitting the segfault. Manual re-execution completes the job.

---

## Log Location Conventions

All crontab jobs follow this logging pattern:
```
~/.pm_logs/<job_name>.log                    # Rolling logs
~/.pm_logs/<job_name>_<YYYYMMDD>.log        # Date-stamped logs (reports, backups)
```

Common log patterns:
- `be_a_studio_daily.log` - Be:A Studio daily collection
- `nightly_healthcheck.log` - 인성이 블로그 health check
- `insung_health_cron.log` - Prod server health
- `service_health.log` - Service health checks
- `daily_YYYYMMDD.log` - Daily reports
- `weekly_YYYYMMDD.log` - Weekly reports

---

## Pitfalls

### 1. Assuming systemd for everything
Be:A Studio uses **crontab**, not systemd. Always check `crontab -l` before assuming systemd services exist.

### 2. Missing Hermes cron status
Hermes cron jobs are separate from crontab. Use `cronjob action=list` to see Hermes-managed jobs (currently only gstack auto-update).

### 3. Silent failures in crontab
Crontab jobs redirect to logs but don't notify on failure. **Always check the log file** to verify execution, not just that the cron exists.

### 4. Segfault recovery required
Be:A Studio's daily job **requires manual re-execution** when it segfaults. Checking the log alone won't fix it—re-run the script.

### 5. Timezone confusion
User's crontab uses **UTC for scheduling** but logs show KST times in comments. Check both:
- Schedule in crontab: `30 5 * * *` = 05:30 UTC
- Log comments: `# Be:A Studio 일일 콘텐츠 수집 (매일 05:30)` = 05:30 KST

---

## Common Tasks

### Add new crontab job
```bash
crontab -e  # Edit with default editor
```

Format:
```cron
# Comment describing the job (KST time preferred)
MM HH * * * cd /path/to/project && command >> ~/.pm_logs/job.log 2>&1
```

### Database-driven cleanup automation

When implementing cleanup jobs for completed work, use this safety pattern:

**Workflow**: Check completion status → Verify backup exists → Delete local files

**Key principles:**
- Never delete without backup verification
- Check database/app state, not just file age
- Log every deletion with verification proof
- Handle multiple project types with different logic
- Monitor disk space for critical storage situations

**Pattern implementation:**
1. Query database for completion markers (e.g., `drive_url IS NOT NULL` for uploaded songs)
2. For each completed item:
   - Check if backup exists in Google Drive (`rclone ls gdrive:backup/path`)
   - If no backup: create it first (`rclone copy local_file gdrive:backup/`)
   - Delete local file (`rm local_file`)
   - Log action with confirmation
3. Also clean up old temporary files (7+ days old)
4. Report disk usage before/after and alert if critically full (>95%)

**Example cron entry:**
```cron
# 작업 완료 파일 정리 — 매일 저녁 10시
0 22 * * * /usr/bin/python3 /home/window11/scripts/cleanup_completed_files.py >> /home/window11/.pm_logs/cleanup_$(date +\\%Y\\%m\\%d).log 2>&1
```

**Reference implementation**: `references/cleanup-automation-pattern.md` (includes production example: `/home/window11/scripts/cleanup_completed_files.py`)
**Cache cleanup pattern**: `references/cache-cleanup-pattern.md` (Hermes, npm, uv, camoufox cache management)

### Verify cron job executed
1. Check log exists: `ls -la ~/.pm_logs/job.log`
2. Check recent entries: `tail -50 ~/.pm_logs/job.log`
3. Check for errors: `grep -i error ~/.pm_logs/job.log`

### Debug failed cron job
1. Manually run the command:
   ```bash
   cd /path/to/project && bash script.sh
   ```
2. Check for path issues (cron has limited PATH)
3. Check environment variables (cron has minimal env)
4. Verify log redirection syntax (`>>` not `>`, `2>&1` included)

### Monitor cron job performance
```bash
# Track execution time
grep "^\\[" ~/.pm_logs/be_a_studio_daily.log | tail -20
```

### Cache cleanup for disk space management
When disk space is low (especially on Windows C: drive), clean up caches to free space:

**Quick cache cleanup**:
```bash
# Check cache sizes
du -sh ~/.hermes/checkpoints/legacy-* ~/.npm/_cacache ~/.cache/uv ~/.cache/camoufox

# Run automated cleanup script
bash /home/window11/scripts/cleanup_c_drive.sh
```

**Individual cache cleanup**:
```bash
# Hermes legacy checkpoints (9.8GB+)
hermes checkpoints clear-legacy --force

# npm cache (3GB+)
npm cache clean --force

# uv cache (1GB+)
uv cache clean

# camoufox cache (1.4GB+)
rm -rf ~/.cache/camoufox
```

**Windows C: drive recovery**:
```bash
# After cleanup, if Windows still shows 100% usage, restart WSL
# From Windows PowerShell:
wsl --shutdown
```

**Schedule periodic cleanup**:
```bash
# Add to crontab for monthly cleanup (1st of month at 03:00)
0 3 1 * * bash /home/window11/scripts/cleanup_c_drive.sh >> /home/window11/.pm_logs/cache_cleanup_$(date +\\%Y\\%m\\%d).log 2>&1
```

**Reference**: `references/cache-cleanup-pattern.md` - Detailed patterns and safety considerations for cache cleanup.

### Find all crontab jobs for a project
```bash
crontab -l | grep -i project-name
```

---

## References

- `references/be-a-studio-segfault.md` - Detailed error context and recovery procedures for the enrich_news.py segfault
- `references/cron-inventory.md` - Complete inventory of all cron jobs with schedules and log locations
- `references/cleanup-automation-pattern.md` - Database-driven cleanup automation pattern with backup verification
- `references/cache-cleanup-pattern.md` - Cache cleanup patterns for Hermes, npm, uv, camoufox with WSL/Windows considerations

## Scripts

- `scripts/verify-cron-status.sh` - Interactive verification script (run with `bash ~/.hermes/skills/devops/cron-management/scripts/verify-cron-status.sh`)
- `../../scripts/cleanup_c_drive.sh` - Cache cleanup for Hermes, npm, uv, camoufox (15GB+ space recovery)
- `../../scripts/cleanup_completed_files.py` - Database-driven file cleanup with Google Drive backup verification
