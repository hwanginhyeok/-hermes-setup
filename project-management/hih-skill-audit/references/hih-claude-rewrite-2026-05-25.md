# hih-claude 스킬 재작성 사례 (2026-05-25)

## 문제

- **폴더명**: `hih-claude`
- **기존 내용**: OpenAI Codex용 스킬 (name: codex)
- **문제점**: 사용자가 "Claude 관련 스킬"로 찾을 수 없음, 네이밍 부정합

## 해결

### 1. Claude Code CLI로 재작성

**기존 (Codex용)**:
```yaml
name: codex
description: "Delegate coding to OpenAI Codex CLI"
```

**신규 (Claude Code용)**:
```yaml
name: hih-claude
description: |
  Delegate coding to Claude Code CLI (features, PRs, reviews).
  Claude Code CLI is Anthropic's autonomous coding agent.
  Use when: "claude coding", "claude review", "claude feature", "claude PR"
```

### 2. Claude Code CLI 특성 반영

| 항목 | Codex | Claude Code |
|------|-------|-------------|
| PTY | 필수 | **불필요** |
| 기본 모델 | GPT-4o | **Claude Sonnet 4.6 (1M context)** |
| Context | 128K | **1M (Sonnet), 200K (Opus)** |
| 한국어 | 약함 | **강함** |
| Git | 필수 | **필수** |

### 3. 스킬 구조

- **243 lines** (기존 130 → 113 증가)
- YAML frontmatter 포함 ✅
- user_invocable: true ✅
- allowed-tools 명시 ✅
- Use when 트리거 포함 ✅

### 4. 주요 섹션

1. **핵심 원리**: Claude Code CLI 특성 (PTY 불필요, 1M context)
2. **전제 조건**: CLI 설치, 계정 로그인, Git 저장소
3. **실행 모드**: One-Shot, Background, Interactive
4. **PR 리뷰**: 단일/배치 리뷰
5. **기능 개발**: 신규 기능, 버그 수정, 리팩토링
6. **커스텀 에이전트**: 리뷰어, 테스터 정의
7. **모델 선택**: Sonnet (기본) / Opus (정확도)
8. **규칙**: Git 필수, PTY 불필요, 비용 주의
9. **Codex vs Claude Code 비교표**
10. **사용 예시**
11. **에러 처리**
12. **검증 사례**

## 테스트 결과

### CLI 버전 확인
```bash
$ claude --version
2.1.150 (Claude Code)
```

### One-shot 테스트
```bash
$ cd /tmp/test-claude-interactive && git init
$ claude -p "Add a Python function to calculate fibonacci numbers"
Created `fibonacci.py:1` with an iterative O(n) implementation...
```

### 결과 확인
```python
def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + 1
    return a
```

### 실제 프로젝트 테스트
```bash
$ cd ~/project-manager
$ claude -p "현재 프로젝트 구조를 분석해서..."
# PM 프로젝트의 SSOT 원칙을 준수하며 정상 동작
```

## 학습점

1. **네이밍 일치**: 폴더명과 SKILL.md의 name:을 일치시켜야 함
2. **실제 사용성**: 사용자가 "Claude"로 찾을 수 있도록 폴더명을 유지
3. **내용 재작성**: 잘못된 내용(Codex)을 올바른 내용(Claude Code)으로 완전 교체
4. **비교표 추가**: 기존 대안(Codex)과의 명확한 차이점 제시
5. **테스트 필수**: 실제 환경에서 CLI 동작을 검증

## 적용 가능한 패턴

다른 스킬에서도 유사한 네이밍 부정합 발견 시:
1. 폴더명을 유지할지 내용을 맞출지 결정
2. 폴더명이 더 명확하면 내용 재작성
3. 내용이 더 명확하면 폴더명 변경 (단, 심링크면 원본도 고려)
4. 비교표를 추가해서 사용자 선택 도와

## 참고

- Claude Code CLI 문서: https://docs.anthropic.com/en/docs/claude-code/overview
- hih-codex 스킬과 구분: Codex는 OpenAI, Claude Code는 Anthropic
