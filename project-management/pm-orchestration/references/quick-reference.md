# PM 명령어 퀵 레퍼런스

## 기본 명령어

### 현황 확인
```bash
pm status          # 통합 현황 대시보드
pm health          # 디렉토리 건강 진단
pm backup          # 백업 현황
pm tasks           # 통합 태스크 목록
pm validate        # 설정 + 태스크 + 심링크 검증
pm sessions        # AI 세션별 모델 + 상태
```

### 신규 최적화 명령어
```bash
pm sync-summary [--project NAME]     # 태스크 요약 동기화
pm cron-health [--telegram]          # Cron 건강 모니터링
pm blocked [--graphviz] [--priority] # 블로커 추적 및 분석
```

---

## 아침 루틴

```bash
pm status
pm blocked
pm cron-health
pm sync-summary
```

---

## 주간 리뷰

```bash
pm blocked --graphviz
cd ~/project-manager/docs/systems
dot -Tpng blockers.dot -o blockers.png
pm blocked --priority
```

---

## 블로커 우선순위

- **P1**: 자동화 핵심 기능 정체 → 즉시 해소
- **P2**: 일반 블로커 → 이번 주 내 해소 권장
- **P3**: 사용자 결정/외부 의존 → 기다림

---

## 관련 스킬

- `/hih-task` - 태스크 브리핑 + 관리
- `/hih-clear` - 세션 종료 정리 루틴
- `/hih-git` - 전체 프로젝트 git 브리핑
- `/hih-cron` - cron 추가/수정
- `parallel-worker-pool` - tmux 워커 풀 병렬 작업 관리
