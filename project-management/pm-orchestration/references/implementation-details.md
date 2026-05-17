# PM 최적화 구현 상세

## 개요
2026-05-15에 PM 시스템의 운영 효율을 개선하기 위해 3가지 핵심 자동화 기능을 추가했습니다.
PM이 READ-REVIEW-RE-DIRECT-VERIFY 순환을 더 빠르게 수행할 수 있도록 설계되었습니다.

---

## 1. 태스크 요약 자동 동기화 (`sync_task_summary.py`)

### 문제
자식 프로젝트가 CURRENT_TASK.md를 업데이트해도 TASK.md 요약이 수동으로 갱신됨

### 해결
매일 자동으로 전체 프로젝트의 태스크 현황을 수집하고 요약을 갱신

### 기능
- CURRENT/PREPARED/FINISHED 태스크 수 자동 카운트
- Blocked 태스크 수 자동 추적
- TASK.md 요약 섹션 자동 업데이트
- 프로젝트별 개별 동기화 가능 (`--project` 옵션)

### 사용
```bash
# 전체 동기화
pm sync-summary

# 특정 프로젝트만
pm sync-summary --project 인성이
```

### Cron
매일 00:00 실행

---

## 2. Cron 건강 모니터링 (`cron_health_monitor.py`)

### 문제
be-a-studio 등 cron이 간헐적으로 segfault로 멈추는데 PM이 자동 감지 못 함

### 해결
각 cron 로그의 마지막 타임스탬프를 확인하여 24h+ 멈춘 cron을 자동 감지

### 기능
- 8개 주요 cron 로그 모니터링 (주식부자, PM, be-a-studio)
- 마지막 실행 시간 기준 예상 간격 대비 지연 감지
- CRITICAL/WARNING 우선순위 분류
- 텔레그램 알림 옵션

### 사용
```bash
# 기본 확인
pm cron-health

# 텔레그램 알림 전송
pm cron-health --telegram
```

### 모니터링 대상
| Cron 이름 | 로그 경로 | 예상 간격 | 중요도 |
|-----------|----------|----------|--------|
| 주식부자 시황 수집 (KR) | ~/.pm_logs/news_kr.log | 2시간 | CRITICAL |
| 주식부자 시황 수집 (US) | ~/.pm_logs/news_us.log | 2시간 | CRITICAL |
| 주식부자 아침 브리핑 | ~/stock/logs/briefing_morning.log | 36시간 | CRITICAL |
| 주식부자 저녁 브리핑 | ~/stock/logs/briefing_evening.log | 36시간 | CRITICAL |
| PM MD 크기 체크 | ~/.pm_logs/md_size_check.log | 36시간 | WARNING |
| PM WSL 백업 | ~/.pm_logs/wsl_backup.log | 36시간 | CRITICAL |
| be-a-studio 일간 작업 | ~/.pm_logs/be_a_studio_daily.log | 36시간 | CRITICAL |
| be-a-studio 클린업 | ~/.pm_logs/bea_cleanup.log | 36시간 | WARNING |

### Cron
- 매 6시간 모니터링 (00:00, 06:00, 12:00, 18:00)
- 매일 09:00 텔레그램 알림

---

## 3. 블로커 추적 및 분석 (`blocked_tracker.py`)

### 문제
전체 블로커 현황을 한눈에 보기 어렵고, 해소 우선순위 판단이 어려움

### 해결
전체 프로젝트의 블로커를 수집하고, 우선순위별 정렬 + 의존성 체인 분석

### 기능
- 전체 프로젝트 블로커 자동 수집 (CURRENT_TASK.md blocked 필드)
- 우선순위 자동 분류 (P1: 자동화 핵심, P2: 일반, P3: 사용자 결정/외부 의존)
- 의존성 체인 추론 (예: icloud-blog ← 인성이)
- Graphviz DOT 파일 생성 (의존성 시각화)

