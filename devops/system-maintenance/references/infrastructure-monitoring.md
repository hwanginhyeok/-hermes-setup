# Infrastructure Monitoring Setup

## Overview

Automated monitoring for critical infrastructure:
- C drive usage (Windows side)
- WSL2 VHDX size
- Windows Temp folder size

## Implementation (2026-05-20)

### Script Location

`~/project-manager/scripts/infra_monitor.sh` → `~/.hermes/scripts/infra_monitor.sh`

### Hermes Cron Registration

```bash
# List job
hermes cron list | grep "인프라 모니터링"

# Job details:
# Name: 인프라 모니터링
# Schedule: 0 */6 * * * (every 6 hours)
# Deliver: origin (PM session)
# Mode: no-agent (script stdout delivered directly)
```

### Thresholds

| Resource | Threshold | Action |
|----------|-----------|--------|
| C drive usage | 90% | Alert to PM + Telegram |
| WSL2 VHDX | 70GB | Warning (compaction recommended) |
| Windows Temp | 10GB | Warning (cleanup recommended) |

## Manual Execution

```bash
# Run manually
~/.hermes/scripts/infra_monitor.sh

# Check log
tail -20 ~/.pm_logs/infra_health.log
```

## Log Format

```
[2026-05-20 21:26:24] C:81% VHDX:76GB Temp:24GB
```

## Alert Flow

1. **Script detects threshold exceeded**
2. **Creates alert in** `~/.pm_logs/infra_alert.log`
3. **Sends Telegram via** `pm_bot.py`
4. **PM receives alert** via `deliver=origin`

## WSL2 VHDX Issue (2026-05-20 Analysis)

### Problem

- WSL internal usage: 60GB / 1007GB (6%)
- VHDX file size: 77GB
- **Waste: ~17GB** (file doesn't auto-shrink)

### Root Cause

Dynamic VHD behavior:
- Grows when files created
- Does NOT shrink when files deleted
- Requires manual compaction

### Compaction Procedure

```bash
# Step 1: Inside WSL - Zero free space
sudo dd if=/dev/zero of=/zero bs=1M || rm -f /zero
sudo poweroff -f

# Step 2: PowerShell (Admin) - Compact VHDX
wsl --shutdown
Optimize-VHD -Path "C:\Users\window11\AppData\Local\wsl\{GUID}\ext4.vhdx" -Mode Full
```

### Schedule

**Recommendation**: Monthly compaction
- Before compaction: 77GB
- After compaction: ~60GB
- **Savings: ~17GB**

## C Drive Volatility (2026-05-20)

### Fluctuation Causes

1. **WSL2 VHDX growth** (primary)
2. Windows Temp accumulation
3. Windows update caches
4. Application caches (Chrome, etc.)

### Monitoring Strategy

- Check every 6 hours
- Alert at 90% usage
- Recommend cleanup actions

### Cleanup Commands

```bash
# Windows Temp (from WSL)
du -sh /mnt/c/Users/*/AppData/Local/Temp
# Manual cleanup from Windows recommended

# Chrome AI models (3.4GB savings)
rm -rf ~/.config/google-chrome/OptGuideOnDeviceModel/*/weights
rm -rf ~/.config/chrome-suno/OptGuideOnDeviceModel/*/weights
```

## Integration with Hermes Cron

### Prerequisites

1. **Hermes Gateway running**
   ```bash
   hermes gateway status
   # Start if not running: tmux send-keys -t hermes:1.1 "hermes gateway run" Enter
   ```

2. **Script installed**
   ```bash
   ls -l ~/.hermes/scripts/infra_monitor.sh
   ```

3. **Cron job registered**
   ```bash
   hermes cron list | grep "인프라 모니터링"
   ```

### Adding New Checks

Edit `~/.hermes/scripts/infra_monitor.sh`:

```bash
# Add new check
NEW_VALUE=$(some_command)
if [ "$NEW_VALUE" -gt "$THRESHOLD" ]; then
    echo "[$TS] 🟡 New check: ${NEW_VALUE}" >> "$ALERT_LOG"
fi
```

## Troubleshooting

### Job not firing

```bash
# Check gateway status
hermes gateway status

# Check job exists
hermes cron list | grep "인프라"

# Manually run to test
~/.hermes/scripts/infra_monitor.sh
```

### Alerts not sending

```bash
# Check pm_bot.py
python3 ~/project-manager/bot/pm_bot.py send "Test message"

# Check alert log
tail -20 ~/.pm_logs/infra_alert.log
```

### False alerts

- Adjust thresholds in `infra_monitor.sh`
- Add cooldown period to prevent repeated alerts
- Use `find` command with `-mtime` for age-based checks

## Related Documentation

- `wsl2-disk-analysis.md` - Complete WSL2 disk procedures
- `tmux-session-management.md` - Hermes gateway in tmux

## Future Improvements

- [ ] Automatic VHDX compaction scheduling
- [ ] Integration with Windows Task Scheduler for Temp cleanup
- [ ] Historical trend tracking (graph C drive usage over time)
- [ ] Predictive alerts (trend analysis before threshold hit)
