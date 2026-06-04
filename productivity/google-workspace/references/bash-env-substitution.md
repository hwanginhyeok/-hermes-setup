# Bash 환경변수 대체 패턴

## 문제
`alias claude-glm='ANTHROPIC_AUTH_TOKEN="$Z_AI_API_KEY" ...'`에서 `$Z_AI_API_KEY`가 직접 대체되지 않음

## 해결 방법

### 방법 1: eval 사용
```bash
alias claude-glm='eval $(cat ~/.secrets) && export ANTHROPIC_AUTH_TOKEN="$Z_AI_API_KEY" ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" API_TIMEOUT_MS=300000 claude'
```

### 방법 2: bash -c 사용
```bash
bash -c "source ~/.secrets && claude --model glm-5.1 ..."
```

### 방법 3: 함수 정의 후 export
```bash
load_zai() {
  source ~/.secrets
  export ANTHROPIC_AUTH_TOKEN="$Z_AI_API_KEY"
  export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
  export API_TIMEOUT_MS=300000
}

alias claude-glm='load_zai && claude'
```

## 패턴 비교

| 패턴 | 동작 | 설명 |
|-------|------|------|
| `VAR="value"` | 대체 안 됨 | 따옴표 안 값 그대로 사용 |
| `export VAR="$OTHER"` | 대체 안 됨 | 이미 export된 변수를 참조 |
| `eval $(cat file)` | 대체 됨 | 파일 내용을 평가하여 실행 |
| `bash -c "source file; cmd"` | 대체 됨 | 새 쉘에서 source 후 명령 실행 |

## 권장 방법

**eval 또는 bash -c 사용** - 변수 대체가 필요할 때마다
