# Complete Cron Job Inventory

**Last updated:** 2026-05-14

## Hermes Cron (1 job)

| Job ID | Name | Schedule | Script | Status |
|--------|------|----------|---------|--------|
| 0346a5f2559c | gstack 자동 업데이트 | Daily 06:00 | `bash ~/.hermes/skills/gstack-update.sh` | Active, never executed |

## Traditional Crontab (20+ jobs)

### Project Manager

| Schedule | Script | Log |
|----------|--------|-----|
| 0 7 * * * | `daily_report.py` | `~/.pm_logs/daily_YYYYMMDD.log` |
| 0 22 * * 0 | `weekly_report.py` | `~/.pm_logs/weekly_YYYYMMDD.log` |
| 0 0 * * * | `overnight_runner.py` | `~/.pm_logs/overnight_YYYYMMDD.log` |
| 0 * * * * | `service_health.py` | `~/.pm_logs/service_health.log` |
| 0 3 * * 0 | `log_rotate.sh` | `~/.pm_logs/log_rotate.log` |

### Stock Analysis

| Schedule | Script | Log | Notes |
|----------|--------|-----|-------|
| 0 21 * * * | `run_briefing.sh morning` | `logs/briefing_cron.log` | 06:00 KST |
| 0 9 * * * | `run_briefing.sh evening` | `logs/briefing_cron.log` | 18:00 KST |
| 0 * * * * | `collect_and_classify.py` | `logs/news_collect.log` | Hourly |
| 10 * * * * | `update_geoinvest.py` | `logs/geoinvest_update.log` | |
| 5 * * * * | `update_stockinvest.py` | `logs/stockinvest_update.log` | |
| 0 4 * * * | `review_entities.py` | `logs/entity_review.log` | |
| 30 20 * * * | `deep_analysis.py` | `logs/deep_analysis.log` | 05:30 KST |
| 30 8 * * * | `deep_analysis.py` | `logs/deep_analysis.log` | 17:30 KST |
| 0 8 * * 0 | tmux send-keys "주간 분석 해줘..." | - | Sunday 08:00 KST |
| 0 8 * * * | `earn_reporter.py` | `~/.pm_logs/earn_reporter_YYYYMMDD.log` | |
| 0 10 * * * | `collect_delivery_signals.py` | `~/.pm_logs/delivery_signals.log` | |

### Be:A Studio

| Schedule | Script | Log | Notes |
|----------|--------|-----|-------|
| 30 5 * * * | `scripts/run_daily.sh` | `~/.pm_logs/be_a_studio_daily.log` | **Known segfault issue** |
| 0 6 * * * | `scripts/feed_health_check.py` | `~/.pm_logs/feed_health.log` | |
| 30 3 * * * | `scripts/cleanup_pipeline_artifacts.py` | `~/.pm_logs/bea_cleanup.log` | |

### 인성이 블로그 (insung_blog)

| Schedule | Script | Log | Notes |
|----------|--------|-----|-------|
| 0 5 * * * | `nightly_healthcheck.py` | `~/.pm_logs/nightly_healthcheck.log` | |
| */5 * * * * | `scripts/server_health.sh --quiet` | `~/.pm_logs/insung_health_cron.log` | Prod health |
| 0 * * * * | `scripts/regression_cron.sh --quiet` | `~/.pm_logs/insung_regression_cron.log` | Hourly |
| 5 * * * * | `scripts/monitor_bot_run_log.py` | `~/.pm_logs/monitor_bot_run.log` | |
| 0 */6 * * * | `scripts/run_all_scrapers.py` | `~/.pm_logs/insung_scraper_cron.log` | |
| */30 * * * * | `scripts/webstore_status_check.sh` | (inline) | |
| 0 9 * * * | `scripts/photo_pipeline.py plan` | `~/.pm_logs/photo_pipeline.log` | |

### Supabase Retention

| Schedule | Script | Log | Notes |
|----------|--------|-----|-------|
| 15 * * * * | `scripts/cleanup_expired_campaigns.py` | `~/.pm_logs/cleanup_expired.log` | |
| 0 3 * * * | `scripts/cleanup_bot_run_log.py` | `~/.pm_logs/cleanup_bot_run.log` | 14+ days |
| 0 4 * * 0 | `scripts/cleanup_visit_log.py` | `~/.pm_logs/cleanup_visit.log` | Sunday, 30+ days |
| 30 4 * * 0 | `scripts/cleanup_rejected_comments.py` | `~/.pm_logs/cleanup_rejected.log` | Sunday, 30+ days |
| 0 6 * * * | `scripts/monitor_db_usage.py` | `~/.pm_logs/monitor_db.log` | |

### Other Projects

| Schedule | Script | Log | Notes |
|----------|--------|-----|-------|
| 7 9-23 * * * | `scripts/silence_watch.py` | `~/.pm_logs/silence_watch.log` | insung_blog |
| 1 9 * * * | `scripts/token_guard.py` | `logs/token_guard.log` | music-lab |
| @reboot | `open-all.sh` | `~/.pm_logs/tmux_boot.log` | project-manager |

## Log Location Conventions

- **Rolling logs:** `~/.pm_logs/<name>.log`
- **Date-stamped:** `~/.pm_logs/<name>_YYYYMMDD.log`
- **Stock logs:** `~/stock/logs/<name>.log`
- **Be:A Studio logs:** `~/.pm_logs/be_a_studio_daily.log` (crontab) or `~/be-a-studio/logs/<name>.log` (project-specific)

## Timezone Notes

- Crontab schedules are in **UTC**
- Comments in crontab show **KST** times for reference
- Check both when debugging schedule issues
