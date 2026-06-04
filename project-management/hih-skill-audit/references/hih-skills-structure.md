# hih 스킬 라이브러리 구조

## 카테고리별 분류

### 세션 관리 (4개)
- `hih-task`: 태스크 브리핑 + 인터랙티브 관리
- `hih-clear`: 세션 종료 루틴
- `hih-all-clear`: 전 프로젝트 세션 일괄 정리
- `hih-vnc`: VNC 연결 상태 확인

### 개발 워크플로우 (4개)
- `hih-dev`: 기능 개발 풀 파이프라인
- `hih-dual`: builder/reviewer 사이클
- `hih-glm`: GLM 외부 리뷰어
- `hih-claude`: Claude Code CLI 위임

### Git (1개)
- `hih-git`: 전체 프로젝트 git 상태 브리핑

### Cron/자동화 (1개)
- `hih-cron`: cron 점검 + 추가/수정

### 사고 프레임워크 (2개)
- `hih-fp`: 제1원칙 + 머스크 5단계
- `hih-ontology`: 온톨로지적 사고

### 지식 관리 (1개)
- `hih-difficulty`: DIFFICULTY.md 관리

## 저장소 구조

### 로컬 스킬 (~/.hermes/skills/)
- `hih-all-clear`
- `hih-claude`
- `hih-cron`
- `hih-dev`
- `hih-dual`
- `hih-glm`

### 심링크 스킬 (→ ~/hih-skills/)
- `hih-clear` → `/home/window11/hih-skills/hih-clear`
- `hih-difficulty` → `/home/window11/hih-skills/hih-difficulty`
- `hih-fp` → `/home/window11/hih-skills/hih-fp`
- `hih-git` → `/home/window11/hih-skills/hih-git`
- `hih-ontology` → `/home/window11/hih-skills/hih-ontology`
- `hih-task` → `/home/window11/hih-skills/hih-task`
- `hih-vnc` → `/home/window11/hih-skills/hih-vnc`

## 스킬 메타데이터 표준

### 필수 필드
```yaml
---
name: hih-xxx
description: |
  간단한 설명. Use when: "키워드1", "키워드2"
user_invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---
```

### 선택 필드
```yaml
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
```

## 스킬 길이 가이드라인

| 길이 | 상태 | 조치 |
|------|------|------|
| < 100 lines | 🟢 적정 | - |
| 100-300 lines | 🟡 주의 | 섹션 검토 |
| > 300 lines | 🔴 리팩토링 | scripts/ 분리 |

## 관련 문서

- SSOT: `~/project-manager/global-rules/ssot.md`
- 스킬 작성: `~/.hermes/skills/software-development/hermes-agent-skill-authoring/SKILL.md`
- hih 스킬 관리: `~/project-manager/global-rules/llm-architecture.md`
