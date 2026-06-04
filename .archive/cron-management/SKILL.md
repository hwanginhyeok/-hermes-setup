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
| **Hermes cron** | AI-driven scheduled tasks (via `hermes cron`) | `hermes cron list` | Delivered to target (local/email) |
| **Hermes Gateway** | REQUIRED for Hermes cron to work | `hermes gateway status` | `~/.hermes/logs/gateway.log` |
| **crontab** | Traditional Unix scheduled jobs | `crontab -l` | `~/.pm_logs/<name>.log` |
| **systemd timers** | Service-level recurring tasks | `systemctl --user list-units --type=service` | `journalctl -u <service>` |

---

## Quick Verification Workflow

When asked to verify cron execution status:

1. **Check Hermes Gateway status** (CRITICAL - Hermes cron won't work without it)
   ```bash
   hermes gateway status
   # If "not running": Hermes cron jobs won't fire
   # Start with: tmux new -s hermes 'hermes gateway run'
   ```

2. **List all Hermes cron jobs**
   ```bash
   hermes cron list
   ```
   Check: `next_run_at`, `last_run_at`, `last_status`
   
   **⚠️ Common issue**: Gateway not running = jobs don't execute
   - System cron (crontab) works independently
   - Hermes cron requires `hermes gateway run` in background
   - Check logs show "Gateway is not running" → jobs won't fire

3. **List traditional crontab**
   ```bash
   crontab -l
   ```
   Look for: scheduled commands, log file paths

4. **Check crontab logs** (log pattern: `~/.pm_logs/<name>.log`)
   ```bash
   tail -50 ~/.pm_logs/be_a_studio_daily.log
   # or search by date
   grep "2026051[0-9]" ~/.pm_logs/be_a_studio_daily.log
   ```

5. **Check systemd services** (if applicable)
   ```bash
   systemctl --user list-units --type=service
   systemctl --user status <service-name>
   ```

---

## Current Cron Inventory

### Hermes Cron (7 jobs as of 2026-05-20)

**Critical**: All Hermes cron jobs require `hermes gateway run` to be active.

| Job Name | Schedule | Script | Deliver | Purpose |
|----------|----------|--------|---------|---------|
| gstack 자동 업데이트 | 0 6 * * * | gstack-update.sh | local | Update gstack skills |
| 인프라 모니터링 | 0 */6 * * * | infra_monitor.sh | origin | C drive/WSL2 monitoring |
| 주식부자 시황 KR | 13 * * * * | stock_news_kr.sh | local | Korean market news |
| 주식부자 시황 US | 43 * * * * | stock_news_us.sh | local | US market news |
| 주식부자 모닥 브리핑 | 0 6 * * * | stock_briefing_morning.sh | local | Morning briefing |
| 주식부자 이브닝 브리핑 | 0 18 * * * | stock_briefing_evening.sh | local | Evening briefing |
| be-a-studio 일간 작업 | 30 5 * * * | bea_daily.sh | local | Daily content pipeline |

**⚠️ Check**: `hermes gateway status` - if not running, jobs won't fire
**Start**: `tmux send-keys -t hermes:1.1 'hermes gateway run' Enter` or run via `open-all.sh`

**Migration note**: These jobs were migrated from system crontab to Hermes cron for better monitoring and alerting. Original crontab entries have been removed.

### Crontab Jobs (remaining after Hermes cron migration)

**Migration to Hermes cron completed 2026-05-20**: The following jobs remain in system crontab because they either:
- Are not yet migrated to Hermes cron
- Have external dependencies that work better with crontab
- Need to run even if Hermes Gateway is down

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

### 2. Missing Hermes cron status / Gateway confusion
Hermes cron jobs are separate from crontab. Use `hermes cron list` to see Hermes-managed jobs (currently only gstack auto-update).

**⚠️ CRITICAL**: Hermes cron **requires Gateway running** to execute jobs.
- System cron (crontab) works independently via cron daemon
- Hermes cron requires `hermes gateway run` in background
- Check: `hermes gateway status` → "not running" means jobs won't fire
- Start in tmux for persistence: `tmux new -s hermes 'hermes gateway run'`

**Common confusion**: User expects Hermes cron jobs to run automatically, but Gateway is not running.

### 3. Silent failures in crontab
Crontab jobs redirect to logs but don't notify on failure. **Always check the log file** to verify execution, not just that the cron exists.

### 4. Don't trust memory about cron failures
**CRITICAL:** Memory descriptions of cron failures (e.g., "Segfault", "crashes") may be outdated. Always verify actual execution:
- Check recent log timestamps (log files may be weeks old = job not running)
- Check `crontab -l` to confirm job is actually registered
- Check file permissions (`ls -la script.py` - should be 755 for executables)

**False positive example:** Memory said "enrich_news.py Segfault" but investigation revealed:
- No recent logs (3 weeks old)
- No cron entry registered
- Wrong permissions (664 instead of 755)
- **Actual issue:** Job wasn't running at all, not a Segfault

### 5. Segfault recovery required
Be:A Studio's daily job **requires manual re-execution** when it segfaults. Checking the log alone won't fix it—re-run the script.

### 6. Script path requirements for Hermes cron
Hermes cron only accepts **relative paths** under `~/.hermes/scripts/`. Absolute paths will fail with:
```
Script path must be relative to ~/.hermes/scripts/. Got absolute or home-relative path: '/absolute/path'
```

**Fix**: Copy script to `~/.hermes/scripts/` and use filename only:
```bash
cp /path/to/script.sh ~/.hermes/scripts/
hermes cron create "0 2 * * *" "desc" --script "script.sh"
```

### 7. Deliver target selection
- Use `deliver=origin` for alerts requiring PM attention (disk space, critical failures)
- Use `deliver=local` for routine logging (news collection, briefings)
- `origin` sends to PM session, `local` only writes to logs

### 8. Timezone confusion
User's crontab uses **UTC for scheduling** but logs show KST times in comments. Check both:
- Schedule in crontab: `30 5 * * *` = 05:30 UTC
- Log comments: `# Be:A Studio 일일 콘텐츠 수집 (매일 05:30)` = 05:30 KST

---

## Common Tasks

### Add new Hermes cron job
```bash
# Script must be in ~/.hermes/scripts/
hermes cron create "0 */2 * * *" "작업 설명" --name "작업명" --script "script.sh" --no-agent --deliver "origin"
```

**Deliver targets**:
- `origin`: Send to PM session (for alerts requiring action)
- `local`: Log only (no notification)
- `telegram`: Send to Telegram via pm-bot

**Script requirements**:
- Must be in `~/.hermes/scripts/` (relative path only)
- Absolute paths will fail
- Use `--no-agent` for scripts without LLM involvement

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
