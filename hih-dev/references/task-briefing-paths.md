# Task Briefing Paths Reference

## Problem

**Hardcoded briefing paths cause issues:**
- Original: `/tmp/hih_task_B.md`
- Problem: No project separation, manual creation required, auto-incomplete

## Solution

**Project-specific briefing directories:**
```bash
BRIEF_DIR="~/project-manager/content_queue/task_briefings/{프로젝트명}"
mkdir -p "$BRIEF_DIR"
```

**Best practice template:**
```bash
# 브리핑 파일 작성 (프로젝트별 디렉토리 + 타임스탬프)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BRIEF_PATH="$BRIEF_DIR/hih_task_${TIMESTAMP}_B.md"

cat > "$BRIEF_PATH" << 'EOF'
## 서브태스크 B: {제목}

### 담당 파일 (이 파일들만 수정)
- {파일 경로}

### 구현 목표
{구체적 목표}

### 완료 조건
- [ ] {체크리스트}

### 주의
- pane1 에이전트와 파일 겹침 없음
- 담당 파일 외 수정 금지
- 완료 시 git add + commit (push는 PM 지시 대기)
EOF

# 에이전트에게 전달
tmux send-keys -t {세션}:1.2 "cat $BRIEF_PATH" Enter
```

## Benefits

1. **Project separation**: Each project has its own briefing directory
2. **Conflict prevention**: Timestamps prevent file collisions
3. **Audit trail**: All briefings preserved for history
4. **Automation ready**: Structured paths enable future auto-generation

## Session Context

**2026-05-17 PM Session:**
- Issue: hih-dev 스킬의 지시문 경로가 `/tmp/hih_task_B.md`로 하드코딩됨
- Improvement: 프로젝트별 브리핑 디렉토리 + 타임스탬프 추가
- Result: 구조화된 경로로 충돌 방지 + 감사 추적 가능