# PM 세션 크래시 후 상태 복구 — 진단 상세

**목적**: 세션이 팅기거나 모델 전환으로 끊긴 후, PM이 어제 작업을 추적하고 미해결 이슈를 이어서 진행하기 위한 진단 레시피.

## 1차 진단: daily_latest.json (가장 빠른 전체 현황 파악)

경로: `~/.pm_logs/daily_latest.json`

구조 (주요 섹션):
- `git[]` — 프로젝트별 브랜치, clean/dirty, uncommitted 수, 마지막 커밋
- `tasks[]` — 프로젝트별 active_count + top_tasks 목록
- `total_active_tasks` — 전체 활성 태스크 수
- `cron_errors[]` — 최근 24h 로그에서 검출된 에러 (file, count, samples)
- `unpushed[]` — 원격에 안 올라간 커밋 수
- `stale_tasks[]` — 오래된 태스크 (project, id, desc, start_date, days)
- `broken_symlinks[]` — 깨진 심링크 경로
- `warnings[]` — 경고

읽기 요령:
```python
# JSON 파서가 거부당하면 read_file로 직접 읽기
# offset 파라미터로 섹션별 읽기 가능
# "total_lines"과 "hint"를 확인해서 끊어 읽기
```

## 2차 진단: session_search + git log

```
session_search(limit=5)                  # 최근 세션 제목/시간
session_search(query="키워드")            # 주제별 검색

cd {프로젝트} && git log --oneline -10    # 최근 커밋
tmux list-sessions                        # 활성 세션 + 생성 시간
```

session_search의 preview가 잘리는 경우가 많으므로, git log와 CURRENT_TASK.md를 교차 검증해서 실제 작업 내용을 파악한다.

## 3차 진단: 크론 에러 로그

에러 로그 위치:
- `~/.pm_logs/*.log` — PM, overnight, daily 리포트
- `~/stock/logs/*.log` — stock 브리핑, earn_reporter
- `~/be-a-studio/logs/*.log` — BEA 관련

에러 카테고리별 대처:

### ImportError: NumPy 버전 충돌
```
# 원인: 시스템 /usr/lib/python3/dist-packages/matplotlib 가 NumPy 1.x로 컴파일됨
# pip가 NumPy 2.x로 업그레이드하면서 ABI 충돌
# cron이 .venv가 아닌 시스템 Python을 사용할 때 발생

# 해결 1: .venv matplotlib 재설치
cd ~/stock && .venv/bin/pip install --upgrade matplotlib numpy

# 해결 2: cron이 시스템 Python을 쓰는 경우 cron 스크립트 수정
# #!/usr/bin/python3 → #!/home/window11/stock/.venv/bin/python3
```

### telegram.error.Conflict (getUpdates 충돌)
```
# 원인: 같은 봇 토큰으로 여러 프로세스가 폴링
# 진단: ps aux | grep bot → PID별 cwd 확인
# ls -la /proc/{PID}/cwd → 어느 프로젝트의 봇인지 식별

# 해결:
# 1. 중복 프로세스 식별 (music-lab/bot.py, x-bot/bot.py, pm_bot.py)
# 2. 같은 토큰을 쓰는 게 아니면 → 과거 잔류 프로세스 kill
# 3. systemctl --user restart {서비스명}
# 4. 필요시 Telegram webhook 삭제: curl 텔레그램 deleteWebhook API
```

### rclone upload failed
```
# 원인: GDrive 원격 토큰 만료 또는 대상 경로 변경
# 에러: oauth2: "invalid_grant" "Token has been expired or revoked."
# 해결: DISPLAY=:1 rclone config reconnect gdrive:  (VNC에서 브라우저 열림, 사용자가 직접 Google 로그인)
# 검증: rclone ls gdrive: --max-depth 1
# 주의: 파이프라인이 렌더까지는 완료하고 업로드만 조용히 실패함 → 로그에서 invalid_grant 검색
```

### NameError: name 'category' is not defined (be-a-studio content_planner)
```
# 원인: candidates JSON 구조 불일치
# - candidates JSON 최상위 필드: brand (not category)
# - plan_data.content 구조: summary 있음, full_text/transcript 없음
# - transcript는 candidates item 최상위에만 있음 (plan_data에 미포함)
#
# 버그 1 (BAS-102): content_planner.py에서 card_data.get("category") 호출
# → 수정: brand = card_data.get("brand", "").lower()
#
# 버그 2 (2026-05-14): plan_data에 transcript 미포함으로 LLM이 요약만 받음
# → 수정: daily_planner.py에서 plan_data에 transcript 주입
#   if not plan_data.get("content", {}).get("full_text"):
#       transcript = item.get("transcript", "")
#       if transcript:
#           plan_data.setdefault("content", {})["full_text"] = transcript
#
# 진단: python3 -c 로 실제 candidates JSON 필드 확인
# cd /home/window11/be-a-studio && python3 -c "
# import json; c = json.loads(open('content_queue/daily_candidates/DATE.json').read())
# for item in c:
#     pd = item.get('plan_data', {})
#     print(item.get('card_id'), 'transcript=', len(item.get('transcript','')),
#           'plan_summary=', len(pd.get('content',{}).get('summary','')),
#           'plan_full_text=', len(pd.get('content',{}).get('full_text','')))"
```

## 트리아제 분류

| 등급 | 기준 | 예시 |
|------|------|------|
| P0 | 자동화 장애 (cron이 매일 실패) | 크론 ImportError, pm_bot Conflict |
| P1 | 기능 개발/버그 (수동 우회 가능) | rclone 실패, unpushed 커밋 |
| P2 | 정리/개선 | 깨진 심링크, stale 태스크 |

## 실제 사례

### 2026-05-13 세션 복구
- **상황**: 5/12 21:40 모델 전환으로 인성이 TASK 브리핑 세션 중단
- **패턴**: daily_latest.json → session_search(5) → 각 프로젝트 git log + CURRENT_TASK → cron 에러 로그
- **발견**: Stock 브리핑 NumPy 충돌 + pm_bot 17만건 Conflict + earn_reporter rclone 실패 + unpushed 7건
- **조치**: 터미널 권한 차단으로 사용자에게 명령어 제공 후 대기

### 함정: daily_latest.json 파서 거부
- `python3 -m json.tool` 실행이 거부될 수 있음
- `read_file`로 직접 읽고 offset으로 분할 읽기
- JSON 파서보다 직접 읽기가 안정적
