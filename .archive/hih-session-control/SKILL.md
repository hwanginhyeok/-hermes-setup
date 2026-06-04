---
name: hih-session-control
description: tmux 세션 및 pane 제어. PM에서 다른 세션의 에이전트를 시작/종료/관리. WSL 환경에서의 작업 방식.
tags: [tmux, session, pane, orchestration, WSL]
---

# hih-session-control

tmux 세션 및 pane 제어 스킬. PM에서 다른 세션의 에이전트를 시작/종료/관리합니다.

## 언제 사용?

- PM에서 다른 프로젝트 세션의 에이전트 시작/종료
- 여러 세션에 병렬 작업 배정
- 세션 상태 실시간 모니터링
- 특정 pane의 출력 캡처

## 전제 조건

1. tmux 실행 중이어야 함
2. 대상 세션이 존재해야 함
3. WSL 환경에서 Windows 브라우저 접근 가능

## 주요 명령어

| 명령 | 설명 |
|------|------|
| `status [세션]` | 세션 상태 확인 |
| `start-agent [세션] [pane]` | 에이전트 시작 |
| `stop-agent [세션] [pane]` | 에이전트 종료 |
| `capture [세션] [pane]` | pane 출력 캡처 |
| `list` | 모든 세션 목록 |
| `kill [세션]` | 세션 종료 |

## Step 1: 세션 상태 확인

```bash
# 특정 세션
STATUS=$(tmux capture-pane -t "$SESSION" -p | tail -10)

# 모든 세션
tmux list-sessions -F "#{session_name}: #{session_windows} windows, #{window_panes} panes"
```

### 상태 분석

```bash
# Claude 실행 중인지 확인
PANE_OUTPUT=$(tmux capture-pane -t "$SESSION.$PANE" -p)
if echo "$PANE_OUTPUT" | grep -qE "Cogitated for|Brewed for|Worked for|Sautéed for|Cooked for|Baked for"; then
    STATUS="running"
else
    STATUS="idle"
fi
```

## Step 2: 에이전트 시작

```bash
# pane에 에이전트 시작
tmux send-keys -t "$SESSION.$PANE" "claude --add-dir ~/project-manager" Enter

# 또는 특정 프로젝트 경로 지정
tmux send-keys -t "$SESSION.$PANE" "cd /home/window11/stock && claude" Enter
```

### 에이전트 시작 완료 대기

```bash
# 최대 60초 대기
for i in {1..12}; do
    OUTPUT=$(tmux capture-pane -t "$SESSION.$PANE" -p | tail -5)
    if echo "$OUTPUT" | grep -qE "Cogitated for|Brewed for"; then
        echo "✅ 에이전트 시작 완료"
        break
    fi
    sleep 5
done
```

## Step 3: 에이전트 종료

```bash
# /exit 명령으로 에이전트 종료
tmux send-keys -t "$SESSION.$PANE" "/exit" Enter
sleep 2
```

### 종료 확인

```bash
# bash 프롬프트 확인
OUTPUT=$(tmux capture-pane -t "$SESSION.$PANE" -p | tail -3)
if echo "$OUTPUT" | grep -q "$"; then
    echo "✅ 에이전트 종료 완료"
else
    echo "⚠️ 에이전트 여전히 실행 중"
fi
```

## Step 4: 병렬 작업 배정

```bash
# 여러 세션에 에이전트 동시 시작
SESSIONS=("bea" "stock" "insung" "music")

for SESSION in "${SESSIONS[@]}"; do
    tmux send-keys -t "$SESSION.2" "claude --add-dir ~/project-manager" Enter
done

echo "✅ 모든 세션에 에이전트 배정 완료"
```

## Step 5: 출력 캡처 및 PM으로 전송

```bash
# 다른 세션의 마지막 출력 캡처
OUTPUT=$(tmux capture-pane -t "bea.1.1" -p -S -3000)

# PM 세션으로 전송 (PM에서 읽을 수 있게)
tmux send-keys -t "PM:1.2" "echo '=== bea 세션 출력 ==='" Enter
tmux send-keys -t "PM:1.2" "echo '$OUTPUT'" Enter
```

## WSL 환경에서의 주의사항

### Windows 브라우저 접근

WSL에서는 `http://localhost:3000` 대신 Windows 브라우저에서 접근해야 합니다:

```bash
# Windows 경로로 URL 전달
URL="http://localhost:3000/dashboard"
WSL_PATH="/mnt/c/Users/window11/AppData/Local/Microsoft/Edge/User Data/Default/URL"

# WSL에서는 직접 안 열림
# Windows 브라우저에서 직접 열어야 함
```

### pane 번호 확인

```bash
# pane 수 확인
PANE_COUNT=$(tmux list-panes -t "$SESSION" | wc -l)

# open-all.sh 구조
# PM: 4 panes
# bea/stock/insung/music: 2 panes (pane1=claude, pane2=bash)

if [ "$PANE_COUNT" -lt 2 ]; then
    echo "⚠️ 세션에 pane이 부족합니다"
fi
```

## 예시

### 예시 1: bea 세션에 에이전트 시작

```bash
# PM에서
tmux send-keys -t "bea.2" "claude --add-dir ~/project-manager" Enter

# 완료 대기
sleep 20

# 출력 확인
tmux capture-pane -t "bea.2" -p | tail -20
```

### 예시 2: 여러 세션 병렬 작업 배정

```bash
# PM에서
SESSIONS=("bea" "stock" "insung")
for S in "${SESSIONS[@]}"; do
    tmux send-keys -t "$S.2" "claude --add-dir ~/project-manager" Enter
done
```

### 예시 3: stock 세션 출력 캡처

```bash
# PM에서 stock 세션의 마지막 20줄 캡처
OUTPUT=$(tmux capture-pane -t "stock.1.1" -p -S -3000)

# PM 세션에 표시
tmux send-keys -t "PM:1.2" "echo '=== stock 세션 출력 (최근 20줄) ==='" Enter
tmux send-keys -t "PM:1.2" "echo '$OUTPUT'" Enter
```

## 도구

- `tmux send-keys` - 명령어 전송
- `tmux capture-pane` - 출력 캡처
- `tmux list-sessions` - 세션 목록
- `tmux list-panes` - pane 목록

## 관련 스킬

- `hih-all-clear` - 전체 세션 정리
- `hih-task` - 태스크 관리
- `pm-orchestration` - PM 오케스트레이션

---

**Remember**: PM에서 다른 세션을 제어할 때는 tmux send-keys를 사용하고, 결과를 capture-pane으로 확인합니다.
