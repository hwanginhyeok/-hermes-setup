---
name: hih-system-maintenance
title: HIH_2 System Maintenance
description: HIH_2 프로젝트 시스템 유지보수 — 디렉토리 구조 관리, 데이터 파일 경로 확인, cronjob 모니터링, 로그 회전, 디스크 정리.
tags: [system-maintenance, hi2, devops, automation]
user_invocable: true
---

# HIH_2 System Maintenance

HIH_2 프로젝트의 시스템 유지보수 작업을 자동화하고 표준화합니다.

## 개요

HIH_2 프로젝트는 **여러 데이터 소스**와 **자동화된 cronjob 시스템**으로 운영됩니다. 이 스킬은 시스템 건전성을 유지하기 위한 유지보수 작업을 정의합니다.

---

## 1. 디렉토리 구조 관리

### 필수 디렉토리 생성

**실행 타이밍**:
- 프로젝트 설정 시 (최초 1회)
- cronjob 추가 시
- 새로운 보고서 타입 추가 시

**필수 디렉토리**:
```bash
# 보고서 저장소
mkdir -p HIH_Claude/{cron_monitoring,production_status,standup_daily,bom_dfme_check,dfmea_status,weekly}

# 데이터 저장소 (이미 존재)
# HIH_Claude/데이터/

# 산출물 (이미 존재)
# HIH_Claude/산출물/
```

**자동화 스크립트**:
```bash
#!/bin/bash
# setup_hih2_directories.sh

REQUIRED_DIRS=(
    "HIH_Claude/cron_monitoring"
    "HIH_Claude/production_status"
    "HIH_Claude/standup_daily"
    "HIH_Claude/bom_dfme_check"
    "HIH_Claude/dfmea_status"
    "HIH_Claude/weekly"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "Created: $dir"
    else
        echo "Exists: $dir"
    fi
done
```

---

## 2. 데이터 파일 경로 확인

### SSOT 데이터 파일 경로

**중요**: HIH_2 프로젝트의 데이터 파일은 **모두 `HIH_Claude/데이터/`** 에 있습니다.

| 파일 | 용도 | 경로 |
|------|------|------|
| `parts_tracking.csv` | 생산 현황 | `HIH_Claude/데이터/parts_tracking.csv` |
| `issues.csv` | 이슈 DB | `HIH_Claude/데이터/issues.csv` |
| `dfmea_issue_status.csv` | DFMEA 상태 | `HIH_Claude/데이터/dfmea_issue_status.csv` |
| `schedule_milestones.csv` | 마일스톤 | `HIH_Claude/데이터/schedule_milestones.csv` |
| `blockers.csv` | 블로커 현황 | `HIH_Claude/데이터/blockers.csv` |

### 경로 불일치 확인 절차

**cronjob 생성 전 반드시 수행**:
```bash
# 1. 파일 존재 확인
ls -lh HIH_Claude/데이터/parts_tracking.csv

# 2. 경로 검증
pwd  # 프로젝트 루트 확인
realpath HIH_Claude/데이터/parts_tracking.csv

# 3. 스킬 정의 경로와 일치 확인
grep -r "parts_tracking.csv" .claude/skills/hih-production/
```

**Pitfall**: 
- ❌ `projects/ss500/parts_tracking.csv` (잘못됨)
- ✅ `HIH_Claude/데이터/parts_tracking.csv` (올바름)

---

## 3. Cronjob 모니터링

### 상태 확인

**모든 cronjob 조회**:
```python
cronjob(action="list")
```

**출력 필드**:
- `job_id`: 고유 ID
- `name`: cronjob 이름
- `last_run_at`: 마지막 실행 시각
- `last_status`: 마지막 실행 상태 (success/failed/null)
- `last_delivery_error`: 마지막 에러 메시지
- `next_run_at`: 다음 실행 예정 시각
- `enabled`: 활성화 여부

### 일일 모니터링 리포트

**cronjob**: HIH Cron Monitoring Daily Report  
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

## 4. 로그 회전

### 로그 파일 관리

**로그 위치**: `~/.pm_logs/` (crontab 기반 job)  
**Hermes cron**: 보고서 파일 자체가 로그

**로그 회전 패턴**:
```
~/.pm_logs/
├── job_name.log              # 현재 로그 (rolling)
└── job_name_YYYYMMDD.log     # 일일 보고서
```

**로그 회전 cron**:
```cron
# 로그 회전 — 매주 일요일 03:00
0 3 * * 0 /usr/bin/logrotate ~/.pm_logs/*.log -state ~/.pm_logs/logrotate.state
```

---

## 5. 디스크 정리

### 캐시 정리

**Hermes 캐시** (9.8GB+):
```bash
hermes checkpoints clear-legacy --force
```

**npm 캐시** (3GB+):
```bash
npm cache clean --force
```

**uv 캐시** (1GB+):
```bash
uv cache clean
```

**camoufox 캐시** (1.4GB+):
```bash
rm -rf ~/.cache/camoufox
```

### 디스크 사용량 확인

**WSL/Windows C: 드라이브**:
```bash
# WSL 내부에서 확인
df -h /mnt/c

# Windows PowerShell에서 확인
# Get-PSDrive C
```

**정리 후 WSL 재시작** (필요시):
```powershell
# Windows PowerShell
wsl --shutdown
```

---

## 6. 정기 유지보수 일정

### 일일 (Daily)
- [ ] Cronjob 상태 확인 (자동: Cron Monitoring Daily Report)
- [ ] 디스크 사용량 확인 (95%+ 경고)
- [ ] 로그 파일 에러 확인

