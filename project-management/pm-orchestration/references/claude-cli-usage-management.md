# Claude CLI 사용량 관리

**문제:** 너무 많은 Claude CLI 병렬 실행 → 사용량 초과 → 작업 불가
**발생:** 12개 프로세스 × ~700MB = 총 8.4GB RAM 소모

## 문제 감지

```bash
# Claude CLI 프로세스 수 확인
ps aux | grep claude | grep -v grep | wc -l

# 메모리 사용량 총계 확인
ps aux | grep claude | grep -v grep | awk '{sum+=$6} END {print "Total:", sum/1024/1024, "GB"}'

# 각 프로세스별 메모리 사용량
ps aux | grep claude | grep -v grep | awk '{print $11, $6/1024/1024, "MB"}'
```

## 해결 방안

### 1. 불필요한 프로세스 중지

```bash
# --add-dir 프로세스 중지 (최근 사용하지 않은 것들)
pkill -f "claude --add-dir"

# 특정 세션의 Claude만 중지
pkill -f "claude --session <session_id>"
```

### 2. Bash pane 사용

Claude CLI 응답 중인 pane에 입력 불가 → 새 bash pane 사용:

```bash
# bea 세션 예시
tmux send-keys -t bea:1.3 "cd ~/be-a-studio && ..." Enter  # Claude → ❌
tmux send-keys -t bea:1.4 "cd ~/be-a-studio && ..." Enter  # Bash → ✅
```

### 3. Claude 응답 상태 확인

```bash
# 특정 pane 상태 확인
tmux capture-pane -t bea:1.3 -p | grep -E "Cogitated|Undulating"

# 전체 세션에서 응답 중인 Claude 찾기
for session in PM bea stock insung music; do
  for pane in 1 2 3; do
    result=$(tmux capture-pane -t ${session}:1.${pane} -p 2>/dev/null | grep -E "Cogitated|Undulating")
    if [ -n "$result" ]; then
      echo "${session}:1.${pane} - Claude 응답 중"
    fi
  done
done
```

## 예방

### 최대 병렬 프로세스 제한

```bash
# 최대 4개만 허용 (PM + 3개 프로젝트)
CLAUDE_COUNT=$(ps aux | grep claude | grep -v grep | wc -l)
if [ $CLAUDE_COUNT -gt 4 ]; then
  pkill -f "claude --add-dir"
fi
```

### cron 건강 체크 스크립트에 추가

```bash
# project-manager/scripts/cron_health_monitor.py
def check_claude_processes():
    import subprocess
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    claude_count = result.stdout.count('claude') - 2  # header + grep 프로세스
    
    if claude_count > 4:
        log_warning(f"Claude CLI 과다: {claude_count}개 (>4)")
        # 알림 전송
        send_telegram_alert(f"Claude CLI 과다: {claude_count}개")
```

## 관련 문제

- **tmux pane 구조:** 각 세션에 1개 Claude pane + 병렬 작업용 bash panes
- **메모리 제한:** Claude CLI ~700MB/프로세스
- **사용량 초과:** 여러 프로세스 동시 실행 시 API 한도 초과