# Partial vs Full Pipeline Cron 혼동 사례

## 문제 증상
- PM이 cron.md SSOT를 확인하니 "✅ 작동 중"으로 기재
- 실제 crontab에는 `enrich_news_v2.py` 단독 실행만 있음
- **전체 파이프라인인 `run_daily.sh`가 누락됨**

## 원인 분석

### 잘못된 상태 (수정 전)
```bash
# crontab -l 출력
30 5 * * * cd ~/be-a-studio && python3 scripts/enrich_news_v2.py --raw content_queue/daily_raw/$(date +\%Y\%m\%d).json >> logs/enrich_news_v2.log 2>&1
```

### 올바른 상태 (수정 후)
```bash
# crontab -l 출력
30 5 * * * cd /home/window11/be-a-studio && bash scripts/run_daily.sh >> logs/run_daily_$(date +\%Y\%m\%d).log 2>&1
```

## 핵심 차이

| 항목 | Partial (enrich_news_v2.py만) | Full (run_daily.sh) |
|------|-------------------------------|---------------------|
| 실행 범위 | enrich 단계 1개만 | 전체 파이프라인 |
| 포함 단계 | enrich_news_v2.py | collector → enrich → curator → planner → copier → renderer → GDrive |
| raw 파일 생성 | ❌ 없음 (별도 collector 필요) | ✅ 있음 (run_daily.sh 내부 포함) |
| 문제점 | raw 파일 없으면 enrich 실패 (5/18~19 증상) | 모든 단계 자동 실행 |

## 진단 절차

### 1. 로그 확인
```bash
# enrich 단독 실행 시 오류
tail -20 /home/window11/be-a-studio/logs/enrich_news_v2.log
# 출력: [ERROR] raw 파일 없음: content_queue/daily_raw/20260518.json
```

### 2. raw 파일 존재 확인
```bash
ls -lh /home/window11/be-a-studio/content_queue/daily_raw/
# 5/16: ✅ 있음, 5/17: ✅ 있음, 5/18: ❌ 없음, 5/19: ❌ 없음
```

### 3. crontab 검증
```bash
crontab -l | grep -E "(be-a-studio|run_daily|enrich_news)"
# enrich_news_v2.py만 있으면 → run_daily.sh로 교체 필요
```

### 4. wrapper 스크립트 내용 확인
```bash
head -50 /home/window11/be-a-studio/scripts/run_daily.sh | grep "enrich_news"
# enrich_news가 run_daily.sh 내부에 포함된 것 확인
```

## 해결 방법

### 1. Partial cron 제거 + Full cron 추가
```bash
# 현재 crontab 백업
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt

# enrich_news_v2.py 제거 + run_daily.sh 추가
# (스크립트로 처리 권장)

# 적용
crontab /tmp/crontab_with_bea_daily.txt
```

### 2. 검증
```bash
# 다음 날 05:30 이후 확인
ls -lh /home/window11/be-a-studio/logs/run_daily_20260520.log
ls -lh /home/window11/be-a-studio/content_queue/daily_raw/20260520.json
```

## 교훈

1. **Wrapper 스크립트 존재 확인**: 단일 스크립트 cron 있으면, 그 상위 wrapper가 있는지 확인
2. **raw 파일 생성 여부**: enrich 등 downstream 단계만 있고 upstream(collector)가 없으면 비정상
3. **로그 파일명 확인**: `enrich_news_v2.log` vs `run_daily_YYYYMMDD.log` — 후자가 전체 파이프라인

## 방지 방법

### PM 검증 체크리스트
- [ ] cron.md SSOT 기재 내용
- [ ] 실제 crontab 등록 여부 (`crontab -l | grep project_name`)
- [ ] 로그 파일 존재 여부
- [ ] raw 파일 생성 주기 (매일 있는지)

**원칙**: 로그 파일 존재 ≠ cron 등록됨 (수동 실행으로 로그 남을 수도 있음)
