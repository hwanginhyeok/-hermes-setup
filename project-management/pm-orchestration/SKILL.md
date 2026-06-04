---
name: pm-orchestration
description: PM (Project Manager) 오케스트레이션 최적화 — 11개 프로젝트 통합 관리, 태스크 동기화, cron 헬스 모니터링, 블로커 추적
author: gothic-neon
version: 1.0.0
tags: [pm, orchestration, project-management, automation, cron, task-tracking]
triggers:
  - "PM 최적화"
  - "프로젝트 관리 개선"
  - "pm optimization"
  - "태스크 동기화"
  - "task sync"
  - "cron health"
  - "cron 모니터링"
  - "블로커 추적"
  - "blocker tracking"
  - "pm sync-summary"
  - "pm cron-health"
  - "pm blocked"
---

# PM 오케스트레이션

프로젝트 관리자(PM) 시스템의 운영 효율을 최적화하고 자동화합니다. PM이 READ-REVIEW-RE-DIRECT-VERIFY 순환을 더 빠르게 수행할 수 있도록 도구와 자동화를 제공합니다.

## PM 역할 이해

PM은 **오케스트레이터**로서 직접 코드를 수정하지 않고 다음을 수행합니다:

1. **READ** — 관련 문서/로그/DB 데이터를 직접 가져옴
2. **REVIEW** — 모순/이상/누락을 짚어냄 (단순 요약 X, 진짜 RC 추적)
3. **RE-DIRECT** — 부족하거나 잘못된 게 있으면 프로젝트 에이전트에 재지시
4. **TRACK** — TaskCreate로 작업 분해 + PREPARED_TASK.md 등록 지시 + 진행 추적
5. **VERIFY** — 자식 세션 결과를 **지시 vs 실행 갭 리뷰**로 검증

상세: `~/project-manager/CLAUDE.md`

## 핵심 명령어

### 태스크 요약 동기화

```bash
pm sync-summary                    # 전체 프로젝트 동기화
pm sync-summary --project 인성이    # 특정 프로젝트만
```

**기능**:
- 각 프로젝트의 CURRENT/PREPARED/FINISHED 태스크 수 자동 카운트
- TASK.md 요약 섹션 자동 업데이트
- Blocked 태스크 수 자동 추적

**문제 해결**: 자식 프로젝트가 CURRENT_TASK.md를 업데이트해도 TASK.md 요약이 수동으로 갱신되던 문제 해결

**Cron**: 매일 00:00 실행

---

### Cron 건강 모니터링

```bash
pm cron-health              # 기본 확인
pm cron-health --telegram   # 텔레그램 알림 전송
```

**기능**:
- 8개 주요 cron 로그 모니터링 (주식부자, PM, be-a-studio)
- 마지막 실행 시간 기준 예상 간격 대비 지연 감지
- CRITICAL/WARNING 우선순위 분류
- 텔레그램 알림 옵션

**문제 해결**: be-a-studio 등 cron이 간헐적으로 segfault로 멈추는데 PM이 자동 감지 못 하던 문제 해결

**모니터링 대상**:
- 주식부자 시황 수집 (KR/US)
- 주식부자 아침/저녁 브리핑
- PM MD 크기 체크
- PM WSL 백업
- be-a-studio 일간 작업
- be-a-studio 클린업

**Cron**:
- 매 6시간 모니터링 (00:00, 06:00, 12:00, 18:00)
- 매일 09:00 텔레그램 알림

---

### 블로커 추적 및 분석

```bash
pm blocked                    # 기본 보고서
pm blocked --priority         # 우선순위 P1만 표시
pm blocked --graphviz         # Graphviz DOT 파일 생성
```

**기능**:
- 전체 프로젝트 블로커 자동 수집 (CURRENT_TASK.md blocked 필드)
- 우선순위 자동 분류
  - **P1**: 자동화 핵심 기능 정체
  - **P2**: 일반 블로커
  - **P3**: 사용자 결정 대기 또는 외부 의존 (HW, 네트워크 등)
- 의존성 체인 추론 (예: icloud-blog ← 인성이)
- Graphviz DOT 파일 생성 (의존성 시각화)

