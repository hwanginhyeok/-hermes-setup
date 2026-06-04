---
name: 3-person-review
description: "Parallel 3-person review system (Codex + GLM + Claude) with tmux panes or delegate_task"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Review, Code-Review, Parallel-Execution, Multi-Model, Tmux, Quality]
---

# 3-Person Review System

Run parallel code/DFMEA/issue reviews across 3 LLMs (Codex + GLM + Claude) for quality and perspective diversity.

## When to use

- DFMEA analysis (hih-issue skill integration)
- Critical code review before merge
- Design document review
- Issue root cause analysis
- Any decision requiring multiple perspectives

## Two Execution Modes

### Mode 1: tmux Panes (CLI-based)

Use when you have CLI tools installed and want visual control.

**Prerequisites:**
- tmux installed
- Codex: `codex login --device-auth` (OAuth required)
- Claude: `claude --login` (if using Claude CLI)
- GLM: API key configured in Hermes

**Workflow:**

```bash
# 1. Create review window
tmux new-window -n review -d
tmux split-window -h -t review
tmux split-window -v -t review.1

# Result: 3 panes (0, 2, 3)

# 2. Send review tasks to each pane
# Pane 0 (Codex)
tmux send-keys -t review.0 "codex exec 'Review this code...'" Enter

# Pane 1 (GLM) - uses Hermes API
tmux send-keys -t review.1 "hermes chat 'Review this code...' --model glm-5.0" Enter

# Pane 2 (Claude) - uses Hermes API
tmux send-keys -t review.2 "hermes chat 'Review this code...' --model claude-opus-4-8" Enter

# 3. Wait for completion
sleep 30  # adjust based on task complexity

# 4. Capture results
codex_result=$(tmux capture-pane -t review.0 -p)
glm_result=$(tmux capture-pane -t review.1 -p)
claude_result=$(tmux capture-pane -t review.2 -p)

# 5. Save results
echo "$codex_result" > /tmp/codex_review.txt
echo "$glm_result" > /tmp/glm_review.txt
echo "$claude_result" > /tmp/claude_review.txt

# 6. Cleanup
tmux kill-window -t review
```

**Pitfalls:**
- ⚠️ **Codex OAuth required**: Without `codex login --device-auth`, returns `401 Unauthorized`
- ⚠️ **Claude CLI login required**: Without `claude --login`, returns `Not logged in`
- ⚠️ **Pane numbering**: After splits, panes are 1, 2, 3 (not 0, 1, 2) - verify with `tmux list-panes -t review`
- ⚠️ **Authentication timing**: OAuth must complete before Codex commands work

### Mode 2: delegate_task (API-based) — RECOMMENDED

Use when you want reliable API-based execution without CLI logins.

**Prerequisites:**
- Hermes API configured for each provider
- Provider accounts: OpenRouter (Claude), Z.AI (GLM), OpenAI (Codex)

**Workflow:**

```python
from delegate_task import delegate_task

results = delegate_task(
    tasks=[
        {
            "goal": "DFMEA analysis: VCU CAN failure. Identify Function, Failure Mode, Effect.",
            "model": "glm-5.0",
            "provider": "zai-glm",
            "timeout": 120
        },
        {
            "goal": "DFMEA analysis: VCU CAN failure. Identify Function, Failure Mode, Effect.",
            "model": "claude-opus-4-8",
            "provider": "openrouter",
            "timeout": 120
        },
        {
            "goal": "DFMEA analysis: VCU CAN failure. Identify Function, Failure Mode, Effect.",
            "model": "gpt-4",
            "provider": "openai",
            "timeout": 120
        }
    ],
    timeout=300  # 5 minutes total
)

# Results is a list of {task_index, status, summary, error}
for result in results:
    if result["status"] == "completed":
        print(f"Reviewer {result['task_index']}: {result['summary']}")
```

**Advantages over tmux:**
- ✅ No CLI login required
- ✅ Timeout handling built-in
- ✅ Parallel execution managed automatically
- ✅ Error recovery easier

**Pitfalls:**
- ⚠️ **Timeout sensitive**: Default may be too short for complex tasks. Set appropriate timeout per task.
- ⚠️ **API rate limits**: Parallel calls may hit provider limits. Add delays if needed.

## Result Synthesis

After collecting 3 reviews:

```python
# 1. Extract key findings from each
reviews = [codex_result, glm_result, claude_result]

# 2. Identify commonalities
common_points = find_common_elements(reviews)

# 3. Identify differences
differences = find_unique_elements(reviews)

# 4. Synthesize final conclusion
final = {
    "consensus": common_points,
    "perspectives": {
        "codex": unique_codex,
        "glm": unique_glm,
        "claude": unique_claude
    },
    "recommendation": synthesize(common_points, differences)
}
```

## Integration with hih-issue Skill

The 3-person review system is designed to integrate into the hih-issue skill's DFMEA analysis mode:

```python
# In hih-issue skill, after Step H (Multi-FM identification)

# Step I-1: 3-person review
reviews = delegate_task(tasks=[...])  # Mode 2 preferred

# Step I-2: Synthesis
synthesis = synthesize_reviews(reviews)

# Step I-3: Update WP with synthesis
wp_content = update_working_paper(wp_content, synthesis)
```

## Example Output Format

```
=== 3-Person DFMEA Review ===

[Common Consensus]
- Function: All reviewers identified CAN communication as core function
- Failure Mode: All identified CAN transmission failure
- Effect: All identified vehicle control impact

[Unique Perspectives]
Codex: "CAN message transmission function" - technical focus
GLM: "CAN communication control" - system focus
Claude: "CAN interface connection" - safety-focused

[Final Recommendation]
Function: VCU CAN message transmission function
Failure Mode: CAN message transmission failure
Effect: Autonomous driving stop and safe mode transition
Severity: H (safety impact)
Occurrence: M (occurs under specific conditions)
Detection: M (CAN monitoring possible)
AP: H (urgent improvement needed)
```

## Template: 3-Person Review Script

See `scripts/run_3person_review.py` for a ready-to-use script that handles:
- tmux pane creation
- Task distribution
- Result capture
- Synthesis
- Cleanup