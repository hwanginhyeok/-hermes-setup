# tmux 워커 풀 오케스트레이션 패턴

> 2026-05-13 세션에서 확립된 PM + w1/w2/w3 운영 실전 패턴

## 워커 시작 절차

```bash
# 1. 세션 생성 (open-all.sh로 한 번만)
bash ~/project-manager/open-all.sh

# 2. 워커에 프로젝트 할당
tmux send-keys -t w1 C-u   # 버퍼 잔여 텍스트 클리어 (필수!)
tmux send-keys -t w1 "source ~/.bashrc && cd ~/insung_blog && claude --add-dir ~/insung_blog --add-dir ~/project-manager" Enter

# 3. 로딩 확인 (10초 대기 후 ❯ 프롬프트)
sleep 10
tmux capture-pane -t w1 -p | grep -E "❯|Opus|Sonnet" | tail -3
```

## 워커 응답 없을 때 해결 순서

claude 세션이 입력 받고 반응 없는 경우 (showing_question / ctx 포화 상태):

```
1. Enter 재전송 — tmux send-keys -t w1 Enter
2. 안 되면 Escape × 2 → C-u → 재입력
3. 여전히 막히면 /clear 후 재지시
4. ctx 90%+ + 긴 세션이면 무조건 /clear
```

## /clear 후 재지시 패턴

/clear는 대화 이력을 날리므로 핵심만 짧게:

```bash
# 잘못된 예 (너무 긺, 여러 줄)
tmux send-keys -t w1 "1번부터 3번 작업하고..." Enter  # 여러 줄 입력 안 됨

# 올바른 예 (핵심 한 문장)
tmux send-keys -t w1 "tesla_api.py LEVEL_THRESHOLDS important=10으로 수정하고 커밋해." Enter
```

여러 작업 지시가 필요하면 하나씩 완료 확인 후 다음 지시.

## 멀티 워커 병렬 오케스트레이션

```bash
# 한 번에 3개 워커에 각각 작업 던지기
tmux send-keys -t w1 "CURRENT_TASK.md 읽고 1-60 버그 수정해" Enter
tmux send-keys -t w2 "uncommitted 정리하고 커밋해" Enter
tmux send-keys -t w3 "BAS-107 작업 시작해" Enter

# 60초 후 전체 상태 체크
sleep 60
for w in w1 w2 w3; do
  echo "--- $w ---"
  tmux capture-pane -t $w -p -S -8 2>/dev/null | grep -v '^$' | tail -5
done
```

## showing_question 상태 판별

워커가 옵션 메뉴를 띄워놓고 기다리는 상태:
```
  1. 옵션 A
  2. 옵션 B
  ...
Enter to select · ↑/↓ to navigate · Esc to cancel
```

→ Escape로 닫고 C-u 후 원하는 내용 직접 입력.
→ `"1번"`, `"2번"` 입력보다 구체적 지시가 더 안정적:
  - ❌ `"1번으로 해줘"`
  - ✅ `"BAS-57 바로 재개해. Playwright persistent_context로 구현해."`

## ctx + 세션 시간 관리

| ctx | 세션 시간 | 권장 조치 |
|-----|----------|-----------|
| ~90% | 어느 시간이나 | /clear 고려 |
| ~85% | 10시간+ | /clear 필수 |
| 100% (포화) | - | 입력 불가. /clear 또는 재시작 |

## "new task? /clear to save Nk tokens" 경고

이 메시지가 상태바에 뜨면 claude가 /clear를 권장하는 상태.
반응이 느려지거나 입력이 막히기 시작함.
→ 즉시 `/clear`하고 핵심 작업만 재지시.

## 여러 줄 입력이 필요한 경우

tmux send-keys는 멀티라인이 잘 안 됨. 대신:

```bash
# 방법 1: 작업을 한 문장으로 요약
tmux send-keys -t w1 "CURRENT_TASK.md 읽고 P1부터 순서대로 작업해. 각 완료 시 커밋." Enter

# 방법 2: 순차적으로 한 번에 하나씩
# → 첫 번째 완료 확인 후 두 번째 지시
```

## 워커 해제

```bash
tmux send-keys -t w1 "/exit" Enter
# claude 종료 → 빈 bash 복귀
# 다음 프로젝트 할당 전 C-u로 버퍼 클리어
```
