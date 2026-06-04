---
name: 3-person-review-system
title: 3-Person Review System Architecture
description: tmux pane 기반 병렬 리뷰 시스템 - Codex + GLM + Claude 3자 리뷰, 토론, 결론 도출 패턴
tags: [Review, Quality-Assurance, Parallel-Execution, Tmux, Multi-Agent, Decision-Making]
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Review, Quality-Assurance, Parallel-Execution, Tmux, Multi-Agent, Decision-Making]
---

# 3-Person Review System

tmux pane 기반 병렬 리뷰 시스템 - 3개의 독립적 리뷰어가 병렬로 리뷰 후 토론 및 결론을 도출하는 패턴.

## When to Use

- **DFMEA Working Paper 리뷰**: Codex(SW) + GLM(공학) + Claude(논리)
- **코드 PR 리뷰**: 복수의 AI 리뷰어로 다각적 검증
- **설계 문서 검토**: 기술, 비즈니스, 논리 3축 검증
- **위험성 평가**: 다양한 관점에서 리스크 식별

## Architecture Overview

```
┌─────────────────────────────────────────┐
│  오케스트레이터 (현재 세션)              │
│                                         │
│  1. tmux pane 생성 (3개 분할)            │
│  2. 각 pane에서 리뷰어 실행             │
│  3. 결과 수집 (tmux capture-pane)       │
│  4. 토론 및 결론 도출                  │
│  5. 최종 보고                           │
└─────────────────────────────────────────┘
```

## Core Pattern: tmux Pane-Based Parallel Review

### Step 1: Pane Setup

```bash
# 새로운 윈도우 생성
tmux new-window -n review

# 3개 pane으로 분할
tmux split-window -h  # 수평 분할 (왼/오)
tmux split-window -v  # 하단 분할 (오른쪽을 상/하)
tmux select-pane -t 0 # 왼쪽 pane 선택
tmux split-window -v  # 왼쪽을 상/하

# 결과:
# Pane 0 (왼쪽 상) | Pane 1 (오른쪽 상)
# ----------------+------------------
# Pane 2 (왼쪽 하) | Pane 3 (오른쪽 하)
```

### Step 2: Reviewer Execution

```bash
# 각 pane에서 리뷰어 실행
tmux send-keys -t 0 "hih-codex 'Review this...'" Enter
tmux send-keys -t 1 "hih-glm 'Review this...'" Enter
tmux send-keys -t 2 "hih-claude 'Review this...'" Enter
```

**Alternative: delegate_task 방식 (간단)**
```python
from hermes import delegate_task

results = delegate_task(tasks=[
    {
        "goal": "Codex review",
        "model": "gpt-4",
        "provider": "openai",
        "prompt": "Review this..."
    },
    {
        "goal": "GLM review",
        "model": "glm-4.7",
        "provider": "zai-glm",
        "prompt": "Review this..."
    },
    {
        "goal": "Claude review",
        "model": "claude-opus-4-7",
        "prompt": "Review this..."
    }
])
```

### Step 3: Result Collection

```bash
# 각 pane 결과 캡처
tmux capture-pane -t 0 -p > /tmp/review_codex.txt
tmux capture-pane -t 1 -p > /tmp/review_glm.txt
tmux capture-pane -t 2 -p > /tmp/review_claude.txt

# cleanup
tmux kill-window -t review
```

### Step 4: Discussion & Consensus

```
1. 의견 정리 및 분류
   - 일치: 모두 동의 → 즉시 반영
   - 충돌: 리뷰어 간 상이한 의견 → 토론
   - 누락: 어느 리뷰어도 언급하지 않음 → 추가 질문
   ↓
2. 상대 의견 제시
   - 각 리뷰어에게 상대 의견 전달
   - 근거 요청
   ↓
3. 반론 및 재검토
   - 상대 의견에 대한 근거 제시
   - 원칙 재확인
   - 추가 문서 검토 (필요 시)
   ↓
4. 합의 도출
   - 최종 결론
   - 수정 사항 명시
   - 다음 단계
```

### Step 5: Final Report

```markdown
## 3자 리뷰 보고서

### 리뷰어 의견

#### 리뷰어 1
**주요 관점:** ...
**의견:** ...

#### 리뷰어 2
**주요 관점:** ...
**의견:** ...

#### 리뷰어 3
**주요 관점:** ...
**의견:** ...

### 토론

**의견 차이:**
- **리뷰어 1 vs 2**: ...
  - **결론:** ...

**충돌 해결:**
- ...

### 최종 결론

**합의 사항:**
1. ...
2. ...

**다음 단계:**
- ...
```

## Reviewer Configuration Examples

### DFMEA Review Pattern

