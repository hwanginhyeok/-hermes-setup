# Hermes Cron Job Model Mismatch Troubleshooting

**Issue:** Cron jobs fail with "No LLM provider configured" even though the user's session has a working provider.

**Root cause:** Cron jobs have their own model/provider configuration that can differ from the user's active session. When a cron job uses a provider without a corresponding API key in `.env`, execution fails.

## Discovery Timeline (2026-06-04)

### Initial State
- User session: Working with `glm-4.7` / `zai-glm` provider
- 3 cron jobs in error state:
  - `a3a1476442f9` - HIH Daily Standup + DFMEA Check
  - `25414ac1161a` - HIH Cron Monitoring Daily Report
  - `d4491c9f3454` - Production Status Daily Report

### Investigation Process

1. **Check cron job output logs:**
   ```bash
   ls -lt ~/.hermes/cron/output/a3a1476442f9/
   # Found: 2026-06-04_09-00-20.md
   ```

2. **Read error details:**
   ```bash
   tail -30 ~/.hermes/cron/output/a3a1476442f9/2026-06-04_09-00-20.md
   # Error: RuntimeError: No LLM provider configured
   ```

3. **Check cron job configuration:**
   ```bash
   cronjob action=list | grep -A 15 "a3a1476442f9"
   # Result:
   #   model: anthropic/claude-sonnet-4
   #   provider: openrouter
   ```

4. **Check user's active session config:**
   ```bash
   hermes status | grep -E "Model:|Provider:"
   # Result:
   #   Model:        glm-4.7
   #   Provider:     zai-glm
   ```

5. **Check .env for API keys:**
   ```bash
   grep -E "OPENROUTER_API_KEY|Z_AI_API_KEY|GLM_API_KEY" ~/.hermes/.env
   # Result:
   #   OPENROUTER_API_KEY= (empty)
   #   Z_AI_API_KEY=221e72...Yorl (present)
   ```

### Root Cause Identified

**Mismatch discovered:**
- Cron jobs: Configured to use `openrouter` provider
- `.env`: No `OPENROUTER_API_KEY` set
- User session: Working with `zai-glm` provider (has API key)

**Why this happens:**
- Cron jobs execute in isolated sessions
- They don't inherit the user's active session provider
- Each job has its own `model` and `provider` setting
- If that provider's API key is missing from `.env`, the job fails

## Resolution

### Step 1: Update all cron jobs to match session config

```bash
# Update each failing job
cronjob action=update job_id=a3a1476442f9 --model glm-4.7 --provider zai-glm
cronjob action=update job_id=25414ac1161a --model glm-4.7 --provider zai-glm
cronjob action=update job_id=d4491c9f3454 --model glm-4.7 --provider zai-glm

# Update remaining jobs for consistency
cronjob action=update job_id=ac8568bf1d8a --model glm-4.7 --provider zai-glm
cronjob action=update job_id=966d7b80f25c --model glm-4.7 --provider zai-glm
cronjob action=update job_id=ca0a29f19baf --model glm-4.7 --provider zai-glm
cronjob action=update job_id=e09bcf88318f --model glm-4.7 --provider zai-glm
cronjob action=update job_id=ec9224b54478 --model glm-4.7 --provider zai-glm
cronjob action=update job_id=9b4323865299 --model glm-4.7 --provider zai-glm
```

### Step 2: Ensure API key exists in .env (optional if key already present)

```bash
# Check if key exists
grep "^Z_AI_API_KEY=" ~/.hermes/.env

# If empty, add it (replace with actual key)
sed -i 's|^Z_AI_API_KEY=.*|Z_AI_API_KEY=your_actual_key_here|' ~/.hermes/.env
```

### Step 3: Verify fix with manual run

```bash
# Trigger job manually
cronjob action=run job_id=a3a1476442f9

# Wait for execution (30-60 seconds)
sleep 60

# Check latest output
ls -lt ~/.hermes/cron/output/a3a1476442f9/ | head -2
tail -30 ~/.hermes/cron/output/a3a1476442f9/<latest_file>.md

# Success indicators:
# - No "RuntimeError: No LLM provider configured"
# - Job completed with output
# - Report files created (e.g., HIH_Claude/standup_daily/YYYY-MM-DD.md)
```

## Prevention

### When changing user's session provider

After running `hermes model` to change the active provider:

```bash
# 1. Get new provider info
hermes status | grep -E "Model:|Provider:"

# 2. List all cron jobs
cronjob action=list

# 3. Update each job to match
# (Batch update loop if many jobs)
```

### When adding new cron jobs

Always specify the model/provider that matches the user's session:

```bash
# Before creating, check current provider
hermes status | grep -E "Model:|Provider:"

# Create job with matching config
cronjob action=create \
  --name "My Job" \
  --schedule "0 9 * * *" \
  --model glm-4.7 \
  --provider zai-glm \
  --prompt "Job prompt here"
```

## Quick Reference Commands

### Check cron job model:
```bash
cronjob action=list | grep -E "job_id|model:|provider:" | paste - - -
```

### Check user session model:
```bash
hermes status | grep -E "Model:|Provider:"
```

### Check .env for API keys:
```bash
grep -E "_API_KEY=" ~/.hermes/.env | grep -v "^#"
```

### Update single job:
```bash
cronjob action=update job_id=<id> --model <model> --provider <provider>
```

### Batch update all jobs:
```bash
# Extract all job IDs
cronjob action=list --format json | jq -r '.[].job_id' | while read id; do
  cronjob action=update job_id=$id --model glm-4.7 --provider zai-glm
done
```

## Error Log Examples

### Before Fix (Model Mismatch)
```
# Cron Job: HIH Daily Standup + DFMEA Check (FAILED)
Job ID: a3a1476442f9
Run Time: 2026-06-04 09:00:20

## Error
RuntimeError: No LLM provider configured. Run `hermes model` to select a provider, or run `hermes setup` for first-time configuration.
```

### After Fix (Success)
```
# Cron Job: HIH Daily Standup + DFMEA Check
Job ID: a3a1476442f9
Run Time: 2026-06-04 09:28:36

[Job output with successful execution]

**✅ 브리핑 저장 완료**: `HIH_Claude/standup_daily/2026-06-04.md`
```

## Related Issues

### Gateway Not Running
If jobs show "Gateway is not running" instead of provider error:
```bash
hermes gateway install
```

### Session vs Cron Config
Remember: User session config (`config.yaml`) and cron job config are **separate**. They must be synchronized manually.

## Provider-Specific API Keys

| Provider  | API Key Variable      | Example Format          |
|-----------|-----------------------|-------------------------|
| openrouter| OPENROUTER_API_KEY    | sk-or-...               |
| zai-glm   | Z_AI_API_KEY          | 221e72...Yorl           |
| zai-glm   | GLM_API_KEY           | 221e72...Yorl           |
| anthropic | ANTHROPIC_API_KEY     | sk-ant-...              |
| openai    | OPENAI_API_KEY        | sk-...                  |
| google    | GOOGLE_API_KEY        | AIza...                 |

**Note:** Some providers support multiple variable names (e.g., `Z_AI_API_KEY` and `GLM_API_KEY` both work for zai-glm).

## Summary

**Key insight:** Cron job failures with "No LLM provider configured" are usually **model mismatch** issues, not missing provider configuration. The fix is to sync the cron job's model/provider settings with the user's active session and verify the required API key exists in `.env`.