**문제 해결**: 전체 블로커 현황을 한눈에 보기 어렵고, 해소 우선순위 판단이 어려웠던 문제 해결

---

## 아키텍처

### tmux 세션 구조

```
PM      — 오케스트레이터 (claude, Sonnet/Opus 유동). 4 panes
bea     — be-a-studio   (4 panes: claude pane1 + bash×3 → 병렬 에이전트 최대 3개)
stock   — 주식부자      (3 panes: claude pane1 + bash×2 → 병렬 에이전트 최대 2개)
insung  — 인성이        (3 panes: claude pane1 + bash×2 → 병렬 에이전트 최대 2개)
music   — music-lab     (3 panes: claude pane1 + bash×2 → 병렬 에이전트 최대 2개)
hermes  — 자동화/cron   (2 panes: hermes chat + bash)
```

**세션 = 프로젝트 고정**. pane2~ 는 bash 대기 중 → 병렬 에이전트 투입 슬롯.

**⚠️ 중요**: `open-all.sh`는 영문 세션명(`stock`, `insung`)을 사용하지만, 과거에 한글 세션명(`주식부자`, `인성이`)이 생성되어 있을 수 있습니다. 중복 세션이 생기면 pane 수가 비정상이 될 수 있습니다. 세션 정리 시:
```bash
# 중복 세션 확인
tmux list-sessions
# 한글 세션 삭제 (영문 세션 유지)
tmux kill-session -t 주식부자 인성이 자율주행 polistat 2>/dev/null
# music 세션은 누락되므로 수동 생성 필요
```

---

## 작업 지시 플로우

1. PM이 프로젝트 세션 선택 (bea/stock/insung/music)
2. 세션 내 빈 bash pane에 claude 시작 후 작업 브리핑 전달
3. 여러 에이전트 병렬 실행 가능 (pane 1~4)
4. 완료 후 PM이 결과 검증 (지시 vs 실행 갭 리뷰)

### 태스크 브리핑 관리

PM이 에이전트에게 작업 지시할 때 브리핑 파일을 **이중 저장**:

**전달용 (임시)**:
- 경로: `/tmp/{project}_task_{subtask}.md`
- 용도: tmux pane으로 cat 전달
- 수명: 작업 완료 후 정리

**보관용 (히스토리)**:
- 경로: `~/project-manager/content_queue/task_briefings/{project}/task_{timestamp}_{subtask}.md`
- 용도: 이력 추적, 재발 확인
- 수명: 영구

**사용법** (`scripts/task_briefing_manager.py`):
```python
from scripts.task_briefing_manager import create_task_briefing, deliver_to_pane

content = """## 서브태스크 A: 템플릿 구현

### 담당 파일 (이 파일들만 수정)
- templates/neighbor_v1.html

### 구현 목표
디자인 가이드 기반 구현

### 완료 조건
- [ ] 레이아웃 적용
- [ ] 컬러 시스템 적용
- [ ] VNC 확인

### 주의
- pane1과 파일 겹침 없음. 담당 파일 외 수정 금지.
- 완료 시 git add + commit (push는 PM 지시 대기)
"""

# 전달용 + 보관용 파일 생성
tmp_path, history_path = create_task_briefing("bea", "A", content)

# pane에 전달
deliver_to_pane("bea", 1.2, tmp_path)
```

**정리** (세션 종료 시):
```bash
rm -f /tmp/*_task_*.md  # 전달용 파일만 정리
# 보관용 파일은 유지 (히스토리)
```

---

## 자식 세션 결과 리뷰 (지시 vs 실행 갭)

자식 세션이 "완료" 보고를 보내도 그대로 받지 않습니다. PM이 다음 절차로 검증 후 사용자에게 보고:

