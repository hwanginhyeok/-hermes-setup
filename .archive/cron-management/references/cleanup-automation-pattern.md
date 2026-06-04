# Database-Driven Cleanup Automation Pattern

Safety-first pattern for cleaning up completed work files after backup verification.

## Problem Statement

After projects complete work (YouTube uploads, video renders, data processing), temporary files accumulate and consume disk space. Simple time-based deletion is risky—files might still be needed.

## Solution Pattern

### Three-Phase Workflow

**Phase 1: Identify completed work**
- Query application database for completion markers
- Examples: `youtube_url IS NOT NULL`, `status = 'complete'`, final output exists
- Get list of safe-to-delete files

**Phase 2: Verify backup exists**
- Check Google Drive for backup: `rclone ls gdrive:backup/path/file.ext`
- If missing, create backup first: `rclone copy local_file gdrive:backup/path`
- Log backup confirmation

**Phase 3: Safe deletion**
- Delete local file: `rm local_file`
- Log deletion with verification proof
- Report total files cleaned and space freed

## Implementation Template

```python
#!/usr/bin/env python3
"""Database-driven cleanup with backup verification"""

import sqlite3
import subprocess
from pathlib import Path

# Configuration
DB_PATH = "/path/to/project/data.db"
BACKUP_PATH = "gdrive:project/backups"
LOG_FILE = "/home/user/.pm_logs/cleanup_YYYYMMDD.log"

def check_gdrive_file(remote_path):
    """Check if file exists in Google Drive"""
    result = subprocess.run(
        ['rclone', 'ls', f'gdrive:{remote_path}'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0 and bool(result.stdout.strip())

def backup_to_gdrive(local_file, remote_path):
    """Backup file to Google Drive"""
    result = subprocess.run(
        ['rclone', 'copy', local_file, f'gdrive:{remote_path}'],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def cleanup_completed_items():
    """Main cleanup workflow"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query for completed items
    cursor.execute("""
        SELECT song_id, local_path 
        FROM songs 
        WHERE status = 'complete' 
        AND (youtube_url IS NOT NULL AND youtube_url != '')
    """)
    
    completed_items = cursor.fetchall()
    deleted_count = 0
    
    for item_id, local_path in completed_items:
        if not local_path:
            continue
            
        local_file = Path(local_path)
        if not local_file.exists():
            continue
        
        # Check backup
        gdrive_path = f"{BACKUP_PATH}/{item_id}.mp3"
        
        if not check_gdrive_file(gdrive_path):
            # Create backup first
            if backup_to_gdrive(str(local_file), gdrive_path):
                os.remove(str(local_file))
                deleted_count += 1
        else:
            # Already backed up, safe to delete
            os.remove(str(local_file))
            deleted_count += 1
    
    conn.close()
    return deleted_count

if __name__ == "__main__":
    deleted = cleanup_completed_items()
    print(f"Deleted {deleted} files")
```

## Project-Specific Examples

### Music Lab (Suno songs)
- **Completion marker**: `suno_songs.drive_url IS NOT NULL` (note: NOT `youtube_url`)
- **Database**: `data/music-lab.db`, table `suno_songs`
- **File location**: `data/suno/{song_id}.mp3`
- **Backup path**: `gdrive:music-lab/backups/{song_id}.mp3`
- **Also cleans**: 7+ day old Suno files in `data/suno/`
- **Pitfall**: Column names vary—use `PRAGMA table_info()` to verify schema

### My Politics Stats (Rendered audio)
- **Completion marker**: Final video exists (`R-08-final.mp4` or `R-08.mp4`)
- **File location**: `remotion/out/audio/R-08/*.mp3`
- **Backup path**: `gdrive:my-politics-stats/backups/audio/{filename}`
- **Also cleans**: 7+ day old temporary files in `remotion/out/*.tmp`
- **Pitfall**: Don't delete audio if final video doesn't exist

### Generic Pattern
- **Completion marker**: Whatever your app uses to mark "done"
- **File location**: Where temporary files live
- **Backup path**: `gdrive:project-name/backups/{category}/{filename}`
- **Also cleans**: Age-based old temp files (7+ days typical)

## Cron Registration

```bash
# Add to crontab
crontab -e

# Entry (runs daily at 22:00)
0 22 * * * /usr/bin/python3 /home/user/scripts/cleanup_script.py >> /home/user/.pm_logs/cleanup_$(date +\%Y\%m\%d).log 2>&1
```

## Safety Checks

1. **Never delete without backup verification**
2. **Log every action** with timestamps and file paths
3. **Report disk usage before/after** for verification
4. **Test manually first** before scheduling as cron
5. **Handle errors gracefully**—log and continue, don't crash on one file

