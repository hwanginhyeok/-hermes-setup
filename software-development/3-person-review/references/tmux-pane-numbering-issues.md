# Tmux Pane Numbering After Splits

When creating multi-pane layouts in tmux, pane numbering changes after each split operation. This is a common pitfall.

## Example: 3-Pane Layout

```bash
# Step 1: Create window
tmux new-window -n review -d
# Result: 1 pane (pane 0)

# Step 2: Horizontal split
tmux split-window -h -t review
# Result: 2 panes (pane 0, pane 1) - LEFT is 0, RIGHT is 1

# Step 3: Vertical split on RIGHT pane
tmux split-window -v -t review.1
# Result: 3 panes (pane 1, pane 2, pane 3)
# - pane 1: LEFT (original)
# - pane 2: TOP RIGHT
# - pane 3: BOTTOM RIGHT
```

**Key insight:** After `split-window -v -t review.1`, the target pane (1) is split into two NEW panes (2 and 3). Pane 1 becomes a reference, not a valid pane number anymore.

## Verification

Always verify pane numbering before sending commands:

```bash
tmux list-panes -t review
# Output example:
# 1: [104x29] [history 0/10000, 2409 bytes] %16
# 2: [104x28] [history 0/10000, 2369 bytes] %18 (active)
# 3: [103x58] [history 0/10000, 3564 bytes] %17
```

Note: Actual pane numbers may differ from expected due to tmux's internal renumbering.

## Safe Pattern

```bash
# 1. Create window
tmux new-window -n review -d

# 2. Split and capture pane IDs
tmux split-window -h -t review
panes=$(tmux list-panes -t review -F '#{pane_index}')

# 3. Use actual pane IDs from list
for pane_id in $(echo "$panes" | head -2); do
    tmux send-keys -t "$pane_id" "echo 'Pane $pane_id'" Enter
done
```

## Common Mistake

```bash
# WRONG - assumes sequential numbering
tmux send-keys -t review.0 "codex ..." Enter
tmux send-keys -t review.1 "glm ..." Enter
tmux send-keys -t review.2 "claude ..." Enter
# Error: "can't find pane: 0" or wrong pane gets command

# CORRECT - verify first
tmux list-panes -t review
# Then use actual pane IDs from output
```

## Pane ID vs Pane Index

- **Pane ID**: Internal tmux identifier, shown in `tmux list-panes` output
- **Pane Index**: Sequential number (0, 1, 2, ...) - may change after splits

**Rule:** Always use pane IDs, not assumptions about sequential numbering.

## Related Commands

```bash
# List panes with their IDs
tmux list-panes -t review

# List panes with formatted output
tmux list-panes -t review -F '#{pane_index}: #{pane_width}x#{pane_height}'

# Show pane with specific ID
tmux display -p -t review.1 '#{pane_id}'
```

## Debugging

If commands go to wrong pane:

```bash
# Check which pane is active
tmux display -p '#{pane_id}'

# Check all panes in window
tmux list-panes -t review

# Try pane selection manually in tmux:
# Ctrl-b, q - shows pane numbers momentarily
# Type number to switch to that pane
```

## Lesson from Session

We discovered that after:
1. `tmux new-window` → 1 pane
2. `tmux split-window -h` → 2 panes (0, 1)
3. `tmux split-window -v -t review.1` → 3 panes (1, 2, 3)

The final pane IDs were 1, 2, 3 - NOT 0, 1, 2 as expected.

This is because:
- Pane 1 (RIGHT) was split into panes 2 and 3
- Pane 1 remains as a parent reference but panes 2 and 3 are the actual active panes
- Pane 0 (LEFT) remains unchanged

**Takeaway:** Always verify `tmux list-panes -t <window>` after creating complex layouts.