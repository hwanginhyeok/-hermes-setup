---
name: hih-design-fix
category: ui-ux
description: 기존 UI/UX 디자인 수정 및 개改善 스킬. 시각적 문제 분석, 사용성 개선, 반응형/접근성 수정.
tags: [design, ui, ux, frontend, css, accessibility]
---

# hih-design-fix

기존 UI/UX 디자인 수정 및 개선 스킬.

## 언제 사용?

- 기존 페이지/컴포넌트의 디자인 문제 발견 시
- 사용자 피드백 반영으로 수정 필요 시
- 시각적 일관성, 간격, 색상, 레이아웃 개선 시
- 접근성, 반응형 이슈 수정 시

## 절차

### STEP 1 - 현황 파악

1. **현재 디자인 캡처**
   - `browser_navigate`로 페이지 접속
   - `browser_vision`으로 현재 UI 스캔

2. **문제점 분석**
   - 레이아웃 간격 (margin/padding 불균형)
   - 색상 대비, 폰트 사이즈
   - 반응형 동작 (모바일/태블릿)
   - 접근성 (WCAG 기준)

### STEP 2 - 개선 방향 수립

1. **디자인 원칙 확인**
   - 프로젝트의 디자인 시스템 참조 (styleguide, theme)
   - 브랜드 가이드라인 체크

2. **개선 항목 우선순위**
   - 사용자 경험에 큰 영향 → 우선
   - 시각적 미세 조정 → 나중

### STEP 3 - 수정 적용

1. **코드 수정**
   - CSS/Styled Components/Tailwind 수정
   - 컴포넌트 props 조정
   - 반응형 미디어 쿼리 추가

2. **실시간 프리뷰**
   - `browser_vision`으로 수정 후 결과 확인
   - Before/After 비교

### STEP 4 - 검증

1. **교차 브라우저 테스트**
   - Chrome, Firefox, Safari 렌더링 확인

2. **반응형 체크**
   - 모바일 (375px), 태블릿 (768px), 데스크톱 (1440px)

3. **접근성 체크**
   - 색상 대비 4.5:1 이상
   - 키보드 네비게이션
   - 스크린 리더 테스트

### STEP 5 - 3자 리뷰 (hih-dual 통합)

**참고**: 디자인 수정 후 3자 리뷰 진행 권장

1. **리뷰 발사**
   - hih-dual 스킬 호출 (builder + reviewer + PM)
   - GLM reviewer가 시각적 문제 비판적 분석
   - PM 검증: 거짓 우려 제거

2. **리뷰 기준**
   - 레이아웃 간격 (margin/padding)
   - 색상 대비 (WCAG 4.5:1)
   - 반응형 동작
   - 접근성 (keyboard, screen reader)

3. **리뷰 후 처리**
   - CRITICAL 항목: 즉시 수정
   - INFORMATIONAL 항목: 우선순위 판단
   - OK 항목: 그대로 유지

**사용 예**:
```bash
# 디자인 수정 후
/hih-dual "디자인 수정 리뷰 - 레이아웃 간격, 색상 대비 확인"
```

### STEP 5 - 3자 리뷰 (hih-dual 통합)

**참고**: 디자인 수정 후 3자 리뷰 진행 권장

**모델**:
- builder: **Opus 4.8** (최신)
- reviewer: **GLM 5.0** (최신)
- PM: 사용자 검증

1. **리뷰 발사**
   - hih-dual 스킬 호출 (builder + reviewer + PM)
   - GLM 5.0 reviewer가 시각적 문제 비판적 분석
   - PM 검증: 거짓 우려 제거

2. **리뷰 기준**
   - 레이아웃 간격 (margin/padding)
   - 색상 대비 (WCAG 4.5:1)
   - 반응형 동작
   - 접근성 (keyboard, screen reader)

3. **리뷰 후 처리**
   - CRITICAL 항목: 즉시 수정
   - INFORMATIONAL 항목: 우선순위 판단
   - OK 항목: 그대로 유지

**사용 예**:
```bash
# 디자인 수정 후
/hih-dual "디자인 수정 리뷰 - 레이아웃 간격, 색상 대비 확인"
```

### STEP 6 - 문서화

1. **수정 내역 기록**
   - CLAUDE.md의 DIFFICULTY.md나 CHANGELOG에 기록
   - 수정 전후 스크린샷 저장

## 핵심 원칙

- **최소 변경**: 필요한 부분만 수정, 과잉 디자인 금지
- **일관성**: 기존 디자인 시스템과 통합 유지
- **사용자 중심**: 미학보다 사용성 우선
- **반복 가능**: 동일 이슈 재발 방지를 위한 패턴화

## 피트폴

### 스킬 발견/사용 어려움
- **스킬 위치**: 새 스킬은 `~/.hermes/skills/`에 생성됨
  - 사용자가 사용자의 프로젝트 `.claude/skills/` 심링크를 찾을 수도 있음
  - 전역 스킬을 먼저 확인: `skills_list`
  - 스킬 패스 확인: `skill_view(name='skill-name')`
- **경로 혼선**: WSL 환경에서 프로젝트 경로 vs 마운트 경로 혼동 주의
  - `~/project-name` vs `/mnt/c/Users/...`
  - `pwd`로 현재 위치 확인 필요

### OAuth/인증 설정
- **redirect_uri**: WSL에서는 `http://localhost:3000` 권장 (localhost:1 포트 충돌 가능)
- **scope 파라미터**: 여러 스코프를 `+`로 연결할 때 URL 길이 주의
- **에러 분석**: OAuth 실패 시 URL 스코프 파싱 오류 확인 먼저

### 문서 정리
- **docs/plans/ vs .claude/**:
  - `docs/plans/`: 프로젝트 계획 상세 문서
  - `.claude/`: 현재 세션용 스킬/규칙
  - 각 목적이 다르므로 섞지 말 것

---

## 도구

이 스킬을 호출하면 다음 단계들이 **자동으로 순차 실행**됩니다:

### 수정 모드
```
hih-design-fix 호출
  ↓
1. 현재 상태 스캔 (browser_navigate + browser_vision)
  ↓
2. 문제점 자동 분석
  ↓
3. 수정 방안 수립
  ↓
4. 코드 자동 수정 (patch)
  ↓
5. 수정 후 자동 검증 (browser_vision)
  ↓
6. Before/After 비교 리포트
```

**사용법:**
```bash
# 기본 수정
/hih-design-fix

# 특정 영역만 수정
/hih-design-fix --scope header

# 접근성만 수정
/hih-design-fix --focus accessibility
```

## 내부적으로 사용하는 도구

이 스킬은 다음 도구들을 **자동으로 순차 사용**합니다:
- `browser_navigate` - 페이지 접속
- `browser_vision` - UI 스캔 및 Before/After 비교
- `read_file` - 코드 읽기
- `patch` - 파일 편집
- `terminal` - 스타일 검증

## 예시

```bash
# 1. 페이지 접속 및 문제 확인
browser_navigate("http://localhost:3000/dashboard")
browser_vision("레이아웃 간격 불균형, 색상 대비 낮은 곳 찾아줘")

# 2. 코드 수정
patch(path="app/components/Dashboard.tsx", ...)

# 3. 결과 확인
browser_vision("수정 후 간격, 색상 개선되었는지 확인")
```

## 관련 스킬

- `hih-design-new` - 새로운 디자인 생성
- `gstack-design-review` - 시각적 QA
- `gstack-design-shotgun` - 여러 디자인 변형 생성

---

**Remember**: 디자인 수정은 "예쁘게"가 아니라 "잘 쓰게"가 목표다.
