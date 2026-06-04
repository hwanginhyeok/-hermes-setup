# HIH_2 Task Analysis & Cronjob Creation Workflow

> **발견 시점**: 2026-05-29  
> **목적**: HIH_2 프로젝트 업무를 분석하고 자동화 cronjob을 생성하는 표준 워크플로우

---

## 1. Task Analysis 단계

### 1.1 태스크 파일 수집

```bash
# 핵심 태스크 파일 읽기
CURRENT_TASK.md
PREPARED_TASK.md  
FINISHED_TASK.md
DIFFICULTY.md
```

### 1.2 자동화 패턴 식별

**자동화 키워드 매핑**:
```python
patterns = {
    'daily': ['데일리', 'standup', '브리핑', '진행사항', 'daily'],
    'weekly': ['주간', 'weekly', 'week'],
    'sync': ['노션', 'Notion', '동기화', 'sync', '갱신', '업데이트'],
    'monitoring': ['DFMEA', '이슈', '모니터링', '점검', 'health', '체크', '검증'],
    'reporting': ['보고서', 'report', 'Excel', '생성', '작성', '주간보고'],
    'data_collection': ['데이터', 'CSV', 'collect', 'fetch', 'DB', 'database', '발굴'],
    'documentation': ['문서', '작성', '정리', '매뉴얼', 'SOP'],
    'quality': ['품질', 'QC', 'IQC', 'EOL', '검사', '시험', 'DVP']
}
```

### 1.3 Cronjob 후보 분류

**우선순위 기준**:
- **P0**: 긴급 (오늘/내일 마감)
- **P1**: 중요 (이번 주)
- **P2**: 일반 (다음 주)
- **P3**: 저순위 (시간 날 때)

---

## 2. Cronjob 생성 단계

### 2.1 사전 준비 (필수)

```bash
# 1. 디렉토리 구조 생성
mkdir -p HIH_Claude/{cron_monitoring,production_status,standup_daily,bom_dfme_check,dfmea_status,weekly}

# 2. 데이터 파일 경로 확인
ls -lh HIH_Claude/데이터/parts_tracking.csv
ls -lh HIH_Claude/데이터/issues.csv

# 3. 스킬 경로 확인
grep -r "parts_tracking" .claude/skills/
```

### 2.2 Cronjob 생성

**기본 템플릿**:
```python
cronjob(
    action="create",
    model={"model": "anthropic/claude-sonnet-4", "provider": "openrouter"},
    name="<Job Name>",
    prompt="<Detailed prompt with correct paths>",
    schedule="<Cron schedule>",
    skills=["hih-dev"]  # 또는 ["hih-production"]
)
```

### 2.3 스케줄 패턴

**HIH_2 표준 스케줄**:
```cron
# 일일 (Daily)
0 8 * * 1-5   # 평일 08:00 - Production Status
0 9 * * 1-5   # 평일 09:00 - Daily Standup
0 23 * * *    # 매일 23:00 - Notion Sync

# 주간 (Weekly)
0 9 * * 1     # 월요일 09:00 - APQP Tracker
0 10 * * 1    # 월요일 10:00 - DFMEA Check
0 11 * * 3    # 수요일 11:00 - BOM vs DFMEA Check
0 17 * * 5    # 금요일 17:00 - Weekly Report
```

---

## 3. Cronjob Monitoring 단계

### 3.1 상태 확인

```python
cronjob(action="list")
```

**출력 필드 확인**:
- `last_run_at`: 마지막 실행 시각
- `last_status`: 마지막 상태 (success/failed/null)
- `last_delivery_error`: 에러 메시지
- `next_run_at`: 다음 실행 예정

### 3.2 에러 디버깅

**공통 에러 패턴**:

1. **보고서 파일 미생성**
   - 디렉토리 권한 확인: `ls -la HIH_Claude/production_status/`
   - 스킬 직접 실행 테스트
   - 파일 시스템 쓰기 권한 검증

2. **데이터 파일을 찾을 수 없음**
   - 경로 일치 확인 (스킬 정의 vs cronjob prompt)
   - 절대 경로 사용

3. **last_delivery_error가 null**
   - Hermes cron 시스템 로그 확인
   - 스킬 로딩 실패 가능성

---

## 4. 실전 사례 (2026-05-29)

### 생성된 Cronjob: 9개