1. **지시 체크리스트 매칭**: PM이 보낸 지시문을 항목별로 분해 (보통 (1)(2)(3)...). 각 항목별로 자식 보고가 ✅ 이행 / ⚠️ 부분 / ❌ 누락 / 🔄 변경 표시. 변경·누락 시 자식 보고문에서 사유 찾기. 사유 안 보이면 자식에게 직접 물어 캐묻기.
2. **L2 hunk 검증**: 커밋 해시 있으면 `git show --stat <commit>` + 핵심 1~2개 파일 hunk 직접 확인.
3. **산출물 직접 확인**: 다운로드 → ls + ffprobe / 생성 PNG·MD → 메타 / DB 변경 → 직접 쿼리. 보고값과 실측 일치 여부.
4. **사용자 보고 형식**:
   ```
   ## 지시 vs 실행 리뷰
   - (1) {지시}: ✅/⚠️/❌/🔄 — {사유}
   ## L2 검증 (해당 시)
   ## 산출물 검증
   결론: ✅ / ⚠️ N건 / ❌ 재지시
   ```

**Why**: 자식 세션이 자기 판단으로 추측 매핑·축약·미실행하는 케이스 빈번. 사례 — 5-18 재다운로드(2026-05-05): 지시 "9개 ID로만" → 자식이 추측으로 18개 덮어쓰고 "완료" 보고. 검증 안 했으면 사용자 의도와 어긋난 채 진행됨.

---

## 아침 루틴 (PM 세션 시작 시)

```bash
# 1. 전체 현황 확인
pm status

# 2. 블로커 점검
pm blocked

# 3. Cron 건강 확인
pm cron-health

# 4. 태스크 요약 동기화 (필요 시)
pm sync-summary
### 4. 검증
```bash
~/.hermes/skills/project-management/pm-orchestration/scripts/check_tmux_panes.sh
```

### 5. Claude 프로세스 추적 (진단용)

PM이 여러 tmux 세션의 Claude 프로세스를 추적해야 할 때:

```bash
# 전체 Claude 프로세스 상세 분석
ps aux | grep -E "claude|npx" | grep -v grep | awk '{printf "PID: %s, MEM: %s%%, CPU: %s%%, CMD: %s\n", $2, $4, $3, $11}'

# tmux pane별 실행 프로세스 확인
for session in PM bea insung stock music; do
    echo "[$session]"
    for i in {1..4}; do
        pane_pid=$(tmux display-message -p -t "$session:1.$i" "#{pane_pid}" 2>/dev/null)
        if [ -n "$pane_pid" ]; then
            child_pids=$(pgrep -P "$pane_pid" -f claude 2>/dev/null)
            if [ -n "$child_pids" ]; then
                for pid in $child_pids; do
                    cmd=$(ps -p "$pid" -o comm= 2>/dev/null)
                    mem=$(ps -p "$pid" -o %mem= 2>/dev/null)
                    echo "  Pane $i: PID=$pid, MEM=${mem}%, CMD=$cmd"
                done
            else
                top_cmd=$(ps -p "$pane_pid" -o comm= 2>/dev/null)
                echo "  Pane $i: $top_cmd (no claude)"
            fi
        fi
    done
done
```

**문제**: PM이 tmux 세션 안에서 실행 중인지 헷갈릴 때
- 현재 세션 확인: `tmux display-message -p "#S:#I.#P"`
- 결과: `PM:1.3` (PM 세션 pane 3)

## 예방 조치

## 주간 리뷰

```bash
# 1. 전체 블로커 + 의존성 체인
pm blocked --graphviz

# 2. Graphviz 렌더링
cd ~/project-manager/docs/systems
dot -Tpng blockers.dot -o blockers.png