## Production Example

**Full implementation**: `/home/window11/scripts/cleanup_completed_files.py`

This production script handles:
- Multi-project cleanup (Music Lab + Politics Stats)
- Database-driven completion detection
- Google Drive backup verification
- Cross-filesystem scanning (Linux + WSL Windows)
- Comprehensive logging with timestamps
- Disk usage reporting before/after
- Graceful error handling

**Key features**:
- Uses `sqlite3` for Music Lab database queries
- Uses `subprocess` for rclone operations
- Implements `datetime.timedelta` for age-based cleanup
- Generates daily log files with date stamps
- Reports cleanup statistics (files deleted, space freed)

**Cron entry**:
```cron
# 작업 완료 파일 정리 — 매일 저녁 10시
0 22 * * * /usr/bin/python3 /home/window11/scripts/cleanup_completed_files.py >> /home/window11/.pm_logs/cleanup_$(date +\\%Y\\%m\\%d).log 2>&1
```

## Monitoring

Check cleanup effectiveness:
```bash
# View recent cleanup logs
tail -50 ~/.pm_logs/cleanup_*.log

# Check disk usage
df -h /home/user

# Verify Google Drive backups
rclone ls gdrive:project/backups/
```

## Disk Space Alerting

When scanning for cleanup candidates, also check for critical disk space:

```python
def check_disk_space(path, threshold_percent=95):
    """Check if disk space is critically low"""
    result = subprocess.run(['df', '-h', path], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    if len(lines) >= 2:
        usage_line = lines[1]
        usage_percent = int(usage_line.split()[4].replace('%', ''))
        if usage_percent >= threshold_percent:
            log(f"⚠️ CRITICAL: Disk space at {usage_percent}% on {path}")
            return True
    return False

# Usage in cleanup script
if check_disk_space('/mnt/c', threshold_percent=95):
    log("Windows C: drive critically full - prioritize cleanup")
```

**Real-world discovery**: Windows C: drive was at 99.4% usage (237GB/238GB) during cleanup scan. This indicates cleanup automation should prioritize Windows filesystem monitoring.

## Recovery

If wrong files were deleted:
1. Check Google Drive backup: `rclone ls gdrive:project/backups/`
2. Restore from backup: `rclone copy gdrive:project/backups/file.mp3 ./`
3. Update database if needed to mark as not-completed

## Key Takeaways

- **Database state drives cleanup**, not just file age
- **Backup verification is mandatory** before deletion
- **Project-specific logic** (completion markers vary)
- **Graceful error handling**—one failure shouldn't stop all cleanup
- **Logging for audit trail**—what was deleted and why

## Advanced Patterns

### Cross-Filesystem Scanning (WSL + Windows)

When running in WSL, also scan Windows filesystems for cleanup opportunities:

```python
import subprocess
from pathlib import Path

# Windows paths via WSL mount
WINDOWS_PATHS = [
    "/mnt/c/Users/username/Downloads",
    "/mnt/c/Users/username/Desktop",
    "/mnt/c/Users/username/Documents",
    "/mnt/d/",  # D: drive if exists
]

def scan_windows_filesystem():
    """Scan Windows filesystem for large files"""
    for win_path in WINDOWS_PATHS:
        if not Path(win_path).exists():
            continue
            
        # Find large audio/PDF files
        subprocess.run([
            'find', win_path,
            '-type', 'f',
            '(',
            '-name', '*.mp3', '-o',
            '-name', '*.pdf', '-o',
            '-name', '*.wav',
            ')',
            '-size', '+1M',
            '-exec', 'ls', '-lh', '{}', ';'
        ])
```

**Pitfall**: Windows filesystem access via WSL has performance overhead. Limit scans to specific directories and use file size filters.

### Database Schema Verification

Never assume database schema—verify column names before querying:

```python
def verify_schema(conn, table_name, expected_columns):
    """Verify database has expected columns"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    actual_columns = {col[1] for col in cursor.fetchall()}
    
    missing = set(expected_columns) - actual_columns
    if missing:
        raise ValueError(f"Missing columns in {table_name}: {missing}")
    
    return actual_columns

# Usage
conn = sqlite3.connect(DB_PATH)
columns = verify_schema(conn, 'suno_songs', ['song_id', 'drive_url', 'status'])
cursor.execute(f"SELECT {','.join(columns)} FROM suno_songs WHERE status = 'complete'")
```

**Real-world issue**: Template assumed `youtube_url` column, but actual schema uses `drive_url`. Schema verification prevents `OperationalError: no such column` errors.