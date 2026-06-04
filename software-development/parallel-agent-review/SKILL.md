---
name: parallel-agent-review
description: "Execute parallel multi-agent reviews using tmux panes for consensus-driven analysis"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Parallel-Execution, Multi-Agent, Tmux, Code-Review, Consensus]
    related_skills: [subagent-driven-development, debugging-hermes-tui-commands]
---

# Parallel Agent Review

Execute parallel multi-agent reviews using tmux panes for consensus-driven analysis. Each agent runs in its own pane, outputs are captured, and consensus is derived.

## When to use

- **3-person review systems**: Codex + GLM + Claude for code/DFMEA reviews
- **Consensus-driven analysis**: Multiple AI perspectives on the same problem
- **Quality gates**: Independent verification before approval
- **Complex debugging**: Different models/languages for the same issue
- **DFMEA analysis**: S/O/D scoring with multiple reviewers

## Prerequisites

- tmux installed and running
- Each agent CLI configured (codex, hermes, claude, etc.)
- Sufficient terminal pane space (3+ panes needed)

## Architecture

```
┌─────────────────────────────────────────┐
│  Orchestrator (current session)         │
│                                         │
│  1. Create review window                │
│  2. Split into N panes                   │
│  3. Send prompts to each pane           │
│  4. Wait for completion                  │
│  5. Capture pane outputs                │
│  6. Derive consensus                    │
│  7. Report findings                     │
└─────────────────────────────────────────┘
```

## Pane Setup

### 3-Pane Layout (Code Review)

```bash
# Create review window
tmux new-window -n review -d

# Split horizontally for 2 panes
tmux split-window -h -t review

# Split right pane vertically for 2 more
tmux split-window -v -t review.1

# Result: 3 panes (review.0, review.1, review.2)
```

### Pane Indexing

Panes are indexed from 1, not 0:
```
review.1 ─────────┐
                 │
review.2 ─────────┼──┐
                 │  │
review.3 ─────────┴──┘
```

**Use `tmux list-panes -t review` to verify** before sending commands.

## Execution Pattern

### Step 1: Send Prompts

```bash
# Pane 1: Codex
tmux send-keys -t review.1 "codex exec 'Review this code and suggest 3 improvements'" Enter

# Pane 2: GLM (via hermes)
tmux send-keys -t review.2 "hermes chat 'Review this code and suggest 3 improvements' --model glm-5.0 --provider zai-glm" Enter

# Pane 3: Claude (via hermes)
tmux send-keys -t review.3 "hermes chat 'Review this code and suggest 3 improvements' --model claude-opus-4-8 --provider openrouter" Enter
```

### Step 2: Wait for Completion

```bash
# Wait for execution (adjust timeout based on task complexity)
sleep 30

# Optional: Monitor pane status
tmux list-panes -t review -F "#{pane_index}: #{pane_current_command}"
```

### Step 3: Capture Outputs

```bash
# Capture each pane output
tmux capture-pane -t review.1 -p > /tmp/review_codex.txt
tmux capture-pane -t review.2 -p > /tmp/review_glm.txt
tmux capture-pane -t review.3 -p > /tmp/review_claude.txt
```

### Step 4: Parse and Compare

```python
# Extract review content from captured files
reviews = {}
for agent in ['codex', 'glm', 'claude']:
    with open(f'/tmp/review_{agent}.txt') as f:
        content = f.read()
        # Extract the review portion (after prompt echo)
        reviews[agent] = parse_review(content)

# Derive consensus
consensus = find_common_points(reviews)
divergences = identify_differences(reviews)
```

### Step 5: Report Findings

```
## 3-Agent Review Results

### Common Findings (Consensus)
• Issue 1: ...
• Issue 2: ...

### Divergent Opinions
• Codex suggested X, GLM suggested Y
• Claude emphasized Z, others missed it

### Recommended Action
Based on consensus: [action]
```

## Common Agent Configurations

### Code Review Trio

| Agent | Model | CLI Command |
|-------|-------|-------------|
| Codex | o3/o4 | `codex exec` |
| GLM | 5.0 | `hermes chat --model glm-5.0 --provider zai-glm` |
| Claude | 4.8 (Opus) | `hermes chat --model claude-opus-4-8 --provider openrouter` |

### DFMEA Analysis Trio

