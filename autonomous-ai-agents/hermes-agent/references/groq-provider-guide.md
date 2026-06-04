# Groq Provider for Hermes - Integration Guide

## Overview

Groq provides fast inference on open-source models (Llama, Mixtral, Gemma) via LPU (Language Processing Unit) architecture.

## Installation

```bash
# Python SDK
python3 -m venv ~/.venv-groq
source ~/.venv-groq/bin/activate
pip install groq
```

## API Key Setup

1. Register: https://console.groq.com/keys
2. Get API key
3. Set environment variable:
   ```bash
   export GROQ_API_KEY="gsk_xxx..."
   # Or add to ~/.bashrc or ~/.zshrc
   ```

## Python SDK Usage

```python
from groq import Groq
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

# Simple chat
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "안녕?"}]
)
print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "1부터 10까지 숫자세기"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# List models
models = client.models.list()
for model in models.data:
    print(f"- {model.id}")
```

## Available Models

| Model | Size | Context | Use Case |
|-------|------|---------|----------|
| llama-3.3-70b-versatile | 70B | 128K | General-purpose, best quality |
| llama-3.1-70b-versatile | 70B | 128K | General-purpose |
| llama-3.1-8b-instant | 8B | 128K | Ultra-low latency, real-time |
| mixtral-8x7b-32768 | 46.7B | 32K | MoE, longer context |
| gemma2-9b-it | 9B | 8K | Google Gemma 2, chat |
| whisper-large-v3 | - | - | Audio transcription (STT) |

## Pricing (as of 2026-06-04)

- llama-3.3-70b: $0.59/1M input + $0.79/1M output
- llama-3.1-70b: $0.59/1M input + $0.79/1M output
- llama-3.1-8b: $0.05/1M input + $0.08/1M output
- mixtral-8x7b: $0.27/1M input + $0.27/1M output
- gemma2-9b: $0.20/1M input + $0.20/1M output

## Hermes Integration

### Config.yaml Addition

```yaml
model:
  provider: groq  # Or use as fallback

custom_providers:
- name: groq
  base_url: https://api.groq.com/openai/v1
  key_env: GROQ_API_KEY
  api_mode: openai_chat
  model: llama-3.3-70b-versatile

# Auxiliary use cases
auxiliary:
  fast_chat:
    provider: groq
    model: llama-3.1-8b-instant  # Ultra-low latency
  audio_transcribe:
    provider: groq
    model: whisper-large-v3
  code_review:
    provider: groq
    model: llama-3.3-70b-versatile
```

### Recommended Use Cases

✅ **Good for**:
- Real-time chatbots (8B instant model)
- High-volume text generation (low cost)
- Code generation/review (70B quality)
- Audio transcription (Whisper)
- TTS (speech synthesis)

❌ **Avoid for**:
- High-quality Korean translation (Claude/GPT superior)
- Complex visual analysis (no vision support)
- Research-grade reasoning (GPT-4 level)

## Pros and Cons

### Pros
- ⚡ Very fast inference (Groq LPU)
- 💰 Low cost ($0.19/1M for 70B)
- 🎯 Streaming support
- 🎤 Audio processing (Whisper, TTS)
- 🔓 Open-source models (Llama, Mixtral, Gemma)

### Cons
- 🔑 Requires API key (free registration needed)
- 📉 No GPT-4 level models (Llama 3.3 is top)
- 🇰🇷 Korean quality = Llama level (good but not best)
- 👀 No vision support
- 🔧 No native CLI tool (Python SDK only)

## Comparison with Other Providers

| Provider | Model | Speed | Cost | Korean | Vision |
|----------|-------|-------|------|--------|--------|
| Groq | Llama 3.3 70B | ⚡⚡⚡ | 💰💰 | 🟡 | ❌ |
| Anthropic | Claude Opus 4.8 | ⚡⚡ | 💰💰💰💰 | 🟢🟢 | ✅ |
| OpenAI | GPT-4 | ⚡ | 💰💰💰 | 🟢🟢 | ✅ |
| GLM (Z.ai) | GLM 5.0 | ⚡⚡ | 💰💰💰 | 🟢 | ❌ |

## Testing and Verification

```bash
# Test Python SDK
source ~/.venv-groq/bin/activate
python3 << 'EOF'
from groq import Groq
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

# Simple test
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "한국어로 안녕"}],
    max_tokens=50
)
print(response.choices[0].message.content)
EOF

# Test streaming
python3 << 'EOF'
from groq import Groq
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "1부터 5까지"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
EOF
```

## Audio Processing (Whisper + TTS)

```python
# Audio transcription (STT)
with open("audio.mp3", "rb") as file:
    transcription = client.audio.transcriptions.create(
        file=(file.name, file.read()),
        model="whisper-large-v3",
        language="ko"
    )
    print(transcription.text)

# Text-to-speech (TTS)
speech = client.audio.speech.create(
    model="playai-tts",  # Check latest TTS model
    voice="Arc",
    input="안녕하세요"
)

with open("output.mp3", "wb") as f:
    f.write(speech.content)
```

## References

- Official docs: https://console.groq.com/docs
- Pricing: https://console.groq.com/docs/pricing
- Models: https://console.groq.com/docs/models
- Python SDK: https://github.com/groq/groq-python

## Case Study: 2026-06-04 Analysis

**Task**: Evaluate Groq for Hermes integration

**Findings**:
- Python SDK v1.4.0 installed successfully
- API key required (https://console.groq.com/keys)
- 6 chat models + 1 audio model available
- Ultra-low latency on 8B model
- Llama 3.3 70B provides near-GPT-4 quality

**Recommendation**:
- Use as auxiliary provider for:
  - Fast chat (llama-3.1-8b-instant)
  - Code review (llama-3.3-70b-versatile)
  - Audio processing (whisper-large-v3)
- Not for primary Korean tasks (use GLM/Claude instead)

**Next Steps**:
1. Register at console.groq.com
2. Get API key
3. Add to Hermes config.yaml
4. Test with auxiliary use cases