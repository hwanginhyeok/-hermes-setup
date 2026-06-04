# Cronjob 디버깅 워크플로우

**작성일**: 2026-05-29  
**사용자**: 황인혁 (전력제어개발팀)  
**목적**: HIH_2 프로젝트 cronjob 실패 시 표준화된 디버깅 절차

---

## 문제 발생 (2026-05-29)

### 증상
- 9개 cronjob 등록 완료
- 3개 job 실행됨 (모두 실패):
  - Production Status Daily Report (09:00:34)
  - HIH Daily Standup + DFMEA Check (09:00:34)
  - HIH Cron Monitoring Daily Report (09:00:34)
- 보고서 파일 미생성
- `last_delivery_error`가 null (에러 메시지 없음)

### 에러 메시지
```
RuntimeError: No LLM provider configured. 
Run `hermes model` to select a provider, or run `hermes setup` for first-time configuration.
```

---

## 표준 디버깅 절차

### Step 1: Cronjob 상태 확인

```python
cronjob(action="list")
```

**확인 필드**:
- `job_id`: 고유 ID
- `last_run_at`: 마지막 실행 시각
- `last_status`: 마지막 실행 상태 (success/failed/null)
- `last_delivery_error`: 마지막 에러 메시지
- `next_run_at`: 다음 실행 예정 시각

**출력 예시**:
```
{
  "job_id": "d4491c9f3454",
  "name": "Production Status Daily Report",
  "last_run_at": "2026-05-29T09:00:34.582740+09:00",
  "last_status": "error",
  "last_delivery_error": null,
  "next_run_at": "2026-06-01T08:00:00+09:00"
}
```

---

### Step 2: 출력 디렉토리 확인

**Cronjob 출력 위치**:
```
~/.hermes/cron/output/<job_id>/
```

**디렉토리 구조**:
```bash
~/.hermes/cron/
├── jobs.json                    # 모든 job 설정
├── output/
│   ├── 25414ac1161a/           # Cron Monitoring job
│   │   ├── 2026-05-28_14-43-08.md
│   │   └── 2026-05-29_09-00-34.md
│   ├── a3a1476442f9/           # Daily Standup job
│   │   └── 2026-05-29_09-00-34.md
│   └── d4491c9f3454/           # Production Status job
│       ├── 2026-05-29_08-03-33.md
│       └── 2026-05-29_09-00-34.md
└── .tick.lock
```

**확인 명령**:
```bash
# 전체 출력 디렉토리 확인
ls -la ~/.hermes/cron/output/

# 특정 job 출력 확인
ls -la ~/.hermes/cron/output/<job_id>/

# 최근 실행 파일 확인
cat ~/.hermes/cron/output/<job_id>/$(ls -t ~/.hermes/cron/output/<job_id>/ | head -1)
```

---

### Step 3: 에러 로그 확인

**출력 파일 형식**:
```markdown
# Cron Job: <Job Name> (FAILED)

**Job ID:** <job_id>
**Run Time:** YYYY-MM-DD HH:MM:SS
**Schedule:** <cron_expression>

## Prompt
[스킬 전체 내용 + 사용자 지시사항]

## Error
```
에러 메시지
```
```

**에러 섹션 추출**:
```bash
# Error 섹션만 확인
grep -A 10 "## Error" ~/.hermes/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md

# 전체 내용 확인
cat ~/.hermes/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md
```

---

## 일반적인 에러 유형별 해결책

### 1. LLM Provider 미구성 (CRITICAL)

**증상**:
```
RuntimeError: No LLM provider configured. 
Run `hermes model` to select a provider
```

**원인**:
- Hermes cron 시스템이 LLM provider 설정 없이 실행됨
- LLM 호출 필요 시 자동 실패

**해결**:
```bash
# Provider 목록 확인
hermes model list

# Provider 선택
hermes model select <provider_name>

# 또는 전체 설정
hermes setup
```

**사전 확인**:
- cronjob 생성 전 `hermes model list` 실행
- "No provider selected" 상태면 먼저 구성

---

### 2. 파일 경로 불일치

**증상**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'projects/ss500/parts_tracking.csv'
```

**원인**:
- 스킬 정의 경로와 실제 파일 경로 불일치
- Cronjob prompt에서 상대 경로 사용

**해결**:
```bash
# 1. 실제 파일 위치 확인
find . -name "parts_tracking.csv"
# → HIH_Claude/데이터/parts_tracking.csv

