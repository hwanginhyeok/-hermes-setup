# Worker 프로젝트 전환 시 자주 발생하는 pitfall 패턴

> 2026-05-14 세션에서 w1을 stock→music-lab으로 전환하다 반복 실패한 사례에서 추출.

## Pitfall A: `/exit`가 claude 프롬프트로 들어감

**상황**: w1에서 stock claude가 실행 중인 상태에서 `/exit` send-keys 전송.
claude가 이미 응답 중이거나 처리 중이면 `/exit`가 chat 입력으로 들어가서
claude가 `/exit`에 반응하며 다른 작업을 시작한다.

**증상**: capture-pane에서 `❯` 프롬프트가 계속 보임 (bash `$`가 아님).

**Fix 순서**:
1. `C-c` 전송 → 현재 작업 중단
2. sleep 1
3. `/exit` Enter
4. sleep 3
5. capture-pane으로 `window11@...$` bash 프롬프트 확인
6. 확인 후에만 새 `cd PROJECT && claude ...` 전송

## Pitfall B: 새 명령이 claude가 아닌 bash로 들어갔는데 다시 claude가 뜸

**상황**: `/exit` 후 bash 프롬프트에서 `cd ~/music-lab && claude ...` 전송.
그런데 bash history에 `source ~/.bashrc && cd ~/stock && claude ...`가 있으면
readline이 자동완성/히스토리로 stock을 열 수 있음.

**Fix**: 새 명령 전 항상 `C-u` 전송으로 readline 버퍼 초기화.

## Pitfall C: 이미 실행 중인 claude가 cd 명령을 Bash 도구로 실행

**상황**: w1에 stock claude가 있는 상태에서 `cd ~/music-lab && claude ...` 전송.
stock claude는 이걸 사용자 메시지로 받아서 "새 프로젝트 시작" 해석 후
자기 Bash 도구로 `cd ~/music-lab && claude --add-dir ...`를 실행 → 중첩 claude 생성.

**Fix**: capture-pane으로 현재 세션 상태 반드시 확인 후 전송.
- `❯` → claude 실행 중 → `/exit` 먼저
- `$` → bash → C-u 후 새 명령 가능

## 검증 패턴 (권장)

```bash
# 1. 현재 상태 확인
tmux capture-pane -t w1 -p | tail -3

# 2. bash인지 claude인지 판별
# bash: 마지막 줄에 "window11@DESKTOP...$ " 포함
# claude: 마지막 줄에 "❯" 포함, 또는 상태바에 📁project 표시

# 3. claude면 종료
tmux send-keys -t w1 C-c
sleep 1
tmux send-keys -t w1 "/exit" Enter
sleep 3

# 4. bash 확인 후 C-u + 새 명령
tmux capture-pane -t w1 -p | grep -q '\$' && echo "bash OK" || echo "NOT bash - retry"
tmux send-keys -t w1 C-u
sleep 0.3
tmux send-keys -t w1 "cd ~/music-lab && claude --add-dir ~/music-lab --add-dir ~/project-manager" Enter
```
