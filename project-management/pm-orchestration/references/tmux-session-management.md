# TMUX Session Management Patterns (2026-05-20)

## 표준 세션 구조

2026-05-20에 재구성된 표준:

| 세션 | Panes | 용도 | 경로 |
|------|------|------|------|
| PM | 4 | 오케스트레이터 (claude + bash×3) | ~/project-manager |
| bea | 2 | be-a-studio (claude + bash) | ~/be-a-studio |
| stock | 2 | 주식부자 (claude + bash) | ~/stock |
| insung | 2 | 인성이 (claude + bash) | ~/insung_blog |
| music | 2 | music-lab (claude + bash) | ~/music-lab |
| hermes | 2 | 자동화 (gateway + hermes chat) | ~ |

## 영문 세션명만 사용

**이유**: `open-all.sh`는 영문 세션명만 관리

**문제**: 한글 세션명(주식부자, 인성이, 자율주행)이 있으면 중복 생성

**해결**:
```bash
# 한글 세션 삭제
tmux kill-session -t 주식부자 인성이 자율주행 polistat 2>/dev/null

# 스크립트 재실행
cd ~/project-manager && ./open-all.sh
```

## open-all.sh 동작

### 자동 보완
- 세션이 있으면 pane 수 확인
- 설정된 pane 수보다 적으면 자동 추가
- 많으면 그대로 유지

### 실행 옵션
```bash
./open-all.sh              # 전체 생성
./open-all.sh --print      # 드라이런
./open-all.sh --kill       # 프로젝트 세션만 종료 (PM/hermes 유지)
./open-all.sh --kill-all   # 전체 종료
```

## Hermes 세션 특수 구성

### 구조
- Pane 1: `hermes gateway run` (cron 스케줄러 - 상시 실행)
- Pane 2: `hermes chat` (명령 인터페이스)

### open-all.sh 설정 (lines 121-130)
```bash
if ! tmux has-session -t hermes 2>/dev/null; then
    tmux new-session -d -s hermes -c "$HOME"
    tmux send-keys -t "hermes:1.1" "hermes gateway run" Enter
    tmux split-window -t "hermes:1" -h -c "$HOME"
    tmux send-keys -t "hermes:1.2" "hermes chat" Enter
    tmux select-pane -t "hermes:1.1"
fi
```

### Gateway 상태 확인
```bash
hermes gateway status
```

## 에이전트 투입 패턴

### 단일 에이전트
```bash
# stock 세션 pane 2에 에이전트 시작
tmux send-keys -t stock:1.2 "claude --add-dir ~/project-manager" Enter
```

### 병렬 에이전트 (여러 세션)
```bash
# bea, stock, insung에 동시 에이전트 시작
for session in bea stock insung; do
    tmux send-keys -t ${session}:1.2 "claude --add-dir ~/project-manager" Enter
done
```

### 에이전트 종료
```bash
# 특정 pane의 에이전트 종료
tmux send-keys -t bea:1.2 "/exit" Enter
```

## Pane 출력 캡처

### 단일 세션
```bash
# 마지막 50줄
tmux capture-pane -t stock:1.1 -p | tail -50

# 전체
tmux capture-pane -t stock:1.1 -p
```

### 전체 세션 현황
```bash
# 기본
tmux list-sessions

# 상세 (pane 수 포함)
tmux list-sessions -F "#{session_name}: #{window_panes} panes"
```

## 작업 위임 플로우

### 1. 태스크 브리핑 준비
```bash
cat > /tmp/hih_task_stock.md << 'EOF'
## 서브태스크: 테슬라 Q4 실적 분석
- 10-K 파일 다운로드
- 주요 지표 추출
- 전년동기 비교
EOF
```

### 2. 에이전트 시작 + 브리핑 전달
```bash
# 에이전트 시작
tmux send-keys -t stock:1.2 "claude --add-dir ~/project-manager" Enter

# 브리핑 전달
tmux send-keys -t stock:1.2 "cat /tmp/hih_task_stock.md" Enter
```

### 3. 완료 대기
```bash
# 에이전트 응답 상태 확인
tmux capture-pane -t stock:1.2 -p | grep -E "Cogitating|Undulating|Claude>"
```

### 4. 완료 후 종료
```bash
tmux send-keys -t stock:1.2 "/exit" Enter
```

## 문제 해결

### Pane 수가 맞지 않을 때

**증상**: PM은 4개, 나머지는 2개여야 하는데 다름

**원인 1**: 한글 세션 중복
```bash
# 해결
tmux list-sessions | awk -F: '{print $1}'
# 한글 세션 삭제 후 open-all.sh 재실행
```

**원인 2**: 스크립트 하드코딩 불일치
```bash
# open-all.sh 확인
grep -E "create_project_session|pane_count" ~/project-manager/open-all.sh
```

### Gateway가 실행 중이 아닐 때

**증상**: `hermes gateway status` → "Gateway is not running"

**해결**:
```bash
# hermes 세션 pane1에서
tmux send-keys -t hermes:1.1 C-c  # 기존 프로세스 중지
tmux send-keys -t hermes:1.1 "hermes gateway run" Enter
```

### 세션이 없을 때

**증상**: `tmux capture-pane` → "can't find session"

**해결**:
```bash
cd ~/project-manager && ./open-all.sh
```

## 모니터링 스크립트

### 전체 세션 health 체크
```bash
for session in PM bea stock insung music hermes; do
    echo "=== $session ==="
    tmux capture-pane -t $session:1.1 -p | tail -5
    echo ""
done
```

### Claude 프로세스 수 확인
```bash
ps aux | grep claude | grep -v grep | wc -l
```

## 관련 문서

- `~/project-manager/open-all.sh` - 세션 생성 스크립트
- `~/project-manager/CLAUDE.md` - PM 행동 원칙
- `pm-orchestration` 스킬 - PM 오케스트레이션 전체
