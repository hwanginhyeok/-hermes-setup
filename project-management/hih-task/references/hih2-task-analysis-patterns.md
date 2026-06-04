# HIH_2 Task Analysis Patterns for Automation

Analysis performed on 2026-05-28 to identify recurring patterns in HIH_2 project tasks that could benefit from cron job automation.

## Critical Path Information (2026-06-04 Updated)

**HIH_2 Project Structure**:
- **Root project path**: `/home/gint_pcd/projects/HIH_2/`
  - Contains: `TASK.md`, `CURRENT_TASK.md`, `PREPARED_TASK.md`, `FINISHED_TASK.md`
  - These are the primary task management files at project root
  
- **Claude workspace**: `/home/gint_pcd/projects/HIH_2/HIH_Claude/`
  - Contains: Reports, references, output files, analysis results
  - Subdirectories: `보고서/`, `데이터/`, `산출물/`, `참고자료/`, etc.

**PITFALL**: Do NOT assume task files are in `~/HIH_Claude/` — they are at project root.
**PITFALL**: Do NOT assume Claude files are at project root — they are in `HIH_Claude/` subdirectory.

**Path Discovery Pattern** (when working with HIH_2):
```bash
# Always verify actual paths first
find ~ -maxdepth 3 -name "HIH_Claude" -o -name "HIH_2" 2>/dev/null
# Expected output:
# /home/gint_pcd/projects/HIH_2
# /home/gint_pcd/projects/HIH_2/HIH_Claude

# Task files are at project root
ls /home/gint_pcd/projects/HIH_2/{CURRENT,PREPARED,FINISHED}_TASK.md

# Claude outputs are in HIH_Claude subdirectory
ls /home/gint_pcd/projects/HIH_2/HIH_Claude/standup_daily/
```

## Task Distribution

- **Current (진행중)**: 5 tasks
- **Prepared (준비중)**: 46 tasks  
- **Finished (완료)**: 35+ tasks
- **Total Active**: 51 tasks
- **Automation Candidates**: 45 tasks

## Automation Pattern Categories

### 1. DAILY (2 tasks)
**Pattern**: Daily status checks and health monitoring

**Key Tasks**:
- C-133: DFMEA 자동감지 시스템 동작 확인
- C-197: Notion → Obsidian + GDrive 동기화

**Recommended Cron**:
```bash
# Daily DFMEA health check (already exists via /hih-standup skill)
0 8 * * * cd ~/projects/HIH_2 && python3 dfmea_check.py >> ~/.pm_logs/hih2_dfmea_daily.log 2>&1

# Daily Notion sync (already exists via /hih-notion-sync skill)
0 20 * * * cd ~/projects/HIH_2 && python3 notion_sync.py >> ~/.pm_logs/hih2_notion_sync.log 2>&1
```

### 2. WEEKLY (2 tasks)
**Pattern**: Weekly reporting and data updates

**Key Tasks**:
- C-128: SS1000 BOM 다운로드 + PUA 시트 기구 형상 확인
- C-197: Notion 전체 동기화 (weekly component)

**Recommended Cron**:
```bash
# Weekly BOM check (Friday afternoon)
0 17 * * 5 cd ~/projects/HIH_2 && python3 bom_validator.py >> ~/.pm_logs/hih2_bom_weekly.log 2>&1

# Weekly report generation (Friday evening)
0 18 * * 5 cd ~/projects/HIH_2 && python3 weekly_report_gen.py >> ~/.pm_logs/hih2_weekly_$(date +\%Y\%m\%d).log 2>&1
```

### 3. SYNC (13 tasks)
**Pattern**: Data synchronization across systems (BOM, Notion, datasheets, Excel)

**Key Tasks**:
- C-169: 노즐 12→20개 변경 → DVP·CP 갱신
- C-171: 부품 데이터시트 PDF 정본 일괄 수집
- C-188: MBD params_ssot DS 갱신

**Characteristics**:
- Triggered by external changes (spec updates, BOM changes)
- Bidirectional sync (Notion ↔ Local)
- Version tracking required
- Excel export/import cycles

