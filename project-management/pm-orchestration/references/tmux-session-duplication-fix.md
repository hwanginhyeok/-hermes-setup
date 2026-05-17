# tmux 세션 중복 문제 해결

## 문제 증상
- `open-all.sh` 실행 후 특정 세션의 pane 수가 비정상 (1개만 생성됨)
- 영문 세션명(`stock`, `insung`)과 한글 세션명(`주식부자`, `인성이`)이 중복 존재

## 원인
- `open-all.sh`는 영문 세션명으로 생성 시도
- 과거에 한글 세션명으로 생성된 세션이 존재하면 중복됨
- `tmux has-session` 체크가 대소문자/한글 비교에서 엇갈림

## 해결 절차

### 1. 현재 상태 확인
```bash
tmux list-sessions
tmux list-panes -t 주식부자:1 2>/dev/null | wc -l
tmux list-panes -t stock:1 2>/dev/null | wc -l
```

### 2. 중복 세션 정리
```bash
# 한글 세션 삭제
tmux kill-session -t 주식부자 인성이 자율주행 polistat 2>/dev/null

# 영문 세션 유지 확인
tmux list-sessions
```

### 3. 누락된 세션/pane 보완
```bash
# music 세션 누락 시 생성
if ! tmux has-session -t music 2>/dev/null; then
    tmux new-session -d -s music -c "$HOME/music-lab"
    tmux send-keys -t "music:1.1" "claude --add-dir $HOME/project-manager" Enter
    tmux split-window -t "music:1" -c "$HOME/music-lab"
    tmux split-window -t "music:1" -c "$HOME/music-lab"
    tmux select-layout -t "music:1" main-vertical
    tmux select-pane -t "music:1.1"
fi

# pane 수 보완 (insung의 경우)
tmux split-window -t "insung:1" -c "$HOME/insung_blog"
tmux select-layout -t "insung:1" main-vertical
```

### 4. 검증
```bash
~/.hermes/skills/project-management/pm-orchestration/scripts/check_tmux_panes.sh
```

## 예방 조치
- `projects.yaml`의 프로젝트명(한글)과 `open-all.sh`의 세션명(영문) 일치 유지
- 향후 새 프로젝트 추가 시 영문 세션명만 사용 권장

## 해결 사례
- **날짜**: 2026-05-17
- **증상**: PM 4 panes 정상, bea 4 panes 정상, stock/insung 1 pane만 생성됨
- **원인**: 한글 세션(`주식부자`, `인성이`)이 먼저 생성되어 영문 세션(`stock`, `insung`) 생성 시도가 실패
- **결과**: 중복 세션 정리 후 모든 세션 정상화
