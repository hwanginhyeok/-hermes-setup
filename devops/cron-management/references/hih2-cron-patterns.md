# HIH_2 Project Cron Automation Patterns

**Date**: 2026-05-29  
**Project**: HIH_2 (SS500 Speed Sprayer APQP/DFMEA 자동화)  
**Purpose**: 프로젝트 관리 cronjob 시스템 구축 사례

---

## Overview

HIH_2 프로젝트에서 **9개의 interconnected cronjob**을 구축하여 APQP, DFMEA, 생산 현황 모니터링을 자동화했습니다. 주간 약 4시간 45분의 시간 절감과 24/7 품질 리스크 감지 시스템을 구현했습니다.

---

## Cron Inventory

### 일일 (Daily) - 4개

| # | Cron 이름 | 주기 | 다음 실행 | 용도 |
|---|----------|------|----------|------|
| 1 | Production Status Daily Report | 평일 08:00 | - | 생산 현황 + PFD HTML 갱신 |
| 2 | HIH Daily Standup + DFMEA Check | 평일 09:00 | - | 데일리 브리핑 + DFMEA 검토 |
| 3 | HIH Cron Monitoring Daily Report | 평일 09:00 | - | Cron 상태 모니터링 |
| 4 | Notion → Obsidian Sync | 매일 23:00 | - | Notion DB 동기화 |

### 주간 (Weekly) - 5개

| # | Cron 이름 | 주기 | 용도 |
|---|----------|------|------|
| 5 | APQP Progress Tracker | 월 09:00 | APQP 산출물 진행률 추적 |
| 6 | MBD Parameters Datasheet Sync | 월 10:00 | 데이터시트 발굴값 자동 반영 |
| 7 | DFMEA Weekly Status Check | 월 10:00 | DFMEA 미분석 이슈 점검 |
| 8 | BOM vs DFMEA Consistency Check | 수 11:00 | BOM vs DFMEA 일치성 검증 |
| 9 | HIH Weekly Report Generator | 금 17:00 | 주간보고 자동 생성 |

---

## Execution Infrastructure

**Tool**: Hermes Agent `cronjob` (native cron scheduling system)

**Creation example**:
```python
cronjob(
    action="create",
    name="Production Status Daily Report",
    schedule="0 8 * * 1-5",  # Weekdays 8am
    skill="hih-production",
    prompt="..."
)
```

**Status checking**:
```python
cronjob(action="list")
# Returns: job_id, last_run_at, last_status, next_run_at
```

---

## Interconnection Patterns

### 1. Data Flow Dependencies

```
Notion DB → Notion Sync → Obsidian → Daily Standup → Weekly Report
                                     ↓
                           Cron Monitoring
```

### 2. Quality Monitoring Network

```
parts_tracking.csv → Production Status → PFD HTML
                       ↓
                  Cron Monitoring
                       ↓
BOM + DFMEA → BOM vs DFMEA Check → Consistency Report
```

### 3. APQP Progress Tracking

```
APQP 산출물 → APQP Tracker → 갭 분석 갱신
                  ↓
           Cron Monitoring → Weekly Report
```

---

## Report File Structure

```
HIH_Claude/
├── cron_monitoring/
│   └── YYYY-MM-DD_daily_cron_report.md
├── bom_dfme_check/
│   └── YYYY-MM-DD_consistency_report.md
├── production_status/
│   ├── YYYY-MM-DD_daily_production_report.md
│   └── pfd_YYYY-MM-DD.html
├── standup_daily/
│   └── YYYY-MM-DD.md
├── weekly/
│   └── YYYY-MM-DD_주간보고.md
└── dfmea_status/
    └── DFMEA_Weekly_Status_YYYY-MM-DD.md
```

---

## Key Learnings

### 1. 데이터 파일 경로 불일치 (CRITICAL)

**Problem**: 
- Cronjob prompt에서 `projects/ss500/parts_tracking.csv`로 지정
- 실제 파일은 `HIH_Claude/데이터/parts_tracking.csv`에 존재
- Production Status Daily Report 실행 실패

**Solution**:
- **스킬 정의 경로를 SSOT로 사용**: SKILL.md에 명시된 경로를 그대로 따름
- **파일 존재 미리 검증**: cronjob 생성 전 `ls` 명령으로 확인
- **절대 경로 선호**: 프로젝트 루트(`HIH_Claude/`) 기준

**Fixed paths**:
```python
# ❌ Wrong
projects/ss500/parts_tracking.csv

# ✅ Correct
HIH_Claude/데이터/parts_tracking.csv
```

### 2. 보고서 저장 디렉토리 누락

**Problem**:
- `HIH_Claude/cron_monitoring/`, `HIH_Claude/production_status/` 등이 생성 안됨
- Cron Monitoring Daily Report 실행 실패

**Solution**:
- cronjob 생성 시 디렉토리 자동 생성 로직 추가
- 또는 스킬 setup 단계에서 디렉토리 구조 생성

**Required directories**:
```bash
mkdir -p HIH_Claude/{cron_monitoring,production_status,standup_daily,bom_dfme_check,dfmea_status,weekly}
```

### 3. Self-Monitoring Pattern

**Pattern**: Cronjob이 다른 cronjob 상태를 모니터링

