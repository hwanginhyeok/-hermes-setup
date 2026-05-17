# Ollama Troubleshooting

## Installation Issues

### "command not found: ollama"
**Cause**: Not in PATH or not installed

**Fix**:
```bash
# Check if installed
which ollama

# If not, reinstall
curl -fsSL https://ollama.com/install.sh | sh

# Log out and back in for PATH to update
```

### Permission Denied
**Cause**: Trying to run as root or wrong user

**Fix**: Don't use sudo. Ollama runs as `ollama` user:
```bash
# Wrong
sudo ollama serve

# Right
systemctl start ollama  # Runs as ollama user
```

## Service Issues

### Service Won't Start
**Check logs**:
```bash
journalctl -u ollama -n 50
```

**Common causes**:
- Port 11434 already in use
- Corrupted model cache
- Missing GPU drivers

### GPU Not Detected (CPU Only)
**Symptom**: `ollama ps` shows `PROCESSOR: CPU`

**WSL2 Fix**:
1. Install NVIDIA WSL drivers in **Windows** (not Linux)
2. Verify with `nvidia-smi` in WSL2
3. Restart Ollama: `systemctl restart ollama`

**Linux Fix**:
```bash
# Verify NVIDIA driver
nvidia-smi

# Install CUDA toolkit if needed
sudo apt install nvidia-cuda-toolkit
```

**Apple Silicon Fix**: Should work automatically on M1/M2/M3

## Model Issues

### Pull Fails / Slow Download
**Symptoms**: Timeout, partial download, slow speeds

**Fix**:
```bash
# Check disk space
df -h ~/.ollama/models

# Retry with specific tag
ollama pull llama3.2:latest

# If corrupt, remove and retry
ollama rm llama3.2
ollama pull llama3.2
```

### Model Too Large
**Symptoms**: OOM killed, system freeze

**Fix**: Pull smaller variant:
```bash
# Instead of 70B
ollama pull llama3.2:70b  # Don't

# Use 7B or 3B
ollama pull qwen2.5:3b   # Do
```

### "Context Length Exceeded"
**Cause**: Input + output > model's context window

**Fix**:
- Use smaller prompt
- Pull extended context model: `llama3.2:32k`
- Summarize and iterate

## Runtime Issues

### Slow Inference
**Check**:
```bash
# Verify GPU usage
ollama ps  # Should show GPU %, not CPU

# Check system load
htop
```

**Common causes**:
- Running on CPU instead of GPU
- Model too large for available VRAM
- Multiple concurrent requests

### High Memory Usage
**Normal**: Models are loaded into RAM/VRAM

**Reduce**:
```bash
# Use smaller model
ollama run qwen2.5:3b

# Auto-unloads after 5 min idle, or force unload:
pkill -f ollama  # Kills everything
systemctl restart ollama
```

### Korean/Multilingual Output Garbled
**Cause**: Model doesn't support language well

**Fix**: Use Qwen or Gemma:
```bash
# Instead of Llama
ollama run llama3.2  # Weak Korean

# Use Qwen
ollama run qwen2.5:3b  # Strong Korean
```

## API Issues

### Connection Refused on port 11434
**Check**:
```bash
# Verify service running
systemctl status ollama

# Test locally
curl http://localhost:11434/api/tags

# If firewall blocks, allow port
sudo ufw allow 11434
```

### Streaming Not Working
**Cause**: `stream: false` in API call

**Fix**:
```bash
# Enable streaming
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "test",
  "stream": true  # ← Change to true
}'
```

## Getting Help

1. Check logs: `journalctl -u ollama -f`
2. Verify with `ollama ps` and `nvidia-smi`
3. Search: https://github.com/ollama/ollama/issues
4. Model library: https://ollama.com/library
