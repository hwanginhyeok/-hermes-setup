# Cache Cleanup Patterns

## Quick Cache Size Check
```bash
# Check common cache sizes before cleanup
du -sh ~/.hermes/checkpoints/legacy-* ~/.npm/_cacache ~/.npm/_npx ~/.cache/uv ~/.cache/camoufox
```

## Cache Cleanup Commands

### Hermes Legacy Checkpoints
**Size**: 5-10GB per legacy archive
**Frequency**: Monthly
**Command**:
```bash
# Check current usage
hermes checkpoints list

# Clear with force flag (required for automation)
hermes checkpoints clear-legacy -f
```

**Pitfall**: Interactive prompt without `-f` flag hangs in cron
**Recovery**: Use `echo "y" | hermes checkpoints clear-legacy` or `-f` flag

### npm Cache
**Size**: 1-5GB
**Frequency**: Weekly
**Commands**:
```bash
# Standard cleanup
npm cache clean --force

# Aggressive cleanup (remove entire cache)
rm -rf ~/.npm/_cacache ~/.npm/_npx
```

### uv Cache
**Size**: 500MB-2GB
**Frequency**: Monthly
**Commands**:
```bash
# Standard cleanup
uv cache clean

# Complete removal
rm -rf ~/.cache/uv
```

### Python Cache (pip, pytest)
**Size**: 200MB-1GB
**Frequency**: Monthly
**Commands**:
```bash
# pip cache
pip cache purge

# pytest cache
rm -rf ~/.cache/pytest
```

### Browser/Application Caches
**camoufox**: 500MB-3GB
```bash
rm -rf ~/.cache/camoufox
```

**Chrome/Firefox**: 1-5GB (browser-specific)
```bash
# Chrome
rm -rf ~/.cache/google-chrome ~/.config/google-chrome/Default/Cache

# Firefox
rm -rf ~/.cache/mozilla
```

## Disk Space Recovery Procedure

### When Disk is Critical (>95%)

**Step 1: Identify hogs**
```bash
# Check current usage
df -h /home

# Find top directories
du -sh /home/window11/* | sort -hr | head -10
```

**Step 2: Quick cleanup**
```bash
# Safe to run immediately
npm cache clean --force
uv cache clean
rm -rf ~/.cache/uv ~/.cache/camoufox
```

**Step 3: Verify impact**
```bash
# Check space recovered
df -h /home

# Test critical systems
systemctl --user status blog-api blog-worker
```

### WSL/Windows Disk Space Considerations

**WSL caching behavior**:
- WSL caches disk usage data
- `df -h` may show 100% even after cleanup
- Actual space freed after WSL restart

**Windows side verification**:
```powershell
# From Windows PowerShell
wsl --shutdown
```

**Expected recovery**:
- After 15GB cache cleanup: 100% → ~93%
- Full WSL restart required for accurate reading

## Scheduling Cache Cleanup

### Cron Entry for Monthly Cleanup
```bash
# First of month at 03:00
0 3 1 * * /usr/bin/bash /home/window11/scripts/cleanup_c_drive.sh >> /home/window11/.pm_logs/cache_cleanup_$(date +\\%Y\\%m\\%d).log 2>&1
```

### Combined Cleanup Script Pattern
```bash
#!/bin/bash
set -e

echo "=== Cache cleanup started ==="

# Check disk before
df -h /home

# Hermes (largest impact)
if [ -d "$HOME/.hermes/checkpoints" ]; then
    hermes checkpoints clear-legacy -f
fi

# npm
if command -v npm &> /dev/null; then
    npm cache clean --force
fi

# uv
if command -v uv &> /dev/null; then
    uv cache clean
fi

# App caches
rm -rf ~/.cache/uv ~/.cache/camoufox ~/.cache/pytest

# Check disk after
df -h /home

echo "=== Cache cleanup complete ==="
```

## Verification After Cleanup

### System Health Check
```bash
# 1. Verify critical services
systemctl --user status blog-api blog-worker x-bot music-bot

# 2. Test project functionality
cd ~/music-lab && python3 -c "import sqlite3; print('DB OK')"

# 3. Check disk improvement
df -h /home

# 4. Verify no orphaned processes
ps aux | grep -E "(cleanup|python)" | grep -v grep
```

### Rollback Plan
If cleanup causes issues:
```bash
# Recreate npm cache (auto on next npm install)
# Just run any npm install

# Recreate uv cache (auto on next package install)
# Just run any uv command

# Restore Hermes checkpoints (NOT POSSIBLE)
# Legacy checkpoints are permanently deleted
# Ensure you have backups before clearing
```

## Cache Size Baseline (2026-05-15)

| Cache | Normal Range | Warning (>2x) | Critical (>5x) |
|--------|--------------|----------------|----------------|
| Hermes legacy | 5-10GB | 20GB+ | 50GB+ |
| npm | 1-5GB | 10GB+ | 25GB+ |
| uv | 500MB-2GB | 4GB+ | 10GB+ |
| camoufox | 500MB-3GB | 6GB+ | 15GB+ |

Use these baselines for automated alerts in monitoring scripts.