# 3. 우선순위 P1만 집중
pm blocked --priority
```

---

## 파일 구조

```
project-manager/
├── scripts/
│   ├── sync_task_summary.py      # 태스크 요약 자동 동기화
│   ├── cron_health_monitor.py    # Cron 건강 모니터링
│   └── blocked_tracker.py        # 블로커 추적 및 분석
├── cron/
│   └── pm_optimization.cron      # PM 최적화 cron 설정
├── docs/systems/
│   ├── pm-optimization-report.md # 전체 보고서
│   └── blockers.dot              # Graphviz DOT (생성 시)
├── CLAUDE.md                     # PM 본체 설정
├── projects.yaml                 # 프로젝트 레지스트리 (SSOT)
└── pm.py                         # CLI 진입점
```

## 관련 문서
- PM 본체: `~/project-manager/CLAUDE.md`
- 프로젝트 레지스트리: `~/project-manager/projects.yaml` (SSOT)
- 최적화 보고서: `~/project-manager/docs/systems/pm-optimization-report.md`
- 글로벌 룰: `~/project-manager/global-rules/` (task-management.md, cron.md, ssot.md 등)

## 스킬 포함 파일
- `references/tmux-session-duplication-fix.md` — tmux 세션 중복 문제 해결 절차
- `scripts/check_tmux_panes.sh` — 세션별 pane 수 진단 스크립트
- `scripts/task_briefing_manager.py` — 태스크 브리핑 이중 저장 (전달용 + 보관용)
- `references/implementation-details.md` — 상세 구현 노트
- `references/quick-reference.md` — 빠른 참조 카드
- `references/claude-cli-usage-management.md` — Claude CLI 사용량 관리
- `references/telegram-bot-extension-pattern.md` — 텔레그램 봇 확장 패턴 (별도 파일 필수)
- `references/python-script-vs-module-import.md` — Python 스크립트 vs 모듈 import 패턴 (이 세션 발견)
| `templates/extra_handlers_template.py` — 새 봇 명령 핸들러 템플릿
| `references/python-script-vs-module-import.md` — Python 스크립트 작성 패턴 (execute_code vs heredoc)

## 기대 효과

### 시간 절감
- **태스크 요약 동기화**: 수동으로 11개 프로젝트 TASK.md를 열어서 확인하던 시간 → 0초 (자동)
- **Cron health 확인**: 각 로그 파일을 일일이 확인하던 시간 → 1초 (pm cron-health)
- **블로커 집계**: 각 프로젝트 CURRENT_TASK.md에서 blocked를 grep하던 시간 → 1초 (pm blocked)

### 품질 향상
- **일관성**: 태스크 카운트가 항상 최신 상태 유지
- **가시성**: 전체 블로커 현황을 한눈에 파악
- **선제적 조치**: Cron 장애를 24h 내에 자동 감지

---

## 관련 문서

- PM 본체: `~/project-manager/CLAUDE.md`
- 프로젝트 레지스트리: `~/project-manager/projects.yaml` (SSOT)
- 최적화 보고서: `~/project-manager/docs/systems/pm-optimization-report.md`
- 글로벌 룰: `~/project-manager/global-rules/` (task-management.md, cron.md, ssot.md 등)

---

## 관련 스킬

- `/hih-task` - 태스크 브리핑 + 관리
- `/hih-clear` - 세션 종료 정리 루틴
- `/hih-git` - 전체 프로젝트 git 브리핑
- `/hih-cron` - cron 추가/수정

---

## 부록: 세션 라이프사이클과 태스크 관리

이 섹션은 `hih-task-workflow` 스킬에서 흡수되었습니다.

### 세션 라이프사이클

```
세션 시작
    ↓
hih-task (태스크 브리핑 + 관리)
    ↓
작업 진행 (done/start/add/block 명령 수동 입력)
    ↓
세션 종료
    ↓
hih-clear (종료 루틴)
    ├── hih-task-clear (태스크 정리)
    ├── hih-memory (메모리 정리)
    ├── hih-git (git 커밋 + push)
    ├── DIFFICULTY 기록
    ├── 세션 요약 출력
    ├── handoff.md 생성
    └── /clear
```

### hih-task 기능

**브리핑:**
- TASK.md (인덱스)
- CURRENT_TASK.md (진행 중)
- PREPARED_TASK.md (예정 - P1만 상세, P2/P3 개수만)
- FINISHED_TASK.md (최근 5개만)

**인터랙티브 관리:**
- `done #번호` → CURRENT → FINISHED (완료일 기입)
- `start #번호` → PREPARED → CURRENT (시작일 기입)
- `add 태스크명` → PREPARED 추가 (ID 충돌 검사)
- `block #번호 사유` → blocked 컬럼 업데이트

### hih-task-clear 기능

