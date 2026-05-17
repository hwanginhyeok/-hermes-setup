---
name: ollama-local-llm
description: Ollama local LLM setup and management — install, configure, pull models, run inference
category: mlops
---

# Ollama Local LLM Management

Ollama is a lightweight local LLM runner that supports hundreds of models including Llama, Qwen, Gemma, Mistral, and more. It runs on Linux, macOS, and WSL2 with GPU acceleration.

## Core Concepts

- **Models**: Pulled from ollama.com/library (e.g., `llama3.2`, `qwen2.5:3b`, `gemma3:4b`)
- **Tags**: Models have size tags like `:3b`, `:7b`, `:latest` (default)
- **Context**: Default 4096 tokens, expandable based on model
- **GPU**: Automatically uses available GPU (NVIDIA, Apple Silicon)

## Installation

### Linux/WSL2

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify:
```bash
ollama --version
```

The install script creates a systemd service and adds the `ollama` user.

### Service Management

Check if running:
```bash
ps aux | grep ollama | grep -v grep
# Or:
ollama ps
```

Start service (if not running):
```bash
systemctl start ollama
```

Enable at boot:
```bash
systemctl enable ollama
```

## Model Management

### Pull Models

```bash
# Pull latest (usually 7B parameter model)
ollama pull llama3.2

# Pull specific size
ollama pull qwen2.5:3b
ollama pull gemma3:4b
ollama pull mistral:7b

# List available models
ollama list
```

**Model selection guide** (see `references/model-guide.md`):
- **3B**: Fast, low VRAM (~4GB), good for quick tasks
- **4B**: Balanced speed/quality, ~6GB VRAM
- **7B**: Default quality, ~8GB VRAM
- **14B+**: Best quality, needs 16GB+ VRAM

### Remove Models

```bash
ollama rm <model-name>
```

## Running Inference

### Interactive Chat

```bash
ollama run qwen2.5:3b
```

### One-shot Queries

```bash
echo "Your question here" | ollama run llama3.2

# Or with /dev/stdin for multi-line
cat <<EOF | ollama run mistral
Analyze this data:
[...]
EOF
```

### API Mode

Ollama exposes a REST API on `http://localhost:11434`:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:3b",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

## Checking Status

View running models:
```bash
ollama ps
```

Output shows:
- NAME: Model name
- SIZE: VRAM usage
- PROCESSOR: GPU % or CPU
- CONTEXT: Token window size
- UNTIL: Auto-unload time (5m idle)

## Common Workflows

### Test Korean/Non-English Support

```bash
echo "안녕! 한글로 대화할 수 있니?" | ollama run qwen2.5:3b
```

Qwen2.5 and Gemma models have excellent multilingual support.

### Quick Validation Script

```bash
#!/bin/bash
# Quick health check

echo "=== Ollama Status ==="
ollama --version
echo ""

echo "=== Service ==="
ps aux | grep ollama | grep -v grep || echo "Not running"
echo ""

echo "=== Models ==="
ollama list
echo ""

echo "=== Test Inference ==="
echo "Hello, can you respond briefly?" | ollama run qwen2.5:3b
```

## Pitfalls

### WSL2 GPU Not Detected
- **Symptom**: `PROCESSOR: CPU` in `ollama ps`
- **Fix**: Install NVIDIA WSL drivers in Windows, not just Linux
- **Verify**: `nvidia-smi` should work in WSL2

### Service Already Running
- **Symptom**: Second ollama serve process fails or port conflict
- **Fix**: Check existing process first: `ps aux | grep ollama | grep -v grep`
- **Note**: Install script creates systemd service automatically — don't run `ollama serve` manually if already running

### Model Pull Fails/Slow
- **Mirror issues**: Ollama can use HuggingFace mirrors if ollama.com is slow
- **Disk space**: Models are 2GB-20GB each; check with `df -h`

### Service Won't Start
- **Port conflict**: Nothing else should use port 11434
- **User permissions**: Install script creates `ollama` user; don't run as root

### Context Window Issues
- **Default 4096**: For longer contexts, pull larger models or use quantized versions
- **Error**: "context length exceeded" means input + response > context window

## Integration Examples

### Hermes Agent (Primary Integration)

Hermes Agent can use Ollama models via OpenAI-compatible API. This requires complete config.yaml setup.

#### Configuration Steps

```bash
# 1. Set main model
hermes config set model.provider ollama
hermes config set model.default qwen2.5:3b
hermes config set model.context_length 64000

# 2. Configure Ollama provider
# Edit config.yaml and add to providers:
providers:
  ollama:
    base_url: http://localhost:11434/v1
    api_key: ollama

# 3. Configure ALL auxiliary models (critical!)
# Hermes requires these for compression, vision, etc.:
auxiliary:
  vision:
    provider: ollama
    model: qwen2.5:3b
    base_url: http://localhost:11434/v1
    api_key: ollama
    context_length: 64000
  compression:
    provider: ollama
    model: qwen2.5:3b
    base_url: http://localhost:11434/v1
    api_key: ollama
    context_length: 64000
  web_extract:
    provider: ollama
    model: qwen2.5:3b
    base_url: http://localhost:11434/v1
    api_key: ollama
    context_length: 64000
  session_search:
    provider: ollama
    model: qwen2.5:3b
    base_url: http://localhost:11434/v1
    api_key: ollama
    context_length: 64000
  skills_hub:
    provider: ollama
    model: qwen2.5:3b
    base_url: http://localhost:11434/v1
    api_key: ollama
    context_length: 64000

# 4. Configure delegation (for subagent tasks)
delegation:
  provider: ollama
  model: qwen2.5:3b
  base_url: http://localhost:11434/v1
  api_key: ollama
  context_length: 64000
```

