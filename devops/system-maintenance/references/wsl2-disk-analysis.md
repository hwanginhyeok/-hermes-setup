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
```powershell
# From PowerShell (Admin)
wsl --shutdown
# Navigate to WSL folder and optimize VHDX
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
