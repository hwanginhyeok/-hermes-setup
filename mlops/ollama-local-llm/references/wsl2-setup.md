# WSL2-Specific Ollama Setup

## Environment Detection

```bash
# Check WSL2 environment
uname -a
# Should show: ...-microsoft-standard-WSL2

# Check OS
cat /etc/os-release | grep "NAME\|VERSION"
# Ubuntu 24.04.4 LTS (Noble Numbat) is common
```

## Installation on WSL2 Ubuntu

Standard install works on WSL2:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

The installer automatically:
- Creates systemd service (requires WSL2 systemd enabled)
- Adds `ollama` user
- Installs to `/usr/local/bin/ollama`

## Verify GPU Access

```bash
# NVIDIA GPU detection
nvidia-smi

# Should show GPU info
# If not working: install NVIDIA WSL drivers in Windows (not Linux)
```

## Service Status on WSL2

```bash
# Check if running
ps aux | grep ollama | grep -v grep

# View active models
ollama ps

# Example output:
# NAME          ID              SIZE      PROCESSOR    CONTEXT    UNTIL
# qwen2.5:3b    357c53fb659c    2.8 GB    100% GPU     4096       4 minutes from now
```

## Recommended Models for WSL2

```bash
# Lightweight (good for testing, ~4GB VRAM)
ollama pull qwen2.5:3b
ollama pull gemma3:4b

# Balanced (default quality, ~8GB VRAM)
ollama pull llama3.2

# Test Korean support
echo "안녕! 한글로 대화할 수 있니?" | ollama run qwen2.5:3b
```

## WSL2-Specific Issues

### Systemd Required

For systemd services to work in WSL2, ensure `/etc/wsl.conf` has:

```ini
[boot]
systemd=true
```

Then restart WSL2 from PowerShell:

```powershell
wsl --shutdown
# Then re-enter WSL2
```

### Performance Tips

- **Models on Windows filesystem**: Access models via `/mnt/c/` if stored on Windows
- **VRAM sharing**: WSL2 shares GPU memory with Windows — close other GPU apps
- **Network**: Ollama binds to localhost; accessible from Windows via `localhost:11434`

## Paths

- Binary: `/usr/local/bin/ollama`
- Models: `~/.ollama/models/` (Linux home, not Windows)
- Service: `systemctl --user status ollama` (user-level) or `systemctl status ollama` (system-level)

## Quick Validation

```bash
#!/bin/bash
# WSL2 Ollama health check

echo "=== WSL2 Environment ==="
uname -a | grep -q microsoft && echo "✓ WSL2 detected" || echo "✗ Not WSL2"

echo ""
echo "=== NVIDIA GPU ==="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "✗ No NVIDIA GPU"

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
