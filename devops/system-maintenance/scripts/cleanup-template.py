#!/usr/bin/env python3
"""
Template for automated file cleanup with backup verification
Usage: Copy this script and customize for your specific project needs
"""

import os
import subprocess
import sqlite3
from datetime import datetime
from pathlib import Path

# ============ PROJECT-SPECIFIC CONFIGURATION ============
# Modify these for each project

PROJECT_NAME = "project-name"
DB_PATH = "/path/to/database.db"
LOCAL_FILES_DIR = "/path/to/local/files"
GDRIVE_REMOTE = "gdrive:backups/project-name/"

# Query to find completed work
COMPLETED_QUERY = """
    SELECT id, file_path, backup_path 
    FROM files_table 
    WHERE status = 'complete' 
    AND backup_verified = TRUE
"""

# ============ CORE FUNCTIONS ============

def log(message):
    """Unified logging with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def get_work_complete_items():
    """Query database for work that is complete"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(COMPLETED_QUERY)
    items = cursor.fetchall()
    conn.close()
    
    log(f"Found {len(items)} completed items")
    return items

def verify_gdrive_backup(remote_path):
    """Check if file exists on Google Drive"""
    try:
        result = subprocess.run(
            ['rclone', 'ls', f'gdrive:{remote_path}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except Exception as e:
        log(f"Google Drive verification failed: {e}")
        return False

def backup_to_gdrive(local_path, remote_path):
    """Copy file to Google Drive"""
    try:
        result = subprocess.run(
            ['rclone', 'copy', local_path, f'gdrive:{remote_path}'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            log(f"✅ Backup successful: {local_path} → {remote_path}")
            return True
        else:
            log(f"❌ Backup failed: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ Backup error: {e}")
        return False

def cleanup_completed_items():
    """Main cleanup function"""
    log(f"=== {PROJECT_NAME} cleanup started ===")
    
    # Get completed work
    items = get_work_complete_items()
    
    deleted_count = 0
    backup_count = 0
    
    for item_id, local_path, remote_path in items:
        if not local_path:
            continue
            
        local_file = Path(local_path)
        if not local_file.exists():
            log(f"⚠️  Local file not found: {local_file}")
            continue
        
        # Check if backup exists
        if not verify_gdrive_backup(remote_path):
            log(f"📦 No backup found, creating: {remote_path}")
            if backup_to_gdrive(str(local_file), remote_path):
                backup_count += 1
            else:
                log(f"⏭️  Skipping due to backup failure")
                continue
        else:
            log(f"✓ Backup verified: {remote_path}")
        
        # Delete local file
        try:
            file_size = local_file.stat().st_size
            os.remove(str(local_file))
            log(f"🗑️  Deleted: {local_file} ({file_size/1024/1024:.1f} MB)")
            deleted_count += 1
        except Exception as e:
            log(f"❌ Delete failed: {e}")
    
    # Summary
    log(f"=== Cleanup complete ===")
    log(f"Backups created: {backup_count}")
    log(f"Files deleted: {deleted_count}")
    
    # Disk space check
    log("Current disk usage:")
    subprocess.run(['df', '-h', '/home'])

if __name__ == "__main__":
    cleanup_completed_items()
