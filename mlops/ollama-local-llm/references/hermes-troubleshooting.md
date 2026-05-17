# Hermes Agent + Ollama Integration Troubleshooting

**Last Updated**: 2026-05-05
**Hermes Version**: v0.12.0
**Ollama Version**: 0.20.0

## Quick Reference: Provider Configuration

| Provider Type | Config Required | When To Use |
|---------------|-----------------|-------------|
| `custom` | `providers.custom.base_url` + `providers.custom.api_key` | Custom endpoints (Ollama, local servers) |
| `ollama` | `providers.ollama.base_url` + `providers.ollama.api_key` | Ollama (recommended over `custom`) |
| `openrouter` | None (uses env var) | OpenRouter API |
| `anthropic` | None (uses env var) | Anthropic API |

## Understanding Provider Routing and Fallback Behavior

Hermes Agent has a **fallback mechanism** that automatically switches to a backup provider when the primary model fails. This is **by design**, not a bug.

### How Fallback Works

```
Primary Model (config)
    ↓ (fails)
Fallback Model (config)
    ↓ (fails)
Default Fallback: glm-4.6 via zai-glm
```

**Common failure triggers**:
- Invalid model ID for the provider (e.g., `qwen2.5:3b` on OpenRouter)
- Network connectivity issues
- Provider service downtime
- Authentication errors
- Timeout
- Missing provider configuration

### Symptom: "Model is not a valid model ID" Error

When you see this error:
```
⚠️  API call failed: qwen2.5:3b is not a valid model ID
🔄 Primary model failed — switching to fallback: glm-4.6 via zai-glm
```

**What's happening**: Hermes tried to use `qwen2.5:3b` (an Ollama model ID) with OpenRouter, which doesn't recognize it.

### Configuration Mistakes That Trigger Fallback

#### Mistake 1: Wrong Provider + Wrong Model ID

```yaml
# ❌ WRONG: OpenRouter provider with Ollama model ID
model:
  provider: openrouter
  default: qwen2.5:3b  # OpenRouter doesn't know this ID
```

**Fix**: Use OpenRouter's model ID or switch to Ollama provider
```yaml
# ✅ Option A: Use OpenRouter's model ID
model:
  provider: openrouter
  default: qwen/qwen-2.5-3b-instruct

# ✅ Option B: Use Ollama provider
model:
  provider: ollama
  default: qwen2.5:3b
```

#### Mistake 2: Custom Provider Not Configured

```yaml
# ❌ WRONG: Declared custom provider but didn't configure it
model:
  provider: custom
  default: qwen2.5:3b
  base_url: http://localhost:11434/v1  # This alone is NOT enough!
  api_key: ollama

# Missing providers.custom section → Hermes falls back to OpenRouter
```

**Fix**: Add provider configuration
```yaml
# ✅ CORRECT
model:
  provider: custom
  default: qwen2.5:3b
  base_url: http://localhost:11434/v1
  api_key: ollama

providers:
  custom:
    base_url: http://localhost:11434/v1
    api: http://localhost:11434/v1
    api_key: ollama
```

#### Mistake 3: Ollama Provider Not Configured

```yaml
# ❌ WRONG: Declared ollama provider but didn't configure it
model:
  provider: ollama
  default: qwen2.5:3b

# Missing providers.ollama section!
```

**Fix**: Add provider configuration
```yaml
# ✅ CORRECT
model:
  provider: ollama
  default: qwen2.5:3b

providers:
  ollama:
    base_url: http://localhost:11434/v1
    api_key: ollama
```

#### Mistake 4: Auxiliary Models Not Configured

```yaml
# ❌ WRONG: Main model uses Ollama, but auxiliary models default elsewhere
model:
  provider: ollama
  default: qwen2.5:3b

# Missing auxiliary sections → they default to OpenRouter
```

**Fix**: Configure ALL auxiliary models
```yaml
# ✅ CORRECT
model:
  provider: ollama
  default: qwen2.5:3b

auxiliary:
  vision:
    provider: ollama
    model: qwen2.5:3b
    base_url: http://localhost:11434/v1
    api_key: ollama
  compression:
    provider: ollama
    model: qwen2.5:3b
    base_url: http://localhost:11434/v1
    api_key: ollama
  # ... configure ALL auxiliary sections
```

