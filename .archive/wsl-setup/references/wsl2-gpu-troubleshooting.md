# WSL2 GPU Troubleshooting

## Common Issues

### Issue 1: nvidia-smi not found

**Symptoms**:
```bash
$ nvidia-smi
Command 'nvidia-smi' not found
```

**Root Cause**: NVIDIA WSL drivers not installed on Windows host

**Resolution**:
1. Download NVIDIA WSL drivers from: https://developer.nvidia.com/cuda/wsl
2. Install on Windows (NOT in WSL)
3. Restart WSL: `wsl --shutdown` (from PowerShell)
4. Re-enter WSL and verify:
```bash
nvidia-smi
# Should show GPU info
```

### Issue 2: Ollama using CPU despite GPU available

**Symptoms**:
```bash
$ ollama ps
NAME          ID              SIZE      PROCESSOR    CONTEXT    UNTIL
qwen2.5:3b    357c53fb659c    2.8 GB    CPU          4096       4 minutes from now
```

**Verification**:
```bash
# Check GPU access
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
# Example output: NVIDIA GeForce RTX 3080, 10779 MB

# Check Ollama GPU detection
OLLAMA_DEBUG=1 ollama serve
# Look for GPU detection logs
```

**Resolution**:
- Ensure NVIDIA WSL drivers installed (see Issue 1)
- Close GPU-heavy Windows applications (gaming, rendering) - WSL shares VRAM
- Check Ollama GPU configuration (no manual config needed in recent versions)

### Issue 3: Slow model loading from Windows filesystem

**Symptoms**:
- Models take very long to load
- High I/O wait in `top`

**Verification**:
```bash
# Check where models are stored
ls -la ~/.ollama/models/
# Should show model files

# If models are on Windows (bad performance)
ls -la /mnt/c/.../models/
```

**Resolution**:
- Store models in Linux home: `~/.ollama/models/`
- Ollama defaults to Linux home - this is the correct location
- Avoid accessing models from `/mnt/c/` or `/mnt/d/`

## Performance Tips

1. **VRAM Sharing**: WSL2 shares GPU memory with Windows
   - Close Windows GPU apps before running ML workloads
   - Monitor VRAM: `nvidia-smi -l 1`

2. **Disk Performance**: Linux filesystem is faster than Windows mounts
   - Use `~/.ollama/models/` (Linux home)
   - Avoid `/mnt/c/`, `/mnt/d/` for model storage

3. **Network**: Ollama binds to localhost
   - Accessible from Windows via `http://localhost:11434`
   - No port forwarding needed

## Quick Health Check

```bash
#!/bin/bash
# WSL2 GPU + Ollama health check

echo "=== WSL2 Environment ==="
uname -a | grep -q microsoft && echo "✓ WSL2 detected" || echo "✗ Not WSL2"

echo ""
echo "=== NVIDIA GPU ==="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "✗ No NVIDIA GPU or drivers not installed"

echo ""
echo "=== Ollama Status ==="
ollama --version 2>/dev/null || { echo "✗ Ollama not installed"; exit 1; }

echo ""
echo "=== Service ==="
ps aux | grep -v grep | grep -q ollama && echo "✓ Running" || echo "✗ Not running"

echo ""
echo "=== Models ==="
ollama list

echo ""
echo "=== Test Inference ==="
echo "Hello!" | ollama run qwen2.5:3b 2>/dev/null || echo "✗ Inference failed"
```

## Systemd for Ollama Service

**Check systemd status**:
```bash
systemctl --user status ollama
```

**Enable systemd in WSL** (if not running):
```ini
# /etc/wsl.conf
[boot]
systemd=true
```

Restart WSL from PowerShell: `wsl --shutdown`

## Reference: WSL Setup (Ollama-specific)

From hermes-setup/mlops/ollama-local-llm/references/wsl2-setup.md

**Recommended Models for WSL2**:
```bash
# Lightweight (~4GB VRAM)
ollama pull qwen2.5:3b
ollama pull gemma3:4b

# Balanced (~8GB VRAM)
ollama pull llama3.2

# Test Korean support
echo "안녕! 한글로 대화할 수 있니?" | ollama run qwen2.5:3b
```

**Paths**:
- Binary: `/usr/local/bin/ollama`
- Models: `~/.ollama/models/` (Linux home, NOT Windows)
- Service: `systemctl --user status ollama`