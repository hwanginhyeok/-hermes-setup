# Goal-First Task Management Workflow

## Problem Statement

Current workflow weaknesses:
1. **hih-task** only outputs briefings, operates independently
2. **hih-dev** runs independently, weak connection to briefings
3. **Goals scattered across CURRENT_TASK.md** - no centralized goal tracking
4. **Parallel decomposition based only on file boundaries** - ignores goal dependencies

## Solution: goal-first Skill

### Purpose

Goal-based task decomposition + tracking system that bridges hih-task and hih-dev.

### File Structure

```
project-manager/
├── GOAL.md                      # Goal definitions (success criteria, priority, dependencies)
├── SUBTASKS.md                  # Subtask decomposition (files, agents, completion criteria)
├── PROGRESS.md                  # Progress tracking (progress, blockers, risks)
└── GOAL_ARCHIVE/{YYYY-MM}.md    # Completed goals archive
```

### Execution Workflow

```
goal-first → CURRENT_TASK.md → hih-dev → PROGRESS.md → FINISHED → GOAL_ARCHIVE
```

### Execution Steps

**Step 1: Goal Definition**
- Define goal (what problem are we solving?)
- Success criteria (how do we know we're done?)
- Priority (P1/P2/P3)
- Dependencies (what must be done first?)

**Step 2: Goal Decomposition**
- Break down into subtasks
- Identify dependencies between subtasks
- Map subtasks to files and agents
- Define completion criteria per subtask

**Step 3: Task Assignment**
- Assign subtasks to tmux panes/agents
- Deliver task briefings with goal context
- Explain "why this subtask is needed"

**Step 4: Progress Tracking**
- Track completion percentage
- Identify blockers and risks
- Update PROGRESS.md in real-time

**Step 5: Completion Verification**
- Verify success criteria are met
- Goal achievement percentage calculation
- Move to GOAL_ARCHIVE if 100% complete

### Integration with Existing Skills

**hih-task improvements:**
1. Integrate goal-first for goal-based task creation
2. Add goal display in briefings (show parent goal for current tasks)
3. Auto-calculate goal achievement on completion
4. Analyze goal impact when blocked

**hih-dev improvements:**
1. Goal-based parallel decomposition (file boundaries + goal dependencies)
2. Deliver goals to agents on assignment (context of why subtask is needed)
3. Check goal achievement on completion reports (success criteria)
4. Verify goal achievement rate during integration testing

### Goal Definition Template

```markdown
# GOAL.md

## Current Goals

### {GOAL-ID}: {Goal Title}

**Priority**: P1/P2/P3

**Success Criteria**:
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] {Criterion 3}

**Dependencies**:
- {GOAL-ID}: {Goal Title} (must complete first)

**Target Date**: {YYYY-MM-DD}

**Status**: 🟢 In Progress / 🟡 Blocked / 🔴 Critical

**Progress**: {X}%

**Subtasks**: {SUBTASKS.md 참조}
```

### Subtask Decomposition Template

```markdown
# SUBTASKS.md

## {GOAL-ID}: {Goal Title}

### Subtask A: {Title}

**Responsible Files**:
- {file1.py}
- {file2.html}

**Agent**: pane {X} ({claude/bash})

**Completion Criteria**:
- [ ] {Criterion 1}
- [ ] {Criterion 2}

**Dependencies**:
- {SUBTASK-ID}: {Title}

**Status**: 🟢 In Progress / 🟡 Blocked / ✅ Complete

---

### Subtask B: {Title}

... (same structure)
```

### Progress Tracking Template

```markdown
# PROGRESS.md

## {GOAL-ID}: {Goal Title}

**Overall Progress**: {X}%

### Subtask Status

| Subtask | Status | Progress | Blocker |
|---------|--------|----------|---------|
| A | 🟢 In Progress | 60% | None |
| B | ✅ Complete | 100% | None |
| C | 🟡 Blocked | 20% | API rate limit |

### Risks

- {Risk 1}: {Mitigation plan}
- {Risk 2}: {Mitigation plan}

### Notes

{Session notes, decisions made, etc.}
```

### Implementation Priority

1. **P1**: Create goal-first skill (core)
2. **P2**: Integrate goal-first into hih-task
3. **P3**: Integrate goal-first into hih-dev
4. **P4**: Goal-based parallel decomposition feature
5. **P5**: Auto-calculate goal achievement rates

### Example Workflow

**User Request**: "Make the comment bot more stable"

**Step 1: goal-first - Define Goal**
```
GOAL-001: Improve comment bot stability

Success Criteria:
- [ ] Zero crashes in 24h period
- [ ] <1% error rate on posts
- [ ] Auto-restart on crash

Priority: P1
Target Date: 2026-06-01
```

**Step 2: goal-first - Decompose into Subtasks**
```
SUBTASK-001A: Add error handling (insung_blog/main.py)
SUBTASK-001B: Implement health check (insung_blog/health.py)
SUBTASK-001C: Add auto-restart (scripts/restart_comment_bot.sh)
```

**Step 3: goal-first - Assign to Panes**
```
pane 1.2 → SUBTASK-001A
pane 1.3 → SUBTASK-001B
pane 1.4 → SUBTASK-001C
```

**Step 4: hih-dev - Parallel Implementation**
Agents receive task briefings with goal context:
"This subtask is needed to achieve GOAL-001: Improve comment bot stability"

**Step 5: Progress Tracking**
Update PROGRESS.md in real-time as agents complete subtasks.

**Step 6: Verification**
- Check if all success criteria are met
- Verify goal achievement rate is 100%
- Archive to GOAL_ARCHIVE/2026-05.md

## Related Skills

- `/hih-task` - Task briefing + management
- `/hih-dev` - Full development pipeline
- `/pm-orchestration` - PM orchestration optimization

## References

- hih-task analysis: `~/.hermes/skills/project-management/hih-task/SKILL.md`
- hih-dev analysis: `~/.hermes/skills/project-management/hih-dev/SKILL.md`
- Task briefing management: `references/task-briefing-paths.md`

---

**Created**: 2026-05-28
**Status**: 🟢 Design Phase
**Next**: Implement goal-first skill (P1)