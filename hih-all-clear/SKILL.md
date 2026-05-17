---
name: hih-all-clear
description: 전 프로젝트 세션 일괄 정리. 각 세션 상황 파악 → /hih-clear → /clear. PM 오케스트레이터용 배치 종료 루틴.
user_invocable: true
---

# /hih-all-clear 스킬

PM에서 한 번에 **모든 프로젝트 tmux 세션** 정리 + 종료.

## 언제 쓰나

- 하루 작업 마무리 시 전 세션 한꺼번에 정리
- PC 재시작 전 전 프로젝트 깔끔하게 handoff
- 장기 세션 context 고갈 직전 일괄 리셋

## 실행 순서

### 1. 세션 목록 파악
```bash
tmux list-sessions | awk -F: '{print $1}' | grep -v '^PM$'
```

대상 세션 (`projects.yaml` 기반):
- 인성이, insung_blog, 주식부자, 자율주행, music-lab, be-a-studio, polistat, 포트폴리오
- 모니터/보조 세션은 제외 (`*-monitor` 등)

### 2. 사전 상황 파악 (요약 보고)
각 세션마다:
- `tmux capture-pane -t {session} -p | tail -10` — 현재 상태
- pane별 context 잔량 추출 (`[Opus 4.6 ...] NN%` 라인)
- idle/busy 판정
- git status 요약 (uncommitted 개수)

결과 테이블로 출력:
```
| 세션 | context | 상태 | uncommitted | 비고 |
|------|---------|------|-------------|------|
```

### 3. 병렬 /hih-clear 송신

각 세션에 `/hih-clear` 송신 (tmux send-keys):
```bash
for session in "${sessions[@]}"; do
  tmux send-keys -t "$session" '/hih-clear' Enter
done
```

**병렬 실행** — 각 세션이 독립적으로 정리. 평균 3-5분.

### 4. 완료 폴링

각 세션이 "세션 정리 완료" 또는 "/clear 실행 준비됨" 문구 출력할 때까지 대기:
- 30초 간격 폴링
- 최대 15분 타임아웃
- 완료된 세션부터 순차 /clear

### 5. /clear 송신

완료된 세션부터 `/clear`:
```bash
tmux send-keys -t "$session" '/clear' Enter
```

### 6. 최종 확인
각 세션 clear 후 3초 대기 → capture로 Claude Code 시작 화면 확인.

### 7. PM 세션 자체 처리
PM 세션은 자기 자신을 /clear 못 함. 내부에서 /hih-clear 실행 후 사용자에게 안내:

```
## PM 세션 마지막
모든 프로젝트 세션 정리 완료.
PM 세션은 사용자가 터미널에 /clear 직접 입력하세요.
```

### 8. 종합 보고

```markdown
## /hih-all-clear 결과 — {날짜}

### 정리된 세션 (N개)
| 세션 | /hih-clear | /clear | 커밋 | 메모리 |
|------|:---------:|:------:|:----:|:------:|
| 인성이 | ✓ | ✓ | 53커밋 ahead | ✓ |
| 주식부자 | ✓ | ✓ | 2커밋 ahead | - |
...

### 실패/스킵 (있으면)
- {세션}: 사유

### PM 세션
- /hih-clear 완료
- 사용자가 /clear 직접 입력 필요

### 다음 세션
전 프로젝트 handoff.md 저장됨. 아침에 해당 세션 진입 시 자동 로드.
```

## 주의사항

- **실행 중인 작업 중단 위험**:
  - busy 세션(진행 중인 tool)에 /hih-clear 송신하면 **큐에 쌓이거나 무시될 수 있음**
  - 사전 idle 판정 필수
  - busy면 경고 + 사용자에게 계속 진행할지 확인

- **uncommitted 파일 보호**:
  - /hih-clear가 자체적으로 커밋 처리하지만 이중 확인
  - 민감 파일(.env, credentials) 자동 커밋 금지

- **git push 금지**:
  - 각 세션의 /hih-clear는 push 안 함
  - PM이 일괄 push는 별도 스킬/결정

- **병렬 실행 한도**:
  - 8개 세션 동시 /hih-clear → 메모리 부담
  - 동시 4개씩 나눠 배치도 가능

## 자동화 참고

구현 시 shell 스크립트 또는 Python 래퍼로:
```python
# scripts/hih_all_clear.py (제안)
#!/usr/bin/env python3
import subprocess, time, yaml

def main():
    sessions = get_project_sessions()  # projects.yaml 기반
    for s in sessions:
        check_idle(s) or warn_and_skip(s)
    parallel_send(sessions, '/hih-clear')
    wait_for_all_done(sessions, timeout=900)
    parallel_send(completed, '/clear')
    report()

if __name__ == "__main__":
    main()
```

또는 순수 bash:
```bash
scripts/hih-all-clear.sh
```

## 관련 스킬/룰

- `~/.claude/skills/hih-clear` — 단일 세션 정리
- `~/.claude/skills/hih-task` — 태스크 브리핑
- `~/.claude/skills/hih-git` — 전체 git 브리핑 + 일괄 push
- `global-rules/parallel-delegation.md` — 병렬 실행 원칙
- `global-rules/test-after-change.md` — 자동 테스트 원칙
