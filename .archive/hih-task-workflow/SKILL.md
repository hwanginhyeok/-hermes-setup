---
name: hih-task-workflow
description: hih-task와 hih-clear 사이의 워크플로우 이해. 세션 라이프사이클과 태스크 관리의 자동화 한계.
user_invocable: false
---

# hih-task 워크플로우

## 세션 라이프사이클

```
세션 시작
    ↓
hih-task (태스크 브리핑 + 관리)
    ↓
작업 진행 (done/start/add/block 명령 수동 입력)
    ↓
세션 종료
    ↓
hih-clear (종료 루틴)
    ├── hih-task-clear (태스크 정리)
    ├── hih-memory (메모리 정리)
    ├── hih-git (git 커밋 + push)
    ├── DIFFICULTY 기록
    ├── 세션 요약 출력
    ├── handoff.md 생성
    └── /clear
```

## hih-task 기능

**브리핑:**
- TASK.md (인덱스)
- CURRENT_TASK.md (진행 중)
- PREPARED_TASK.md (예정 - P1만 상세, P2/P3 개수만)
- FINISHED_TASK.md (최근 5개만)

**인터랙티브 관리:**
- `done #번호` → CURRENT → FINISHED (완료일 기입)
- `start #번호` → PREPARED → CURRENT (시작일 기입)
- `add 태스크명` → PREPARED 추가 (ID 충돌 검사)
- `block #번호 사유` → blocked 컬럼 업데이트

## hih-task-clear 기능

세션 종료 시 hih-clear 내부에서 자동 호출:

1. 완료/신규 태스크 반영
2. ID 충돌 검사
3. depends 갱신
4. task_audit 실행 (좀비/중복/고아/정체/blocked/P1 인플레이션 처리)
5. TASK.md 인덱스 재계산
6. task_audit 재검증

## 자동화 한계

**중요**: 작업 완료 후 자동으로 `done` 처리되지 않음

- 에이전트가 작업을 완료해도 사용자가 수동으로 `done #번호` 입력해야 함
- 세션 종료 시 hih-task-clear가 정리하지만, 이건 "이번 세션에 완료된 것을 FINISHED로 이동"하는 것
- 진행 중인 태스크는 그대로 CURRENT에 남음

## PM vs 프로젝트 세션

| | PM 세션 | 프로젝트 세션 |
|---|---|---|
| **hih-task** | 읽기만 | 읽기 + 수정 가능 |
| **수정 권한** | 없음 | 있음 |
| **지시 방법** | tmux send-keys로 각 세션에 전달 | 직접 수정 |

## 관련 스킬

- `hih-task` — 태스크 브리핑 + 관리
- `hih-task-clear` — 태스크 정리 (hih-clear 내부에서 자동 호출)
- `hih-clear` — 세션 종료 루틴 전체
- `hih-all-task-clear` — 전체 태스크만 일괄 정리 (git/memory 제외)
- `hih-all-clear` — 전체 세션 일괄 정리 (태스크 + git + memory + clear)

---

**Remember**: 태스크 관리는 반자동. 사용자가 명령어로 제어하고, 스킬은 파일 정리와 audit를 자동화.
