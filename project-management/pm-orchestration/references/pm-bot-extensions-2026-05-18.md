# 텔레그램 PM-Bot 확장 (2026-05-18)

## 추가된 명령

| 명령 | 기능 | 예시 |
|--------|----------|-------|
| `/add` | 프로젝트에 태스크 추가 | `/add bea 네이버 발행 로직 개발 P1` |
| `/auto` | 자동화 작업 등록 | `/auto bea 1시간마다 태스크 체크` |
| `/sync` | automations/ → cron 동기화 | `/sync` |
| `/monitor` | 실시간 태스크/자동화/cron 상태 | `/monitor` |

## 워크플로우
1. 텔레그램에서 `/auto`로 자동화 등록
2. `/sync`로 automations/ 폴더를 cron에 동기화
3. cron이 주기적으로 `trigger_automation.py` 실행
4. `trigger_automation.py`가 해당 tmux 세션에 명령 전송
5. 텔레그램으로 알림 전송

## ⚠️ Pitfalls
- **pm_bot.py 직접 수정 주의**: 문자열 이스케이프 문제 (`\n` 등) 발생 가능
  - **✅ 올바른 방법**: `extra_handlers.py`에 함수 작성 후 import
  - **❌ 피해야 할 것**: heredoc로 직접 삽입 시 `\n` 이스케이프 문제 발생
- **cron 중복 방지**: `sync_automations_to_cron.py`가 `PM-AUTO-GEN: START/END` 마커로 블록 관리
- **봇 재시작**: `restart_pm_bot.sh` 사용 (기존 프로세스 중지 → PID 관리 → 로그 확인)

## 관련 문서
`docs/PM-BOT-사용법.md` - 텔레그램 사용법 상세

---

## 세션 생성 규칙
- `/add`로 추가된 태스크는 자동으로 PREPARED_TASK.md에 추가됨
- `/auto`로 등록된 자동화는 `automations/` 폴더에 저장
- `/sync`는 기존 cron을 보존하면서 PM-AUTO-GEN 블록만 갱신

## 자동화 파일 포맷
```markdown
# 자동화 — {project}

## 작업 설명
{description}

## 생성일
{YYYY-MM-DD HH:MM:SS}
```