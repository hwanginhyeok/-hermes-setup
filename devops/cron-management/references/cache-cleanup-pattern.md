# Cache Cleanup Pattern for Disk Space Management

Safe patterns for cleaning up various cache and temporary files to free disk space, with special attention to WSL/Windows hybrid environments.

## Problem Statement

Development environments accumulate cache files (package managers, application caches, legacy checkpoints) that consume significant disk space. Simple deletion of cache directories is safe but requires understanding what each cache does and how to safely clean it.

## Cache Inventory

### Large Cache Sources

| Cache Type | Location | Typical Size | Safe to Delete | Recovery |
|------------|----------|--------------|----------------|----------|
| **Hermes legacy checkpoints** | `~/.hermes/checkpoints/legacy-*` | 9.8GB+ | ✅ Yes (via `hermes checkpoints clear-legacy`) | Not needed (old per-project repos) |
| **npm cache** | `~/.npm/_cacache` | 1-3GB | ✅ Yes (via `npm cache clean`) | Auto-regenerated on next install |
| **npm npx cache** | `~/.npm/_npx` | 1-2GB | ✅ Yes (via `npm cache clean`) | Auto-regenerated |
| **uv cache** | `~/.cache/uv` | 500MB-1GB | ✅ Yes (via `uv cache clean`) | Auto-regenerated on next install |
| **camoufox cache** | `~/.cache/camoufox` | 1-2GB | ✅ Yes (delete directory) | Auto-regenerated |
| **Python pip cache** | `~/.cache/pip` | 100-500MB | ✅ Yes (via `pip cache purge`) | Auto-regenerated |

## Safe Cleanup Patterns

### 1. Hermes Legacy Checkpoint Cleanup

**Context**: Hermes v2 migration moved per-project shadow repos to `legacy-*` directories. These are no longer needed once you're confident in the new single-store system.

**Safe cleanup command**:
```bash
# Check legacy archives
hermes checkpoints list

# View legacy size
du -sh ~/.hermes/checkpoints/legacy-*

# Delete legacy archives (requires confirmation)
hermes checkpoints clear-legacy

# Force deletion (skip confirmation)
hermes checkpoints clear-legacy --force
```

**Verification**:
```bash
# Check remaining checkpoint size
hermes checkpoints list

# Verify all projects still work
hermes checkpoints list | grep "live"
```

**Pitfall**: Don't delete `~/.hermes/checkpoints/store/` - this contains current per-project state (318.9MB vs 9.8GB legacy).

**Real-world example**:
```bash
# Before cleanup
hermes checkpoints list
# Legacy archives (1):
#   legacy-20260512-083334  9.8 GB

# After cleanup
hermes checkpoints clear-legacy --force
# Deleted 1 archive(s), reclaimed 9.8 GB.
```

### 2. npm Cache Cleanup

**Safe cleanup command**:
```bash
# Check cache size
du -sh ~/.npm

# Clean all npm cache
npm cache clean --force

# Verify cleanup
du -sh ~/.npm
```

**What gets cleaned**:
- `~/.npm/_cacache` - Content-addressable cache for package downloads
- `~/.npm/_npx` - npx package cache
- Temporary installation files

**Recovery**: Cache auto-regenerates on next `npm install` or `npx` command. Slight performance impact on first use after cleanup.

### 3. uv Cache Cleanup

**Safe cleanup command**:
```bash
# Check cache size
du -sh ~/.cache/uv

# Clean all uv cache
uv cache clean

# Verify cleanup
du -sh ~/.cache/uv
```

**What gets cleaned**: Compiled wheels, source archives, build artifacts.

**Recovery**: Cache auto-regenerates on next `uv pip install` or `uv sync` command.

### 4. Camoufox Cache Cleanup

**Safe cleanup command**:
```bash
# Check cache size
du -sh ~/.cache/camoufox

# Delete entire cache
rm -rf ~/.cache/camoufox

# Verify cleanup
du -sh ~/.cache/camoufox
```

**What gets cleaned**: Browser profile, cached assets, session data.

**Recovery**: Cache auto-regenerates on next camoufox initialization.

## Automation Script

**Full cache cleanup script**: `/home/window11/scripts/cleanup_c_drive.sh`