#### ⚠️ CRITICAL: Custom Provider Configuration (2026-05-05)

**Status**: When using `provider: custom` in config.yaml, you must configure the `providers.custom` section. The `model.provider` setting alone is NOT enough.

**How custom provider works**:
- Hermes looks at `providers.custom.base_url` for the API endpoint
- If `providers.custom` is missing or incomplete, Hermes falls back to OpenRouter
- This triggers the fallback model: `glm-4.6` via `zai-glm`

**Common pitfall**: Setting `model.provider: custom` without properly configuring `providers.custom`:

```yaml
# ❌ WRONG: Declared custom provider but didn't configure it
model:
  provider: custom
  default: qwen2.5:3b
  base_url: http://localhost:11434/v1  # This alone is NOT enough!
  api_key: ollama

# Missing providers.custom section → Hermes falls back to OpenRouter
```

**Correct Configuration for Ollama via Custom Provider**:

```yaml
# ✅ CORRECT: Both model and providers sections configured
model:
  provider: custom
  default: qwen2.5:3b
  base_url: http://localhost:11434/v1
  api_key: ollama
  context_length: 64000

providers:
  custom:
    base_url: http://localhost:11434/v1
    api: http://localhost:11434/v1
    api_key: ollama

# ALL auxiliary models must also use custom provider
auxiliary:
  vision:
    provider: custom
    model: qwen2.5:3b
    base_url: http://localhost:11434/v1
    api_key: ollama
  compression:
    provider: custom
    model: qwen2.5:3b
    base_url: http://localhost:11434/v1
    api_key: ollama
  # ... configure ALL auxiliary sections
```

**Alternative: Use named provider (recommended for Ollama)**:

```yaml
# ✅ BETTER: Use named provider "ollama" instead of "custom"
model:
  provider: ollama
  default: qwen2.5:3b
  context_length: 64000

providers:
  ollama:
    base_url: http://localhost:11434/v1
    api_key: ollama
```

**Verification steps**:
```bash
# 1. Check current provider setting
hermes config get model.provider

# 2. Verify Ollama is running
ollama ps

# 3. Test Ollama directly
echo "test" | ollama run qwen2.5:3b

# 4. Check logs for provider routing
tail -50 ~/.hermes/logs/agent.log | grep -E "Provider|Endpoint|custom"

# Expected: "Provider: custom  Endpoint: http://localhost:11434/v1"
# Bug: "Provider: custom  Endpoint: https://openrouter.ai/api/v1"
```

**Common mistakes**:
❌ `provider: custom` without `providers.custom.base_url`
❌ Setting `model.base_url` but NOT `providers.custom.base_url`
❌ Forgetting to configure auxiliary models
❌ Using OpenRouter model IDs with custom provider pointing to Ollama

**Full troubleshooting guide**: See `references/hermes-troubleshooting.md` for detailed debugging steps.

#### Context Window Minimum

Hermes requires 64K context. Small models (qwen2.5:3b has 32K) will fail with:
```
Model qwen2.5:3b has a context window of 32,768 tokens, which is below the minimum 64,000
```
**Fix**: Override with `context_length: 64000` in config.yaml for ALL model sections (main + all auxiliary).

Note: This overrides validation but doesn't actually extend the model's capacity.

#### Empty Responses

If Ollama returns empty responses, Hermes falls back to auxiliary providers. This happens when:
- Auxiliary models not configured (compression, vision, etc. must ALL be set)
- API format mismatch between Ollama and Hermes expectations
- Provider routing bug (see above)

**Fix**: Ensure ALL auxiliary sections have full `provider: custom` configuration.

**Test Configuration**:
```bash
# Quick test
hermes chat -q "2 + 2는?"

# Verify Ollama is responding
curl -s http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2.5:3b", "messages": [{"role": "user", "content": "Test"}], "stream": false}'
```

#### Model Selection for Hermes

- **qwen2.5:3b**: Fastest (1.9GB), but requires context_length override
- **llama3.2**: Balanced (2.0GB), better English
- **gemma3:4b**: Largest installed (3.3GB), best quality
- **Recommendation**: For Hermes, use 7B+ models if available for better tool use

### Python (requests)

```python
import requests

response = requests.post('http://localhost:11434/api/generate', json={
    'model': 'qwen2.5:3b',
    'prompt': 'Explain quantum computing',
    'stream': False
})
print(response.json()['response'])
```

### Node.js

```javascript
const response = await fetch('http://localhost:11434/api/generate', {
  method: 'POST',
  body: JSON.stringify({
    model: 'llama3.2',
    prompt: 'Write a haiku',
    stream: false
  })
});
const data = await response.json();
console.log(data.response);
```

## References

- `references/hermes-troubleshooting.md` — **UPDATED**: Complete Hermes integration troubleshooting, custom provider config, fallback behavior
- `references/zai-glm-provider.md` — **UPDATED**: Z.AI GLM commercial API provider configuration and troubleshooting
- `references/profile-management.md` — **NEW**: Hermes profile hierarchy, when profiles override global config, troubleshooting
- `references/model-guide.md` — Model selection, size tradeoffs, multilingual support
- `references/wsl2-setup.md` — WSL2-specific setup and GPU configuration
- `references/troubleshooting.md` — Common errors and fixes
- `templates/hermes-config.yaml` — **UPDATED**: Complete working config.yaml template for Hermes with Ollama
- `scripts/health-check.sh` — Automated validation script
