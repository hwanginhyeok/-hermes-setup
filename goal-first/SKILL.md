---
name: goal-first
description: 목표 기반 태스크 분해 + 추적 시스템. hih-task, hih-dev, investigate 통합 핵심.
user_invocable: true
---

# /goal-first — 목표 기반 태스크 분해 + 추적

**용도**: 새 프로젝트/기능/버그 해결을 목표 기반으로 체계적으로 분해 + 추적

**사용 타이밍**: "새 기능 추가", "버그 해결", "목표 설정", "계획 세워줘" 등 목표 기반 작업 요청

---

## STEP 1: 목표 정의

### 1.1 GOAL.md 생성/확인
```bash
GOAL_PATH="CURRENT_GOAL.md"

if [ ! -f "$GOAL_PATH" ]; then
  cat > "$GOAL_PATH" << 'EOF'
# GOAL.md

## 목표
[구체적인 목표 기술]

## 성공 조건
- [ ] 조건1
- [ ] 조건2
- [ ] 조건3

## 우선순위
P1 / P2 / P3

## 의존성
- 선행 목표: 없음 또는 [GOAL_ID]
- 후속 목표: 없음 또는 [GOAL_ID]

## 위험 요소
- 위험1: [완화 방안]
- 위험2: [완화 방안]

## 생성일
YYYY-MM-DD
EOF
fi
```

### 1.2 목표 ID 생성
```bash
GOAL_ID="G$(date +%Y%m%d_%H%M%S)"
```

---

## STEP 2: 서브태스크 분해

### 2.1 파일 경계 기준 분해
```bash
# 독립적인 파일만 분해 가능
# ❌ 분해 불가: 단일 파일 내 기능 추가
# ✅ 분해 가능: models/*.py, views/*.py 별도

SUBTASKS_PATH="SUBTASKS.md"

cat > "$SUBTASKS_PATH" << 'EOF'
# SUBTASKS.md

## 서브태스크 목록

| ID | 서브태스크 | 담당 파일 | 에이전트 | 완료 조건 | 상태 |
|----|----------|----------|---------|----------|------|
| A | [제목] | [파일 경로] | [pane] | [조건] | pending |
| B | [제목] | [파일 경로] | [pane] | [조건] | pending |
| C | [제목] | [파일 경로] | [pane] | [조건] | pending |

## 의존성 그래프
A → B → C (A 완료 후 B 시작)

## 목표 달성률
0% (0/3 완료)
EOF
```

---

## STEP 3: 진행 추적

### 3.1 PROGRESS.md 생성
```bash
PROGRESS_PATH="PROGRESS.md"

cat > "$PROGRESS_PATH" << 'EOF'
# PROGRESS.md

## 진행 현황

| 서브태스크 | 진도 | 상태 | 차단 | 비고 |
|----------|------|------|------|------|
| A | 0% | pending | 없음 | |
| B | 0% | pending | 없음 | |
| C | 0% | pending | 없음 | |

## 목표 달성률
0% (0/3 완료)

## 차단 사항
- 없음

## 위험 요소 현황
- 위험1: [상태]
- 위험2: [상태]

## 최종 완료일
미정
EOF
```

---

## STEP 4: 에이전트 배정 (hih-dev 통합)

### 4.1 hih-dev 워크플로우에 통합
```bash
# hih-dev STEP 1.5 병렬 분해 판단 시
# goal-first → 서브태스크 분해 → 에이전트 배정

for subtask in A B C; do
  pane="1.$((SUBTASK_INDEX + 1))"
  
  # 브리핑 생성
  BRIEF_PATH="content_queue/task_briefings/{PROJECT}/goal_${TIMESTAMP}_${subtask}.md"
  
  cat > "$BRIEF_PATH" << EOF
## 서브태스크 ${subtask}: [제목]

### 목표 (GOAL.md)
[목표 내용]

### 성공 조건 (GOAL.md)
- [ ] 조건1
- [ ] 조건2
- [ ] 조건3

### 담당 파일 (이 파일들만 수정)
- [파일 경로]

### 완료 조건
- [ ] 구현 완료
- [ ] 테스트 통과
- [ ] 성공 조건 충족

### 주의
- pane1 에이전트와 파일 겹침 없음
- 담당 파일 외 수정 금지
- 완료 시 git add + commit (push는 PM 지시 대기)
- 완료 시 SUBTASKS.md 상태 업데이트
EOF

  # 에이전트 배정
  tmux send-keys -t {SESSION}:${pane} "claude --add-dir {PROJECT_PATH}" Enter
  tmux send-keys -t {SESSION}:${pane} "cat $BRIEF_PATH" Enter
done
```

---

## STEP 5: 진행 모니터링 + 업데이트