```bash
#!/bin/bash
# C 드라이브 공간 확보를 위한 캐시 삭제 스크립트

set -e

echo "=== C 드라이브 공간 확보 시작 ==="

# 시작 전 디스크 사용량
echo "시작 전 디스크 사용량:"
df -h /mnt/c

total_freed=0

# 1. Hermes 레거시 체크포인트 (9.8G)
echo ""
echo "1️⃣ Hermes 레거시 체크포인트 삭제 중..."
if [ -d "$HOME/.hermes/checkpoints/legacy-20260512-083334" ]; then
    size_before=$(du -sh "$HOME/.hermes/checkpoints/legacy-20260512-083334" | cut -f1)
    hermes checkpoints clear-legacy --force
    echo "✅ Hermes 레거시 삭제 완료: ${size_before}"
    total_freed=$((total_freed + 98))
else
    echo "⚠️  Hermes 레거시 폴더 없음"
fi

# 2. npm 캐시 (3.1G)
echo ""
echo "2️⃣ npm 캐시 삭제 중..."
if [ -d "$HOME/.npm/_cacache" ]; then
    size_before=$(du -sh "$HOME/.npm" | cut -f1)
    npm cache clean --force
    echo "✅ npm 캐시 삭제 완료: ${size_before}"
    total_freed=$((total_freed + 31))
else
    echo "⚠️  npm 캐시 폴더 없음"
fi

# 3. uv 캐시 (946M)
echo ""
echo "3️⃣ uv 캐시 삭제 중..."
if command -v uv &> /dev/null; then
    size_before=$(du -sh "$HOME/.cache/uv" 2>/dev/null | cut -f1 || echo "0M")
    uv cache clean
    echo "✅ uv 캐시 삭제 완료: ${size_before}"
    total_freed=$((total_freed + 1))
else
    echo "⚠️  uv 명령어 없음"
fi

# 4. camoufox 캐시 (1.4G)
echo ""
echo "4️⃣ camoufox 캐시 삭제 중..."
if [ -d "$HOME/.cache/camoufox" ]; then
    size_before=$(du -sh "$HOME/.cache/camoufox" | cut -f1)
    rm -rf "$HOME/.cache/camoufox"
    echo "✅ camoufox 캐시 삭제 완료: ${size_before}"
    total_freed=$((total_freed + 14))
else
    echo "⚠️  camoufox 캐시 폴더 없음"
fi

# 종료 후 디스크 사용량
echo ""
echo "종료 후 디스크 사용량:"
df -h /mnt/c

echo ""
echo "=== 총 확보 공간: 약 ${total_freed}GB ==="
echo "✅ 캐시 삭제 완료!"
```

**Usage**:
```bash
chmod +x /home/window11/scripts/cleanup_c_drive.sh
bash /home/window11/scripts/cleanup_c_drive.sh
```

## WSL/Windows Specific Considerations

### C Drive Critical Space Situation

**Symptom**: Windows C: drive shows 100% usage even after cleanup in WSL.

**Cause**: WSL caches filesystem metadata. Space freed in WSL doesn't immediately reflect in Windows.

**Recovery**:
```bash
# From Windows PowerShell (not WSL)
wsl --shutdown

# Restart WSL and check space
wsl
df -h /mnt/c
```

**Real-world example**:
```bash
# After cleanup in WSL
df -h /mnt/c
# C:\\  238G  237G  1.5G 100% /mnt/c

# After WSL restart
df -h /mnt/c
# C:\\  238G  222G  16G  93% /mnt/c  # ~15GB freed
```

### Windows Filesystem Access via WSL

When cleaning Windows paths from WSL:
```bash
# Windows paths are mounted under /mnt/
/mnt/c/              # C: drive
/mnt/d/              # D: drive
/mnt/c/Users/username/  # User profile

# Example: Check Windows Downloads
du -sh /mnt/c/Users/window11/Downloads

# Example: Find large files on Windows
find /mnt/c/Users/window11/Desktop -type f -size +10M -exec ls -lh {} \;
```

**Performance consideration**: Windows filesystem access via WSL has overhead. Use specific directory targeting and file size filters to limit scan time.

## Disk Space Monitoring

### Check Critical Space

