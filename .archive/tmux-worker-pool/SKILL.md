---
name: tmux-worker-pool
version: 1.0.0
description: tmux 기반 다중 프로젝트 병렬 관리 시스템. PM 세션이 각 프로젝트 에이전트(bea/insung/stock/music)에 작업을 지시하고 결과를 검증합니다.
skill_category: project-management
last_updated: 2026-05-17
---

# tmux 워커 풀 관리

다중 프로젝트를 tmux 세션으로 병렬 관리하는 아키텍처. PM 세션이 각 프로젝트 에이전트에 작업을 지시하고 결과를 검증합니다.

## 세션 구조

| 세션 | panes | 역할 | 경로 |
|------|-------|------|------|
| PM | 4 | 오케스트레이터 (claude + bash×3) | ~/project-manager |
| bea | 4 | be-a-studio (claude + bash×3) | ~/be-a-studio |
| insung | 3 | 인성이 (claude + bash×2) | ~/insung_blog |
| stock | 3 | 주식부자 (claude + bash×2) | ~/stock |
| music | 3 | music-lab (claude + bash×2) | ~/music-lab |
| hermes | 2 | 자동화/cron (hermes chat + bash) | ~ |

pane 1은 claude 자동 시작, 나머지는 bash 대기 중.

## 세션 시작

### 전체 생성
```bash
cd ~/project-manager
./open-all.sh
```

### 🔴 Pitfall: split-window -p vs -v
`split-window -p`는 퍼센트로 분할하지만, 4개 pane을 만들 때 실제로는 2개만 생성되는 문제가 있음. 이유: `-p`가 상대 크기로 계산되면서 누산 오류 발생.

**증상**: 4 pane을 요청했는데 2 pane만 생성됨

**해결**: `split-window -v` 사용 + 명시적 높이 지정
```bash
# ❌ 문제: split-window -p
tmux split-window -p 75 -c ~/be-a-studio  # 첫 번째 분할
tmux split-window -p 50 -c ~/be-a-studio  # 두 번째 분할 (실제로는 pane 2개만 생성됨)

# ✅ 해결: split-window -v + 명시적 높이
tmux split-window -v -l 60 -c ~/be-a-studio   # 첫 번째 분할 (60% 높이)
tmux split-window -v -l 30 -c ~/be-a-studio   # 두 번째 분할 (30% 높이)
tmux split-window -v -c ~/be-a-studio         # 세 번째 분할 (나머지 10%)
```

`open-all.sh`의 `create_project_session()` 함수를 수정하여 `-p` 대신 `-v -l` 사용.

### 중복 세션 문제 해결
`open-all.sh`는 영문 세션명(`stock`, `insung`, `music`)을 생성하지만, `projects.yaml`은 한글 프로젝트명(`주식부자`, `인성이`, `music-lab`)을 사용합니다. 기존 한글 세션이 있으면 중복 생성됩니다.

**해결:**
```bash
# 한글 세션 삭제
tmux kill-session -t 주식부자
tmux kill-session -t 인성이
tmux kill-session -t 자율주행
tmux kill-session -t polistat

# 재생성
./open-all.sh
```

### 개별 세션 접속
```bash
tmux attach -t PM      # PM 세션
tmux attach -t bea     # be-a-studio
tmux attach -t insung  # 인성이
tmux attach -t stock   # 주식부자
tmux attach -t music   # music-lab
```

## 에이전트 투입

### 자동 투입 (/hih-dev 스킬)
구분되는 기능 개발 시 자동으로 서브태스크 분해 → 병렬 에이전트 시작

### 수동 투입
```bash
# bea 세션 pane 2에 에이전트 시작
tmux send-keys -t bea:1.2 "claude --add-dir ~/project-manager" Enter

# 태스크 브리핑 전달
cat > /tmp/hih_task_B.md << 'EOF'
서브태스크 B: ...
EOF
tmux send-keys -t bea:1.2 "cat /tmp/hih_task_B.md" Enter

# 에이전트 종료
tmux send-keys -t bea:1.2 "/exit" Enter
```

## 상태 확인

### 전체 세션 현황
```bash
tmux list-sessions
```

### 특정 세션의 pane 수
```bash
tmux list-panes -t PM:1    # PM 세션의 window 1
tmux list-panes -t bea:1.1 # bea 세션의 pane 1
```

### PM 도구로 현황
```bash
cd ~/project-manager
python3 pm.py sessions    # 전체 세션 상태
python3 pm.py status      # 통합 현황 대시보드
```

## 작업 지시 플로우

1. PM이 프로젝트 세션 선택 (bea/stock/insung/music)
2. 세션 내 빈 bash pane에 claude 시작 후 작업 브리핑 전달
3. 여러 에이전트 병렬 실행 가능 (pane 1~4)
4. 완료 후 PM이 결과 검증 (지시 vs 실행 갭 리뷰)

## pane 추적

### 현재 실행 중인 Claude 프로세스 확인
```bash
# tmux pane별 실행 프로세스
for session in PM bea insung stock music; do
    echo "[$session]"
    for i in {1..4}; do
        pane_pid=$(tmux display-message -p -t "$session:1.$i" "#{pane_pid}" 2>/dev/null)
        if [ -n "$pane_pid" ]; then
            child_pids=$(pgrep -P "$pane_pid" -f claude 2>/dev/null)
            if [ -n "$child_pids" ]; then
                for pid in $child_pids; do
                    cmd=$(ps -p "$pid" -o comm= 2>/dev/null)
                    mem=$(ps -p "$pid" -o %mem= 2>/dev/null)
                    echo "  Pane $i: PID=$pid, MEM=${mem}%, CMD=$cmd"
                done
            fi
        fi
    done
done
```

### 현재 세션 위치 확인
```bash
echo "Session: $(tmux display-message -p '#S:#I.#P')"
```

## 주의사항

### 중복 세션 방지
- 한글 세션명(`주식부자`, `인성이`)과 영문 세션명(`stock`, `insung`)이 공존하면 안 됩니다
- `open-all.sh` 실행 전 기존 세션 확인 필요

### 에이전트 종료 확인
- `/exit`로 정상 종료하지 않으면 좀비 프로세스 남음
- `ps aux | grep claude`로 불필요한 프로세스 확인

### 메모리 관리
- Claude 프로세스 1개당 약 2~3% RAM (400MB)
- 너무 많은 에이전트 동시 실행 시 메모리 부족 가능

## 규칙

- 세션 = 프로젝트 고정 (세션마다 다른 프로젝트)
- PM은 코드 직접 수정 X (분석·리뷰·재지시만)
- 결과 보고는 "지시 vs 실행 갭 리뷰"로 검증

## 관련 문서

- `~/project-manager/CLAUDE.md` — PM 행동 원칙
- `~/project-manager/global-rules/` — 글로벌 규칙
- `projects.yaml` — 프로젝트 레지스트리 (SSOT)