세션 종료 시 hih-clear 내부에서 자동 호출:

1. 완료/신규 태스크 반영
2. ID 충돌 검사
3. depends 갱신
4. task_audit 실행 (좀비/중복/고아/정체/blocked/P1 인플레이션 처리)
5. TASK.md 인덱스 재계산
6. task_audit 재검증

### 자동화 한계

**중요**: 작업 완료 후 자동으로 `done` 처리되지 않음

- 에이전트가 작업을 완료해도 사용자가 수동으로 `done #번호` 입력해야 함
- 세션 종료 시 hih-task-clear가 정리하지만, 이건 "이번 세션에 완료된 것을 FINISHED로 이동"하는 것
- 진행 중인 태스크는 그대로 CURRENT에 남음

### PM vs 프로젝트 세션

| | PM 세션 | 프로젝트 세션 |
|---|---|---|
| **hih-task** | 읽기만 | 읽기 + 수정 가능 |
| **수정 권한** | 없음 | 있음 |
| **지시 방법** | tmux send-keys로 각 세션에 전달 | 직접 수정 |

**Remember**: 태스크 관리는 반자동. 사용자가 명령어로 제어하고, 스킬은 파일 정리와 audit를 자동화.

---

## 부록: 세션 보고 시스템 관리

이 섹션은 `session-report-management` 스킬에서 흡수되었습니다.

### 목적

#### 하루 단위 보고 저장

- **위치**: `~/.hermes/session_reports/daily/`
- **포맷**: `summary_YYYYMMDD_HHMMSS.md`
- **내용**: 완료 태스크, 진행 중, 신규, 블로커, 커밋, 다음 TODO

#### 월별 자동 아카이빙

- **월초(1일 자정)**: 이전 달 보고 → `archived/YYYY-MM/daily/` 이동
- **보관 정책**: 최신 달만 `daily/` 유지

#### 최적화 제안

- **키워드 빈도 분석**: 댓글 봇, 테스트, 배포 등 빈도 확인
- **자동화 제안**: 빈도 높은 키워드 기반 스킬/스크립트 제안

### 아카이빙 스크립트

```python
# 월초 자동 실행
python ~/.hermes/scripts/monthly_report_archive.py
```

**기능:**
- 이전 달 보고 아카이빙
- 키워드 빈도 분석
- 최적화 제안 생성

### Hermes Cron

```
이름: 월간 보고 아카이빙 + 최적화
스케줄: 0 0 1 * *
다음 실행: 매월 1일 자정
```

---

## 부록: tmux 워커 풀 병렬 작업

이 섹션은 `parallel-worker-pool` 스킬에서 흡수되었습니다.

### 병렬 워커 풀 원칙

한 프로젝트에서 3개 워커(w1/w2/w3)가 **동시 병렬 작업**을 진행합니다.

**장점**: 병렬 속도, 컨텍스트 깊이(새로 시작됨), 학습 효과

**단점**: 중복 작업 가능성, PM 부하(작업 분배+결과 통합)

### 워커 할당 패턴

**단일 프로젝트 집중**:
```
w1 → 메인 작업 (차트/시그널 등 핵심 기능)
w2 → 보조 작업 (백테스트/데이터)
w3 → 보조 작업 (UI/텍스트/문서)
```

**작업 분배 원칙**:
1. **독립성** — 각 워커의 작업이 파일 충돌 방지 (다른 파일 작업)
2. **순서 의존** — w1 → w2 → w3 순으로 결과 활용
3. **프로젝트 전환** — 한 프로젝트 끝나면 전체 워커 이동

### PM 작업 지시 플로우

1. **작업 분해**: 단일 태스크를 3개 독립 서브태스크로 분해
2. **동시 할당**: `tmux send-keys -t w1/w2/w3`로 동시 지시
3. **결과 통합**: w1 완료 → w2/w3에서 활용 → 전체 검증 → 커밋

### 장애 해결

**Pane 수 부족 / 세션 중복**:
- **증상**: `open-all.sh` 실행 후 pane이 4개가 아님
- **원인**: 하드코딩된 영문 세션명(`stock`, `insung`)과 `projects.yaml`의 한글 프로젝트명(`주식부자`, `인성이`) 불일치
- **해결**: 한글 세션 삭제 후 재생성