```python
import subprocess

def check_disk_space(path, threshold_percent=95):
    """Check if disk space is critically low"""
    result = subprocess.run(['df', '-h', path], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    if len(lines) >= 2:
        usage_line = lines[1]
        usage_percent = int(usage_line.split()[4].replace('%', ''))
        if usage_percent >= threshold_percent:
            print(f"⚠️ CRITICAL: Disk space at {usage_percent}% on {path}")
            return True
    return False

# Usage
if check_disk_space('/mnt/c', threshold_percent=95):
    print("Windows C: drive critically full - prioritize cleanup")
```

### Multi-Filesystem Check

```bash
# Check all major filesystems
df -h /home /mnt/c /mnt/d
```

**Real-world discovery**: Windows C: drive was at 99.4% usage (237GB/238GB) during cleanup scan, making space recovery critical.

## Cron Integration

Add cache cleanup to cron schedule:

```bash
# Add to crontab
crontab -e

# Monthly cache cleanup (1st of month at 03:00)
0 3 1 * * bash /home/window11/scripts/cleanup_c_drive.sh >> /home/window11/.pm_logs/cache_cleanup_$(date +\\%Y\\%m\\%d).log 2>&1
```

**Frequency considerations**:
- **Weekly**: If you do heavy package management
- **Monthly**: If moderate package usage (recommended)
- **Quarterly**: If minimal package usage

## Safety Checklist

Before running cache cleanup:

- [ ] Verify disk space is actually low (`df -h`)
- [ ] Check critical projects aren't in active development
- [ ] Test cleanup commands individually first
- [ ] Verify tool commands exist (`hermes --version`, `npm --version`, `uv --version`)
- [ ] Have WSL restart plan ready (for Windows C: drive)
- [ ] Backup any critical project data

After cleanup:

- [ ] Verify disk space increased
- [ ] Test Hermes projects still work (`hermes checkpoints list`)
- [ ] Test npm install still works
- [ ] Test uv install still works
- [ ] Restart WSL if Windows C: drive still shows 100%

## Pitfalls

### 1. Deleting Hermes Store Instead of Legacy

**Wrong**: `rm -rf ~/.hermes/checkpoints/store/`
**Right**: `hermes checkpoints clear-legacy --force`

The `store/` directory contains current project state (~318MB), while `legacy-*` contains old per-project repos (~9.8GB+).

### 2. Assuming Windows Space Updates Immediately

**Pitfall**: Running cleanup in WSL and expecting Windows disk space to update immediately.

**Reality**: WSL caches filesystem metadata. Windows disk space only updates after `wsl --shutdown` and restart.

### 3. Removing Critical Project Data

**Risk**: Using generic `find` and `rm` without database verification.

**Safety**: Always use database-driven cleanup pattern (see `references/cleanup-automation-pattern.md`) for project files, not cache cleanup pattern.

### 4. Forcing Cleanup During Active Development

**Risk**: Running cache cleanup while installing packages or building projects.

**Safety**: Run cleanup during idle periods or schedule for low-activity times (3 AM, weekends).

## Recovery

If something breaks after cache cleanup:

### Hermes Projects Not Working

```bash
# Check checkpoints
hermes checkpoints list

# If projects missing, restore from git
cd /path/to/project
git status
git checkout -- .
```

### npm Install Failing

```bash
# Clear npm cache again
npm cache clean --force

# Reinstall project
npm install
```

### uv Install Failing

```bash
# Clear uv cache again
uv cache clean

# Reinstall project
uv pip install -r requirements.txt
```

## Key Takeaways

- **Cache is safe to delete** - it auto-regenerates
- **Hermes legacy ≠ Hermes store** - delete legacy, keep store
- **WSL caching affects Windows disk reporting** - restart WSL to see changes
- **Tool-specific commands** - use `hermes`, `npm`, `uv` built-in cleanup, not manual `rm`
- **Monitor before cleanup** - verify space is actually low
- **Schedule appropriately** - avoid active development times
- **Test after cleanup** - verify tools still work

## References

- `references/cleanup-automation-pattern.md` - Database-driven project file cleanup
- `scripts/cleanup_c_drive.sh` - Production cache cleanup script
- `scripts/cleanup_completed_files.py` - Production file cleanup with backup verification