**Implementation Pattern**:
```python
# Generic sync wrapper
def sync_with_validation(source, target, validator):
    """
    Sync source → target with validation
    - validator checks data integrity
    - Creates backup before sync
    - Logs all changes
    - Raises alert on validation failure
    """
    backup(target)
    changes = detect_changes(source, target)
    if changes:
        apply_changes(target, changes)
        if not validator(target):
            restore(target)
            alert("Validation failed")
```

### 4. MONITORING (14 tasks)
**Pattern**: Health checks, issue tracking, and status monitoring

**Key Tasks**:
- C-192: 춘천 시연회 준비 (event monitoring)
- C-133: DFMEA 자동감지 시스템 동작 확인
- C-152: CAN-Edge 또는 CAN 로거 장비 양산품 탑재 검토
- C-137: 이슈 전수조사 나머지 11건 DFMEA 분석 검토

**Characteristics**:
- Threshold-based alerts (AP=H items)
- Trend tracking (SOD score changes)
- Dependency monitoring (blocked tasks)
- Event countdown (test dates, delivery dates)

**Implementation Pattern**:
```python
# Generic monitoring wrapper
def monitor_with_alerts(checks, alert_config):
    """
    Run monitoring checks and send alerts
    - checks: list of (name, function, threshold)
    - alert_config: notification settings
    """
    results = {}
    for name, func, threshold in checks:
        value = func()
        results[name] = value
        if exceeds_threshold(value, threshold):
            send_alert(name, value, threshold)
    return results
```

### 5. REPORTING (18 tasks)
**Pattern**: Document generation, Excel exports, status reports

**Key Tasks**:
- C-156: APQP P0-2 Pre-launch Control Plan 통합 매트릭스
- C-158: APQP P1-1 PPAP 패키지 인덱스 18 Element 매핑
- C-159: APQP P1-2 MSA Plan (EOL/CBA FCT Gage R&R)

**Characteristics**:
- Template-driven generation
- Data aggregation from multiple sources
- Excel export with formatting
- Version control and approval workflow

**Implementation Pattern**:
```python
# Generic report generator
def generate_report(template, data_sources, output_format):
    """
    Generate report from template + data
    - template: markdown/jinja/excel template
    - data_sources: dict of data queries
    - output_format: 'md', 'xlsx', 'pdf'
    """
    data = {name: query(src) for name, src in data_sources.items()}
    report = render_template(template, data)
    if output_format == 'xlsx':
        export_to_excel(report)
    elif output_format == 'pdf':
        convert_to_pdf(report)
    return report
```

### 6. DATA_COLLECTION (15 tasks)
**Pattern**: Automated data gathering, migration, and cataloging

**Key Tasks**:
- C-140: 기존 데이터 → Obsidian 마이그레이션 (CSV/MD → 노트 변환)
- C-142: MBD 파라미터 SSOT 구축 — 실측/데이터시트 기반 파라미터 시트 작성
- C-152: CAN-Edge 또는 CAN 로거 장비 양산품 탑재 검토

**Characteristics**:
- Batch processing of existing data
- Format conversion (CSV → MD, PDF → text)
- Metadata extraction and tagging
- SSOT (Single Source of Truth) maintenance

### 7. DOCUMENTATION (23 tasks)
**Pattern**: Technical writing, spec definition, manual creation

**Key Tasks**:
- C-158: APQP P1-1 PPAP 패키지 인덱스 18 Element 매핑
- C-164: 외부교반기 DPW80-12 시험데이터 발굴/사양 확정
- C-170: IEC 60068(11건) + ISO 16750(4건) 정본 구매 또는 도서관 발췌

**Characteristics**:
- Standard document templates (PPAP, APQP, DFMEA)
- Version control and approval workflow
- Cross-referencing between documents
- Multi-format output (MD, Excel, PDF)

### 8. QUALITY (7 tasks)
**Pattern**: Quality assurance, testing plans, inspection procedures

**Key Tasks**:
- C-156: APQP P0-2 Pre-launch Control Plan 통합 매트릭스
- C-159: APQP P1-2 MSA Plan (EOL/CBA FCT Gage R&R)
- C-157: APQP P0-3 DVP&R 마스터 매트릭스 작성

**Characteristics**:
- Test procedure definition
- Measurement system analysis (MSA)
- Control plan integration (IQC, LQC, EOL, OQC)
- Gage R&R studies

## Immediate Automation Opportunities

### Priority P0: Already Implemented
✅ `/hih-standup` - Daily standup with DFMEA health check (C-133)
✅ `/hih-notion-sync` - Notion synchronization (C-197)
✅ `/hih-weekly-report` - Weekly reporting (C-128, C-176)
✅ `/hih-production` - Production status analysis (PFD generation)

### Priority P1: New Automation Needed

#### 1. DFMEA Weekly Review (`dfmea-weekly-review`)
**Purpose**: Automatic review of DFMEA analysis gaps

**Trigger**: Weekly (Monday morning)

**Scope**:
- Check `dfmea_issue_status.csv` for unanalyzed issues
- Identify issues without S/O/D scores
- Alert on AP=H items without mitigation plans
- Generate summary report

**Implementation**:
```python
# dfmea_weekly_review.py
import pandas as pd
from pathlib import Path

def check_unanalyzed_issues():
    df = pd.read_csv('HIH_Claude/dfmea_issue_status.csv')
    unanalyzed = df[df['status'] != 'analyzed']
    
    if len(unanalyzed) > 0:
        alert(f"{len(unanalyzed)} issues need DFMEA analysis")
        return unanalyzed
    return None

def check_high_priority_gaps():
    df = pd.read_csv('HIH_Claude/dfmea_issue_status.csv')
    high_ap = df[df['ap_score'] == 'H']
    no_mitigation = high_ap[high_ap['mitigation_plan'].isna()]
    
    if len(no_mitigation) > 0:
        alert(f"{len(no_mitigation)} AP=H items without mitigation")
        return no_mitigation
    return None
```

#### 2. APQP Progress Tracker (`apqp-tracker`)
**Purpose**: Track APQP artifact completion progress

**Trigger**: Weekly (Friday afternoon)

**Scope**:
- Check `산출물/00_APQP_갭분석_실행계획_V01_*.xlsx`
- Calculate completion percentage per Phase
- Identify overdue artifacts
- Generate progress dashboard

**Metrics**:
- Phase completion: P0 (xx%), P1 (xx%), P2 (xx%), P3 (xx%)
- Overdue items: count + list
- Next week priorities: P1 items due within 7 days

#### 3. BOM Validator (`bom-validator`)
**Purpose**: Validate BOM consistency across documents

**Trigger**: On BOM changes + weekly check

**Scope**:
- Compare BOM entries across:
  - `projects/ss500/BOM/`
  - `산출물/01_DFMEA/` (parts referenced)
  - `산출물/03_Control_Plan/` (inspection points)
- Identify orphan references (part in DFMEA but not in BOM)
- Check for obsolete part numbers

**Validation Rules**:
- All DFMEA parts must exist in BOM
- All BOM parts must have datasheet (for T1/T2 parts)
- Control Plan inspection points must reference valid BOM items

## Task Analysis Methodology

### Step 1: Parse Task Files
Extract tasks from markdown tables:
```python
def parse_table(lines):
    for line in lines:
        if line.startswith('| C-'):
            parts = [p.strip() for p in line.split('|')[1:-1]
            tasks.append({'id': parts[0], 'title': parts[1], ...})
```

### Step 2: Pattern Matching
Define automation patterns:
```python
patterns = {
    'daily': ['데일리', 'standup', '브리핑', '진행사항'],
    'weekly': ['주간', 'weekly', 'week'],
    'sync': ['노션', 'Notion', '동기화', 'sync', '갱신'],
    'monitoring': ['DFMEA', '이슈', '모니터링', '점검', '체크'],
    # ...
}
```

### Step 3: Cron Candidate Identification
```python
cron_candidates = []
for task in tasks:
    detected = [p for p, keywords in patterns.items() 
                if any(kw in task['title'] + task['extra'] for kw in keywords)]
    if detected:
        cron_candidates.append({'task': task, 'patterns': detected})
```

### Step 4: Priority Sorting
```python
priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
cron_candidates.sort(key=lambda x: priority_order.get(x['priority'], 99))
```

### Step 5: Grouping and Recommendations
Group by pattern type and recommend cron jobs:
- Daily patterns → `0 8 * * *` (daily 8 AM)
- Weekly patterns → `0 18 * * 5` (Friday 6 PM)
- Sync patterns → triggered by file changes
- Monitoring patterns → check intervals (hourly/daily)

## Integration with Existing Skills

### Daily Standup Execution Pattern (2026-06-04)

**Successfully Tested Approach**:
```python
# Correct path structure for HIH_2 standup
hih_path = Path("/home/gint_pcd/projects/HIH_2")  # Root for task files

# Task files are at project root
current_task = hih_path / "CURRENT_TASK.md"
prepared_task = hih_path / "PREPARED_TASK.md"
finished_task = hih_path / "FINISHED_TASK.md"

# Claude outputs are in HIH_Claude subdirectory
standup_dir = hih_path / "HIH_Claude" / "standup_daily"
dfmea_check_script = hih_path / "HIH_Claude" / "dfmea_check.py"
dfmea_output = hih_path / "HIH_Claude" / "dfmea_latest_check.txt"
parts_tracking = hih_path / "HIH_Claude" / "parts_tracking.csv"

# P0/P1 task extraction pattern
p0_tasks = []
p1_tasks = []
for line in content.split('\n'):
    if '| C-' in line:
        if '[P0]' in line or '| **P0**' in line:
            p0_tasks.append(line.strip())
        elif '[P1]' in line or '| P1' in line:
            p1_tasks.append(line.strip())

# Standup file output
standup_file = standup_dir / f"{today_iso}.md"
```

**Key Learning**: The dual-path structure (root for tasks, subdirectory for outputs) must be respected in all HIH_2 automation scripts.

### HIH Standup (`/hih-standup`)
- Already handles daily DFMEA health check
- Outputs "DFMEA 검토 필요" section
- No additional cron needed
- **Uses correct path structure**: `projects/HIH_2/` for tasks, `HIH_Claude/` for outputs

### HIH Notion Sync (`/hih-notion-sync`)
- Handles Notion → local synchronization
- Downloads issues, meetings, weekly DBs
- Manual trigger via `/hih-notion-sync` command

### HIH Weekly Report (`/hih-weekly-report`)
- Generates weekly reports in MD + Excel
- Uploads to Notion weekly DB
- Manual trigger via `/hih-weekly-report` command

### HIH Production (`/hih-production`)
- Analyzes production status and blockers
- Generates PFD HTML
- Manual trigger via `/hih-production` command

## Recommended Cron Schedule

Based on task analysis, recommended cron additions:

```crontab
# HIH_2 Automation Schedule
# DFMEA Weekly Review - Monday 8 AM
0 8 * * 1 cd ~/projects/HIH_2 && python3 scripts/dfmea_weekly_review.py >> ~/.pm_logs/hih2_dfmea_weekly.log 2>&1

# APQP Progress Tracker - Friday 6 PM
0 18 * * 5 cd ~/projects/HIH_2 && python3 scripts/apqp_tracker.py >> ~/.pm_logs/hih2_apqp_$(date +\%Y\%m\%d).log 2>&1

# BOM Validator - Daily noon (on BOM changes + weekly check)
0 12 * * * cd ~/projects/HIH_2 && python3 scripts/bom_validator.py >> ~/.pm_logs/hih2_bom_daily.log 2>&1

# MBD Parameter Sync - Wednesday 10 AM
0 10 * * 3 cd ~/projects/HIH_2 && python3 scripts/mbd_params_sync.py >> ~/.pm_logs/hih2_mbd_sync.log 2>&1
```

## Notes

- All HIH_2 automation candidates already have skills (`/hih-*`)
- Main gap is **weekly scheduled execution** of existing skills
- Priority: Add cron triggers to existing skills, not new implementations
- Monitor cron execution via `~/.pm_logs/hih2_*.log`
- Alert on failures via existing notification channels

## Related Skills

- `hih-task` - Project task briefing and session cleanup
- `hih-standup` - Daily standup with DFMEA health check
- `hih-notion-sync` - Notion synchronization
- `hih-weekly-report` - Weekly report generation
- `hih-production` - Production status analysis and PFD generation
