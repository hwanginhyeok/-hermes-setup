# Cleanup Automation Patterns

## File Cleanup Template

This template shows the pattern for creating automated cleanup scripts that verify work completion and backup before deletion.

### Core Pattern
```python
#!/usr/bin/env python3
"""
Automated file cleanup with backup verification
Pattern: Check work status → Backup → Verify → Delete
"""

def cleanup_completed_files():
    """Main cleanup function following safety-first pattern"""
    
    # 1. Verify work completion (database check)
    completed_items = get_completed_from_db()
    
    for item in completed_items:
        local_file = item.local_path
        
        # 2. Backup to remote storage
        gdrive_path = f"backups/{item.id}.mp3"
        backup_to_gdrive(local_file, gdrive_path)
        
        # 3. Verify backup exists
        if check_gdrive_file(gdrive_path):
            # 4. Only then delete local file
            os.remove(local_file)
            log(f"Deleted verified: {local_file}")

def check_gdrive_file(remote_path):
    """Verify file exists on Google Drive"""
    result = subprocess.run(
        ['rclone', 'ls', f'gdrive:{remote_path}'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0 and bool(result.stdout.strip())

def backup_to_gdrive(local_file, remote_path):
    """Copy file to Google Drive"""
    subprocess.run(
        ['rclone', 'copy', local_file, f'gdrive:{remote_path}'],
        capture_output=True,
        text=True
    )
```

### Work Completion Indicators

**Music projects** (Music Lab, audio files):
- `suno_songs` table: `status='complete' AND youtube_url IS NOT NULL`
- Final file exists: `*-final.mp4`, `*-merged.mp3`
- Local path populated in database

**Video/rendering projects** (My Politics Stats):
- Final rendered video exists: `R-08-final.mp4`
- Directory contains both video and audio files
- Upload/sync completed flag set

**Blog/web projects** (Insung Blog, Be:A Studio):
- Article published status in database
- Images uploaded to cloud
- Post confirmed visible on platform

## Disk Space Hogs (Discovered 2026-05-15)

| Item | Size | Cleanup Command | Frequency |
|-------|-------|----------------|------------|
| Hermes legacy checkpoints | 9.8GB | `hermes checkpoints clear-legacy -f` | Monthly |
| npm cache | 1.8GB | `npm cache clean --force` | Weekly |
| npx cache | 1.3GB | `rm -rf ~/.npm/_npx` | Weekly |
| uv cache | 946MB | `uv cache clean` | Monthly |
| camoufox cache | 1.4GB | `rm -rf ~/.cache/camoufox` | Monthly |
| Suno downloads | Variable | Custom script | Daily |

## Cron Scheduling Best Practices

**Low-impact windows**:
- 22:00-23:00 (post-work hours)
- 03:00-05:00 (early morning)
- Avoid 09:00-18:00 (peak work hours)

**Log file naming**:
```bash
# Include date for automatic rotation
cleanup_$(date +\%Y\%m\%d).log
memory_update_$(date +\%Y\%m\%d).log
```

**Error handling**:
```bash
# Redirect both stdout and stderr
2>&1

# Use `set -e` to stop on errors
set -e

# But use `|| true` for non-critical failures
find . -name "*.tmp" -delete || true
```

## Verification Commands

After cleanup, verify systems work:
```bash
# Check disk space
df -h /home

# Restart critical services
systemctl --user restart blog-api blog-worker

# Test project functionality
cd ~/insung_blog && .venv/bin/python main.py --run-once --dry-run
```

## Session-Discovered Issues

### Hermes Cleanup Interactive Prompt
**Problem**: `hermes checkpoints clear-legacy` prompts for confirmation, hangs in cron
**Solution**: Always use `-f` flag for force mode
```bash
# ❌ Wrong for automation
hermes checkpoints clear-legacy

# ✅ Right for cron
hermes checkpoints clear-legacy -f
```

### WSL Disk Space Cache
**Problem**: `df -h` shows 100% even after 15GB freed
**Cause**: WSL caches disk usage, doesn't reflect immediately
**Solution**: Need `wsl --shutdown` to see actual space
**Note**: Inform user, but don't require immediate action
