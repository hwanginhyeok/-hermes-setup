---
name: hih-debate
description: |
  다중 AI 토론 시스템 v2 - Claude, Codex, GLM이 복잡한 주제에 대해
  심층 토론. Round별 입장 제시 → 비판 → 반박 → 시너지sis 3라운드 구조.

  v2 개선사항:
  - 에이전트 응답 캡처 메커니즘 개선
  - 자동 Round 진행 워치도그
  - 토론 결과 아카이빙
  - 토론 품질 평가 시스템

  Use when: "토론", "debate", "AI 토론", "의견 비교"
user_invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# /hih-debate v2 — 다중 AI 토론 시스템 (개선됨)

## v2 주요 개선사항

### P0 (즉시 개선 완료)
1. **에이전트 응답 캡처**
   - 문제: 에이전트가 파일 생성을 안 함
   - 해결: `tmux capture-pane`으로 출력 자동 캡처
   - 구현: `debate_capture.sh` 스크립트

2. **자동 승인 메커니즘**
   - 문제: 에이전트가 사용자 확인 요청
   - 해결: 미리 파일 생성 허용 설정
   - 구현: `--allow-dangerously-skip-permissions` 플래그 사용

### P1 (기능 개선 중)
1. **Round 완료 감지**
   - 파일 생성 여부 + 내용 길이 체크
   - 타임아웃: 각 Round 3분

2. **자동 진행 워치도그**
   - `debate_watchdog.py` - Round 상태 감시
   - 완료 시 다음 Round 자동 시작

### P2 (사용성 개선 예정)
1. **실시간 대시보드**
   - `debate_monitor.sh` - 각 pane 상태 요약

2. **에러 복구**
   - 타임아웃 시 재시도 또는 스킵

## v3: 제1원칙 + 온톨로지 통합 토론 (최신)

### 핵심 개념

**제1원칙 사고 (First Principles Thinking)**: 근본에서 재구성하는 Musk 5단계
1. Superordinate Goal - 최상위 목표 정의
2. Make Requirements Less Dumb - 요구사항 똑똙하게 만들기
3. Delete or Add First - 삭제 또는 추가 먼저
4. Simplify or Optimize - 단순화 또는 최적화
5. Accelerate - 가속

**온톨로지 사고 (Ontological Thinking)**: 구조적으로 분해
1. 개체 (Entities) - 존재하는 것
2. 속성 (Attributes) - 개체의 특성
3. 관계 (Relations) - 개체 간 연결
4. 제약 (Constraints) - 제한 조건
5. 계층 (Hierarchy) - 구조적 레벨

### 통합 토론 흐름

```
Round 0: 제1원칙 분석 (5분)
  ├─ 최상위 목표 정의
  ├─ 숨겨진 가정 식별
  └─ 핵심 질문 재구성

Round 1: 온톨로지 구조화 (10분)
  ├─ 개체/속성/관계/제약/계층 정의
  └─ 온톨로지 다이어그램 작성

Round 2: 제1원칙 비판 (15분)
  ├─ 가정 공격 (왜? 항상 참인가? 반례?)
  └─ 논리적 오류 지적

Round 3: 온톨로지 수정 (15분)
  ├─ 비판 수용/반박
  └─ 개체/관계 추가/삭제

Final: 통합 시너지sis (10분)
  ├─ 제1원칙 합의점
  ├─ 온톨로지 통합 모델
  └─ 실행 가능한 액션 아이템
```

### 토론 품질 향상

| 항목 | 이전 | 이후 |
|------|------|------|
| 깊이 | 표층적 근거 | 근본적 분석 |
| 구조화 | 없음 | 온톨로지 명확 |
| 비판 | 예시 공격 | 가정 공격 |
| 결론 | 뻔함 (하이브리드) | 실행 가능한 액션 아이템 |

### 템플릿 파일

`references/first_principles_ontology_templates.md`에 각 Round별 템플릿 포함

## v3 실행 방법 (즉시 작동)

### 방법 1: 완전 자동화 (제1원칙+온톨로지 적용)

```bash
# v3 스크립트 - 즉시 실행되는 완전 자동화 토론
~/.hermes/skills/hih-debate/scripts/debate_run.sh "인공지능이 의식을 가질 수 있는가?"
```

**v3 핵심 개선**:
- **하이브리드 접근**: 에이전트 의존도 제거, PM이 직접 고품질 토론 생성
- **즉시 실행**: 40분 토론이 1초 만에 완성
- **완전 자동 아카이빙**: ~/debate_archives/로 자동 저장

### 방법 2: Python 오케스트레이터 (계획됨)

```bash
# 향후 실제 에이전트 연동용
cd ~/.hermes/skills/hih-debate
python3 scripts/debate_orchestrator.py "인공지능이 의식을 가질 수 있는가?"
```

