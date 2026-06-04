# Monitoring and Alerting Workflow

## Current Setup (2026-05-20)

### Active Monitors

**System Cron Jobs** (via `crontab -l`):
```bash
# Every 6 hours: Check cron health
0 */6 * * * /usr/bin/python3 /home/window11/project-manager/scripts/cron_health_monitor.py >> ~/.pm_logs/cron_health.log 2>&1

# Daily 09:00: Send Telegram alert if issues found
0 9 * * * /usr/bin/python3 /home/window11/project-manager/scripts/cron_health_monitor.py --telegram >> ~/.pm_logs/cron_health_alert.log 2>&1
```

**What's monitored** (`cron_health_monitor.py`):
- 주식부자 시황 수집 (KR/US) - every 2h
- 주식부자 아침/저녁 브리핑 - every 36h
- PM MD 크기 체크 - every 36h
- PM WSL 백업 - every 36h
- be-a-studio 일간 작업 - every 36h
- be-a-studio 클린업 - every 36h

**What's NOT monitored** (gaps identified):
- ❌ C drive usage (WSL2 VHDX size)
- ❌ WSL2 internal disk usage
- ❌ Windows Temp folder size
- ❌ Hermes Gateway status (jobs won't fire if gateway down)
- ❌ Actual job completion (only checks log timestamps)

### Alerting Chain

```
cron_health_monitor.py detects issue
    ↓
pm_bot.py send_message()
    ↓
Telegram to user (CHAT_ID from ~/x-bot/.env)
    ↓
User sees alert in Telegram
    ↓
User types command to PM session via pm-bot
    ↓
PM (claude in PM:1.1) processes command
    ↓
PM delegates to project session or fixes directly
    ↓
PM sends result back with ===PM-END=== marker
    ↓
pm-bot captures and forwards to Telegram
```

### Known Issues

**1. Alert comes AFTER problem exists**
- Cron health monitor checks every 6h
- Daily Telegram alert at 09:00
- **Gap**: Issue could exist up to 24h before detection

**2. No proactive disk monitoring**
- C drive can hit 90%+ before alert
- WSL2 VHDX bloat not monitored
- **Symptom**: User notices "C drive suddenly full"

**3. Hermes cron confusion**
- System cron (crontab) works independently
- Hermes cron requires gateway running
- Gateway often not running → jobs don't fire
- **Check**: `hermes gateway status`

**4. Work completion not verified**
- Only checks log file timestamps
- Doesn't verify actual work done (DB changes, files created)
- False positives: script runs but fails silently

## Recommended Improvements

### Add Disk Usage Monitoring

**Extend `cron_health_monitor.py`**:
```python
DISK_CHECKS = {
    "WSL home": {
        "path": "/home/window11",
        "threshold_percent": 90,
        "critical": True,
    },
    "C drive": {
        "path": "/mnt/c",
        "threshold_percent": 90,
        "critical": True,
    },
    "WSL2 VHDX": {
        "path": "/mnt/c/Users/window11/AppData/Local/wsl",
        "threshold_gb": 70,  # Before hitting C drive limit
        "critical": True,
    },
}
```

### Add Hermes Gateway Check

**In cron_health_monitor.py**:
```python
def check_hermes_gateway():
    result = subprocess.run(
        ["hermes", "gateway", "status"],
        capture_output=True,
        text=True,
    )
    if "not running" in result.stdout.lower():
        return {
            "name": "Hermes Gateway",
            "status": "CRITICAL",
            "reason": "Gateway not running - Hermes cron jobs won't fire",
            "fix": "Run: tmux send-keys -t hermes:1.1 'hermes gateway run' Enter",
        }
    return None
```

### Background Task Completion Notification

**For long-running tasks**:
```python
# In project agent session
terminal(
    "long_running_task.sh",
    background=True,
    notify_on_complete=True,  # Sends notification when done
)
```

**Notification flow**:
1. Task completes
2. Hermes sends notification to gateway
3. Gateway forwards to PM session
4. PM reviews result and sends to Telegram

## Commands Reference

### Check current status
```bash
# All cron health
python3 ~/project-manager/scripts/cron_health_monitor.py

# With Telegram alert
python3 ~/project-manager/scripts/cron_health_monitor.py --telegram

# Hermes jobs
hermes cron list

# Gateway status
hermes gateway status

# Disk usage
df -h /home /mnt/c
du -sh /mnt/c/Users/*/AppData/Local/wsl/
```

### Manual alert test
```bash
# Send test message to Telegram
python3 ~/project-manager/bot/pm_bot.py send "Test message"
```

### Start Hermes Gateway in tmux
```bash
# In hermes session pane1
tmux send-keys -t hermes:1.1 "hermes gateway run" Enter

# Or start new session
tmux new -s hermes 'hermes gateway run'
```

## Log Locations

- Cron health: `~/.pm_logs/cron_health.log`
- Telegram alerts: `~/.pm_logs/cron_health_alert.log`
- PM bot: `~/.pm_logs/pm_bot.log`
- Individual cron logs: `~/.pm_logs/*.log`

## Typical Workflow

1. **User notices issue** (disk full, job not running)
2. **User asks PM via Telegram**: "Why is disk full?"
3. **PM receives message** via pm-bot relay
4. **PM investigates**:
   - Checks disk usage
   - Reviews cron logs
   - Identifies root cause
5. **PM fixes or delegates**:
   - Direct fix if simple
   - Delegates to project session if complex
6. **PM reports back** with ===PM-END===
7. **User sees result** in Telegram

## Future Enhancements

- [ ] Add C drive/WSL2 VHDX size to cron_health_monitor.py
- [ ] Add Hermes Gateway status check
- [ ] Implement proactive threshold alerts (80%, 90%, 95%)
- [ ] Add work completion verification (DB checks, file existence)
- [ ] Dashboard URL for quick status overview
- [ ] Automatic remediation for common issues (cleanup old logs, etc.)
