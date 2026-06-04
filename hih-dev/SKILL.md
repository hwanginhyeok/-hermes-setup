# /hih-dev — 기능 개발 풀 파이프라인

**용도**: `~/project-manager/` 내의 프로젝트(bea, stock, insung, music)에서 기능 개발 시작

**사용 타이밍**: "개발 시작", "기능 만들어줘", "풀 파이프라인" 등 새 기능 구현 요청

---

## STEP 1: 태스크 확인

### 1.1 CURRENT_TASK.md 체크
```bash
read_file ~/project-manager/CURRENT_TASK.md
```

### 1.2 빈 작업이면 task_briefings/에서 확인
```bash
ls -la ~/project-manager/content_queue/task_briefings/{project}/
```

### 1.3 관련 없으면 사용자에게 확인
- "다른 작업 정리 후 {새 태스크}를 시작할까요?"

---

## STEP 2: 설계 (STEP 2가 완료되지 않은 경우)

### 2.1 규칙 준수
- 코드 수정은 **예외 없이** read_file → write_file 또는 patch
- sed, awk, bash heredoc 금지 (git diff 기능 무력화)

### 2.2 설계 결정 후 CURRENT_TASK.md에 기록
- 설계 원칙 (실용주의, 선검증, 아키텍처)
- 구현 계획 (파일별)

---

## STEP 1.5: 병렬 분해 판단

### 1.5.1 서브태스크 분해 기준
**독립적인 파일 기반 서브태스크**로만 분해 가능:

| 서브태스크 A | 서브태스크 B |
|-------------|-------------|
| `models/*.py` 수정 | `views/*.py` 수정 |
| `views/template1.html` | `views/template2.html` |
| `script_a.py` | `script_b.py` |
| `utils/*.py` + `tests/test_utils.py` | `models/*.py` + `tests/test_models.py` |

**❌ 분해 불가** (파일 공유):
- 단일 파일 내 기능 추가 (line 추가, 함수 추가)
- 단일 파일 버그 수정
- 단일 파일 리팩토링

### 1.5.2 분해 판단
- **복잡한 요청 + 여러 파일**: 분해 후 병렬 진행
- **간단한 요청 + 단일/소수 파일**: 병렬 진행 X (PM → 에이전트 단일 전달)

### 1.5.3 분해 시 태스크 브리핑 작성
```python
# task_briefing_manager.py 사용
from scripts.task_briefing_manager import create_task_briefing, deliver_to_pane

content = """## 서브태스크 A: 템플릿 구현

### 담당 파일 (이 파일들만 수정)
- bea-a-studio/templates/neighbor_v1.html

### 구현 목표
기존 디자인 가이드(architecture-diagram 스킬) 기반으로 구현

### 완료 조건
- [ ] 레이아웃 구조 적용
- [ ] 컬러 시스템 적용
- [ ] VNC localhost:8001에서 시각 확인

### 주의
- pane1 에이전트와 파일 겹침 없음. 담당 파일 외 수정 금지.
- 완료 시 git add + commit (push는 PM 지시 대기)
"""

tmp_path, history_path = create_task_briefing("bea", "A", content)
deliver_to_pane("bea", 1.2, tmp_path)
```

---

## STEP 3: 구현 (병렬 에이전트 투입)

### 3.1 분해된 서브태스크
각 pane에 에이전트 시작 후 브리핑 전달:

```bash
# pane2 에이전트 시작 + 브리핑 전달
tmux send-keys -t bea:1.2 "claude --add-dir ~/be-a-studio" Enter
tmux send-keys -t bea:1.2 "cat /tmp/bea_task_A.md" Enter

# pane3 에이전트 시작 + 브리핑 전달
tmux send-keys -t bea:1.3 "claude --add-dir ~/be-a-studio" Enter
tmux send-keys -t bea:1.3 "cat /tmp/bea_task_B.md" Enter

# pane4 에이전트 시작 + 브리핑 전달
tmux send-keys -t bea:1.4 "claude --add-dir ~/be-a-studio" Enter
tmux send-keys -t bea:1.4 "cat /tmp/bea_task_C.md" Enter
```

### 3.2 단일 에이전트 (분해 불가)
```bash
# pane2 에이전트 시작
tmux send-keys -t bea:1.2 "claude --add-dir ~/be-a-studio" Enter

# 전체 작업 전달
tmux send-keys -t bea:1.2 "cat /tmp/bea_task_single.md" Enter
```

---

## STEP 4: 검증 (L1)

### 4.1 에이전트 완료 보고 체크
- pane별 완료 여부 확인
- 완료 보고 없으면 확인 메시지 전달

### 4.2 에이전트 보고 검증
- 완료 조건 충족 여부
- 담당 파일 외 수정 여부

---

## STEP 5: 리뷰 (L2 Hunk)

### 5.1 hih-dual 스킬 호출
```bash
# bea 세션 pane1에서
/hih-dual
```

### 5.2 PM 검증
- PM이 diff 직접 확인

---

## STEP 6: 통합 + 테스트

### 6.1 병렬 서브태스크 통합
```bash
# bea 세션 pane1에서
git merge service_branch_A
git merge service_branch_B
git merge service_branch_C
```

### 6.2 통합 테스트
```bash
# bea 세션 pane1에서
pytest tests/
```

### 6.3 테스트 실패
- 실패 서브태스크 담당 에이전트에 수정 지시

---

## STEP 7: CI + 승인 게이트 (전체 작업 완료 후)

### 7.1 배포 점검
```bash
# bea 세션 pane1에서
cd ~/be-a-studio

# 배포 테스트 서버
pytest -k test_ci --durations-min=3
```

### 7.2 승인 게이트 점검
- deploy/prod.ip 도달 경로
- deploy/canary/ 경로
- 해당 워커 용량

### 7.3 승인 게이트 미달
- 반려 후 "배포 준비 확인" 재작업

---

## STEP 8: 승인 후 배포

### 8.1 PM 지시 (승인 게이트 달성 후)
```bash
# bea 세션 pane1으로 전달
tmux send-keys -t PM:0.2 "bea: Vercel 배포 승인 — 사용자 확인 완료" Enter
```

### 8.2 bea 세션에서 배포
```bash
# bea 세션 pane1에서
vercel --prod
```

### 8.3 배포 완료 확인
- CI 상태 확인
- 배포 완료 메시지 확인

---

## STEP 9: 배포 완료 보고 + 정리

### 9.1 PM 보고
```bash
# bea 세션 pane1에서
tmux send-keys -t PM:0.2 "bea: 배포 완료 — {commit hash}" Enter
```

### 9.2 PM 정리
- CURRENT_TASK.md → FINISHED_TASK.md
- PM 세션에서 git push

### 9.3 각 에이전트 종료
```bash
tmux send-keys -t bea:1.2 "/exit" Enter
tmux send-keys -t bea:1.3 "/exit" Enter
tmux send-keys -t bea:1.4 "/exit" Enter
```

---

## TASK 브리핑 관리

### 전달용 (/tmp/)
에이전트에게 작업 내용 전달

### 보관용 (content_queue/task_briefings/)
히스토리 추적

### 이동 스크립트
작업 종료 후 보관용으로 이동

### 정리
전달용 파일 정리 (임시 폴더 자동 정리 포함)