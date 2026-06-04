---
name: hih-claude
description: |
  Delegate coding to Claude Code CLI (features, PRs, reviews).
  Claude Code CLI is Anthropic's autonomous coding agent integrated with Claude Sonnet/Opus.
  Use when: "claude coding", "claude review", "claude feature", "claude PR"
user_invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# /hih-claude — Claude Code CLI

Claude Code CLI로 코딩 작업을 위임합니다. Anthropic의 자율 주행 코딩 에이전트입니다.

## 핵심 원리

Claude Code CLI는 `claude` 명령어로 실행되며:
- **기본 모델**: Claude Sonnet 4.6 (1M context) 또는 Opus 4.7 (200K context)
- **Git 네이티브**: 자동으로 diff 추적, commit 제안
- **툴 통합**: Bash, Edit, 파일 시스템에 직접 접근
- **PTY 불필요**: Codex와 달리 PTY 없이도 정상 작동

## 전제 조건

1. **Claude Code CLI 설치**: `~/.local/bin/claude` (이미 설치됨)
2. **Claude 계정 로그인**: `claude` 실행 시 자동 인증 (Max 계정: dlsgur5560@gmail.com)
3. **Git 저장소 필수**: Codex와 동일하게 git 밖에서 실행 거부

## 실행 모드

### 1. One-Shot 모드 (단발 작업)

```bash
# 기본 실행 (현재 디렉토리)
terminal(command="claude -p 'Add dark mode toggle to settings'", workdir="~/project")

# 특정 디렉토리 추가 접근 허용
terminal(command="claude --add-dir ~/project/lib -p 'Refactor the auth module'", workdir="~/project")

# 비용 제한 (USD)
terminal(command="claude --max-budget-usd 0.5 -p 'Fix the login bug'", workdir="~/project")
```

### 2. Background 모드 (장기 작업)

```bash
# 백그라운드 실행
terminal(command="claude --continue -p 'Refactor the entire auth module with tests'", workdir="~/project", background=true)
# Returns session_id

# 진행 상황 확인
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 종료
process(action="kill", session_id="<id>")
```

### 3. 인터랙티브 모드 (세션 지속)

```bash
# 새 세션 시작 (PTY 사용)
terminal(command="claude --name feature-auth", workdir="~/project", pty=true)

# 이전 세션 재개
terminal(command="claude --continue", workdir="~/project", pty=true)

# PR 연동 세션
terminal(command="claude --from-pr 42", workdir="~/project", pty=true)
```

## 주요 플래그

| 플래그 | 효과 |
|-------|------|
| `-p, --print` | 비인터랙티브 출력 (자동 스크립트용) |
| `--continue` | 마지막 대화 재개 |
| `--add-dir <path>` | 추가 디렉토리 접근 허용 |
| `--model <model>` | 모델 지정 (sonnet/opus 또는 전체 이름) |
| `--agent <agent>` | 커스텀 에이전트 지정 |
| `--max-budget-usd <amount>` | 최대 비용 제한 |
| `--from-pr [pr]` | PR에서 세션 재개 |
| `--chrome` | Chrome integration 활성화 |

## PR 리뷰

### 단일 PR 리뷰

```bash
# 현재 브랜치 vs main
terminal(command="claude -p 'Review this branch vs main. Focus on security issues.'", workdir="~/project")

# 특정 PR 번호
terminal(command="claude --from-pr 42 -p 'Review this PR for performance issues'", workdir="~/project")
```

### 배치 PR 리뷰 (병렬)

```bash
# 여러 PR 병렬 리뷰
terminal(command="claude --from-pr 86 -p 'Review PR #86'", workdir="~/project", background=true)
terminal(command="claude --from-pr 87 -p 'Review PR #87'", workdir="~/project", background=true)

# 결과 확인
process(action="list")
```

## 기능 개발 워크플로우

### 1. 신규 기능 구현

```bash
# 간단한 기능
terminal(command="claude -p 'Add user profile page with avatar upload'", workdir="~/project")

# 복잡한 기능 (세션 지속)
terminal(command="claude --name feature-payment -p 'Implement Stripe payment flow with webhook handling'", workdir="~/project", background=true)
```

### 2. 버그 수정

```bash
# 단일 버그
terminal(command="claude -p 'Fix the memory leak in the image processing function'", workdir="~/project")

# 여러 버그 병렬 (worktree 활용)
terminal(command="git worktree add -b fix/bug-78 /tmp/bug-78 main", workdir="~/project")
terminal(command="claude -p 'Fix issue #78: null pointer exception'", workdir="/tmp/bug-78", background=true)
```

