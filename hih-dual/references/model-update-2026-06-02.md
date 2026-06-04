# hih-dual 모델 업데이트 (2026-06-02)

## 업데이트 내역

### 모델 변경

| 역할 | 이전 | 현재 | 이유 |
|------|------|------|------|
| builder | Sonnet 4.6 1M | Opus 4.8 | 더 깊은 추론, 복잡한 로직 처리 |
| reviewer (default) | GLM 4.6 | GLM 5.0 | 최신 버전, default 상태에서 바로 사용 가능 |
| reviewer (alternative) | GLM 5.1 | Codex 5.5 | 제3자 의견, 거짓 우려 과다 시 재리뷰용 |

### SKILL.md 변경사항

1. **description**: "Sonnet 4.6 1M + GLM 4.6" → "Opus 4.8 + GLM 5.0"
2. **핵심 원리 섹션**: 모델명 업데이트
3. **Step 1 (pane 2 전환)**: 제거 (default가 GLM 5.0이라 전환 불필요)
4. **보고 메시지**: "Sonnet 4.6 1M 완료" → "Opus 4.8 완료"
5. **리뷰어 발사**: "Sonnet 4.6" → "Opus 4.8"
6. **Reviewer verbatim**: "GLM 4.6" → "GLM 5.0"
7. **PM 검증**: GLM 5.0도 거짓 우려 던질 수 있음을 명시
8. **보고 포맷**: 모델명 업데이트
9. **에러 처리**: "reviewer 4.6 거짓 우려 5건+" → "reviewer GLM 5.0 거짓 우려 5건+"
10. **Step 10 복귀**: "glm-5.1" → "glm-5.0"
11. **검증 사례**: 최신 모델 업데이트 내역 추가
12. **사용 예**: 복잡한 로직 개발 예시 추가

### config.yaml 변경사항

#### 전역 config.yaml (~/.hermes/config.yaml)

```yaml
custom_providers:
- name: zai-glm
  base_url: https://api.z.ai/api/anthropic
  key_env: Z_AI_API_KEY
  api_mode: anthropic_messages
- name: codex
  base_url: https://api.openai.com
  key_env: OPENAI_API_KEY
  api_mode: openai_chat
  model: gpt-4o-5.5-preview
- name: opus
  base_url: https://api.anthropic.com
  key_env: ANTHROPIC_API_KEY
  api_mode: anthropic_messages
  model: claude-opus-4-8
```

#### PM profile config.yaml (~/.hermes/profiles/pm/config.yaml)

```yaml
model:
  provider: zai-glm
  default: glm-5.0  # glm-4.7 → glm-5.0
```

## 사용법

### Opus 4.8 + GLM 5.0 사이클

```bash
# music-lab cwd에서
/hih-dual "PIPE-F10c — token_guard rate_limit 매칭 픽스. 'rateLimitExceeded' (camelCase→ratelimitexceeded) 누락 케이스 추가 + 테스트 1개"

# 복잡한 로직 개발 (Opus 4.8의 깊은 추론 필요)
/hih-dual "PaymentGateway 클래스 재구성 — 3rd party 통합 예외처리 + idempotency + saga pattern"
```

### Codex 5.5 재리뷰 (거짓 우려 5건+ 시)

```bash
# hih-codex 스킬로 호출 (별도 스킬 필요)
/hih-codex review <commit-hash>
```

## 예상 변화

### Opus 4.8 (builder)
- **장점**: Sonnet 대비 더 깊은 추론, 더 신중한 구현
- **단점**: 응답 속도 느림, 토큰 사용량 증가
- **적용**: 복잡한 로직, 아키텍처 재구성, 중요한 비즈니스 로직

### GLM 5.0 (reviewer)
- **장점**: 4.6 대비 최신 훈련 데이터, 더 정확한 비판
- **단점**: 여전히 거짓 우려 던질 수 있음 (PM 백스톱 필요)
- **적용**: default 상태에서 바로 사용 가능, pane 2 전환 불필요

### Codex 5.5 (alternative reviewer)
- **장점**: 제3자 의견, GLM 5.0의 거짓 우려 필터링
- **단점**: 추가 비용, 더 느린 응답
- **적용**: GLM 5.0이 거짓 우려 5건+ 던질 때 재리뷰용

## 레퍼런스

- Hermes Agent config structure: https://hermes-agent.nousresearch.com/docs/user-guide/configuration
- custom_providers는 YAML list (hyphen prefix), dict 아님
- API key는 환경 변수 (key_env)로만 참조, config.yaml에 하드코딩 금지