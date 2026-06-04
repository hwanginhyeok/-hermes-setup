---
name: portfolio-project-analysis
description: 포트폴리오용 프로젝트 상세 분석 및 역량 추출 워크플로우
author: gothic-neon
version: 1.0.0
tags: [portfolio, project-analysis, skill-extraction, documentation]
triggers:
  - "프로젝트 분석"
  - "포트폴리오"
  - "스킬 정리"
  - "역량 추출"
---

# 포트폴리오 프로젝트 상세 분석

프로젝트를 상세 분석하여 포트폴리오 문서를 작성한 후, 역량(스킬)을 추출하는 워크플로우입니다.

## 워크플로우

### STEP 1: 프로젝트 상세 분석

**순서**: CLAUDE.md → FINISHED_TASK.md → README

**1. CLAUDE.md 읽기**
```bash
read_file ~/{project}/CLAUDE.md
```
추출 항목:
- 프로젝트 개요 (title, description)
- 핵심 기능/방향성
- Tech Stack
- 기간
- 운영 모델

**2. FINISHED_TASK.md 분석**
```bash
read_file ~/{project}/FINISHED_TASK.md
```
추출 항목:
- 완료된 주요 태스크
- 성과 지표 (건수, 시간, 효율)
- 마일스톤/성과

**3. README/URL 확인**
```bash
cat ~/{project}/.env | grep URL
cat ~/{project}/README.md
git log -1 --oneline ~/{project}
```
추출 항목:
- 배포 URL
- 마지막 커밋
- 버전

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

**원칙**:
- 프로젝트 위주의 설명 (기술/성과/URL)
- 스킬/역량 언급 X
- 구체적인 숫자/지표 포함

### STEP 3: 역량(스킬) 추출

**분석 질문**:
1. 이 프로젝트에서 어떤 역량을 사용했는가?
2. 다른 프로젝트와 공통되는 역량은?
3. 이 역량은 스킬로 정의할 수 있을까?

**역량 후보**:
- 콘텐츠 자동화 (be-a-studio)
- 데이터 분석/시각화 (stock, politics-stat)
- 봇/자동화 개발 (insung_blog, music-lab)
- API 연동/통합 (be-a-studio)
- 크론/CI/CD 관리

### STEP 4: 역량 구조화

**역량별 기준**:
- 이름: {동사 명사}
- 정의: {역량이 무엇인가}
- 프로젝트: {적용 프로젝트 목록}
- 기간: {총 경험 기간}
- 성과: {구체적인 성과}

**예시**:
```yaml
콘텐츠-자동화:
  정의: 콘텐츠를 자동으로 생성/변환/발행
  프로젝트: [be-a-studio, insung_blog, music-lab]
  기간: 2024.01 ~ 현재
  성과: 518건 발행, 3분/건 처리, 4채널 동시 발행
```

### STEP 5: 포트폴리오 문서 갱신

**추가 위치**: `src/pages/capabilities/` 또는 `docs/`

**파일 구조**:
```
src/pages/capabilities/
├── index.astro              ← 역량 목록
├── content-automation/     ← 콘텐츠 자동화
├── data-analysis/          ← 데이터 분석
└── bot-automation/         ← 봇/자동화
```

## Pitfalls

### ❌ 하지 말 것
- 프로젝트 분석 전에 스킬 정의 X
- 추상적인 스킬 설명 X
- 구체적인 지표/성과 누락 X
- URL/기간 누락 X

### ✅ 필수 항목
- 프로젝트 기간 (YYYY.MM ~ 현재)
- 핵심 기능 (2-3개)
- 기술 스택 (3-5개)
- 성과 지표 (구체적인 숫자)
- 배포 URL (있으면)

### ⚠️ 주의
- 프로젝트별 CLAUDE.md 형식이 다를 수 있음
- 일부 프로젝트는 FINISHED_TASK.md가 없을 수 있음
- URL은 .env 또는 README에서 확인 필요

## 예시

### be-a-studio 분석

**CLAUDE.md**:
- 프로젝트: Be:A Studio (SNS 통합 발행 허브)
- 채널: YouTube/X/Instagram/Naver Blog
- 역할: 채널별 포맷 변환 + 동시 발행

**FINISHED_TASK.md**:
- 완료 태스크: 130건 (2026-05월)
- 주요 성과: 518건 발행, 3분/건 처리

**프로젝트 소개 글**:
```markdown
## Be:A Studio

> Be:Analogue의 SNS 통합 발행 허브. MACROHARD Builder 콘텐츠를 4개 채널에 동시 발행하는 production engine.

### 기간
2024.01 ~ 현재

### 핵심 기능
- 채널별 포맷 자동 변환
- 텔레그램 승인 워크플로우
- 4채널 동시 발행
- 발행 후 통계 보고

### 기술 스택
- Python 3.12
- python-telegram-bot
- YouTube Data API
- X API (tweepy)
- Instagram API
- Naver Blog API

### 성과
- 518건 발행
- 3분/건 처리 시간
- 4채널 동시 발행

### URL
- [Naver Blog](https://blog.naver.com/letter_hih)
```

**역량 추출**:
- 콘텐츠 자동화 ✅
- 다채널 발행 ✅
- API 연동 ✅

## 관련 스킬

- `/hih-task` - 태스크 관리
- `/pm-orchestration` - PM 오케스트레이션
- `/writing-plans` - 문서 작성 플랜