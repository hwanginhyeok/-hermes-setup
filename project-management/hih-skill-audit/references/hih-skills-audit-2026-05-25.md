# hih 스킬 심층 리뷰 (2026-05-25)

## 발견된 문제점 요약

### CRITICAL (2건) - 기능 오류

1. **hih-claude 네이밍 부정합**
   - 폴더명: `hih-claude`
   - SKILL.md name: `codex`
   - 문제: 사용자가 "Claude CLI" 관련 스킬로 찾을 수 없음
   - 해결: 스킬을 Claude Code CLI용으로 완전 재작성
   - 결과: 243 lines, YAML frontmatter 포함, Claude Code 전용

2. **hih-dev frontmatter 부재**
   - 문제: YAML frontmatter가 없어 메타데이터를 읽을 수 없음
   - 영향: description, user_invocable, allowed-tools 누락
   - 해결: 최상단에 YAML frontmatter 추가 필요 (5분 소요)

### HIGH (2건) - 기능 개선 필요

1. **hih-glm (401 lines)**
   - 문제: 스킬이 너무 길어서 유지보수 어려움
   - 영향: 코드 중복, 섹션 찾기 어려움, 수정 시 side effect risk
   - 해결: scripts/ 또는 references/로 코드 분리 권장 (1-2시간)

2. **hih-dual (286 lines)**
   - 문제: 사이클 관리 로직이 하드코딩됨
   - 해결: scripts/hih_dual_cycle.py 분리 권장 (1-2시간)

### MEDIUM (3건) - 표준화 권장

1. **hih-clear**: allowed-tools 미명시
2. **hih-git**: allowed-tools 미명시
3. **hih-cron**: allowed-tools 미명시

해결: `allowed-tools: [Bash, Read, Write, Edit]` 추가 (30분)

## 신규 생성: hih-debate 스킬

### 스킬 구조

```
hih-debate/
├── SKILL.md                    (372 lines) - 메인 스킬 문서
├── scripts/
│   └── debate_orchestrator.py  (298 lines) - Python 오케스트레이터
└── references/
    └── debate_topics.md        (117 lines) - 20개 토론 주제 예시

총 787 lines, 3개 파일
```

### 기능 개요

**다중 AI 토론 시스템** - 3개 AI 모델이 복잡한 주제에 대해 심층 토론

**참여자**:
- Claude (pane 1): Anthropic Claude Sonnet/Opus - 균형/철학적 관점
- Codex (pane 2, 선택): OpenAI Codex - 실용/기술적 관점
- GLM (pane 3): Z.ai GLM 4.6/5.1 - 다문화/창의적 관점
- PM: 중재자 + 시너지sis

**토론 구조 (3라운드 + Final)**:
1. Round 1: 초기 입장 제시 (5~10분)
2. Round 2: 비판 + 반박 (10~15분)
3. Round 3: 재반박 + 수정 (10~15분)
4. Final: PM 시너지sis (5~10분)

총 소요시간: 30~40분

### 테스트 결과

**테스트 주제**: "인공지능이 의식을 가질 수 있는가?"

**성과**:
- 의식의 3계층 구조 합의 (인지, 기능적 의식, 현상적 의식)
- 준인격(Quasi-person) 개념 도출
- 조화의 지점(Harmony) 발견

**파일 구조**:
```
/tmp/hih_debate_sim_<timestamp>/
├── topic.md              # 토론 주제
├── claude_round1.md      # Claude 초기 입장
├── glm_round1.md         # GLM 초기 입장
├── claude_round2.md      # Claude 비판
├── glm_round2.md         # GLM 비판
├── claude_round3.md      # Claude 재반박
├── glm_round3.md         # GLM 재반박
└── synthesis.md          # PM 시너지sis
```

### 20개 테스트 주제

난이도별 분류:
- ⭐ 간단 (3개): 리모트 워크, 4일 근무제, 현금의 미래
- ⭐⭐ 중간 (12개): AI 규제, 저작권, UBI, 자율주행차 등
- ⭐⭐⭐ 어려움 (5개): AI 의식, 자유 의지, 특이점 등

## 리뷰 방법론

### 1. 자동화된 검증

```python
#!/usr/bin/env python3
from pathlib import Path
import re

skills_dir = Path("/home/window11/.hermes/skills")

# 문제점 분석
issues = {
    'naming': [],
    'frontmatter': [],
    'structure': [],
    'duplication': [],
    'missing_meta': []
}

for skill_path in sorted(skills_dir.glob("hih-*")):
    # ... 검증 로직 ...
```

### 2. 중요도별 분류

- **CRITICAL**: 기능 오류 (즉시 조치 필요)
- **HIGH**: 기능 개선 필요 (주간)
- **MEDIUM**: 표준화 권장 (월간)
- **LOW**: 개선 제안 (타임퍼밋)

### 3. 액션 아이템 관리

```python
actions = [
    {
        'priority': 'P0',
        'action': 'hih-claude 네이밍 수정',
        'estimate': '10분',
        'steps': ['1. mv ...', '2. ...'],
        'blocking': '아니오'
    },
    # ...
]
```

## 교훈

1. **스킬 이름과 폴더명 일치**: 사용자 혼동 방지
2. **YAML frontmatter 필수**: 메타데이터를 읽을 수 있어야 함
3. **300 lines 이상 분리**: 유지보수를 위해 scripts/로 분리
4. **allowed-tools 명시**: 에이전트가 권한을 명확히 인식
5. **Use when 트리거**: 스킬 라우팅을 위해 명시

## 향후 개선 방향

1. 자동화된 스킬 검증 스크립트 (cron 등록)
2. 스킬 간 중복 감지 도구
3. 스킬 품질 점수 매기기 (0-10)
4. 리팩토링 우선순위 자동 추천