| # | Cron 이름 | 주기 | 다음 실행 |
|---|----------|------|----------|
| 1 | Production Status Daily Report | 평일 08:00 | 6/1 08:00 |
| 2 | HIH Daily Standup + DFMEA Check | 평일 09:00 | 6/1 09:00 |
| 3 | HIH Cron Monitoring Daily Report | 평일 09:00 | 6/1 09:00 |
| 4 | Notion → Obsidian Sync | 매일 23:00 | 5/29 23:00 |
| 5 | APQP Progress Tracker | 월 09:00 | 6/1 09:00 |
| 6 | MBD Parameters Datasheet Sync | 월 10:00 | 6/1 10:00 |
| 7 | DFMEA Weekly Status Check | 월 10:00 | 6/1 10:00 |
| 8 | BOM vs DFMEA Consistency Check | 수 11:00 | 6/3 11:00 |
| 9 | HIH Weekly Report Generator | 금 17:00 | 5/30 17:00 |

### 발견된 문제점

1. **디렉토리 누락**: 보고서 저장 디렉토리가 사전에 생성되지 않음
2. **경로 불일치**: `projects/ss500/parts_tracking.csv` vs `HIH_Claude/데이터/parts_tracking.csv`
3. **보고서 미생성**: 3개 job 실행되었으나 파일 생성 안됨

### 해결 조치

1. ✅ 디렉토리 6개 생성 완료
2. ✅ Production Status cronjob prompt 경로 수정
3. ⚠️ 보고서 파일 생성 실패 원인 파악 중

---

## 5. 효과 측정

### 시간 절감 (주간)

| 작업 | 수동 | 자동화 | 절감 |
|------|------|--------|------|
| 데일리 스탠드업 | 10분/일 | 0분 | 50분 |
| Notion 동기화 | 15분/일 | 0분 | 1시간 45분 |
| 주간보고 작성 | 30분/주 | 5분 | 25분 |
| DFMEA 점검 | 20분/주 | 5분 | 15분 |
| 생산 현황 | 10분/일 | 0분 | 50분 |
| APQP 추적 | 15분/주 | 5분 | 10분 |
| **총 절감** | | | **4시간 45분** |

### 품질 향상

- DFMEA 미분석 이슈 누락 방지
- Notion 데이터 로컬 백업 자동화
- 주간보고 누락 방지
- APQP 산출물 지연 즉시 감지
- BOM vs DFMEA 불일치 자동 감지

---

## 6. Pitfalls

### 6.1 Cronjob prompt 작성

**❌ 잘못된 예**:
```
1. projects/ss500/parts_tracking.csv 읽기
2. 분석해서 보고서 작성
3. HIH_Claude/production_status/에 저장
```

**✅ 올바른 예**:
```
1. **데이터 파일 확인**
   - HIH_Claude/데이터/parts_tracking.csv 읽기
   - 파일 존재 검증: ls -lh HIH_Claude/데이터/parts_tracking.csv
   
2. **데이터 분석**
   - Assembly별 조립 가능 수량 계산
   - 블로커 식별
   
3. **보고서 생성**
   - 파일: HIH_Claude/production_status/YYYY-MM-DD_daily_production_report.md
   - 섹션: 요약, 상세, 블로커, 차주 계획
   
4. **사용자 보고**
   - 요약 출력
   - Critical 블로커 즉시 알림
```

### 6.2 테스트 실행 순서

**순서**:
1. 디렉토리 생성
2. 데이터 파일 확인
3. Cronjob 생성
4. **Manual run 테스트**
5. 보고서 파일 확인
6. 정기 스케줄링

---

## 7. Quick Reference

### Task Analysis Commands

```bash
# 태스크 수 파악
grep -E "^\| C-" CURRENT_TASK.md PREPARED_TASK.md | wc -l

# 패턴 분석
grep -E "(daily|weekly|sync|monitoring)" PREPARED_TASK.md | grep "^\| C-"
```

### Cronjob Commands

```python
# 생성
cronjob(action="create", name="...", prompt="...", schedule="...")

# 조회
cronjob(action="list")

# 실행
cronjob(action="run", job_id="...")

# 수정
cronjob(action="update", job_id="...", prompt="...")

# 삭제
cronjob(action="delete", job_id="...")
```

### Verification Commands

```bash
# 디렉토리 확인
ls -la HIH_Claude/{cron_monitoring,production_status,standup_daily,bom_dfme_check,dfmea_status,weekly}

# 파일 생성 확인
find HIH_Claude -name "*2026-05-*" -type f

# 데이터 파일 확인
ls -lh HIH_Claude/데이터/*.csv
```

---

## Related Skills

- `hih-production` - 생산 현황 분석 (Cron Integration Pitfalls)
- `cron-management` - Cron job 관리 표준 절차
- `pm-orchestration` - PM 오케스트레이션 (다중 프로젝트 cronjob)

---

## Version History

- **2026-05-29**: 초기 작성 (Task Analysis → Cronjob Creation → Monitoring 워크플로우 정립)