### 5.1 진도 업데이트
```bash
# 에이전트 완료 보고 시
update_progress() {
  local subtask=$1
  local progress=$2
  local status=$3
  
  # PROGRESS.md 업데이트
  sed -i "/| ${subtask} |/s/| 0% | ${status} |/| ${progress}% | ${status} |/" PROGRESS.md
  
  # SUBTASKS.md 업데이트
  sed -i "/| ${subtask} |/s/| pending |/| ${status} |/" SUBTASKS.md
  
  # 목표 달성률 재계산
  calculate_completion_rate()
}

calculate_completion_rate() {
  local total=$(grep -c "^|" SUBTASKS.md | head -1)
  local completed=$(grep -c "| completed |" SUBTASKS.md)
  local rate=$((completed * 100 / total))
  
  sed -i "s/목표 달성률.*/목표 달성률: ${rate}% (${completed}/${total} 완료)/" SUBTASKS.md
  sed -i "s/목표 달성률.*/목표 달성률: ${rate}% (${completed}/${total} 완료)/" PROGRESS.md
}
```

---

## STEP 6: 완료 검증

### 6.1 성공 조건 체크
```bash
# 전체 서브태스크 완료 시
verify_goal_completion() {
  echo "## 목표 완료 검증"
  echo ""
  
  echo "### 성공 조건 체크"
  # GOAL.md에서 성공 조건 읽기
  grep "^- \[ \]" CURRENT_GOAL.md || echo "✅ 모든 조건 충족"
  
  echo ""
  echo "### 서브태스크 완료 상태"
  grep "| completed |" SUBTASKS.md || echo "⚠️  미완료 서브태스크 있음"
  
  echo ""
  echo "### 목표 달성률"
  grep "목표 달성률" SUBTASKS.md
  
  echo ""
  echo "### 완료일"
  date "+%Y-%m-%d"
}
```

---

## STEP 7: 아카이빙

### 7.1 완료 후 아카이브
```bash
# 모든 서브태스크 완료 시
archive_goal() {
  local year=$(date +%Y)
  local month=$(date +%m)
  local archive_dir="GOAL_ARCHIVE/${year}-${month}"
  local archive_file="${archive_dir}/GOAL_${GOAL_ID}.md"
  
  mkdir -p "$archive_dir"
  
  # GOAL.md + SUBTASKS.md + PROGRESS.md 병합
  cat > "$archive_file" << EOF
# GOAL ${GOAL_ID}

\`\`\`markdown
# GOAL.md
$(cat CURRENT_GOAL.md)
\`\`\`

\`\`\`markdown
# SUBTASKS.md
$(cat SUBTASKS.md)
\`\`\`

\`\`\`markdown
# PROGRESS.md
$(cat PROGRESS.md)
\`\`\`

## 완료일
$(date +%Y-%m-%d)

## 완료 보고
[사용자/PM 완료 보고 내용]
EOF
  
  # 현재 파일 정리
  rm CURRENT_GOAL.md SUBTASKS.md PROGRESS.md
  
  echo "✅ 목표 아카이브 완료: $archive_file"
}
```

---

## hih-task 통합

### 브리핑에 목표 추가
```bash
# hih-task 브리핑 출력 시
echo "## 현재 목표"
if [ -f CURRENT_GOAL.md ]; then
  grep "^## 목표" CURRENT_GOAL.md
  grep "^## 성공 조건" -A 10 CURRENT_GOAL.md
  grep "목표 달성률" SUBTASKS.md
else
  echo "  - 진행 중 목표 없음"
fi
```

---

## hih-dev 통합

### 병렬 분해 시 목표 의존성 고려
```bash
# hih-dev STEP 1.5 병렬 분해 판단 시
# 파일 경계 + 목표 의존성 기준 분해

# 1. 파일 경계 확인
# 2. 목표 의존성 확인 (GOAL.md 의존성)
# 3. 병렬 가능 여부 판단
# 4. 서브태스크 분해 → 에이전트 배정
```

---

## investigate 통합

### 버그 해결 목표 설정
```bash
# investigate 시작 시
cat > INVESTIGATE_GOAL.md << 'EOF'
# INVESTIGATE_GOAL.md

## 버그 증상
[증상 기술]

## 목표 (복구 상태)
[어떤 상태로 복구할 것인가]

## 성공 조건
- [ ] 근본 원인 찾음
- [ ] 수정 완료
- [ ] 회귀 테스트 통과
- [ ] 원래 버그 재현 불가

## 우선순위
P1 / P2 / P3

## 생성일
YYYY-MM-DD
EOF
```

---

## 주의

- **목표 ID**: 고유한 G{YYYYMMDD_HHMMSS} 형식
- **파일 경계**: 독립적인 파일만 분해 가능
- **의존성**: 목표 간 의존성도 관리
- **달성률**: 자동 계산 + 수동 업데이트
- **아카이브**: 월별 GOAL_ARCHIVE/{YYYY-MM}.md

---

## 워크플로우

```
goal-first → GOAL.md → SUBTASKS.md → hih-dev (에이전트 배정)
  → PROGRESS.md (진도 업데이트) → 완료 검증 → GOAL_ARCHIVE
```

---

## 테스트 방법

```bash
# 1. 목표 생성
/hih-task  # 브리핁에 목표 표시
# 또는
/goal-first  # 직접 목표 설정

# 2. 서브태스크 분해
# SUBTASKS.md 확인

# 3. 진행 추적
# PROGRESS.md 확인

# 4. 완료 검증
verify_goal_completion

# 5. 아카이빙
archive_goal
```