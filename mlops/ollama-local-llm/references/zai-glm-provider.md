# Z.AI GLM Provider Configuration

**Last Updated**: 2026-05-05

## Overview

Z.AI (also known as zai-glm in Hermes config) provides access to ChatGLM models, including GLM-4.6. This is a commercial API service, not a local model.

**IMPORTANT**: Hermes has a config hierarchy that affects which model provider is used:

1. **Profile config** (~/.hermes/profiles/<name>/config.yaml) - HIGHEST priority
2. **Global config** (~/.hermes/config.yaml) - Used if no profile is active
3. **Fallback model** - Used if primary provider fails

**Why GLM appears unexpectedly**:
- If you have a profile config (e.g., `profiles/pm/config.yaml`) with `provider: zai-glm`, it OVERRIDES the global Ollama setting
- Profiles are created when you run `hermes profile create <name>` or similar commands
- Check which profile is active: `hermes profile list`
- To use global config instead: delete the profile directory or run `hermes profile delete <name>`

## Configuration

### In custom_providers

The zai-glm provider is defined in `~/.hermes/config.yaml`:

```yaml
custom_providers:
  - name: zai-glm
    base_url: https://api.z.ai/api/anthropic
    key_env: Z_AI_API_KEY
    api_mode: anthropic_messages
```

### As Fallback Provider

Hermes uses zai-glm as the default fallback:

```yaml
fallback_model:
  provider: zai-glm
  model: glm-4.6
```

## API Key

Set the environment variable:

```bash
export Z_AI_API_KEY=your_key_here
```

Or add to `~/.hermes/.env`:

```
Z_AI_API_KEY=your_key_here
```

## Models

Available models (as of 2026-05-05):

- **glm-4.6** - Latest GLM model (recommended)
- **glm-4-plus** - Higher quality
- **glm-4-flash** - Faster responses
- **glm-4-air** - Lightweight

## Verification

Test the API directly:

```bash
curl -X POST https://api.z.ai/api/anthropic/v1/messages \
  -H "x-api-key: $Z_AI_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "glm-4.6",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Common Issues

### Authentication Error

```
{"code":1001,"msg":"Authentication parameter not received in Header, unable to authenticate","success":false}
```

**Cause**: Missing or invalid `Z_AI_API_KEY`

**Fix**: Set the environment variable or check your API key is valid.

### Why GLM Appears When Using Ollama

If you see GLM being used instead of your local Ollama model:

1. **Profile override** - Check if a profile is active: `ls ~/.hermes/profiles/`
   - Profile config OVERRIDES global config
   - Delete profile to use global config: `rm -rf ~/.hermes/profiles/<name>`

2. **Primary model failed** - Check Ollama is running: `ollama ps`
   - If Ollama fails, Hermes falls back to zai-glm

3. **Provider misconfigured** - Verify `providers.custom` or `providers.ollama` in config.yaml
   - See "CRITICAL: Custom Provider Configuration" in main SKILL.md

4. **Model ID mismatch** - Ollama uses `qwen2.5:3b`, OpenRouter uses `qwen/qwen-2.5-3b-instruct`

See `references/hermes-troubleshooting.md` for complete troubleshooting.

## Comparison with Other Providers

| Provider | Type | Endpoint | Cost |
|----------|------|----------|------|
| **zai-glm** | Commercial API | https://api.z.ai/api/anthropic | Pay-per-token |
| **Ollama** | Local | http://localhost:11434/v1 | Free (after model download) |
| **OpenRouter** | Commercial API | https://openrouter.ai/api/v1 | Pay-per-token |

## When to Use Z.AI GLM

- **As fallback**: When local Ollama fails (default Hermes behavior)
- **Higher quality**: GLM-4.6 may outperform smaller local models
- **Multilingual**: Good Korean/Chinese support
- **No GPU**: When you can't run local models

## References

- Z.AI API: https://api.z.ai (check for official docs)
- Hermes provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers
