---
name: hih-production
description: SS500 생산 현황 분석 및 PFD 갱신. parts_tracking.csv + BOM Assembly 구조 분석 → Assembly별 조립 가능 수량, 블로커, 일정 리스크 브리핑 → PFD HTML 재생성. "생산 현황", "양산 상태", "블로커", "공정도", "공정상황 어때", "생산 어때", "양산 어때" 트리거.
allowed-tools: Bash, Read, Grep, Glob, Write, Edit
---

# 생산 현황 분석 (/hih-production)

## 개요

SS500 프로젝트의 생산 현황을 분석하고 PFD(Process Flow Diagram)를 갱신합니다. Assembly별 조립 가능 수량을 계산하고, 블로커를 식별하며, HTML 형식의 공정도를 최신 상태로 유지합니다.

## 사전 조건

- `.claude/rules/manufacturing.md` 규칙 준수 (Assembly 단위 사고)
- 추측 금지 — BOM에 없는 정보를 추정하지 않음
- 사용자 색상 취향 준수 (tmux 테마 기반)

## 입력 데이터

| 파일 | 용도 |
|------|------|
| `HIH_Claude/데이터/parts_tracking.csv` | 부품별 입고/사용/잔고 현황 |
| `HIH_Claude/데이터/schedule_milestones.csv` | 마일스톤 일정/상태 |
| `HIH_Claude/데이터/blockers.csv` | 블로커 현황 |
| `HIH_Claude/산출물/04_PFD/SS500_BOM_Assembly_구조분석.md` | Assembly 계층 구조 |

## 1단계: 데이터 확인

```bash
# 파일 존재 확인
ls -lh HIH_Claude/데이터/parts_tracking.csv
ls -lh HIH_Claude/데이터/schedule_milestones.csv
ls -lh HIH_Claude/데이터/blockers.csv

# 최신 데이터 확인
tail -20 HIH_Claude/데이터/parts_tracking.csv
```

## 2단계: Assembly별 조립 가능 수량 계산

각 Assembly에 대해 **투입 핵심 부품의 최소 확보 수량** = 해당 Assembly 조립 가능 수량.

### 매핑 테이블 (BOM V0.0.11 기준)

| Assembly | 핵심 부품 | 조립 가능 수량 산정 |
|----------|----------|---------------------|
| SFA | Guide Block, Shaft BRKT, Sliding Shaft | MIN(각 부품 잔고) |
| SRA | Guide Block, Sliding Shaft | MIN(각 부품 잔고) |
| CBA | PC Assy, VCU, DCDC, Pump Driver, Harness | MIN(각 부품 잔고) |
| FRA | Frame, Traction Motor, Battery | MIN(각 부품 잔고) |
| PUA | Pump Plate, Solenoid Sub, Manifold | MIN(각 부품 잔고) |
| WTA | Rotation Tank, Level Sensor | MIN(각 부품 잔고) |
| SUA | Front/Rear Shroud, Fan Motor, Spray Pipe | MIN(각 부품 잔고) |
| HOA | Hood, Camera, Headlamp, Control Panel | MIN(각 부품 잔고) |
| One-E | 모든 Sub-Assy 완료 차량 | VHA 완료 차량 수 |

## 3단계: 블로커 식별

Assembly별로:
1. 조립 가능 수량이 0이면 → **블로커** (빨강 #e17055)
2. 조립 가능 수량 < 납품 목표면 → **경고** (노랑 #fdcb6e)
3. 조립 가능 수량 ≥ 납품 목표면 → **완료** (녹색 #00b894)

## 4단계: HTML 재생성

`HIH_Claude/산출물/04_PFD/SS500_PFD_생산공정도_V01_260310.html`을 읽어서,
각 Assembly 카드의 **색상(border-color)**, **badge 텍스트**, **부품 상태 텍스트**를
2단계/3단계 결과로 업데이트합니다.

### 사용자 색상 테마 (tmux Dark Mono 기반)

```python
color_mapping = {
    # One-E Assembly (완성품) - 검정색 (사용자 선호)
    'ONE_E_BORDER': '#000000',
    'ONE_E_BG': '#f8f8f8',
    'ONE_E_TITLE': '#000000',
    'ONE_E_BADGE': '#000000',
    
    # 상태별 색상
    'OK_BORDER': '#00b894',      # 완료/확보 (녹색)
    'WARN_BORDER': '#fdcb6e',    # 부분 확보/경고 (노랑)
    'NG_BORDER': '#e17055',      # 블로커/위험 (빨강)
    'GRAY_BORDER': '#b2bec3',    # 해당없음 (회색)
    
    # 배경색
    'BODY_BG': '#ffffff',        # 순백 배경
    'CARD_BG': '#ffffff',        # 카드 배경
}
```

### One-E Assembly 추가 패턴

One-E(완성품) Assembly는 VHA → EOL → OQC → 출하 흐름 다음에 추가:

```html
<!-- One-E (완성품) -->
<div class="assy-col" style="border-color:#000000;border-width:3px">
  <span class="badge" style="background:#000000;color:#fff">최종완성품</span>
  <div class="assy-title" style="background:#000000;color:#fff">One-E</div>
  <div class="assy-sub">완성차량 (Speed Sprayer SS500)</div>
  <div class="assy-count">모든 Sub-Assy 합류 완료</div>
  <div class="step"><div class="step-sym s-op">○</div><div class="step-txt">VHA 완료차량</div></div>
  <div class="step"><div class="step-sym s-insp">□</div><div class="step-txt">EOL 기능검사 통과</div></div>
  <div class="step"><div class="step-sym s-decision"></div><div class="step-txt">합/부 판정 PASS</div></div>
  <div class="step"><div class="step-sym s-insp">□</div><div class="step-txt">OQC 외관검사 통과</div></div>
  <div class="step"><div class="step-sym s-op">○</div><div class="step-txt">출하 포장</div></div>
  <div class="step"><div class="step-sym s-store"></div><div class="step-txt">고객 인도</div></div>
</div>
```

## 5단계: 브라우저에서 열어 사용자에게 보여줌

```bash
cmd.exe /c start "" "$(wslpath -w 'HIH_Claude/산출물/04_PFD/SS500_PFD_생산공정도_V01_260310.html')" 2>/dev/null
```

## 출력 포맷

```
## SS500 생산 현황 (YYYY-MM-DD 기준)

### Assembly별 조립 가능 수량

| Assembly | 가능 수량 | 병목 부품 | 상태 |
|----------|---------|---------|------|
| SFA/SRA  | X대     | -       | ✅   |
| CBA      | Y대     | VCU    | ⚠️   |
| ...      | ...     | ...    | ...  |

### 블로커 요약

1. (Assembly): (부품) — (상태/일정)
2. ...

### 납품 목표 vs 현실

| 목표 | 일정 | Assembly 제약 | 판단 |
|------|------|-------------|------|
| 2대  | 4/7  | CBA ?대, ... | 가능/불가/확인필요 |
```

## Cronjob Integration Pitfalls

### 데이터 파일 경로 불일치 (CRITICAL)
- **증상**: cronjob 실행 시 "파일을 찾을 수 없음" 에러
- **원인**: cronjob prompt에서 `projects/ss500/parts_tracking.csv`로 지정했지만, 실제 파일은 `HIH_Claude/데이터/parts_tracking.csv`에 있음
- **발견 시점**: 2026-05-29 Production Status Daily Report cronjob 실행 실패
- **해결**: 
  1. **스킬 경로 확인**: SKILL.md에 명시된 경로(`HIH_Claude/데이터/`)를 그대로 사용
  2. **cronjob prompt 수정**: 스킬 정의 경로를 따르도록 수정
  3. **파일 존재 검증**: cronjob 생성 전 `ls` 명령으로 파일 위치 확인
- **수정 예시**:
  ```python
  # ❌ 잘못된 경로
  - projects/ss500/parts_tracking.csv
  
  # ✅ 올바른 경로
  - HIH_Claude/데이터/parts_tracking.csv
  ```

### 보고서 저장 디렉토리 누락 (CRITICAL)
- **증상**: cronjob 실행 시 "디렉토리를 생성할 수 없음" 에러 또는 보고서 파일 미생성
- **원인**: `HIH_Claude/production_status/`, `HIH_Claude/cron_monitoring/` 등의 디렉토리가 사전에 생성되지 않음
- **발견 시점**: 2026-05-29 다중 cronjob 테스트 - 모든 job이 error 상태지만 last_delivery_error가 null
- **해결**: 
  1. **cronjob 생성 전 디렉토리 구조 먼저 생성**:
     ```bash
     mkdir -p HIH_Claude/cron_monitoring
     mkdir -p HIH_Claude/production_status
     mkdir -p HIH_Claude/standup_daily
     mkdir -p HIH_Claude/bom_dfme_check
     mkdir -p HIH_Claude/dfmea_status
     mkdir -p HIH_Claude/weekly
     ```
  2. **스킬에 디렉토리 생성 단계 추가** 또는 setup 문서에 명시
- **필요한 디렉토리**:
  ```
  HIH_Claude/
  ├── production_status/
  ├── cron_monitoring/
  ├── standup_daily/
  ├── bom_dfme_check/
  ├── dfmea_status/
  └── weekly/
  ```

### 보고서 파일 생성 실패 시 디버깅 방법
- **증상**: cronjob이 실행됨(last_run_at 있음)하지만 보고서 파일이 생성되지 않음
- **발견 시점**: 2026-05-29 - 3개 job이 09:00:34에 실행되었으나 모두 error, 생성된 파일 없음
- **확인 절차**:
  1. 디렉토리 권한 확인: `ls -la HIH_Claude/production_status/`
  2. 스킬 직접 실행 테스트로 파일 생성 가능성 확인
  3. 간단한 테스트 cronjob으로 파일 시스템 쓰기 권한 검증
  4. Hermes cron 시스템 로그 확인 (에러 메시지가 last_delivery_error에 없을 경우)
- **해결**: 스킬 로직을 단순화해서 테스트 → 점진적으로 복잡도 증가

## Pitfalls

### 색상 문제 대상 오해 (CRITICAL)
- **증상**: 사용자가 "색깔 변경이 안됐다", "노란색인데"라고 보고
- **함정**: 이것이 **PFD HTML 색상**이라고 가정하고 분석 시작
- **실제 원인**: 사용자는 **Hermes Agent 자신의 터미널 출력 색상**을 말하는 것 (tmux 내에서의 메시지 색상)
- **해결**: 
  1. **먼저 대상 확인**: "PFD HTML의 One-E Assembly 색상인가요? 아니면 제 터미널 출력 색상인가요?"
  2. **tmux 테마 확인**: `cat ~/.tmux.conf` — 사용자는 Dark Mono (흰 배경 + 검정 텍스트) 선호
  3. **두 영역 구분**:
     - **Hermes 터미널 출력**: ANSI escape codes, tmux에 영향받음
     - **프로젝트 아티팩트**: HTML/CSS, 별도 색상 체계
- **세션 기록**: `references/color-confusion-debugging-session-20260528.md`

### HTML 색상 문제 디버깅
- **증상**: 사용자가 "노란색인데"라고 보고함
- **원인**: HTML 파일에 One-E Assembly가 없거나, CSS 클래스 매핑이 잘못됨
- **해결**: 
  1. 먼저 HTML 파일 직접 열어서 색상 코드 확인 (grep '#' filename.html)
  2. BeautifulSoup 미설치 시 regex로 HTML 분석
  3. Assembly 카드의 `style="border-color:#XXXXXX"` 인라인 스타일 확인
  4. 사용자 tmux 테마 색상 참조 (~/.tmux.conf)

### 백업 없이 수정 실수
- **증상**: HTML 파일 망가짐
- **원인**: 백업 없이 직접 수정
- **해결**: 항상 수정 전 `.backup` 파일 생성

### One-E Assembly 누락
- **증상**: 완성품 차량 Assembly가 HTML에 없음
- **원인**: 기존 PFD가 Sub-Assembly만 포함
- **해결**: VHA 영역 다음에 One-E Assembly 추가 (검정색 #000000)

## 참고 자료

- `.claude/skills/hih-production/references/pfd-color-workflow.md` - HTML 색상 분석 워크플로우
- `.claude/skills/hih-production/references/user-color-preferences.md` - 사용자 색상 취향
