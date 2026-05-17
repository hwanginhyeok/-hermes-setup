---
name: system-maintenance
description: Automated system maintenance workflows — disk cleanup, file management, project monitoring, and cron automation for development environments.
---

# System Maintenance

> Automated maintenance patterns for development environments — disk space management, file cleanup, project monitoring, and cron-based automation.

## When to Use This Skill

Trigger this skill when:
- "cleanup", "disk space", "memory management" for projects
- "analyze disk usage", "check disk space", "why is disk full"
- "automate cleanup", "cron job", "schedule cleanup"
- "delete old files", "free up space", "reduce storage"
- "monitor project changes", "track file modifications"
- "Google Drive backup verification"
- "WSL2 disk full", "C drive 100%", "move WSL to another drive"

## Core Principles

### 1. Safety-First Deletion Pattern
All automated cleanup follows this sequence:
```
1. Verify work completion (DB queries, file existence checks)
2. Backup to remote storage (Google Drive, S3, etc.)
3. Confirm backup exists (rclone ls, md5 verification)
4. Only then delete local file
```

### 2. Multi-Layer Backup Verification
- **Database**: Check completion status, timestamps, status flags
- **Remote**: Verify file exists on backup location (`rclone ls`)
- **Checksum**: Compare local/remote hashes for critical files

### 3. Scheduled Automation
- **Low-impact times**: Evening (22:00), early morning (03:00)
- **Log rotation**: Prevent log file bloat (7-30 day retention)
- **Error handling**: Don't fail entire job on single file error

## Common Cleanup Patterns

### Music/Audio Files
**Work complete indicators**:
- YouTube URL populated in database
- Final rendered file exists (e.g., `final.mp4`)
- Status field = `complete` / `published`

**Example**:
```python
# Database query for completed work
cursor.execute("""
    SELECT song_id, local_path, drive_url 
    FROM suno_songs 
    WHERE status = 'complete' AND youtube_url IS NOT NULL
""")
```

### Build/Cache Directories
**Safe to delete**:
- `node_modules/.cache`
- `.npm/_cacache`, `.npm/_npx`
- `.cache/uv`, `.cache/pip`
- `.pytest_cache`, `__pycache__`

**Safe cleanup commands**:
```bash
npm cache clean --force
uv cache clean
rm -rf ~/.cache/uv
hermes checkpoints clear-legacy -f
```

### Temporary Files
**Cleanup criteria**:
- Age: 7-30 days
- Pattern: `*.tmp`, `*.temp`, `*.log.old`
- Location: Dedicated temp directories only

## Project Change Monitoring

### Automated Memory Updates
**Pattern for tracking project changes**:

```python
# 1. MD5 hash comparison for change detection
def get_file_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# 2. Compare against previous state
if current_hash != previous_state.get(key):
    changes.append({
        'project': project_name,
        'type': 'file_change',
        'file': filename,
        'timestamp': datetime.now().isoformat()
    })

# 3. Categorize by priority
priority_rules = {
    'HIGH': ['.claude/rules/', 'DIFFICULTY.md'],
    'MEDIUM': ['CLAUDE.md', 'TASK.md', 'CURRENT_TASK.md']
}
```

### Priority Levels
| Priority | Triggers | Action Required |
|-----------|-----------|----------------|
| 🚨 HIGH | Rule files, DIFFICULTY.md | Memory update required |
| 📋 MEDIUM | CLAUDE.md, TASK files | Review in next session |
| ℹ️ LOW | README, documentation | Informational |

## Disk Space Management

### Discovery Phase (Before Cleanup)
**Always start with analysis to identify the actual problem**:
```bash
# 1. Check overall disk health
df -h

# 2. Find largest directories in WSL home
du -sh ~/* 2>/dev/null | sort -hr | head -20

# 3. Check Python package bloat
du -sh ~/.local/lib/python*/site-packages/* 2>/dev/null | sort -hr | head -30

# 4. Check Windows-side WSL2 disk usage (CRITICAL for C drive issues)
du -sh /mnt/c/Users/*/AppData/Local/wsl/ 2>/dev/null
```

