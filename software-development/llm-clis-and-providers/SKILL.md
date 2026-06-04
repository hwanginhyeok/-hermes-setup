---
name: llm-clis-and-providers
description: LLM CLI 툴 및 Provider 설정 관리. Grok CLI, OpenAI SDK, Groq SDK 등 다양한 LLM 클라이언트 검색, 설치, 설정, 사용법.
tags: [llm, cli, grok, groq, openai, xai, provider, setup]
---

# /llm-clis-and-providers

LLM CLI 툴 및 Provider 설정 관리.

## 언제 사용?

- 새로운 LLM CLI 툴 검색/설치 시
- LLM provider를 Hermes config에 추가 시
- Groq vs xAI Grok 혼동 방지
- 공식 CLI 확인 필요 시

## 자주 사용하는 CLI/SDK

### xAI Grok CLI (공식)

**설치**:
```bash
curl -fsSL https://x.ai/cli/install.sh | bash
```

**버전 확인**:
```bash
grok --version  # 예: grok 0.2.3
```

**사용법**:
```bash
# 로그인
grok login  # 브라우저 인증

# TUI 모드
grok

# Headless 모드
grok -p "프롬프트"
grok -p --output-format json "코드 분석"

# Agent mode (ACP)
grok agent stdio

# 모델 리스트
grok models

# 세션 관리
grok sessions
```

**인증**:
- 브라우저 로그인 (기본)
- 토큰 위치: `~/.grok/auth.json`
- 토큰 유효기간: 7일

**특징**:
- ✅ TUI + Headless 모드
- ✅ ACP (Agent Client Protocol)
- ✅ Memory, MCP, Skills
- ✅ Claude Code 호환

---

### OpenAI SDK (호환 API 많음)

**설치**:
```bash
pip install openai
```

**사용법**:
```python
from openai import OpenAI

client = OpenAI(
    api_key="...",
    base_url="https://api.example.com/v1"
)

response = client.chat.completions.create(
    model="...",
    messages=[{"role": "user", "content": "..."}]
)
```

**호환 API**:
- xAI Grok: `https://api.x.ai/v1`
- Groq: `https://api.groq.com/openai/v1`
- 기타 OpenAI 호환

---

### Groq SDK (전용)

**설치**:
```bash
pip install groq
```

**사용법**:
```python
from groq import Groq

client = Groq(api_key="gsk_...")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "..."}]
)
```

---

## Hermes Provider 추가

### OpenAI 호환 API

```yaml
# config.yaml
custom_providers:
- name: xai
  base_url: https://api.x.ai/v1
  key_env: XAI_API_KEY
  api_mode: openai_chat
  model: grok-2

- name: groq
  base_url: https://api.groq.com/openai/v1
  key_env: GROQ_API_KEY
  api_mode: openai_chat
  model: llama-3.3-70b-versatile
```

### 전용 SDK (Anthropic 등)

```yaml
custom_providers:
- name: zai-glm
  base_url: https://api.z.ai/api/anthropic
  key_env: Z_AI_API_KEY
  api_mode: anthropic_messages
```

---

## 검색 순서 (Pitfall 방지)

새로운 LLM CLI/SDK를 찾을 때는 다음 순서로 검색:

1. **공식 CLI 명령어 확인**: `which <name>` 또는 `<name> --version`
2. **공식 문서**: `<product>.com/docs` 또는 GitHub 레포
3. **PyPI**: `curl https://pypi.org/pypi/<package>/json`
4. **npm**: `npm search <name>`
5. **설치 스크립트**: `curl -fsSL https://<domain>/cli/install.sh`

**❌ 하지 말 것**:
- PyPI에 나온 것만 믿고 CLI가 있다고 단정 짓기
- 이름이 비슷하다고 같은 제품으로 단정 짓기 (Groq ≠ xAI Grok)

---

## 혼동 방지

### Groq vs xAI Grok

| 항목 | Groq | xAI Grok |
|------|------|----------|
| 회사 | Groq (LPU 칩) | x.ai (Elon Musk) |
| 제품 | 추론 인프라/SDK | AI 모델 (Grok-2) |
| CLI | Python SDK만 | 공식 CLI 있음 |
| URL | api.groq.com | x.ai |
| 속도 | 매우 빠름 (LPU) | 빠름 |
| 가격 | $0.19/1M | $0.001/1K |

---

## 현재 환경 확인

### xAI Grok CLI

```bash
# 설치 확인
which grok

# 버전 확인
grok --version

# 인증 상태
ls ~/.grok/auth.json

# 모델 리스트
grok models
```

### Groq SDK

```bash
# 패키지 확인
pip list | grep groq

# 설치 (없으면)
pip install groq
```

---

## 참고 자료

- xAI Grok CLI: `~/.grok/README.md`
- xAI Grok 설치: https://x.ai/cli/install.sh
- Groq SDK: https://console.groq.com/docs/quickstart
- OpenAI SDK: https://github.com/openai/openai-python