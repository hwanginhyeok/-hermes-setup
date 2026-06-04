# 간단한 스킬 작성 가이드

## 핵심 원칙

### 1. 스킬은 간단해야 함

**불필요하게 복잡한 스킬 안 됨**

❌ **피해야 하는 것:**
- 7단계 이상 (bot-health-check.md는 7단계)
- 100줄 이상
- 복잡한 flowchart
- 너무 많은 예외 처리

✅ **목표:**
- 3~5단계 이내
- 50줄 이내
- 명확한 트리거만
- 간결한 판단 규칙

### 2. 중복 피하기

**이미 있는 것을 다시 만들지 말 것:**

| 이미 있는 것 | 사용하는 스킬 |
|-----------|--------------|
| 코드 리뷰 | `/review`, `/codex`, `/hih-glm` |
| 디자인 수정 | `/hih-design-fix`, `gstack-design-review` |
| 디자인 생성 | `/hih-design-new`, `gstack-design-shotgun` |
| 디버깅/조사 | `/investigate`, `gstack-investigate` |
| 브라우징 | `/gstack-browse` |

### 3. gstack 스킬 활용

**넓은 카테고리는 gstack으로:**

| 카테고리 | gstack 스킬 |
|---------|-----------|
| 코드 리뷰 | `/gstack-review` |
| 디자인 | `/gstack-design-consultation`, `/gstack-design-review` |
| QA 테스트 | `/gstack-qa` |
| 브라우징 | `/gstack-browse` |
| 배포 | `/gstack-land-and-deploy` |
| health check | `/gstack-health` |

### 4. 에이전트/agents/ 삭제

**에이전트는 안 씀:**

- agents/는 4월 이전 구버전
- gstack 스킬이 더 강력함
- 유지보수만 늘어남

### 5. .claude/ 최소화

**유지하는 것만:**

```
.claude/
├── rules/           # 코딩/보안/테스트 규칙 (간단한 것만)
├── skills/          # 프로젝트별 스킬 (3~5단계, 50줄 이내)
└── settings.*       # 설정
```

**삭제한 것:**
- agents/ - gstack이 있음
- 100줄+ 스킬 - 너무 복잡
- DEPRECATED 스킬 - outdated 것

## 스킬 작성 템플릿

### 간단한 스킬

```markdown
---
name: simple-skill
category: 프로젝트-카테고리
description: 간단한 설명 (1줄)
tags: [키워드1, 키워드2]
---

# 스킬 이름

## 목적

1~2문장 설명

## 트리거

"키워드1", "키워드2"가 나오면 실행

## 실행 순서

### STEP 1
명령

### STEP 2
명령

## 판단 규칙

| 상황 | 행동 |
|-------|--------|
| 상황1 | 액션1 |
| 상황2 | 액션2 |

## 주의

- 중요한 주의
```

## 양호한 스킬 예시

### ✅ 좋은 예시 (50줄 이내)

```markdown
# service-test.md (109줄 - 너무 긺)
```

→ 5단계로 간소화:

```markdown
# service-test (간소화)

## 트리거
"서비스 시작", "E2E 테스트"

## 실행

### STEP 1: 서비스 확인
systemctl --user status blog-api blog-worker

### STEP 2: 테스트 실행
python main.py --run-once --dry-run

### STEP 3: 로그 확인
journalctl --user -u blog-worker -n 10

## 판단

| 결과 | 행동 |
|-----|-------|
| 정상 | 요약 |
| 실패 | 에러 로그 확인 |
```

## 실제 사례

### 삭제한 것

1. **bot-health-check.md (127줄)**
   - ❌ 7단계, 너무 복잡
   - ✅ blog-telegram는 disabled라 불필요
   - ✅ 댓글 봇은 자동으로 돌아가므로 상태 확인 불필요

2. **cookie-refresh.md (138줄)**
   - ❌ 사용자가 직접 브라우저에서 리프레시
   - ✅ 불필요

3. **agents/ (4개 파일)**
   - ❌ gstack 스킬이 더 강력함
   - ✅ 중복 제거

### 유지하는 것 (간단한 것)

1. **selector-debug.md (129줄)**
   - ⚠️ 너무 긺, 간소화 필요
   - 셀렉터 디버깅은 여전히 필요

2. **service-test.md (109줄)**
   - ⚠️ 너무 긺, 간소화 필요
   - 서비스 테스트는 여전히 필요

## 결론

**간단한 스킬이 좋음:**
- 3~5단계 이내
- 50줄 이내
- 명확한 트리거
- 중복 피하기
- gstack 활용