**See `references/wsl2-disk-analysis.md` for complete WSL2 disk investigation procedures.**

### Common Space Hogs
| Category | Typical Size | Cleanup Method |
|----------|--------------|----------------|
| Hermes legacy checkpoints | 5-10GB | `hermes checkpoints clear-legacy -f` |
| npm cache | 1-5GB | `npm cache clean --force` |
| Python cache | 500MB-2GB | `uv cache clean`, `pip cache purge` |
| Browser cache | 500MB-3GB | Remove specific cache dirs |
| Build artifacts | 1-10GB | Clean `node_modules/.cache` |

### Verification Steps
1. Check disk usage before cleanup: `df -h /home`
2. Run cleanup
3. Check disk usage after cleanup
4. Verify critical systems still work

## Cron Automation

### Cron Entry Pattern
```bash
# Standard pattern
M H * * * /usr/bin/python3 /path/to/script.py >> /path/to/log_$(date +\%Y\%m\%d).log 2>&1

# Example: Daily cleanup at 22:00
0 22 * * * /usr/bin/python3 /home/window11/scripts/cleanup_completed_files.py >> /home/window11/.pm_logs/cleanup_$(date +\%Y\%m\%d).log 2>&1
```

### Scheduling Best Practices
- **Avoid**: Peak hours (09:00-18:00), system boot time
- **Prefer**: Evening (21:00-23:00), early morning (02:00-05:00)
- **Log files**: Include date in filename, rotate monthly
- **Error capture**: Always include `2>&1` in redirect

## Pitfalls

### ❌ Don't Do These
- **Delete without backup verification**: Always confirm remote backup exists
- **Clear active caches mid-session**: Wait for work to complete
- **Use interactive commands in cron**: Commands that prompt will hang
- **Delete based only on age**: Check completion status first

### ⚠️ Common Issues

**Hermes cleanup hangs**:
```bash
# Wrong: Interactive prompt
hermes checkpoints clear-legacy

# Right: Force mode
hermes checkpoints clear-legacy -f
```

**WSL disk space not reflecting after cleanup**:
- WSL caches disk usage; needs restart to reflect
- Windows side: `wsl --shutdown` to see actual space freed
- VHDX files don't auto-shrink; need manual compaction or export/import

**C drive 100% due to WSL2**:
- WSL2 virtual disk can grow to 100GB+ and doesn't auto-shrink
- Check: `du -sh /mnt/c/Users/*/AppData/Local/wsl/`
- Solution: Move WSL2 to D drive or compact VHDX (see `references/wsl2-disk-analysis.md`)

**PowerShell command failures from WSL**:
- Avoid complex PowerShell pipes from Bash (escaping hell)
- Use simple commands or create .ps1 scripts on Windows side first

**Cron jobs not running**:
- Check cron service: `systemctl status cron`
- Verify crontab: `crontab -l`
- Check logs: `tail -f /var/log/cron.log` or user log file

## Templates and Scripts

Use reference scripts in `scripts/` directory:
- `cleanup-template.py` — Base cleanup script with backup verification
- `memory-monitor.py` — Project change monitoring framework
- `cron-setup.sh` — Cron installation helper

**Reference documents**:
- `references/wsl2-disk-analysis.md` — Complete WSL2 disk investigation and recovery procedures

## Verification

After any maintenance task:
1. **Disk space check**: `df -h /home`
2. **Critical services**: Restart and verify (systemd services)
3. **Project functionality**: Run one test command per project
4. **Log review**: Check for errors in cleanup logs

## Related Skills

- `cron-management` — Cron job lifecycle and debugging
- `kanban-worker` — Worker pool orchestration (for parallel cleanup)
