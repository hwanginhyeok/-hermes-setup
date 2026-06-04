---
name: session-report-management
category: project-management
description: 세션 보고 시스템 관리. 하루 단위 보고 저장 + 월별 자동 아카이빙 + 최적화 제안.
tags: [reporting, session, archive, optimization]
---

# /session-report-management

세션 보고 시스템 관리 스킬.

## 목적

### 하루 단위 보고 저장

- **위치**: `~/.hermes/session_reports/daily/`
- **포맷**: `summary_YYYYMMDD_HHMMSS.md`
- **내용**: 완료 태스크, 진행 중, 신규, 블로커, 커밋, 다음 TODO

### 월별 자동 아카이빙

- **월초(1일 자정)**: 이전 달 보고 → `archived/YYYY-MM/daily/` 이동
- **보관 정책**: 최신 달만 `daily/` 유지

### 최적화 제안

- **키워드 빈도 분석**: 댓글 봇, 테스트, 배포 등 빈도 확인
- **자동화 제안**: 빈도 높은 키워드 기반 스킬/스크립트 제안

## 실행 순서

### STEP 1: 현재 달 확인

```bash
CURRENT_MONTH=$(date +"%Y-%m")
ARCHIVE_DIR="$HOME/.hermes/session_reports/archived/$CURRENT_MONTH"
DAILY_DIR="$HOME/.hermes/session_reports/daily"
```

### STEP 2: 아카이빙 (월초)

```bash
# 이전 달 보고 아카이빙
if [ "$DAY" -eq 1 ] && [ "$HOUR" -eq 0 ] && [ "$MINUTE" -eq 0 ]; then
    for dir in "$DAILY_DIR"/20*; do
        [ -d "$dir" ] && mv "$dir" "$ARCHIVE_DIR/"
    done
fi
```

### STEP 3: 키워드 빈도 분석

```python
# 최근 5개 보고 분석
latest_reports = sorted(glob("$DAILY_DIR/summary_*.md"))[-5:]

keywords = {"댓글": 0, "테스트": 0, "배포": 0, "쿠키": 0}

for report in latest_reports:
    content = read(report)
    for kw, count in keywords.items():
        keywords[kw] += content.count(kw)

sorted_kw = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
print("## 키워드 빈도 (최근 5개)")
for kw, count in sorted_kw[:10]:
    print(f"{kw}: {count}회")
```

### STEP 4: 최적화 제안

| 빈도 | 제안 |
|--------|--------|
| 댓글 봇 15+회 | 전용 스킬 생성 고려 |
| 테스트 12+회 | 테스트 자동화 강화 |
| 배포 8+회 | 배포 파이프라인 강화 |

## 스크립트: monthly_report_archive.py

```bash
# 월초 자동 실행
python ~/.hermes/scripts/monthly_report_archive.py
```

**기능:**
- 이전 달 보고 아카이빙
- 키워드 빈도 분석
- 최적화 제안 생성

## Hermes Cron

```
이름: 월간 보고 아카이빙 + 최적화
스케줄: 0 0 1 * *
다음 실행: 매월 1일 자정
```

## 관련

- `hih-clear` - 세션 종료 루틴 (STEP 6에서 보고 저장)
- `monthly_report_archive.py` - 월별 아카이빙 스크립트