| 리뷰어 | 역할 | 모델 | 주요 관점 |
|--------|------|------|----------|
| **Codex** | SW 설계 결함 검증 | GPT-4 | 로직, 상태머신, 코드 표준 |
| **GLM** | 공학적 타당성 + 비즈니스 | GLM-4.7 | 물리 법칙, 안전 마진, 현장 실무성 |
| **Claude** | 제1원칙 사고 + 논리 | Claude Opus 4.7 | 인과관계, S/O/D 평가, AP 판단 |

**리뷰어별 역할 분담:**
- **Codex**: "이 설계 결함이 코드 어디에 반영되어야 하나요?"
- **GLM**: "이 조치가 현장에서 실현 가능한가요?"
- **Claude**: "Cause가 설계 결함 수준인가요?"

### Code PR Review Pattern

| 리뷰어 | 역할 | 모델 | 주요 관점 |
|--------|------|------|----------|
| **Codex** | 코딩 표준 + 아키텍처 | GPT-4 | 명명 규칙, 구조, 의존성 |
| **GLM** | 비즈니스 요구사항 | GLM-4.7 | 기능 충족, 사용자 경험 |
| **Claude** | 테스트 커버리지 | Claude Opus 4.7 | 엣지 케이스, 예외 처리 |

## Implementation Template

```python
import subprocess
import tempfile
from pathlib import Path

def three_person_review(
    context: str,
    reviewers: list[dict],
    output_file: Path
):
    """
    3자 리뷰 실행
    
    Args:
        context: 리뷰 대상 (파일 경로, 내용 등)
        reviewers: 리뷰어 설정 (이름, 스킬, 프롬프트)
        output_file: 결과 저장 경로
    """
    # 1. tmux pane 생성
    subprocess.run(["tmux", "new-window", "-n", "review"])
    
    # 2. pane 분할 (3개)
    subprocess.run(["tmux", "split-window", "-h"])
    subprocess.run(["tmux", "split-window", "-v"])
    subprocess.run(["tmux", "select-pane", "-t", "0"])
    subprocess.run(["tmux", "split-window", "-v"])
    
    # 3. 각 리뷰어 실행
    temp_files = []
    for i, reviewer in enumerate(reviewers):
        # 임시 파일에 프롬프트 작성
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(f"{reviewer['prompt']}\n\nContext:\n{context}")
        temp_file.close()
        temp_files.append(temp_file.name)
        
        # 스킬 실행
        cmd = f"{reviewer['skill']} '{context}'"
        subprocess.run(["tmux", "send-keys", "-t", str(i), cmd, "Enter"])
    
    # 4. 완료 대기 (사용자 개입 필요)
    print("3개 리뷰어가 실행 중입니다. 완료 후 엔터키를 눌러주세요.")
    input()
    
    # 5. 결과 수집
    results = {}
    for i, reviewer in enumerate(reviewers):
        output = subprocess.run(
            ["tmux", "capture-pane", "-t", str(i), "-p"],
            capture_output=True,
            text=True
        )
        results[reviewer['name']] = output.stdout
    
    # 6. cleanup
    subprocess.run(["tmux", "kill-window", "-t", "review"])
    for temp_file in temp_files:
        Path(temp_file).unlink()
    
    return results
```

## Pitfalls

1. **tmux 세션 없음**: tmux가 실행 중이 아니면 pane 생성 실패
   - **해결**: `tmux new-session -d -s review`로 세션 먼저 생성

2. **리뷰어 완료 타이밍**: 각 리뷰어 실행 시간이 다름
   - **해결**: 사용자가 완료 확인 후 수동으로 넘어가기

3. **결과 수집 실패**: capture-pane이 너무 일찍 실행
   - **해결**: 사용자 입력 대기 (`input()`)

4. **Pane 번호 혼동**: tmux pane indexing (0부터 시작)
   - **해결**: 항상 `tmux list-panes`로 확인

5. **delegate_task vs tmux**: tmux가 시각적이지만 관리 복잡
   - **해결**: 간단한 작업은 delegate_task, 복잡한 작업은 tmux

## Alternatives

### Option 1: tmux pane (시각적, 복잡)
- **장점**: 각 리뷰어를 실시간으로 볼 수 있음
- **단점**: 관리 복잡, 사용자 개입 필요

### Option 2: delegate_task (간단, 백그라운드)
- **장점**: 간단, 자동화
- **단점**: 시각화 불가, 진행 상황 모니터링 필요

### Option 3: 혼합
- delegate_task로 실행 → 로그로 결과 확인
- 필요 시 tmux로 시각적 확인

## When NOT to Use

- 단일 리뷰어로 충분한 경우
- 간단한 변경사항 (1~2줄 코드 수정)
- 긴급 상황 (3자 토론에 시간 부족)

## Related Skills

- `codex` - OpenAI Codex CLI 사용
- `claude-code` - Claude Code CLI 사용
- `hih-glm` - GLM 4.7 실행 (프로젝트 스킬)
- `hih-claude` - Claude Opus 4.7 실행 (프로젝트 스킬)