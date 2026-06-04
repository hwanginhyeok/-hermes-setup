---
name: hih-all-task-clear
description: 전 프로젝트 태스크 일괄 정리. PM에서 각 세션에 /hih-task-clear만 보내서 태스크만 정리. git/memory는 제외.
user_invocable: true
---

# /hih-all-task-clear

PM에서 **모든 프로젝트의 태스크만** 일괄 정리. git 커밋/메모리 정리는 제외.

## 언제 쓰나

- 하루 중간에 태스크만 정리하고 싶을 때
- 여러 세션에서 작업 후 태스크 상태만 동기화하고 싶을 때
- 세션 종료 없이 태스크 audit만 하고 싶을 때

## hih-all-clear와의 차이

| | hih-all-task-clear | hih-all-clear |
|---|---|---|
| **대상** | 태스크만 | 전체 (태스크 + git + memory + clear) |
| **실행** | /hih-task-clear만 | /hih-clear 전체 |
| **시간** | 1-2분 | 3-5분 |
| **세션 종료** | 안 함 | 함 (/clear까지) |

## 실행 순서

### 1. 세션 목록 파악

```bash
tmux list-sessions | awk -F: '{print $1}' | grep -v '^PM$'
```

대상 세션 (`projects.yaml` 기반):
- bea, stock, insung, music (focus 프로젝트)
- 기타 활성화된 프로젝트

### 2. 사전 상황 파악 (요약 보고)

각 세션마다:
- `tmux capture-pane -t {session} -p | tail -10` — 현재 상태
- pane별 context 잔량 추출 (`[Opus 4.6 ...] NN%` 라인)
- idle/busy 판정
- **CURRENT_TASK.md 줄 수** (진행 중 태스크)

결과 테이블로 출력:
```
| 세션 | context | 상태 | CURRENT 태스크 | 비고 |
|------|---------|------|--------------:|------|
| bea  | 45%     | idle | 3개           |      |
| stock| 12%     | busy | 1개           | 작업 중 |
| insung| 78%    | idle | 5개           |      |
```

### 3. 병렬 /hih-task-clear 송신

각 세션에 `/hih-task-clear` 송신 (tmux send-keys):
```bash
for session in "${sessions[@]}"; do
  tmux send-keys -t "$session" '/hih-task-clear' Enter
done
```

**병렬 실행** — 각 세션이 독립적으로 태스크 정리. 평균 1-2분.

### 4. 완료 폴링

각 세션이 "task_audit 완료" 또는 "태스크 정리 완료" 문구 출력할 때까지 대기:
- 10초 간격 폴링
- 최대 5분 타임아웃
- 완료된 세션부터 보고

### 5. 종합 보고

```markdown
## /hih-all-task-clear 결과 — {날짜}

### 정리된 세션 (N개)
| 세션 | 상태 | CURRENT | PREPARED | 이슈 |
|------|------|-------:|--------:|------|
| bea  | ✓    | 3→2개  | 12→14개 | 없음 |
| stock| ✓    | 1→1개  | 8→9개   | 정체 1건 |
| insung| ✓   | 5→3개  | 15→15개 | 없음 |

### 발견된 이슈
- stock: 정체 21일+ 태스크 1건 (STK-123)
- insung: P1 인플레이션 (75%)

### 다음 액션
- stock: STK-123 폐기/재시작 결정 필요
- insung: P1→P2 강검 후보 2건
```

## 주의사항

### 실행 중인 작업 중단 위험
- **busy 세션(진행 중인 tool)에 /hih-task-clear 송신하면 큐에 쌓임**
- 사전 idle 판정 필수
- busy면 경고 + 사용자에게 계속 진행할지 확인

### 태스크 파일만 처리
- **git 커밋 안 함** — 변경사항은 working directory에 남음
- **메모리 정리 안 함** — memory는 그대로
- **세션 종료 안 함** — 계속 작업 가능

### 병렬 실행 한도
- 8개 세션 동시 /hih-task-clear → 메모리 부담 적음 (태스크만 정리라서)
- 동시 전체 실행 가능

## 자동화 참고

구현 시 shell 스크립트:
```bash
# scripts/hih-all-task-clear.sh
#!/bin/bash

sessions=(bea stock insung music)

# 1. 상황 파악
for s in "${sessions[@]}"; do
  echo "=== $s ==="
  tmux capture-pane -t "$s" -p | tail -5
done

# 2. 병렬 송신
for s in "${sessions[@]}"; do
  tmux send-keys -t "$s" '/hih-task-clear' Enter
done

# 3. 완료 대기
sleep 90  # 1-2분 대기

# 4. 결과 확인
for s in "${sessions[@]}"; do
  echo "=== $s 결과 ==="
  tmux capture-pane -t "$s" -p | tail -10
done
```

## 관련 스킬

- `hih-task-clear` — 단일 세션 태스크 정리
- `hih-all-clear` — 전체 세션 일괄 정리 (태스크 + git + memory + clear)
- `hih-task` — 태스크 브리핑 + 관리

---

**Remember**: 이 스킬은 "태스크만 정리하고 싶을 때" 쓰는 것. 세션 종료는 hih-all-clear로.