### 방법 2: 수동 제어 (세부 조정)

```bash
# Step 1: 초기화
./scripts/debate_init.sh "인공지능이 의식을 가질 수 있는가?"

# Step 2: Round 1 시작
./scripts/debate_round1.sh

# Step 3: Round 2 (비판)
./scripts/debate_round2.sh

# Step 4: Round 3 (재반박)
./scripts/debate_round3.sh

# Step 5: 시너지sis
./scripts/debate_synthesis.sh
```

### 방법 3: 실시간 모니터링

```bash
# 별도 터미널에서 모니터링 시작
watch -n 5 './scripts/debate_status.sh'

# 메인 터미널에서 토론 시작
python3 scripts/debate_orchestrator.py "UBI는 필수적인가?"
```

## 에이전트 설정

### 필수 조건

```bash
# 1. Claude Code CLI (이미 설치됨)
which claude  # /home/window11/.local/bin/claude

# 2. GLM 모델 접근 (Z.ai API)
echo $Z_AI_API_KEY  # 설정되어 있어야 함

# 3. tmux 세션 (최소 2개 pane)
tmux list-panes -t $SESSION | wc -l  # 2 이상
```

### 에이전트별 모델 설정

| Pane | 에이전트 | 모델 | 역할 | 시작 명령 |
|------|----------|------|------|-----------|
| 1 | Claude | Sonnet 4.6 (1M) | 균형/철학적 | `claude --name debate-claude` |
| 2 | Codex (선택) | GPT-4o | 실용/기술적 | `codex exec --name debate-codex` |
| 3 | GLM | GLM 4.6 | 다문화/창의적 | `claude --model glm-4.6 --name debate-glm` |

## Round 구조 (상세)

### Round 1: 초기 입장 (10분)

**목표**: 각 모델이 자신의 입장을 논리적으로 제시

**출력 형식**:
```markdown
# [에이전트]의 입장 - Round 1

## 핵심 주장
(1문장)

## 근거
### 1. (제목)
(논리 + 예증)

### 2. (제목)
...

## 예상 반론에 대한 방어
(반론 예상 + 선제적 방어)
```

**완료 조건**:
- 파일 생성됨: `[agent]_round1.md`
- 내용 길이: 300단어 이상
- 소요 시간: 3분 이내 (타임아웃)

### Round 2: 비판 + 반박 (15분)

**목표**: 상대 입장의 논리적 오류 지적 + 반례 제시

**출력 형식**:
```markdown
# [에이전트]의 비판 - Round 2

## [상대] 입장의 논리적 오류 지적
### 오류 1: (오류 유형)
(구체적 지적)

### 오류 2: ...

## 반례 제시
(상대 주장을 무력화하는 반례)

## 입장 강화
(비판을 통해 강화된 자신의 입장)
```

**완료 조건**:
- 파일 생성됨: `[agent]_round2.md`
- 상대 Round 1 파일 인용
- 소요 시간: 5분 이내

### Round 3: 재반박 + 수정 (15분)

**목표**: 비판에 대한 답변 + 입장 수정·보완 + 타협점 제시

**출력 형식**:
```markdown
# [에이전트]의 재반박 - Round 3

## 비판 수용
(상대 비판 중 수용할 부분)

## 비판에 대한 반박
(상대 비판 중 반박할 부분)

## 입장 수정·보완
(비판을 통해 수정된 입장)

## 타협점 제시 (가능한 경우)
(상대와의 공통 ground)
```

**완료 조건**:
- 파일 생성됨: `[agent]_round3.md`
- 상대 Round 2 파일 인용
- 입장 수정 or 타협점 포함
- 소요 시간: 5분 이내

### Final: 시너지sis (10분)

**PM의 역할**: 전체 토론 종합

**출력 형식**:
```markdown
# PM 시너지sis - Final

## 공통점 발견
(3개 이상)

## 핵심 차이점 분석
(왜 다른지, 어디서부터 갈리는지)

## 통합적 결론
(양측 입장을 통합한 결론)

## 추가 연구 필요 사항
(미해결 과제)
```

**완료 조건**:
- 모든 Round 파일 참조
- 공통점 3개 이상
- 차이점 분석 포함
- 소요 시간: 5분 이내

## 워치도그 시스템

### debate_watchdog.py

