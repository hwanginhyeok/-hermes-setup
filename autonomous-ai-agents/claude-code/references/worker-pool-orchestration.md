# Worker Pool Orchestration — PM → Worker Dispatch Pattern

> Session-proven pattern from 2026-05-13: PM (Hermes) orchestrating 3 Claude Code workers via tmux.

## Architecture

```
PM  — Hermes session (claude-code provider or GLM). Orchestrator only.
w1  — Claude Code worker 1 (Opus 4.7, 1M context)
w2  — Claude Code worker 2
w3  — Claude Code worker 3
```

PM never writes project code directly. Workers do all coding. PM does READ → REVIEW → RE-DIRECT.

## Startup Sequence

```bash
# 1. Create worker sessions (open-all.sh or manual)
for i in 1 2 3; do
  tmux new-session -d -s "w${i}" -c "$HOME"
done

# 2. Assign project to idle worker
tmux send-keys -t w1 C-u                          # Clear stale buffer FIRST
sleep 0.5
tmux send-keys -t w1 "source ~/.bashrc && cd ~/stock && claude --add-dir ~/stock --add-dir ~/project-manager" Enter

# 3. Wait for claude startup (8-12 seconds for CLAUDE.md + rules + skills loading)
sleep 10

# 4. Verify ready state
tmux capture-pane -t w1 -p -S -5 | grep '❯'      # Should show prompt
```

## Task Dispatch Pattern

```bash
# 5. Send SHORT task (< 80 chars to avoid tmux send-keys issues)
tmux send-keys -t w1 C-u
sleep 0.3
tmux send-keys -t w1 "git status --short" Enter

# 6. Monitor progress (wait 30-60s depending on complexity)
sleep 30
tmux capture-pane -t w1 -p -S -15 | grep -v '^$' | tail -8

# 7. If worker is done (at ❯ with no activity indicator), send next task
# 8. If worker is stuck (text at ❯ but no processing), recover:
tmux send-keys -t w1 Escape Escape   # Dismiss option picker / feedback prompt
sleep 1
tmux send-keys -t w1 C-u             # Clear stale text
sleep 0.5
tmux send-keys -t w1 "new instruction" Enter
```

## Worker Release

```bash
# When task is done or worker needs project switch:
tmux send-keys -t w1 "/exit" Enter
sleep 3
tmux send-keys -t w1 C-u             # Clear any readline history
sleep 0.5
# Now ready for new project assignment
```

## Common Blockers & Recovery

| Blocker | Symptom | Recovery |
|---------|---------|----------|
| Option picker | `Enter to select · ↑/↓ to navigate` | `Escape` → `C-u` → retype |
| Feedback prompt | `How is Claude doing? 1: Bad 2: Fine...` | `Escape` → `"0"` → `Enter`. Can recur every 15-20 min regardless of `/clear` — tied to session wall-clock age, not context usage. Long sessions (6+ hours) get it repeatedly |
| Stuck at ❯ with text | Input visible but not processing | `Escape Escape` → `C-u` → retype |
| Bash history leak | Wrong project launched | `C-c` → wait for bash → `C-u` → retype |
| ctx > 90% | Quality degrades, "new task?" nag | `/clear` (instant reset, ctx → 100%) |
| ctx > 95% | Severe degradation | `/exit` → restart fresh claude session |

## Timing Guidelines

| Action | Wait |
|--------|------|
| claude startup | 8-12 seconds |
| Simple query (git status) | 5-10 seconds |
| Medium task (file edit) | 15-30 seconds |
| Complex task (multi-file refactor) | 45-90 seconds |
| Deep thinking (architecture) | 2-5 minutes |
| Between send-keys retries | 1-2 seconds |

## Worker Pool Status Check

```bash
# Quick check all workers
for w in w1 w2 w3; do
  echo "--- $w ---"
  tmux capture-pane -t $w -p -S -5 | grep -v '^$' | tail -3
  echo ""
done

# Full status via pm.py
python3 ~/project-manager/pm.py sessions
```

## Context Window Budget

Workers start at ~85-94% context after CLAUDE.md + rules + skills load.
- 85-90%: Normal operation, ~2-3 medium tasks before needing reset
- 90-95%: Use `/clear` to instantly reset to 100%. Worker keeps running — no restart delay. Trade-off: all conversation history is wiped (workers get briefed by PM anyway, so this is fine). The status bar will show "new task? /clear to save Nk tokens" prompt — this is the signal to act.
- >95%: `/clear` immediately. If `/clear` doesn't work (worker unresponsive), `/exit` and restart.

**`/clear` vs `/compact` vs restart:**
| Method | Time | Result | When to use |
|--------|------|--------|-------------|
| `/compact` | ~5s | Compresses history, keeps summary | Need to continue current conversation thread |
| `/clear` | ~1s | Wipes all history, ctx → 100% | Worker between tasks, PM will re-brief |
| `/exit` + restart | ~15s | Fresh claude process | Worker stuck or crashed |

**Practical pattern:** When PM checks workers and sees ctx dropping below 90%, proactively send `/clear` BEFORE dispatching the next task. This prevents the "new task?" nag from blocking input.

## After `/clear` — Warm-up Before Complex Instructions

`/clear` wipes conversation history but **keeps project context** (CLAUDE.md, rules, skills). The worker is still in the same project directory with claude running. However, sending a complex multi-step instruction immediately after `/clear` often fails — claude has no conversation context to anchor the task.

**Recommended warm-up pattern:**
```bash
# 1. /clear (already done)
# 2. Send a SHORT warm-up command to establish context
tmux send-keys -t w1 "CURRENT_TASK.md 읽어줘" Enter
sleep 15   # Let it read and respond

# 3. NOW send the actual task instruction (still < 80 chars)
tmux send-keys -t w1 "1-60 importance 분류 버그 수정해" Enter
```

Without warm-up, complex instructions get "작업 리스트를 알려주세요" or similar "I don't have context" responses. With warm-up, the worker reads the task file and self-orients before you give direction.
