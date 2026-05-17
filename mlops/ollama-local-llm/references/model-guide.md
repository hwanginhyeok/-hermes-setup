# Ollama Model Selection Guide

## Model Families

### Llama (Meta)
- **llama3.2**: Latest, excellent general purpose
- **llama3.1**: Still solid, wider tool ecosystem
- **Best for**: English, code, reasoning

### Qwen (Alibaba)
- **qwen2.5**: Strong multilingual (Korean, Chinese, Japanese)
- **qwen2.5:3b**: Fast, good for translations
- **Best for**: Asian languages, bilingual tasks

### Gemma (Google)
- **gemma3**: Latest, instruction-tuned
- **gemma2**: Capable, slightly older
- **Best for**: Safety, general knowledge

### Mistral
- **mistral**: Balanced, efficient
- **mixtral**: Mixture-of-experts, higher quality
- **Best for**: French, code, efficiency

## Size Tradeoffs

| Size | VRAM | Speed | Quality | Use Case |
|------|------|-------|---------|----------|
| 3B   | ~4GB | Fast   | Good    | Quick tasks, low VRAM |
| 4B   | ~6GB | Fast   | Good    | Balanced |
| 7B   | ~8GB | Medium | Very Good | Default choice |
| 14B  | ~14GB| Slow   | Excellent| Complex reasoning |
| 70B+ | ~40GB| Very Slow| Best | Production, research |

## Multilingual Support Rankings

1. **Qwen2.5**: Best for Korean, Chinese, Japanese
2. **Gemma3**: Strong multilingual, but slightly behind Qwen
3. **Llama3.2**: Good for major languages, weaker for CJK
4. **Mistral**: Strong for European languages

## Recommended by Use Case

- **Korean chatbot**: `qwen2.5:3b` or `qwen2.5:7b`
- **Code assistant**: `llama3.2` or `mistral:7b`
- **Fast autocomplete**: `qwen2.5:3b` or `gemma3:4b`
- **General QA**: `llama3.2` (default 7B)
- **Translation**: `qwen2.5:7b` (bilingual strength)

## Context Windows

- Default: 4096 tokens
- Extended: Pull `:32k` or `:128k` variants if available
- Cost: Longer context = slower inference

## Quantization

Models come quantized (compressed) by default:
- **Q4_K_M**: Default, good balance
- **Q5_K_M**: Slightly better quality, larger
- **Q8_0**: Near-fp16 quality, much larger
- **Q2_K**: Fast, lower quality

Most users don't need to worry about this—Ollama picks sensible defaults.