### 사용
```bash
# 기본 보고서
pm blocked

# 우선순위 P1만 표시
pm blocked --priority

# Graphviz DOT 생성
pm blocked --graphviz
```

### 우선순위 분류 규칙
- **P1**: 자동화 관련 → 자동화 핵심 기능 정체
- **P2**: 일반 블로커 → 이번 주 내 해소 권장
- **P3**: 사용자 결정 대기 또는 외부 의존 (HW, 네트워크 등) → 기다림

### 의존성 체인 분석
- icloud-blog → 인성이 우선
- be-a-studio BAS-57 → 사용자 결정 대기

---

## PM CLI 통합

새로운 서브커맨드가 pm.py에 통합되었습니다:

```bash
pm sync-summary [--project NAME]     # 태스크 요약 동기화
pm cron-health [--telegram]          # Cron 건강 모니터링
pm blocked [--graphviz] [--priority] # 블로커 추적 및 분석
```

---

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

## 파일 구조

```
project-manager/
├── scripts/
│   ├── sync_task_summary.py      # 태스크 요약 자동 동기화 (4538 bytes)
│   ├── cron_health_monitor.py    # Cron 건강 모니터링 (5838 bytes)
│   └── blocked_tracker.py        # 블로커 추적 및 분석 (7531 bytes)
├── cron/
│   └── pm_optimization.cron      # PM 최적화 cron 설정
├── docs/systems/
│   └── pm-optimization-report.md # 전체 보고서
└── pm.py                          # CLI (신규 서브커맨드 추가)
```

---

## Cron 스케줄 등록 완료

/etc/crontab에 등록된 스케줄:

| 시간 | 스크립트 | 용도 |
|------|----------|------|
| 00:00 매일 | sync_task_summary.py | 태스크 요약 동기화 |
| 00:00, 06:00, 12:00, 18:00 | cron_health_monitor.py | Cron 건강 모니터링 |
| 09:00 매일 | cron_health_monitor.py --telegram | Cron 건강 + 텔레그램 알림 |

---

## Git 커밋 기록

### 커밋 1: PM optimization: add sync-summary, cron-health, blocked commands
```
1. sync_task_summary.py - 태스크 요약 자동 동기화
2. cron_health_monitor.py - Cron 건강 모니터링
3. blocked_tracker.py - 블로커 추적 및 분석
```

### 커밋 2: PM optimization 완료: cron 등록 + 문서화
```
- pm_optimization.cron: 3개 cron 등록
- pm-optimization-report.md: 전체 보고서 작성
```

---

## 사용 예시

### 아침 루틴 (PM 세션 시작 시)
```bash
pm status          # 전체 현황
pm blocked         # 블로커 확인
pm cron-health     # Cron 건강 확인
pm sync-summary    # 태스크 요약 동기화
```

### 주간 리뷰
```bash
pm blocked --priority      # P1만 집중
pm blocked --graphviz      # 의존성 그래프 생성
cd ~/project-manager/docs/systems
dot -Tpng blockers.dot -o blockers.png
```

---

## 로그 파일

모든 로그는 `~/.pm_logs/`에 저장됩니다:

- `sync_summary.log` - 태스크 요약 동기화 로그
- `cron_health.log` - Cron 건강 모니터링 로그
- `cron_health_alert.log` - Cron 건강 + 텔레그램 알림 로그

---

## 다음 단계 (향후 개선)

1. **지시-실행 갭 자동 검증**: 커밋 메시지에서 태스크 ID 파싱 → 관련 파일 hunk 추출 → PM이 리뷰
2. **의존성 그래프 시각화**: PREPARED_TASK의 depends로 DOT graph 생성 → 블로커 체인 시각화
3. **PM 대시보드 웹 인터페이스**: 현재 TUI지만, 웹에서 접근하면 모바일에서도 PM 가능

---

*생성일: 2026-05-15*
*버전: 1.0*
*상태: ✅ 운영 중*