**Implementation**:
```python
prompt="""
1. List all cronjobs: cronjob(action='list')
2. Analyze status: success/failed/pending
3. Error analysis: last_delivery_error check
4. Generate daily report
5. Alert immediately if failures detected
"""
```

**Benefits**:
- 24/7 cron 건전성 모니터링
- 실패 즉시 알림
- 반복 실패 패턴 감지

### 4. 주간 스케줄 최적화

**Pattern**: 일일/주간 job을 시간대별로 분산

**Schedule**:
```
월요일: 08:00 (생산) → 09:00 (APQP) → 10:00 (MBD + DFMEA)
수요일: 11:00 (BOM 검증)
금요일: 17:00 (주간보고)
매일: 23:00 (Notion Sync)
평일: 09:00 (데일리 + 크론 모니터링)
```

**Benefits**:
- 시스템 부하 분산
- 업무 흐름에 맞춘 타이밍
- 주간마다 최신 상태 유지

---

## Error Recovery

### Production Status Daily Report Error (2026-05-29 08:03)

**Symptom**: `last_status: error`  
**Root cause**: Skill path mismatch (hih-production skill not found)  
**Recovery**: 
1. Verify skill exists: `ls .claude/skills/hih-production/`
2. Fix data path in prompt
3. Re-run manually: `cronjob(action=run, job_id=...)`

### Cron Monitoring Daily Report Error (2026-05-28 14:43)

**Symptom**: `last_status: error`  
**Root cause**: Output directory not created  
**Recovery**:
1. Create directory: `mkdir -p HIH_Claude/cron_monitoring/`
2. Re-run manually
3. Verify report file generation

---

## Automation Impact

### Time Savings

| 작업 | 수동 소요 시간 | 자동화 후 | 주간 절감 |
|------|---------------|----------|----------|
| 데일리 스탠드업 | 10분/일 | 0분 | 50분 |
| Notion 동기화 | 15분/일 | 0분 | 1시간 45분 |
| 주간보고 작성 | 30분/주 | 5분 | 25분 |
| DFMEA 점검 | 20분/주 | 5분 | 15분 |
| APQP 추적 | 15분/주 | 5분 | 10분 |
| 생산 현황 | 10분/일 | 0분 | 50분 |
| MBD 파라미터 | 20분/주 | 5분 | 15분 |
| BOM 검증 | 30분/주 | 5분 | 25분 |
| **총계** | - | - | **4시간 45분** |

### Quality Improvements

1. **DFMEA 미분석 이슈 누락 방지** - 주간 자동 점검
2. **BOM vs DFMEA 불일치 자동 감지** - 주간 일치성 검증
3. **생산 블로커 일일 알림** - 아침 8시 자동 보고
4. **APQP 산출물 지연 즉시 감지** - 월요일 아침 추적
5. **MBD 파라미터 데이터시트 최신화** - 월요일 자동 갱신
6. **Cronjob 상태 24/7 모니터링** - 매일 아침 9시 보고

---

## Best Practices

### 1. Skill Path Alignment
- **항상 스킬 정의된 경로를 SSOT로 사용**
- SKILL.md에 명시된 데이터 경로를 그대로 따름
- 파일 존재 미리 검증 (`ls` 명령)

### 2. Directory Pre-creation
- **cronjob 생성 전 출력 디렉토리 미리 생성**
- 스킬 setup 단계에서 디렉토리 구조 생성
- `mkdir -p`로 중간 디렉토리도 함께 생성

### 3. Self-Monitoring Integration
- **모든 cronjob 시스템에 모니터링 job 추가**
- 실패 즉시 알림, 성공 시 요약만
- 반복 실패 패턴 감지

### 4. Weekly Schedule Optimization
- **일일/주간 job을 시간대별로 분산**
- 업무 흐름에 맞춘 타이밍 (아침/오후/저녁)
- 시스템 부하 고려

### 5. Error Recovery Documentation
- **각 cronjob의 에러 패턴과 복구 절차 문서화**
- Pitfalls 섹션에 기록
- 다음 세서에서 재발 방지

---

## Related Skills

- `hih-production` - 생산 현황 분석 스킬 (데이터 경로 SSOT)
- `hih-dev` - 개발 파이프라인 스킬 (cronjob 실행 엔진)
- `pm-orchestration` - PM 오케스트레이션 (태스크 동기화)

---

## References

- `HIH_Claude/데이터/parts_tracking.csv` - 생산 데이터 SSOT
- `.claude/skills/hih-production/SKILL.md` - 스킬 정의 (데이터 경로)
- `.claude/skills/hih-dev/SKILL.md` - 개발 파이프라인 정의

---

## Author Notes

이 cron automation 시스템은 **HIH_2 프로젝트의 특성**에 맞춰 설계되었습니다:

1. **APQP Phase 2~3** - 산출물 진행률 모니터링 중요
2. **DFMEA AIAG-VDA** - 이슈 전수조사 및 리스크 평가
3. **생산 관리** - Assembly별 조립 가능 수량 추적
4. **Notion 연동** - 이슈 DB/진행사항/회의록 동기화

일반 프로젝트에도 적용 가능한 패턴이지만, **제조/품질 관리 프로젝트**에 최적화되어 있습니다.
