---
name: hih-design-new
category: ui-ux
description: 새로운 UI/UX 디자인 생성 스킬. 컴포넌트, 페이지, 전체 앱 디자인을 처음부터 만들 때 사용.
tags: [design, ui, ux, frontend, prototyping, wireframe]
---

# hih-design-new

새로운 UI/UX 디자인 생성 스킬.

## 언제 사용?

- 새로운 페이지/컴포넌트 디자인 시작 시
- 프로토타입 빠르게 생성 시
- 와이어프레임에서 고피델리티 디자인까지
- A/B 테스트용 여러 디자인 변형 생성 시

## 절차

### STEP 1 - 요구사항 명확화

1. **목적 정의**
   - 해결할 문제: 무엇을 개선?
   - 타겟 사용자: 누구를 위한 디자인?
   - 핵심 기능: 무엇을 해야 하나?

2. **제약 조건 확인**
   - 기술 스택 (React, Vue, Next.js 등)
   - 디자인 시스템 (기존 styleguide, theme)
   - 반응형 요구사항
   - 접근성 표준 (WCAG 2.1 AA)

### STEP 2 - 리서치 & 레퍼런스

1. **벤치마킹**
   - 경쟁사/유사 제품 분석
   - 트렌드 디자인 패턴 참조

2. **사용자 시나리오**
   - 사용자 flow 매핑
   - 핵심 사용 경험 정의

### STEP 3 - 와이어프레임 (low-fi)

1. **레이아웃 구조**
   - 정보 아키텍처
   - 컴포넌트 계층 구조
   - 콘텐츠 우선순위

2. **도구**
   - `pretext` 스킬로 빠른 프로토타입
   - 또는 `sketch` 스킬으로 2~3개 변형 생성

### STEP 4 - 비주얼 디자인 (mid-fi → hi-fi)

1. **스타일 정의**
   - 색상 팔레트 (primary, secondary, semantic)
   - 타이포그래피 (font family, scale, line-height)
   - 간격 시스템 (4px/8px grid)
   - 컴포넌트 variant (default, hover, active, disabled)

2. **디자인 생성**
   - `gstack-design-shotgun`으로 여러 옵션 생성
   - 또는 직접 코드로 구현

3. **반응형 설계**
   - Mobile-first 접근
   - Breakpoint 정의 (375px / 768px / 1024px / 1440px)

### STEP 5 - 프로토타입 & 테스트

1. **인터랙티브 프로토타입**
   - `pretext`로 클릭 가능한 프로토타입 생성
   - 또는 `browser`로 실제 구현 후 테스트

2. **사용성 테스트**
   - 핵심 flow 수행 가능?
   - 예상치 못한 friction 포인트?

### STEP 6 - 구현 준비

1. **디자인 사양서**
   - 컴포넌트 명세서 (props, state, variants)
   - 스타일 가이드 (color, typography, spacing)
   - 아이콘/이미지 리소스

2. **개발 전달**
   - Figma → Code export (또는 직접 코드 작성)
   - Storybook/Chromatic 등에 컴포넌트 등록

## 핵심 원칙

- **사용자 중심**: 예쁘게보다 잘 쓰게
- **간결성**: 최소 요소로 최대 효과
- **일관성**: 디자인 시스템 준수
- **접근성**: 모든 사용자가 사용 가능

## ⚠️ 자동화 한계 (2026-05-20 수정)

**중요**: 이 스킬은 다른 스킬들을 자동으로 호출하지 않습니다.

사용자가 기대한 것: `/hih-design-new` 한 번으로 pretext → gstack-design-shotgun → hih-design-fix 자동 실행

실제 동작: 각 스킬을 **수동으로 순서대로 호출**해야 함

## 올바른 사용법

### 빠른 프로토타입
```bash
# 1. 요구사항 정의 (사용자와 대화)

# 2. 와이어프레임 생성
/pretext

# 3. 여러 디자인 변형 생성
/gstack-design-shotgun

# 4. 선택 후 수정
/hih-design-fix
```

### 고피델리티 디자인
```bash
# 1. 요구사항 정의

# 2. 디자인 리서치
/gstack-design-consultation

# 3. 프로토타입
/pretext

# 4. Production HTML
/gstack-design-html

# 5. 최종 조정
/hih-design-fix
```

## 수동 호출이 필요한 이유

Hermes 스킬 시스템에서:
- 각 스킬은 독립적으로 실행됨
- 스킬이 다른 스킬을 자동으로 호출하려면 `delegate_task`로 구현해야 함
- 현재 구현은 수동 호출 가정

## 향후 개선 방향

메타 스킬(`design-pipeline`)을 만들어 자동화 가능:
```python
# design-pipeline 스킬 내부
def run():
    pretext()
    shotgun_result = gstack_design_shotgun()
    hih_design_fix(shotgun_result)
```

지금은 각 스킬을 순서대로 수동 호출하세요.

## 예시

```bash
# 1. 요구사항 정의 및 리서치
# (사용자와 대화)

# 2. 와이어프레임 생성
pretext
# → 간단한 HTML 프로토타입 생성

# 3. 여러 디자인 변형 생성
gstack-design-shotgun
# → 3~5개 옵션

# 4. 선택 후 수정
hih-design-fix
# → 세부 조정 및 구현
```

## 체크리스트

### STEP 1 완료 기준
- [ ] 목적, 타겟, 핵심 기능 명확
- [ ] 기술/디자인 제약 조건 확인

### STEP 2 완료 기준
- [ ] 3개 이상 레퍼런스 수집
- [ ] 사용자 시나리오 정의

### STEP 3 완료 기준
- [ ] 와이어프레임 1개 이상 생성
- [ ] 정보 아키텍처 확정

### STEP 4 완료 기준
- [ ] 스타일 시스템 정의
- [ ] 반응형 Breakpoint 정의
- [ ] 디자인 1개 이상 생성

### STEP 5 완료 기준
- [ ] 인터랙티브 프로토타입 완성
- [ ] 사용성 테스트 통과

### STEP 6 완료 기준
- [ ] 컴포넌트 명세서 작성
- [ ] 개발자 전달 준비 완료

## 관련 스킬

- `hih-design-fix` - 기존 디자인 수정
- `gstack-design-review` - 시각적 QA
- `gstack-design-consultation` - 디자인 리서치
- `pretext` - 빠른 프로토타이핑
- `sketch` - 와이어프레임 변형

---

**Remember**: 새 디자인은 "와 이거 예쁘다"가 아니라 "와 이거 잘 쓰이네"가 목표다.


## 3자 리뷰 (hih-dual)

**참고**: 디자인 생성 후 3자 리뷰 진행 권장

**모델**:
- builder: **Opus 4.8** (최신)
- reviewer: **GLM 5.0** (최신)
- PM: 사용자 검증

**리뷰 기준**:
- 레이아웃 간격 (margin/padding)
- 색상 대비 (WCAG 4.5:1)
- 반응형 동작
- 접근성 (keyboard, screen reader)

**사용 예**:
```bash
# 디자인 생성 후
/hih-dual "디자인 리뷰 - 레이아웃, 색상, 반응형 확인"
```
