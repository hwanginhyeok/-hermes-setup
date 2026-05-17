# Be:A Studio 파이프라인 트러블슈팅

> 자주 발생하는 cron/파이프라인 문제와 해결법

## cron 흐름 (매일 05:30 KST)

```
run_daily.sh → daily_collector.py (수집 89소스)
            → enrich_youtube.py (transcript)
            → enrich_news.py (본문추출) ← Segfault 간헐적
            → enrich_summary.py (요약)
            → daily_curator.py (GLM 5건 선별)
            → daily_planner.py (GLM 기획안)
            → render_from_plan.py (Playwright 렌더)
            → rclone upload (GDrive)
```

## 자주 발생하는 문제

### 1. enrich_news.py Segfault
- **원인**: Python/C extension 메모리 이슈 (간헐적)
- **해결**: 수동 재실행 `cd /home/window11/be-a-studio && bash scripts/run_daily.sh`
- **로그**: `tail -50 ~/.pm_logs/be_a_studio_daily.log`

### 2. category vs brand 필드명 불일치
- **증상**: `NameError: name 'category' is not defined`
- **원인**: candidates JSON에 `brand` 필드만 있음
- **해결**: `card_data.get("brand", "").lower()` + `.pyc` 캐시 삭제

### 3. rclone GDrive 토큰 만료
- **해결**: `DISPLAY=:1 rclone config reconnect gdrive:` → VNC에서 구글 인증
- **VNC**: https://desktop-plq9e0i.tailec5aa6.ts.net

## 소스 구조
- sources.yaml: YouTube=`{name, id}`, RSS=`{name, rss_url}`
- feed_health_check.py: 매일 06:00, 실패율 ≥30% 텔레그램 알림
