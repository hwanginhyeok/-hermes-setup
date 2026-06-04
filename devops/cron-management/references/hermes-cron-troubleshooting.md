# Hermes Cron Troubleshooting - Critical Errors

## Gateway Not Running

**Symptom:** All cronjobs show "Gateway is not running — jobs won't fire automatically"

**Error message:**
```
⚠️  Gateway is not running — jobs won't fire automatically.
   Start it with: hermes gateway install
```

**Recovery:**
```bash
hermes gateway install
hermes gateway start
hermes gateway status  # Should show "active (running)"
```

**WSL Note:** WSL systemd services may not survive WSL restarts. Consider running in foreground instead:
```bash
# Or use tmux/screen for persistence:
tmux new -s hermes 'hermes gateway run'
```

**Context:** Gateway is the Hermes cron daemon that triggers scheduled jobs. Without it, jobs are registered but never execute.

**Verification:** `hermes gateway status` should show `Active: active (running)`.

---

## No LLM Provider Configured

**Symptom:** Cronjobs fail with `RuntimeError: No LLM provider configured`

**Error message:**
```
RuntimeError: No LLM provider configured. 
Run `hermes model` to select a provider, or run `hermes setup` for first-time configuration.
```

**Recovery:**
```bash
hermes model
# Select a provider (e.g., openrouter, anthropic, z.ai)
```

**Affected jobs:**
- HIH Daily Standup + DFMEA Check
- HIH Cron Monitoring Daily Report
- Production Status Daily Report

**Context:** Hermes cronjobs require an LLM provider to execute prompts. Without provider configuration, jobs fail immediately when they try to run.

**Verification:** Check `~/.hermes/config.yaml`:
```yaml
model:
  default: glm-4.7
  provider: zai-glm
```

**Common providers:**
- `zai-glm` (GLM-4.7) - Custom provider via Z.ai
- `openrouter` (Claude Sonnet/Opus) - Multi-model routing
- `anthropic` (Claude directly) - Official Anthropic API

---

## Diagnostic Priority (2026-06-01)

When Hermes cronjobs fail with "No LLM provider configured":

1. **Check Gateway first:** `hermes gateway status`
   - If inactive → `hermes gateway start`
   - Most common cause on fresh installs

2. **Check provider second:** `cat ~/.hermes/config.yaml | grep -A2 "^model:"`
   - If missing → `hermes model`
   - Usually already configured if Gateway was issue

**User Environment (2026-06-01):**
- Provider: `zai-glm` with `glm-4.7` (already configured)
- Issue was missing Gateway daemon
- Error message "No LLM provider" was misleading - actual cause was Gateway not running

---

## Manual Job Testing

After fixing Gateway or provider issues, test jobs manually:

```bash
# Test specific job
cronjob action=run <job_id>

# Example jobs:
# a3a1476442f9 - HIH Daily Standup + DFMEA Check
# 25414ac1161a - HIH Cron Monitoring Daily Report
# d4491c9f3454 - Production Status Daily Report
```

**Verify execution:**
```bash
# Check output logs
ls -la ~/.hermes/cron/output/<job_id>/

# Latest run
ls -lt ~/.hermes/cron/output/<job_id>/ | head -2

# View metadata
cat ~/.hermes/cron/output/<job_id>/YYYY-MM-DD_HH-MM-SS/metadata.json
```

---

## Cronjob Error Log Analysis

When a job fails, check the metadata file:

```bash
# Find latest run
latest_dir=$(ls -t ~/.hermes/cron/output/<job_id>/ | head -1)
cat ~/.hermes/cron/output/<job_id>/$latest_dir/metadata.json
```

**Key fields:**
- `started_at`: When job started
- `completed_at`: When job finished (null if still running)
- `error`: Error message if failed

**Common errors:**
- Gateway not running → Jobs never start
- No LLM provider → Jobs fail immediately
- Missing skills → Job fails to load skill module
- Network issues → API calls timeout

---

## Full Recovery Checklist

When all cronjobs show errors:

1. ✅ Check Gateway: `hermes gateway status`
   - If inactive: `hermes gateway start`
   
2. ✅ Check Provider: `cat ~/.hermes/config.yaml | grep -A2 "^model:"`
   - If missing: `hermes model`
   
3. ✅ Test single job: `cronjob action=run <job_id>`
   
4. ✅ Verify execution: `ls -la ~/.hermes/cron/output/<job_id>/`
   
5. ✅ Check output: `cat ~/.hermes/cron/output/<job_id>/latest/metadata.json`

**Success criteria:**
- Gateway: `Active: active (running)`
- Provider: Configured in `~/.hermes/config.yaml`
- Job: `last_status: success` in `cronjob action=list`
- Output: Files exist in `~/.hermes/cron/output/<job_id>/`