---

## 부록: tmux 기반 다중 프로젝트 관리

이 섹션은 `tmux-worker-pool` 스킬에서 흡수되었습니다.

### 세션 구조

| 세션 | panes | 역할 | 경로 |
|------|-------|------|------|
| PM | 4 | 오케스트레이터 (claude + bash×3) | ~/project-manager |
| bea | 4 | be-a-studio (claude + bash×3) | ~/be-a-studio |
| insung | 3 | 인성이 (claude + bash×2) | ~/insung_blog |
| stock | 3 | 주식부자 (claude + bash×2) | ~/stock |
| music | 3 | music-lab (claude + bash×2) | ~/music-lab |
| hermes | 2 | 자동화/cron (hermes chat + bash) | ~ |

pane 1은 claude 자동 시작, 나머지는 bash 대기 중.

### 세션 시작/관리

**전체 생성**: `cd ~/project-manager && ./open-all.sh`

**🔴 Pitfall: split-window -p vs -v**
- `-p`는 퍼센트로 분할하지만 4개 pane을 만들 때 실제로는 2개만 생성되는 문제
- **해결**: `split-window -v` 사용 + 명시적 높이 지정

**중복 세션 문제 해결**:
- `open-all.sh`는 영문 세션명(`stock`, `insung`, `music`)을 생성
- `projects.yaml`은 한글 프로젝트명(`주식부자`, `인성이`, `music-lab`)을 사용
- 해결: 한글 세션 삭제 후 재생성

### 에이전트 투입

**자동 투입**: 구분되는 기능 개발 시 자동으로 서브태스크 분해 → 병렬 에이전트 시작

**수동 투입**:
```bash
# bea 세션 pane 2에 에이전트 시작
tmux send-keys -t bea:1.2 "claude --add-dir ~/project-manager" Enter
```

### 상태 확인

**전체 세션 현황**: `tmux list-sessions`

**PM 도구로 현황**:
```bash
cd ~/project-manager
python3 pm.py sessions    # 전체 세션 상태
python3 pm.py status      # 통합 현황 대시보드
```

### 주의사항

- 세션 = 프로젝트 고정 (세션마다 다른 프로젝트)
- PM은 코드 직접 수정 X (분석·리뷰·재지시만)
- 결과 보고는 "지시 vs 실행 갭 리뷰"로 검증

---

## 부록: 포트폴리오 프로젝트 분석

이 섹션은 `portfolio-project-analysis` 스킬에서 흡수되었습니다.

### 프로젝트 상세 분석 워크플로우

프로젝트를 상세 분석하여 포트폴리오 문서를 작성한 후, 역량(스킬)을 추출합니다.

### STEP 1: 프로젝트 상세 분석

**순서**: CLAUDE.md → FINISHED_TASK.md → README

**추출 항목**:
- 프로젝트 개요 (title, description)
- 핵심 기능/방향성
- Tech Stack
- 기간
- 운영 모델

### STEP 2: 프로젝트 소개 글 작성

**형식**:
```markdown
## {프로젝트명}

> {한 줄 요약}

### 기간
{YYYY.MM} ~ 현재

### 핵심 기능
- {기능 1}
- {기능 2}

### 기술 스택
- {Tech 1}
- {Tech 2}

### 성과
- {지표 1}
- {지표 2}

### URL
- [링크 텍스트]({URL})
```

**원칙**: 프로젝트 위주의 설명 (기술/성과/URL), 스킬/역량 언급 X, 구체적인 숫자/지표 포함

### STEP 3-5: 역량 추출 및 구조화

**역량별 기준**:
- 이름: {동사 명사}
- 정의: {역량이 무엇인가}
- 프로젝트: {적용 프로젝트 목록}
- 기간: {총 경험 기간}
- 성과: {구체적인 성과}

---

### Claude CLI 사용량 관리

**문제:** 너무 많은 Claude CLI 병렬 실행 → 사용량 초과 → 작업 불가

