---
name: web-pipeline
description: |
  웹 프로젝트 풀사이클 파이프라인. office-hours → ceo → design → eng → (구현) → review → qa → ship → canary 까지 고정 플로우.
  "웹 파이프라인", "웹 개발 시작", "기능 만들자" 등 웹 프로젝트 시작 시 호출.
category: gstack
triggers:
  - 웹 파이프라인
  - 웹 개발 시작
  - 기능 만들자
  - web pipeline
---

# 웹 프로젝트 풀사이클 파이프라인

## gstack 스킬 로드 방법

Hermes에서 gstack 원본 스킬을 읽으려면 `skill_view(references/)` 대신 직접 읽기:

```python
# skill_view references 심볼릭 링크는 보안 제약으로 차단됨
# 대신 원본 직접 읽기
read_file("/home/window11/.claude/skills/gstack/{스킬명}/SKILL.md")
```

## Office Hours 조기 종료 규칙

office-hours Q1 답변에서 아래 신호가 나오면 **파이프라인을 멈추고 방향 재조정**:
- "아무도 안 씀" + "근데 쓸 거임" → 수요 없는 기능. 댓글봇 등 실사용 기능 먼저.
- "댓글봇이 우선" → 사용자 스스로 우선순위 재확인. 체험단 등 부수 기능은 PREPARED로.
- 단, "구현은 됐고 개선의 문제" → 계속 진행. 기존 구현 기준으로 질문 맞춤형으로 바꿀 것.

## 고정 플로우

```
Phase 0: context-restore  (이전 세션 이어하기)
    ↓
Phase 1: office-hours     (아이디어 검증 — 6가지 질문)
    ↓
Phase 2: ceo-review       (10-star 제품 찾기, 전제 도전)
    ↓
Phase 3: design-review    (UI/UX 있으면 0~10점 평가. API/백엔드만이면 SKIP)
    ↓
Phase 4: eng-review       (아키텍처, 데이터 흐름, 엣지케이스, 테스트 커버리지 확정)
    ↓
Phase 5: IMPLEMENT        (직접 구현. gstack 스킬 사용 안 함)
    ↓
Phase 5.5: codex-review  (Codex 두 번째 의견 + challenge 모드)
    ↓
Phase 6: review           (PR 리뷰 — Claude + Codex 결과 참조)
    ↓
Phase 7: qa               (실제 브라우저 열어서 버그 찾기 + 수정)
    ↓
Phase 8: ship             (버전업 + 체인지로그 + push + PR 생성)
    ↓
Phase 9: land-and-deploy  (PR 머지 → CI 대기 → 배포 → 건강 확인)
    ↓
Phase 10: canary          (배포 후 모니터링 — 에러/성능 회귀 감시)
    ↓
Phase 11: context-save    (다음 세션을 위해 상태 저장)
```

## 실행 규칙

### 각 Phase 시작 시
1. `skill_view(name='gstack-{해당스킬}')` 로 원본 gstack SKILL.md 로드
2. 프롬프트에 맞게 실행
3. 결과를 사용자에게 요약
4. **다음 Phase 진행 여부 확인** — 사용자가 STOP 하면 거기서 context-save 후 종료

### Phase 진행 판단
| 조건 | 액션 |
|------|------|
| 사용자가 "다음" / "계속" | 다음 Phase 자동 진행 |
| 사용자가 "여기까지만" / "STOP" | context-save 후 종료 |
| 사용자가 특정 Phase 건너뛰기 요청 | 해당 Phase SKIP 표시 후 다음으로 |
| 이전 Phase 결과가 부족 | 재실행 or RE-DIRECT |

### Phase 3 (design-review) SKIP 조건
- 백엔드 API만 있는 프로젝트
- DB 마이그레이션/스키마 변경
- 내부 로직 리팩토링 (UI 변화 없음)
- 사용자가 명시적으로 스킵 요청

### Phase 5 (IMPLEMENT) 특별 규칙
- 이 Phase에서만 코드 직접 작성
- gstack 스킬 사용 안 함 (직접 구현)
- 구현 완료 후 자동으로 Phase 6(review) 진입

## 단축 플로우

상황에 따라 중간 Phase 생략 가능:

|| 상황 | 플로우 |
||------|--------|
|| **버그 수정** | investigate → (수정) → review → qa → ship |
|| **UI 수정만** | design-review → (수정) → qa → ship |
|| **배포만** | ship → land-and-deploy → canary |
|| **문서 업데이트** | document-release |
|| **빠른 핫픽스** | (수정) → qa → ship |
|| **이어서 작업** | context-restore → (구현 계속) → review → qa → ship |

### Phase 5.5 (codex-review) 조건
- Phase 5 구현 완료 후 자동 진행
- `codex` 스킬의 challenge 모드로 취약점 공격
- review 단계에서 Codex 결과를 참조하여 검토

## Office Hours 실전 규칙

- **"아무도 안 씀 / 댓글봇이 우선"** → office-hours에서 바로 중단 판정. 기존 구현 개선이면 Q1 수요 질문 스킵하고 "현재 뭐가 제일 안 돼?" 부터 시작
- **기존 구현 있는 경우** → 코드 직접 읽어서 현황 파악 후 CEO Review로 넘어감. 질문 6개 전부 돌 필요 없음 — 핵심 3개로 압축
- **CEO Review 핵심 3가지**: (1) 10-star 버전 확인 (2) 지금 막힌 진짜 이유 (3) 임팩트 큰 범위 A/B/C 제시

## Phase 체크리스트 출력 포맷

각 Phase 완료 시:

```
## Phase N: {스킬명} — ✅ 완료 / ⚠️ 부분 / ❌ 실패

### 핵심 결과
- (결과 요약 1~3줄)

### 다음 Phase
- Phase N+1: {스킬명} — {한줄 설명}
- 진행하시겠습니까?
```

## 주의사항
- office-hours 없이 바로 구현부터 들어가지 않기 (최소 Phase 1은 거칠 것)
- qa 없이 ship 금지 (최소 Phase 7 필수)
- canary 없이 배포 완료로 간주하지 않기
- 각 Phase에서 gstack 원본 스킬 로드 후 그 규칙을 따를 것