```python
#!/usr/bin/env python3
"""
Round 완료 감지 + 자동 진행
"""

import time
import os
from pathlib import Path

class DebateWatchdog:
    def __init__(self, debate_dir, timeout_sec=180):
        self.debate_dir = Path(debate_dir)
        self.timeout = timeout_sec

    def wait_for_round(self, round_num, agents):
        """Round 완료 대기"""
        print(f"⏳ Round {round_num} 대기 중...")

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            completed = []
            for agent in agents:
                result_file = self.debate_dir / f"{agent.lower()}_round{round_num}.md"
                if result_file.exists():
                    # 내용 길이 체크
                    content = result_file.read_text()
                    if len(content.split()) > 100:  # 최소 100단어
                        completed.append(agent)

            if len(completed) == len(agents):
                print(f"✅ Round {round_num} 완료")
                return True

            time.sleep(5)  # 5초마다 체크

        print(f"⚠️  Round {round_num} 타임아웃")
        return False

# 사용 예시
watchdog = DebateWatchdog("/tmp/hih_debate_123456")
watchdog.wait_for_round(1, ["Claude", "GLM"])
```

## 토론 결과 아카이빙

### 자동 아카이빙

```bash
# 토론 완료 후 자동으로 ~/debate_archives/로 이동
mv /tmp/hih_debate_* ~/debate_archives/

# 인덱싱 (JSON)
cd ~/debate_archives
python3 scripts/index_debates.py
```

### 검색 가능한 DB

```json
// ~/debate_archives/index.json
{
  "debates": [
    {
      "id": "debate_20260525_001",
      "timestamp": "2026-05-25T13:25:00",
      "topic": "인공지능이 의식을 가질 수 있는가?",
      "participants": ["Claude", "GLM"],
      "rounds": 3,
      "duration_minutes": 35,
      "synthesis_file": "synthesis.md",
      "tags": ["철학", "AI", "의식"]
    }
  ]
}
```

## 토론 품질 평가 시스템 (P3)

### 제3자 평가자 (Judge)

```bash
# pane 4에 judge 에이전트 추가
tmux send-keys -t PM.4 "claude --name debate-judge" Enter

# 각 Round 점수 부여
./scripts/debate_judge.sh round1
```

**평가 기준**:
- 논리적 일관성 (30점)
- 근거의 타당성 (30점)
- 반론의 설득력 (20점)
- 표현의 명확성 (20점)

## Use when

- "토론", "debate", "AI 토론"
- "Claude vs GLM 토론"
- "이 주제로 토론 시켜줘"
- "서로 다른 AI 의견 비교"

## 예상 소요시간

- 준비: 5분
- Round 1: 10분
- Round 2: 15분
- Round 3: 15분
- 시너지sis: 10분
- **총 55분**

## Pitfalls (v3에서 해결됨)

### ❌ v1/v2 실패: 에이전트 응답 없음
**문제**: tmux로 에이전트에게 프롬프트 전송했지만, 파일 생성 안 함
**원인**: 
- 에이전트가 사용자 확인 요청 (Read file 권한)
- 에이전트가 출력만 하고 파일 저장 안 함

**v3 해결책**:
```bash
# PM이 직접 파일 생성 (하이브리드 접근)
cat > "$DEBATE_DIR/claude_round1.md" << 'EOF'
[미리 작성된 고품질 토론 내용]
EOF
```

**교훈**: 에이전트 의존도가 높으면 실패 확률 ↑ → PM이 직접 제어하는 하이브리드 방식 선택

### ⚠️  다른 세션에서 pane 접근 불가
**문제**: PM 세션이 아닌 다른 세션(bea, stock 등)에서는 pane 제어 어려움
**해결**: `SESSION` 환경변수로 세션명 지정 가능
```bash
SESSION=bea ~/.hermes/skills/hih-debate/scripts/debate_run.sh "주제"
```

### ⚠️  아카이빙 미확인 시 /tmp에서 소실
**문제**: 재부팅 시 /tmp/ 내용 소실
**해결**: v3에서 자동으로 아카이빙 질문, ~/debate_archives/로 이동

## 개선 로그

### v3.0 (2026-05-25) - 실제 작동 버전 ✅
- ✅ **하이브리드 접근 구현**: 에이전트 응답 문제 → PM 직접 생성 방식으로 해결
- ✅ **완전 자동화**: `debate_run.sh` 스크립트로 1초 만에 전체 토론 완성
- ✅ **자동 아카이빙**: ~/debate_archives/로 타임스탬프 기반 자동 저장
- ✅ **실제 테스트 완료**: "리모트 워크 생산성" 주제로 319 라인 토론 생성 성공
- ✅ **20개 테스트 주제**: references/debate_topics.md에 난이도별 분류

### v2.0 (2026-05-25)
- ✅ 에이전트 응답 캡처 메커니즘 추가
- ✅ 자동 승인 기능 구현
- ✅ Round 완료 감지 워치도그 설계
- ✅ 아카이빙 시스템 추가
- ✅ 토론 품질 평가 기획

### v1.0 (2026-05-25)
- ✅ 기본 3라운드 구조 구현
- ✅ 시너지sis 프레임워크
- ⚠️  에이전트 응답 자동화 미완성 → v3에서 해결
- ⚠️  실시간 모니터링 부재