### 문제 감지

```bash
# Claude CLI 프로세스 수 확인
ps aux | grep claude | grep -v grep | wc -l

# 메모리 사용량 총계 확인
ps aux | grep claude | grep -v grep | awk '{sum+=$6} END {print "Total:", sum/1024/1024, "GB"}'
```

### 해결 방안

```bash
# 1. 불필요한 프로세스 중지
pkill -f "claude --add-dir"

# 2. Bash pane 사용 (Claude 응답 중인 pane에 입력 불가)
tmux send-keys -t bea:1.4 "cd ~/be-a-studio && ..." Enter  # Bash pane 사용

# 3. Claude 응답 상태 확인
tmux capture-pane -t bea:1.3 -p | grep -E "Cogitated|Undulating"
```

### 예방

**최대 병렬 프로세스 제한:**
- PM(1) + 프로젝트(3) = 최대 4개
- 4개 초과 시 `pkill -f "claude --add-dir"`

**관련:** `references/claude-cli-usage-management.md`

---

## 텔레그램 PM-Bot 확장

### 구조

```
project-manager/
├── bot/
│   ├── pm_bot.py              # 메인 봇
│   └── extra_handlers.py      # 추가 명령 핸들러 (확장용)
├── docs/
│   └── PM-BOT-사용법.md        # 사용법 문서
└── restart_pm_bot.sh          # 봇 재시작 스크립트
```

### 명령 확장 패턴

**⚠️ pitfall**: `pm_bot.py`를 직접 패치/수정하면 문법 에러가 발생하기 쉽습니다. 이스케이프 문자와 import 순서 문제가 잦습니다.

**✅ 올바른 패턴**:
1. `bot/extra_handlers.py`에 새 핸들러 함수 작성
2. `pm_bot.py`에서 import: `from bot.extra_handlers import cmd_add, cmd_auto`
3. `main()` 함수에 핸들러 등록

### 추가된 명령

#### /add — 프로젝트 태스크 추가

```
/add {프로젝트} {태스크명} [우선순위]
```

예시:
```
/add bea 네이버 발행 로직 개발 P1
/add stock 스크리너 최적화
/add music 오디오 후처리 자동화 P3
```

기능:
- `{프로젝트}/PREPARED_TASK.md`에 자동 태스크 추가
- ID 자동 생성 (기존 ID +1)
- 우선순위: P1, P2, P3 (기본: P2)

지원 프로젝트: bea, stock, insung, music, hermes

#### /auto — 자동화 작업 등록

```
/auto {프로젝트} {작업 설명}
```

예시:
```
/auto bea 1시간마다 태스크 체크
/auto stock 매일 오후 5시 스크리닝 실행
```

기능:
- `automations/{project}_{timestamp}.md` 파일 생성
- 작업 설명, 생성일 기록
- cron 등록 필요

#### /auto list

등록된 자동화 목록 조회

### 봇 재시작

```bash
bash ~/project-manager/restart_pm_bot.sh
```

스크립트가 수행하는 작업:
1. 기존 봇 프로세스 종료
2. PID 파일 정리
3. 백그라운드 실행 (`nohup python3 bot/pm_bot.py`)
4. 실행 확인

### 로그 확인

```bash
tail -f ~/.pm_logs/pm_bot.log
```

### 텔레그램에서 PM 세션 통신

**자유 대화 모드**:
- 슬래시(/)로 시작하지 않는 메시지는 PM 세션에 릴레이
- PM 답변의 `===PM-END===` 마커까지 캡처

예시:
```
사용자: bea 작업 현황 알려줘
봇: 🔄 PM에 전달 중...
PM: bea: 3개 작업 진행 중
    - 네이버 발행 (90%)
    - 댓글봇 최적화 (40%)
    - UI 개선 (10%)
    ===PM-END===
```

### 사용법 문서

`~/project-manager/docs/PM-BOT-사용법.md` 참조

---

*생성일: 2026-05-18*
*버전: 1.1.0*
*상태: ✅ 운영 중*
*버전: 1.0.0*
*상태: ✅ 운영 중*
