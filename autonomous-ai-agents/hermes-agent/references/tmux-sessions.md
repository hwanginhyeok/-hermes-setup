# tmux 세션 구조 참조

## 사용자 환경

- WSL2 (Windows Subsystem for Linux)
- 다중 프로젝트 tmux 세션 구조
- 각 세션은 Claude Code 에이전트 전용

## 표준 세션 구조

```bash
# 전체 생성
~/project-manager/open-all.sh

# 세션 목록 확인
tmux list-sessions

# 특정 세션 접속
tmux attach -t <session>
```

## 세션 정의

| 세션 | Panes | 용도 | 경로 |
|------|-------|------|------|
| PM | 4 | 오케스트레이터 (Claude Code) | ~/project-manager |
| bea | 2 | be-a-studio | ~/be-a-studio |
| stock | 2 | 주식부자 | ~/stock |
| insung | 2 | 인성이 | ~/insung_blog |
| music | 2 | music-lab | ~/music-lab |
| hermes | 2 | Hermes gateway + chat | ~ |

## Pane 구성

- **Pane 1**: Claude Code (주) - 자동 시작
- **Pane 2+**: Bash 대기 - 필요 시 에이전트 추가

## 에이전트 추가 (예시)

```bash
# bea 세션의 pane 2에 에이전트 시작
tmux send-keys -t bea:1.2 "claude --add-dir ~/project-manager" Enter

# 에이전트 종료 후 bash 복귀
tmux send-keys -t bea:1.2 "/exit" Enter
```

## 세션 제어 명령

```bash
# 세션 종료
tmux kill-session -t <session>

# 세션 생성 전 중복 제거
tmux kill-session -t <session> 2>/dev/null

# 모든 프로젝트 세션 종료 (PM/hermes 유지)
./open-all.sh --kill

# 전체 종료
./open-all.sh --kill-all
```

## 주의사항

1. **세션명 표준화**: 영문만 사용 (PM, bea, stock, insung, music, hermes)
2. **한글 세션명 금지**: 혼동 유발 (예: "주식부자", "인성이", "자율주행")
3. **중복 세션 방지**: 생성 전 기존 세션 확인 후 제거
4. **open-all.sh 사용**: 수동 생성 금지, 스크립트로만 생성

## 문제 해결

### 중복 세션 발생 시

```bash
# 한글 세션 제거
tmux kill-session -t 주식부자
tmux kill-session -t 인성이
tmux kill-session -t 자율주행

# 스크립트 재실행
./open-all.sh
```

### Pane 수가 맞지 않을 때

```bash
# 현재 pane 수 확인
tmux list-sessions -F "#{session_name}: #{session_windows} windows, #{window_panes} panes"

# open-all.sh 재실행 (자동 보완)
./open-all.sh
```

## 관련 스킬

- `hih-all-clear`: 전체 세션 일괄 정리
- `hih-dev`: 병렬 에이전트 투입