### 주간 (Weekly)
- [ ] 로그 파일 회전 (자동: logrotate)
- [ ] 캐시 정리 (필요시)
- [ ] 백업 확인 (GDrive, Obsidian)

### 월간 (Monthly)
- [ ] 전체 디스크 정리
- [ ] 오래된 로그 파일 아카이빙 (30일+)
- [ ] 시스템 업데이트 확인

---

## Pitfalls

### 1. 디렉토리 생성 누락
**증상**: cronjob 실행 시 "디렉토리를 생성할 수 없음" 에러  
**원인**: `HIH_Claude/cron_monitoring/` 등이 사전에 생성되지 않음  
**해결**: 
- cronjob 생성 전 디렉토리 자동 생성 로직 추가
- 또는 `setup_hih2_directories.sh` 실행

### 2. 데이터 파일 경로 불일치
**증상**: cronjob 실행 시 "파일을 찾을 수 없음" 에러  
**원인**: `projects/ss500/parts_tracking.csv`로 지정했지만 실제는 `HIH_Claude/데이터/parts_tracking.csv`  
**해결**:
- **스킬 정의 경로를 SSOT로 사용**
- 파일 존재 미리 검증 (`ls` 명령)
- 절대 경로 사용 (`HIH_Claude/데이터/` 기준)

### 3. 로그 파일 미존재
**증상**: `tail: cannot open '/tmp/job.log'` 에러  
**원인**: 로그 파일이 생성되지 않음 (첫 실행)  
**해결**:
- 로그 파일 미리 생성: `touch /tmp/job.log`
- 또는 cronjob에서 자동 생성: `>> /tmp/job.log 2>&1` (redirection이 파일 생성)

### 4. LLM Provider 미구성 (CRITICAL)
**증상**: cronjob 실행 시 모든 job이 동일하게 실패  
**에러 메시지**: `RuntimeError: No LLM provider configured. Run 'hermes model' to select a provider`  
**원인**: Hermes cron 시스템이 LLM provider 설정 없이 cronjob을 실행함  
**발견 시점**: 2026-05-29 Production Status, Daily Standup, Cron Monitoring 3개 job 동시 실패  
**해결**:
```bash
# LLM provider 구성
hermes model

# 또는 전체 설정
hermes setup
```
**사전 확인**:
- cronjob 생성 전 `hermes model list` 실행
- provider가 "No provider selected" 상태면 먼저 구성
- cronjob prompt에서 LLM 호출 필요 시 필수 구성  
**보고서 위치 확인**:
```bash
# 출력 파일은 생성되지만 내용은 에러 메시지만 있음
ls -la ~/.hermes/cron/output/<job_id>/
cat ~/.hermes/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md
```

### 5. Cronjob 디버깅 워크플로우
**표준 절차** (보고서 미생성/실패 시):
1. **cronjob 목록 확인** - `cronjob(action="list")`
2. **실행 상태 확인** - `last_status`, `last_run_at` 필드
3. **출력 디렉토리 확인**:
   ```bash
   ls -la ~/.hermes/cron/output/
   # 각 job_id별 디렉토리 있음
   ls -la ~/.hermes/cron/output/<job_id>/
   # 타임스탬프된 .md 파일 있음
   ```
4. **에러 로그 확인**:
   ```bash
   cat ~/.hermes/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md
   # Error 섹션 확인
   grep -A 10 "## Error" ~/.hermes/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS.md
   ```
5. **에러 유형별 조치**:
   - LLM provider 미구성 → `hermes model` 실행
   - 파일 경로 불일치 → 스킬 정의 경로 확인 및 수정
   - 디렉토리 없음 → `mkdir -p` 실행
6. **재시도 테스트**:
   ```python
   cronjob(action="run", job_id="<job_id>")
   ```

### 6. 디스크 공간 부족
**증상**: "No space left on device" 에러  
**원인**: 캐시/로그 파일 누적  
**해결**:
- 캐시 정리 (Hermes, npm, uv, camoufox)
- 오래된 로그 파일 삭제 (30일+)
- WSL 재시작 (Windows C: 드라이브)

---

## Quick Reference

### 디렉토리 생성
```bash
mkdir -p HIH_Claude/{cron_monitoring,production_status,standup_daily,bom_dfme_check,dfmea_status,weekly}
```

### 데이터 파일 확인
```bash
ls -lh HIH_Claude/데이터/parts_tracking.csv
```

### Cronjob 상태 확인
```python
cronjob(action="list")
```

### 로그 확인
```bash
tail -50 ~/.pm_logs/job_name.log
```

### 디스크 정리
```bash
hermes checkpoints clear-legacy --force
npm cache clean --force
uv cache clean
rm -rf ~/.cache/camoufox
```

---

## Related Skills

- `cron-management` - Cron job 관리 및 모니터링
- `hih-production` - 생산 현황 분석 (데이터 경로 SSOT)
- `pm-orchestration` - PM 오케스트레이션 (cronjob 연동)

---

## References & Support Files

### References (세부 지식 및 워크플로우)
- `references/hih2-task-analysis-cron-workflow.md` - HIH_2 태스크 분석 및 cronjob 생성 전체 워크플로우 (2026-05-29)
- `references/cronjob-debugging-workflow.md` - Cronjob 디버깅 절차 (보고서 미생성 문제 해결)

### Scripts (재실행 가능한 도구)
- `scripts/analyze_hih2_tasks.py` - 태스크 파일 분석 및 자동화 후보 식별 (CURRENT_TASK.md, PREPARED_TASK.md)
- `scripts/setup_hih2_directories.sh` - 필수 디렉토리 구조 일괄 생성

### Templates (예제 파일)
- 추가 필요시 생성 예정