### 3. 리팩토링

```bash
# 모듈 리팩토링
terminal(command="claude --add-dir ~/project/src -p 'Refactor auth module to use dependency injection'", workdir="~/project")

# 전체 프로젝트 리팩토링 (주의: 비용 높음)
terminal(command="claude --effort high -p 'Refactor all API endpoints to use async/await'", workdir="~/project", background=true)
```

## 커스텀 에이전트

```bash
# 리뷰어 에이전트 정의
terminal(command="""claude --agents '{"reviewer": {"description": "Security-focused code reviewer", "prompt": "You are a security expert. Review code for vulnerabilities, SQL injection, XSS, etc."}}' -p 'Review this PR'""", workdir="~/project")

# 테스터 에이전트 정의
terminal(command="""claude --agents '{"tester": {"description": "Test engineer", "prompt": "Write comprehensive tests including edge cases"}}' -p 'Add tests for the payment module'""", workdir="~/project")
```

## 모델 선택

```bash
# Sonnet (기본, 빠름)
terminal(command="claude -p 'Add unit tests for utils.py'", workdir="~/project")

# Opus (정확도 우선, 느림)
terminal(command="claude --model opus -p 'Refactor complex algorithm for performance'", workdir="~/project")

# 특정 모델 버전
terminal(command="claude --model claude-sonnet-4-6 -p 'Fix bug'", workdir="~/project")
```

## 규칙

1. **Git 필수**: 항상 git 저장소 내에서 실행 (Codex와 동일)
2. **PTY 불필요**: Codex와 달리 PTY 없이도 정상 작동
3. **비용 주의**: Opus 사용 시 `--max-budget-usd` 권장
4. **세션 관리**: 장기 작업은 `background=true` + `process` 모니터링
5. **병렬 실행 가능**: 여러 claude 프로세스 동시 실행 (Codex와 동일)
6. **diff 확인**: claude가 자동으로 commit 제안하지만, PM은 반드시 `git diff`로 검증

## Codex vs Claude Code 비교

| 항목 | Codex | Claude Code |
|------|-------|-------------|
| PTY | 필수 | 불필요 |
| 기본 모델 | GPT-4o | Claude Sonnet 4.6 |
| Context | 128K | 1M (Sonnet), 200K (Opus) |
| 설치 | npm | npm (binary) |
| 인증 | OpenAI | Claude 계정 |
| Cost | $20/월 무료 | Claude Max 요금제 |
| 한국어 | 약함 | 강함 |

## 사용 예시

### 간단한 기능
```bash
terminal(command="claude -p 'Add dark mode toggle'", workdir="~/be-a-studio")
```

### 복잡한 기능 (배경)
```bash
terminal(command="claude --continue -p 'Implement OAuth2 flow with Google and GitHub'", workdir="~/be-a-studio", background=true)
process(action="poll", session_id="<id>")
```

### PR 리뷰
```bash
terminal(command="claude --from-pr 123 -p 'Review for security issues'", workdir="~/be-a-studio")
```

### 배치 버그 수정
```bash
# worktree 생성 후 병렬 실행
terminal(command="git worktree add -b fix/bug-1 /tmp/bug-1 main", workdir="~/project")
terminal(command="git worktree add -b fix/bug-2 /tmp/bug-2 main", workdir="~/project")
terminal(command="claude -p 'Fix bug #1'", workdir="/tmp/bug-1", background=true)
terminal(command="claude -p 'Fix bug #2'", workdir="/tmp/bug-2", background=true)
```

## 에러 처리

```bash
# Claude 계정 미로그인
# 에러: "Not logged in. Run 'claude' to authenticate."
# 해결: `claude` 실행 후 브라우저 인증

# Git 저장소 아님
# 에러: "Not in a git repository"
# 해결: `git init` 또는 기존 저장소로 이동

# API 키 만료
# 에러: "Authentication failed"
# 해결: `claude` 재실행으로 재인증
```

## 검증 사례

Claude Code CLI는 이미 PM 환경에서 검증됨:
- CLI 경로: `/home/window11/.local/bin/claude` ✅
- 계정: Claude Max (dlsgur5560@gmail.com) ✅
- 사용량: 12개 병렬 프로세스로 8.4GB RAM 소모 경험 있음 → 필요 시 `pkill -f "claude --add-dir"`로 종료

## Use when

- "claude coding", "claude review", "claude feature", "claude PR"
- "Claude로 구현해줘", "Claude가 리뷰해줘"
- Codex 대안 필요 시 (더 나은 한국어, 더 큰 context)