### Verification Commands

```bash
# 1. Check current provider setting
hermes config get model.provider

# 2. Check current model
hermes config get model.default

# 3. Verify Ollama is running
ollama ps

# 4. Test Ollama API directly
curl -s http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen2.5:3b", "messages": [{"role": "user", "content": "Test"}], "stream": false}'

# 5. Test Hermes with verbose output
hermes chat -q "2 + 2는?" --debug

# 6. Check logs for provider routing and fallback
tail -50 ~/.hermes/logs/agent.log | grep -E "Provider|Endpoint|fallback|switching"
```

### Expected Log Output (Correct Configuration)

**When using Ollama provider**:
```
Provider: ollama
Endpoint: http://localhost:11434/v1
Model: qwen2.5:3b
```

**When fallback triggers**:
```
⚠️  API call failed (attempt 1/3): [error details]
   🔌 Provider: ollama  Model: qwen2.5:3b
🔄 Primary model failed — switching to fallback: glm-4.6 via zai-glm
```

### Config Template: Ollama with Hermes

```yaml
# ~/.hermes/config.yaml

# Main model configuration
model:
  provider: ollama
  default: qwen2.5:3b
  context_length: 64000  # Override Hermes validation (model has 32K)
  fallback: glm-4.6      # Optional: explicit fallback

# Ollama provider configuration
providers:
  ollama:
    base_url: http://localhost:11434/v1
    api_key: ollama
    timeout: 120

# ALL auxiliary models must use Ollama
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

# Delegation (for subagent tasks)
delegation:
  provider: ollama
  model: qwen2.5:3b
  base_url: http://localhost:11434/v1
  api_key: ollama
  context_length: 64000
```

### Common Issues

#### Issue 1: Context Length Validation

**Error**:
```
Model qwen2.5:3b has a context window of 32,768 tokens, which is below the minimum 64,000
```

**Solution**: Override validation (doesn't extend actual capacity):
```yaml
model:
  context_length: 64000  # Silences validation error
```

#### Issue 2: Empty Responses

**Cause**: Provider misconfiguration or incompatibility

**Debug**:
```bash
# Check logs for provider errors
tail -100 ~/.hermes/logs/agent.log | grep -E "ERROR|WARN|provider"

# Verify Ollama is responding
curl http://localhost:11434/v1/models | jq
```

**Solution**: Ensure ALL auxiliary models are configured with correct provider settings.

#### Issue 3: Slow Responses

**Cause**: Ollama not using GPU

**Check**:
```bash
ollama ps
# Look for: PROCESSOR: GPU % (not CPU)

# If using CPU, check GPU:
nvidia-smi

# Verify Ollama GPU detection:
curl http://localhost:11434/api/tags
```

### Environment Details

**WSL2 Ubuntu 24.04**:
```bash
# Systemd enabled
cat /etc/wsl.conf
# [boot]
# systemd=true

# GPU working
nvidia-smi
# NVIDIA GeForce RTX 3090, 24564 MiB

# Ollama using GPU
ollama ps
# PROCESSOR: 100% GPU
```

**Ollama models installed**:
```
NAME                  ID              SIZE      MODIFIED
gemma3:4b            b5dfd6858f43    3.3 GB    2 hours ago
llama3.2             34f5b7f14ed0    2.0 GB    2 hours ago
qwen2.5:3b           54e0b307a986    1.9 GB    2 hours ago
```

### Debug Checklist

- [ ] Verify Ollama is running: `ollama ps`
- [ ] Test Ollama API directly: `curl http://localhost:11434/v1/models`
- [ ] Check Hermes provider setting: `hermes config get model.provider`
- [ ] Verify provider configuration in config.yaml
- [ ] Confirm ALL auxiliary models configured
- [ ] Check logs for provider routing: `tail -50 ~/.hermes/logs/agent.log`
- [ ] Test with simple query: `hermes chat -q "test"`
- [ ] Verify context length override if needed

### Alternative: Use OpenRouter

If you prefer not to use local Ollama:

```yaml
model:
  provider: openrouter
  default: qwen/qwen-2.5-3b-instruct  # OpenRouter's model ID
  fallback: anthropic/claude-sonnet-4.5
```

OpenRouter hosts many of the same models with pay-per-token pricing and no local setup required.
