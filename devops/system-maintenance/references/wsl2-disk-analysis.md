# WSL2 Disk Space Analysis

## WSL2 Disk Architecture

WSL2 stores its entire filesystem in a virtual disk image on Windows:
- **Location**: `C:\Users\<username>\AppData\Local\wsl\distro-folder\`
- **Format**: ext4 VHDX file
- **Size**: Can grow to 256GB+ but doesn't auto-shrink

## Critical Discovery Commands

### 1. Overall Disk Usage
```bash
df -h
```
Look for:
- `/mnt/c` at 100% = Windows C drive full (CRITICAL)
- `/dev/sd*` usage = WSL internal disk usage

### 2. WSL2 Virtual Disk Size (Windows side)
```bash
du -sh /mnt/c/Users/*/AppData/Local/wsl/
```
**Typical sizes**: 50-150GB for active development

### 3. Linux Home Directory Analysis
```bash
# Top-level directories
du -sh ~/* 2>/dev/null | sort -hr | head -20

# Cache directories
du -sh ~/.cache ~/.local ~/.hermes 2>/dev/null

# Python packages (major space hog)
du -sh ~/.local/lib/python*/site-packages/* 2>/dev/null | sort -hr | head -30
```

### 4. Windows AppData Analysis
```bash
# Major space consumers in Windows user profile
du -sh /mnt/c/Users/*/AppData/Local/* 2>/dev/null | sort -hr | head -20
```

## Common Space Hogs in WSL2

| Category | Typical Size | Location | Cleanup Action |
|----------|--------------|----------|----------------|
| **WSL2 virtual disk** | 50-150GB | `AppData\Local\wsl\` | See WSL optimization below |
| **Python packages** | 2-10GB | `~/.local/lib/python*/site-packages/` | Remove unused packages |
| **CUDA/NVIDIA** | 4-6GB | `site-packages/nvidia/` | Remove if not doing CUDA dev |
| **PyTorch** | 1.5-2.5GB | `site-packages/torch/` | Keep if needed |
| **Playwright browsers** | 500MB-1GB | `~/.cache/ms-playwright/` | Remove if unused |
| **Chrome cache** | 300-600MB | `~/.cache/chrome-*` | Safe to remove |
| **npm cache** | 1-5GB | `~/.npm/` | `npm cache clean --force` |
| **pip cache** | 100-500MB | `~/.cache/pip/` | `pip cache purge` |

## WSL2-Specific Solutions

### Option 1: Compact WSL2 Virtual Disk (Immediate 10-30GB recovery)

**Problem**: WSL2 VHDX files are dynamically expanding but don't auto-shrink. Even after deleting large files inside WSL, the VHDX file on Windows remains at its peak size.

**Example from real case**:
- WSL internal usage: 60GB / 1007GB (6%)
- VHDX file size: 77GB
- **Wasted space: ~17GB** (77GB - 60GB actual usage)

**Root cause**: Every file creation expands VHDX. Deletions inside WSL mark space as free but don't truncate the file.

**Compact procedure**:

```bash
# Step 1: Zero-fill free space inside WSL (maximize compaction)
sudo dd if=/dev/zero of=/zero bs=1M || rm -f /zero
sudo poweroff -f  # WSL will terminate after this
```

```powershell
# Step 2: From PowerShell (Admin), compact the VHDX
wsl --shutdown
$wslPath = "$env:USERPROFILE\AppData\Local\wsl\{414e88e4-73c6-4efa-ae2d-4cbd08dfabc4}\ext4.vhdx"
Optimize-VHD -Path $wslPath -Mode Full
```

**Expected result**: 10-30GB recovery on C drive.

**Note**: The GUID in the path (`{414e88e4-73c6-4efa-ae2d-4cbd08dfabc4}`) varies per installation. Find it with:
```powershell
Get-ChildItem "$env:USERPROFILE\AppData\Local\wsl" -Recurse -Filter ext4.vhdx
```

### Option 2: Move WSL2 to Another Drive (Permanent fix)
```powershell
# Export WSL distribution
wsl --export <distro-name> D:\WSL\backup.tar

# Unregister current (keeps VHDX file for backup)
wsl --unregister <distro-name>

# Import to new location
wsl --import <distro-name> D:\WSL\ D:\WSL\backup.tar
```

### Option 3: Clean Windows Side First
```powershell
# Windows built-in cleanup
cleanmgr

# Or via Settings
# Settings → System → Storage → Temporary files
```

## Quick Wins (1-5GB each)

```bash
# Remove unused Python packages (BE CAREFUL - check requirements first)
pip uninstall <package>

# Clear Python caches
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Clear browser automation caches
rm -rf ~/.cache/ms-playwright
rm -rf ~/.cache/chrome-suno

# Clear npm cache
npm cache clean --force