# 2. 스킬 정의 경로 확인
grep -r "parts_tracking.csv" .claude/skills/hih-production/

# 3. Cronjob prompt 수정
# ❌ 틀림: projects/ss500/parts_tracking.csv
# ✅ 맞음: HIH_Claude/데이터/parts_tracking.csv

# 4. Job 재시도
cronjob(action="run", job_id="<job_id>")
```

---

### 3. 디렉토리 없음

**증상**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'HIH_Claude/production_status/'
```

**원인**:
- 보고서 저장 디렉토리가 사전에 생성되지 않음

**해결**:
```bash
# 필수 디렉토리 일괄 생성
mkdir -p HIH_Claude/{cron_monitoring,production_status,standup_daily,bom_dfme_check,dfmea_status,weekly}

# Job 재시도
cronjob(action="run", job_id="<job_id>")
```

---

### 4. 스킬 로딩 실패

**증상**:
```
Skill 'hih-production' not found
```

**원인**:
- 스킬 파일이 존재하지 않거나 경로가 잘못됨

**해결**:
```bash
# 스킬 존재 확인
ls -la .claude/skills/hih-production/

# 스킬 목록 확인
skills_list(category="project-management")

# 필요하면 스킬 재생성 또는 경로 수정
```

---

## 테스트 워크플로우

### Cronjob 생성 후 테스트

1. **Job 생성**:
   ```python
   cronjob(action="create", name="Test Job", ...)
   ```

2. **Job 목록 확인**:
   ```python
   cronjob(action="list")
   # 새 job이 목록에 있는지 확인
   ```

3. **Manual 실행**:
   ```python
   cronjob(action="run", job_id="<job_id>")
   ```

4. **실행 대기** (10-30초):
   ```bash
   sleep 20
   ```

5. **출력 확인**:
   ```bash
   ls -la ~/.hermes/cron/output/<job_id>/
   cat ~/.hermes/cron/output/<job_id>/$(ls -t ~/.hermes/cron/output/<job_id>/ | head -1)
   ```

6. **에러 확인**:
   ```bash
   grep -A 10 "## Error" ~/.hermes/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md
   ```

7. **보고서 확인** (성공 시):
   ```bash
   ls -la HIH_Claude/production_status/
   # YYYY-MM-DD_daily_production_report.md 확인
   ```

---

## Cronjob 상태 모니터링

### 정기 모니터링 Cronjob

**이름**: HIH Cron Monitoring Daily Report  
**주기**: 평일 09:00  
**기능**: 모든 cronjob 상태 분석 + 일일 보고서 생성

**보고서 구조**:
```markdown
# Cron Status Report - YYYY-MM-DD

## Summary
Total: 9 | Success: 7 | Pending: 2 | Failed: 0

## Success Jobs
- Production Status (last: 08:00 today)
- Daily Standup (last: 09:00 today)

## Failed Jobs
⚠️ None

## Next Runs
- Weekly Report: Friday 17:00
- DFMEA Check: Monday 10:00
```

---

## 빠른 참조 (Quick Reference)

### 필수 명령어

```bash
# Cronjob 상태 확인
cronjob(action="list")

# 출력 디렉토리 확인
ls -la ~/.hermes/cron/output/

# 에러 로그 확인
cat ~/.hermes/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md
grep -A 10 "## Error" ~/.hermes/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md

# Provider 구성
hermes model list
hermes model select <provider_name>

# 재시도
cronjob(action="run", job_id="<job_id>")
```

### 필수 경로

```bash
# Cronjob 설정
~/.hermes/cron/jobs.json

# 출력 디렉토리
~/.hermes/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md

# 보고서 저장소
HIH_Claude/{cron_monitoring,production_status,standup_daily,bom_dfme_check,dfmea_status,weekly}

# 데이터 파일
HIH_Claude/데이터/{parts_tracking.csv,issues.csv,dfmea_issue_status.csv}
```

---

## 관련 스킬

- `hih-system-maintenance` - 시스템 유지보수 전반
- `cron-management` - Cron job 관리 일반
- `hih-production` - 생산 현황 분석 (데이터 경로 SSOT)

---

## 변경 이력

| 날짜 | 변경 내용 | 작성자 |
|------|----------|--------|
| 2026-05-29 | 초기 작성 - LLM Provider 문제 해결 및 디버깅 워크플로우 문서화 | Hermes Agent |
