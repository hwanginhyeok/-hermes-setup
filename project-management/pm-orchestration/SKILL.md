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

## PM 작업 지시 플로우

1. PM이 프로젝트 세션 선택 (bea/stock/insung/music)
2. 세션 내 빈 bash pane에 claude 시작 후 작업 브리핑 전달
3. 여러 에이전트 병렬 실행 가능 (pane 1~4)
4. 완료 후 PM이 결과 검증 (지시 vs 실행 갭 리뷰)

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

# 5. tmux 세션 상태 확인 (pane 수 비정상 감지)
~/.hermes/skills/project-management/pm-orchestration/scripts/check_tmux_panes.sh
```

---

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
- `references/implementation-details.md` — 상세 구현 노트
- `references/quick-reference.md` — 빠른 참조 카드

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
- `/hih-git` - 전체 프로젝트 git 브리핑 + 일괄 push/pull
- `/hih-cron` - cron 추가/수정 — 합치기/충돌/중복 방지
- `parallel-worker-pool` - tmux 워커 풀 병렬 작업 관리

---

*생성일: 2026-05-15*
*버전: 1.0.0*
*상태: ✅ 운영 중*