# Clear pip cache
pip cache purge
```

## Immediate Actions for C Drive at 100%

1. **Windows temporary files** (1-5GB):
   - `Win + R` → `cleanmgr` → Select C: → Clean up

2. **Windows Update cleanup** (2-8GB):
   - Settings → System → Storage → Temporary files → Windows Update cleanup

3. **Recycle Bin** (varies):
   - Empty Recycle Bin

4. **WSL2 restart to reflect space**:
   - `wsl --shutdown` from PowerShell, then restart WSL

## Monitoring

```bash
# Create a daily disk space check
0 9 * * * df -h / /mnt/c >> ~/.pm_logs/disk_usage_$(date +\%Y\%m\%d).log
```

## WSL2 Crash Troubleshooting

### Symptoms: "WSL keeps disconnecting" / Segfaults

**Kernel crash indicators in dmesg**:
```bash
dmesg | grep -i "fatal signal\|segfault"
```

Common crash pattern:
```
init: init: potentially unexpected fatal signal 11.
```

This indicates WSL init process crashes (Segfault - signal 11), often across multiple CPUs.

### Root Causes

1. **Windows C drive full** (100% usage) → I/O failures
2. **Memory pressure** → OOM killer terminates processes
3. **WSL memory configuration issues** → Over-allocation
4. **Corrupted WSL instance** → Filesystem corruption

### Diagnosis Commands

```bash
# Check current memory allocation
cat /proc/meminfo | grep -E "MemTotal|SwapTotal"

# Check for kernel crashes
dmesg | tail -50 | grep -i "fatal\|segfault\|oom"

# Check system logs
journalctl -xe --no-pager | tail -100

# Check .wslconfig (Windows side)
cat /mnt/c/Users/*/.wslconfig 2>/dev/null
```

### Common .wslconfig Values

```ini
[wsl2]
memory=16GB          # RAM allocation to WSL2
swap=8GB            # Swap file size
processors=8        # Number of CPU cores

[experimental]
autoMemoryReclaim=gradual  # Automatic memory reclamation
```

**Note**: WSL2 memory is virtual - configured in .wslconfig, not actual physical RAM. 
- 16GB memory + 8GB swap = 24GB total virtual memory available to WSL2
- This does NOT allocate 16GB of physical Windows RAM

### Resolution Steps

**1. Check actual memory usage** (not allocation):
```bash
free -h
# Look at "used" vs "total" - if used << total, memory is not the issue
```

**2. Verify .wslconfig is correct**:
```bash
# From PowerShell (Admin)
notepad $env:USERPROFILE\.wslconfig
# Or from WSL:
cat /mnt/c/Users/$USER/.wslconfig
```

**3. Adjust memory if over-allocated** (reduce if Windows has limited RAM):
```ini
[wsl2]
memory=8GB          # Reduce if Windows has < 16GB total RAM
swap=4GB
processors=4
```

**4. Restart WSL after config changes**:
```powershell
# From PowerShell
wsl --shutdown
# Wait 10 seconds, then restart WSL
```

**5. If C drive is 100%** - THIS IS THE LIKELY CAUSE:
- Clear Windows temp files: `cleanmgr`
- Clear Windows Update cache
- Move WSL2 to D drive (see Option 2 above)
- C drive at 100% causes I/O failures → WSL crashes

### Verification After Fix

```bash
# Monitor for crashes over time
watch -n 10 'dmesg | tail -5'

# Check stability under load
stress-ng --cpu 4 --timeout 60s  # May need: sudo apt install stress-ng
```

## Red Flags

- C drive > 95%: **IMMEDIATE ACTION REQUIRED** (system instability risk, WSL crashes likely)
- WSL2 disk > 80GB: Consider cleanup or moving to D drive
- Python packages > 5GB: Review for unused ML/CUDA packages
- Repeated Segfault 11 in dmesg: Check C drive space first, then WSL memory config

## C Drive Volatility Analysis

**Symptom**: C drive usage fluctuates significantly (e.g., 81% → 95%+ → 81%) without obvious user activity.

**Diagnostic commands**:
```bash
# Quick check
df -h /mnt/c

# Detailed Windows-side breakdown
du -sh /mnt/c/Users/*/AppData/Local/* 2>/dev/null | sort -hr | head -20

# WSL2 VHDX actual size
ls -lh /mnt/c/Users/*/AppData/Local/wsl/*/ext4.vhdx
```

**Common volatility causes** (in order of frequency):

1. **WSL2 VHDX expansion (77GB+)** - Major factor
   - VHDX grows with file creation but never shrinks
   - Even 60GB actual usage can occupy 77GB+ on disk
   - Solution: Compact VHDX (see Option 1 above)

2. **Windows Temp folder accumulation (25GB+)**
   - Location: `C:\Users\<username>\AppData\Local\Temp`
   - Large installers, updates, extracts accumulate
   - Solution: Periodic cleanup or automated deletion

3. **Windows Update caches**
   - Can accumulate 5-15GB after updates
   - Solution: Windows Update cleanup in Settings

4. **Application caches (Chrome, Kakao, etc.)**
   - Chrome: 4GB+ (AI models, cache)
   - Kakao: 5GB+
   - Solution: Clear app caches periodically

**Real-world example**:
- C drive at 81% (192GB / 238GB used)
- WSL2 VHDX: 77GB (but only 60GB actual usage)
- Windows Temp: 25GB
- Potential recovery: 17GB (VHDX compact) + 20GB (Temp cleanup) = **37GB**

**Automation opportunity**: Add to existing cleanup script (`/home/window11/scripts/cleanup_completed_files.py`):
```python
# Add Windows-side cleanup via PowerShell trigger
subprocess.run([
    "powershell.exe", "-Command",
    "Remove-Item -Path '$env:TEMP\\*' -Recurse -Force -ErrorAction SilentlyContinue"
])
```
