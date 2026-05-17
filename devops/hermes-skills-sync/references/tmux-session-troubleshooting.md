# tmux 세션 Pane 수 부족 문제 해결

## 문제 발생 (2026-05-17)

**증상**: `./open-all.sh` 실행해도 pane이 3~4개가 안 생김

**확인된 상태**:
- PM: 4 panes ✅
- bea: 4 panes ✅
- insung: 2 panes ❌ (3개여야 함)
- stock: 3 panes ✅ (하지만 중복 세션 존재)
- music: 미생성 ❌

## 원인 분석

### 1. 세션명 불일치

**`open-all.sh`의 기대**:
```bash
create_project_session "stock" "$HOME/stock" 3
create_project_session "insung" "$HOME/insung_blog" 3
```

**실제 tmux 세션**:
```
주식부자: 1 windows (1 pane only)
인성이: 1 windows (1 pane only)
```

**결과**: `open-all.sh`가 기존 세션을 감지 못하고 새로운 영문 세션(`stock`, `insung`)을 생성

### 2. 복제 세션 생성

```
stock: 3 panes (새로 생성됨) ✅
주식부자: 1 pane (구 세션) ❌
insung: 3 panes (새로 생성됨) ✅
인성이: 1 pane (구 세션) ❌
```

## 해결 방법

### 1단계: 중복 세션 정리

```bash
# 한글 세션 삭제
for session in 인성이 주식부자 자율주행 polistat; do
    tmux kill-session -t "$session" 2>/dev/null && echo "✅ $session 삭제됨"
done
```

### 2단계: 누락된 pane 보완

```bash
# insung 세션에 누락된 pane 1개 추가
current=$(tmux list-panes -t "insung:1" 2>/dev/null | wc -l)
if (( current < 3 )); then
    tmux split-window -t "insung:1" -c "$HOME/insung_blog"
    tmux select-layout -t "insung:1" main-vertical
    tmux select-pane -t "insung:1.1"
    echo "✅ insung (${current}→3 panes 보완)"
fi
```

### 3단계: 누락된 세션 생성

```bash
# music-lab 세션 생성 (누락됨)
if ! tmux has-session -t music 2>/dev/null; then
    tmux new-session -d -s music -c "$HOME/music-lab"
    tmux send-keys -t "music:1.1" "claude --add-dir $HOME/project-manager" Enter
    tmux split-window -t "music:1" -c "$HOME/music-lab"
    tmux split-window -t "music:1" -c "$HOME/music-lab"
    tmux select-layout -t "music:1" main-vertical
    tmux select-pane -t "music:1.1"
    echo "✅ music (3 panes)"
fi
```

### 4단계: 최종 검증

```bash
# 각 세션별 pane 수 확인
for session in PM bea insung stock music; do
    if tmux has-session -t "$session" 2>/dev/null; then
        panes=$(tmux list-panes -t "$session:1" 2>/dev/null | wc -l)
        echo "$session: $panes panes"
    fi
done
```

**예상 출력**:
```
PM: 4 panes
bea: 4 panes
insung: 3 panes
stock: 3 panes
music: 3 panes
```

## 예방 조치

### 1. `open-all.sh`와 `projects.yaml` 일치

**`projects.yaml`**:
```yaml
projects:
  주식부자:
    path: /home/window11/stock
    # ...
  인성이:
    path: /home/window11/insung_blog
    # ...
```

**`open-all.sh`**:
```bash
create_project_session "주식부자" "$HOME/stock" 3
create_project_session "인성이" "$HOME/insung_blog" 3
```

### 2. 세션명 통일

- 영문 세션명: `stock`, `insung`, `music`
- 한글 세션명: `주식부자`, `인성이`, `music-lab`

둘 중 하나를 선택해서 전체적으로 일치시킬 것.

## 관련 문서

- `~/project-manager/open-all.sh` — tmux 세션 생성 스크립트
- `~/project-manager/projects.yaml` — 프로젝트 레지스트리
- `~/project-manager/CLAUDE.md` — tmux 세션 아키텍처 정의

---

*해결일: 2026-05-17*
*상태: ✅ 해결됨*
