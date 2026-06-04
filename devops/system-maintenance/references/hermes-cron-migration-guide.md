# Hermes Cron Migration Guide

Migrating from system crontab to Hermes cron provides:
- Better monitoring via `hermes cron list`
- Automatic Gateway status checks
- Flexible delivery targets (local, origin, telegram)
- Centralized job management

## Migration Workflow

### 1. Identify crontab jobs to migrate
```bash
crontab -l | grep -v "^#"
```

### 2. Create wrapper scripts in ~/.hermes/scripts/

**Important**: Hermes cron only accepts relative paths under `~/.hermes/scripts/`.

```bash
# Example: Stock news collection
cat > ~/.hermes/scripts/stock_news_kr.sh << 'EOF'
#!/bin/bash
cd /home/window11/stock && python3 scripts/collect_news.py --market kr >> ~/.pm_logs/news_kr.log 2>&1
EOF
chmod +x ~/.hermes/scripts/stock_news_kr.sh
```

### 3. Register with Hermes cron
```bash
hermes cron create "13 * * * *" "주식부자 한국 시황 수집" \
  --name "주식부자 시황 KR" \
  --script "stock_news_kr.sh" \
  --no-agent \
  --deliver "local"
```

**Deliver options**:
- `origin`: Send to PM session (alerts requiring action)
- `local`: Log only (routine jobs)
- `telegram`: Send to Telegram

### 4. Verify job registered
```bash
hermes cron list | grep "주식부자 시황 KR"
```

### 5. Remove from crontab
```bash
crontab -e
# Comment out or remove the migrated line
```

### 6. Ensure Gateway is running
```bash
hermes gateway status
# If not running:
tmux send-keys -t hermes:1.1 "hermes gateway run" Enter
```

## Delivery Target Selection Guide

| Target | Use Case | Example |
|--------|----------|---------|
| `origin` | Alerts requiring PM attention | Disk space >90%, critical failures |
| `local` | Routine logging | News collection, briefings |
| `telegram` | User notifications | Daily reports, alerts |

## Script Template

```bash
#!/bin/bash
# Description: Job description for Hermes cron
# Schedule: CRON_FORMAT
# Created: DATE

# Change to project directory
cd /path/to/project

# Run command with logging
command >> ~/.pm_logs/job.log 2>&1
```

## Migration Example (2026-05-20)

**Before (crontab)**:
```cron
# Korean news collection
13 * * * * cd /home/window11/stock && python3 scripts/collect_news.py --market kr >> ~/.pm_logs/news_kr.log 2>&1
```

**After (Hermes cron)**:
- Script: `~/.hermes/scripts/stock_news_kr.sh`
- Job: `주식부자 시황 KR`
- Schedule: `13 * * * *`
- Deliver: `local`

## Troubleshooting

### Script path error
```
Script path must be relative to ~/.hermes/scripts/
```
**Fix**: Move script to `~/.hermes/scripts/` and use filename only.

### Gateway not running
```
⚠️ Gateway is not running — jobs won't fire automatically.
```
**Fix**: Start gateway in tmux session:
```bash
tmux send-keys -t hermes:1.1 "hermes gateway run" Enter
```

### Job not executing
1. Check Gateway status: `hermes gateway status`
2. Verify job exists: `hermes cron list`
3. Check job logs: `hermes logs --tail 50`