| Agent | Role | Strength |
|-------|------|----------|
| Codex | Cause Analysis | Deep logical reasoning |
| GLM | SOD Scoring | Quantitative assessment |
| Claude | Effect Propagation | System-wide impact |

## Integration with hih-issue

When integrating into `hih-issue` skill:

```python
# Step J에서 3자 리뷰 추가
def run_three_person_review(issue_id, wp_content):
    # 1. Create panes
    tmux.new_window(name="review_issue_{issue_id}")
    tmux.split_window(h=True)
    tmux.split_window(v=True, target="review_issue_{issue_id}.1")
    
    # 2. Send prompts
    prompts = [
        f"codex exec 'Review DFMEA WP for issue #{issue_id}: Focus on Cause analysis'",
        f"hermes chat 'Review DFMEA WP for issue #{issue_id}: Focus on SOD scoring' --model glm-5.0",
        f"hermes chat 'Review DFMEA WP for issue #{issue_id}: Focus on Effect propagation' --model claude-opus-4-8"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        tmux.send_keys(f"review_issue_{issue_id}.{i}", prompt)
    
    # 3. Wait and capture
    sleep(60)  # Adjust based on complexity
    
    reviews = {}
    for agent in ['codex', 'glm', 'claude']:
        reviews[agent] = tmux.capture_pane(f"review_issue_{issue_id}.{i}")
    
    # 4. Derive consensus and update WP
    consensus = derive_dfmea_consensus(reviews)
    update_wp_with_consensus(issue_id, consensus)
```

## Pitfalls

### Pane Index Confusion

**Problem**: tmux panes are 1-indexed, not 0-indexed.
```bash
# Wrong
tmux send-keys -t review.0 "echo" Enter  # Error: can't find pane 0

# Correct
tmux send-keys -t review.1 "echo" Enter
```

**Fix**: Always use `tmux list-panes` to verify pane indices before sending commands.

### Async Execution Race Conditions

**Problem**: Sending commands too fast without waiting causes race conditions.
```bash
# Wrong - all commands sent immediately
tmux send-keys -t review.1 "cmd1" Enter
tmux send-keys -t review.2 "cmd2" Enter  # May execute before cmd1 starts
tmux send-keys -t review.3 "cmd3" Enter
```

**Fix**: Add delays between command sends, or use completion detection.
```bash
tmux send-keys -t review.1 "cmd1" Enter
sleep 1
tmux send-keys -t review.2 "cmd2" Enter
```

### Agent Authentication Failures

**Problem**: CLI agents (codex, claude) need OAuth/login before use.
```bash
# Check auth status
codex login status
claude --login status
```

**Fix**: Document auth requirements in skill prerequisites, check before execution.

### Output Parsing Complexity

**Problem**: Captured output includes shell prompts, command echoes, extraneous text.
```
gint_pcd@host:~$ codex exec '...'
[agent output]
gint_pcd@host:~$ 
```

**Fix**: Use markers to delimit output, or parse with regex:
```python
# Use output markers
prompt = f"echo '===REVIEW_START===' && codex exec '...' && echo '===REVIEW_END==='"
# Parse between markers
```

## Performance Considerations

### Timeout Management

- **Simple reviews**: 10-30 seconds per agent
- **Complex analysis**: 1-5 minutes per agent
- **Code generation**: 5-10 minutes per agent

Set timeout based on task complexity:
```python
def wait_for_completion(complexity='medium'):
    timeouts = {
        'simple': 30,
        'medium': 120,
        'complex': 300
    }
    return timeouts.get(complexity, 120)
```

### Resource Usage

- Each pane uses ~100-500MB RAM
- 3 panes = ~300-1500MB RAM total
- Monitor with `htop` or `free -h`

## Cleanup

```bash
# Close review window when done
tmux kill-window -t review

# Or kill pane by pane
for i in {1..3}; do
    tmux kill-pane -t review.$i
done
```

## Verification

```bash
# Verify panes are running
tmux list-windows | grep review

# Verify pane count
tmux list-panes -t review | wc -l  # Should match expected count

# Verify output capture
ls -lh /tmp/review_*.txt
```

## References

- [tmux man page](https://man7.org/linux/man-pages/man1/tmux.1.html)
- [Codex CLI](https://github.com/openai/codex)
- [hih-issue skill](../hih-issue/) - Integration target