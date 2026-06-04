# xAI Grok CLI Discovery - 2026-06-04

## 발견 경로

사용자가 "이런게 있는데 ? curl -fsSL https://x.ai/cli/install.sh | bash 이거 있는거 아님"라고 지적.

## 초기 실수

1. PyPI에서 `grok-cli`, `xai-cli` 등 검색했지만 실제 패키지가 아님 (200 응답이지만 내용 없음)
2. `xai-grok` 커뮤니티 SDK 발견했지만 이건 CLI가 아님
3. `which grok` 명령어 실행하지 않음

## 올바른 검색 순서 (개선)

1. **먼저 `which <name>`**: 이미 설치되어 있는지 확인
   ```bash
   which grok  # → /home/window11/.local/bin/grok
   ```

2. **버전 확인**:
   ```bash
   grok --version  # → grok 0.2.3 (14d81fd87)
   ```

3. **공식 설치 스크립트 확인**:
   ```bash
   curl -fsSL https://x.ai/cli/install.sh | head
   ```

## xAI Grok CLI 상세

### 설치 정보

| 항목 | 값 |
|------|------|
| 버전 | 0.2.3 (14d81fd87) |
| 경로 | /home/window11/.local/bin/grok |
| 설치일 | 5월 27일 |
| 설치 명령 | `curl -fsSL https://x.ai/cli/install.sh \| bash` |

### 구조

```
~/.grok/
├── auth.json          # 인증 토큰 (로그인 후 생성)
├── auth.json.lock     # 현재 있음 (인증 필요)
├── config.toml        # 설정
├── bin/               # 바이너리
├── sessions/          # 세션 저장
├── skills/            # 스킬
├── memory/            # 메모리
├── downloads/         # 다운로드
└── logs/              # 로그
```

### 인증

**로그인 전**:
```
You are not authenticated.
Default model: grok-build
```

**로그인**:
```bash
grok login  # 브라우저 열림 → 인증 → ~/.grok/auth.json 생성
```

**토큰 유효기간**: 7일

### 주요 명령어

```bash
grok                  # TUI 모드
grok -p "프롬프트"     # Headless 모드
grok agent stdio      # Agent mode (ACP)
grok login            # 로그인
grok models           # 모델 리스트
grok sessions         # 세션 관리
grok memory           # 메모리 관리
grok mcp              # MCP 서버
grok update           # 업데이트
grok -m grok-2        # 모델 지정
```

### 옵션

```
-m, --model <MODEL>          모델 지정
-p, --single <PROMPT>        단발 응답
--output-format <FORMAT>    json, streaming-json, plain
--agent <NAME>               Agent 지정
-c, --continue               최근 세션 이어서
```

### 특징

- ✅ TUI + Headless 모드
- ✅ ACP (Agent Client Protocol) 지원
- ✅ Memory, MCP, Skills 지원
- ✅ Claude Code 호환
- ✅ 공식 CLI (자동 완성 스크립트 포함)
- ⚠️ 브라우저 인증 필요
- ⚠️ 토큰 7일 유효

## Groq vs xAI Grok 명확 구분

| 항목 | Groq | xAI Grok |
|------|------|----------|
| 회사 | Groq, Inc. | x.ai (Elon Musk) |
| 제품 | LPU 칩, 추론 인프라 | AI 모델 (Grok-2) |
| CLI | Python SDK만 (`pip install groq`) | 공식 CLI 있음 (`curl | bash`) |
| SDK | `pip install groq` | OpenAI SDK 호환 |
| API URL | api.groq.com | api.x.ai/v1 |
| 속도 | 매우 빠름 (LPU) | 빠름 |
| 가격 | $0.19/1M tokens | $0.001/1K tokens |
| 한국어 | 보통 (Llama) | 우수 |
| Vision | 미지원 | 미지원 |

## 교훈

### Pitfall 1: 이름 혼동

Groq와 xAI Grok는 완전히 다른 회사/제품:
- Groq = 추론 인프라 (LPU 칩)
- xAI Grok = AI 모델

### Pitfall 2: PyPI만 믿지 말기

`xai-grok` 패키지가 있다고 해서 그게 CLI인 것은 아님:
- `xai-grok`: 커뮤니티 Python SDK (CLI 아님)
- 공식 CLI: `curl -fsSL https://x.ai/cli/install.sh | bash`

### Pitfall 3: 검색 순서

올바른 순서:
1. `which <name>` (먼저 이미 설치되어 있는지 확인!)
2. 공식 문서/레포
3. PyPI/npm
4. 설치 스크립트 curl

### Pitfall 4: 호환 API 혼동

xAI Grok은 OpenAI 호환 API 제공:
```python
from openai import OpenAI

client = OpenAI(
    api_key="xai-...",
    base_url="https://api.x.ai/v1"
)
```

하지만 공식 CLI도 있음 - 둘 다 사용 가능.

## Hermes 통합

### Provider 추가 (OpenAI 호환)

```yaml
# config.yaml
custom_providers:
- name: xai
  base_url: https://api.x.ai/v1
  key_env: XAI_API_KEY
  api_mode: openai_chat
  model: grok-2
```

### CLI 사용 (Headless)

```bash
# 스크립트에서
grok -p --output-format json "이 코드 분석해줘" > result.json
```

## 참고

- xAI Grok CLI 문서: `~/.grok/README.md`
- xAI API: https://docs.x.ai/
- Groq SDK: https://console.groq.com/docs/quickstart