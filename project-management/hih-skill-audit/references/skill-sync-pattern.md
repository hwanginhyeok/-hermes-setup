# Skill Sync Pattern - Cross-Device Synchronization

## Problem

Skills managed in `~/.hermes/skills/` need to be synchronized between devices (desktop ↔ notebook).

## Solution

Git-based synchronization with pull/push workflow.

## Repository

- **URL**: https://github.com/hwanginhyeok/-hermes-setup.git
- **Local path**: `~/.hermes/skills/`
- **Branch**: main

## Workflow

### Update Skills (Primary Device)

```bash
cd ~/.hermes/skills

# 1. Make skill updates
#    - Edit SKILL.md
#    - Add references/ or scripts/
#    - Test with skill_view()

# 2. Stage changes
git add hih-dual/SKILL.md ui-ux/hih-design-fix/SKILL.md

# 3. Commit with clear message
git commit -m "feat: update hih skills to latest models

- hih-dual: Opus 4.8 + GLM 5.0 + Codex 5.5
- hih-design-fix: Opus 4.8 + GLM 5.0 + 3자 리뷰
- hih-design-new: Opus 4.8 + GLM 5.0 + 3자 리뷰 추가"

# 4. Push to GitHub
git push origin main
```

### Sync Skills (Secondary Device - e.g., Notebook)

**Option 1: Manual Pull**

```bash
cd ~/.hermes/skills
git pull origin main
```

**Option 2: Use Sync Script**

```bash
# Sync script created at ~/sync_skills_from_repo.sh
bash ~/sync_skills_from_repo.sh
```

**Script Features**:
- Auto-detects existing `.hermes/skills/` directory
- Uses `git pull` if exists, `git clone` if not
- Reports sync status and skill count

### Auto-Sync via Cron

```bash
# Add to crontab
(crontab -l 2>/dev/null; echo "0 8 * * * bash ~/sync_skills_from_repo.sh") | crontab -
```

## Usage Verification

```bash
# Check git status
cd ~/.hermes/skills && git status

# Check last commit
git log --oneline -1

# Verify skill availability
skills_list | grep hih
```

## Case Study: Model Update 2026-06-04

**Task**: Update hih skills to GLM 5.0, Opus 4.8, Codex 5.5

**Steps**:
1. Updated 3 skill files (hih-dual, hih-design-fix, hih-design-new)
2. Committed with descriptive message
3. Pushed to GitHub: `ab5e6e6`
4. Created sync script for notebook usage

**Result**:
- All 21 hih skills verified working
- Models confirmed updated in skill files
- Config.yaml updated with new providers
- Sync script ready for notebook deployment

## Pitfalls

1. **Forgot to stage files**: `git add` before commit
   - Symptom: "Changes not staged for commit"
   - Fix: `git add <files>` or `git add -A`

2. **Sync on wrong branch**: Non-main branch causes confusion
   - Fix: Always `git checkout main` before sync

3. **Local changes uncommitted**: Git pull fails with conflicts
   - Fix: Commit or stash local changes first
   ```bash
   git stash
   git pull origin main
   git stash pop  # If you want local changes back
   ```

4. **Sync script not executable**: Permission denied
   - Fix: `chmod +x ~/sync_skills_from_repo.sh`

5. **Skills directory not git repo**: No remote configured
   - Fix: Initialize and set remote
   ```bash
   cd ~/.hermes/skills
   git init
   git remote add origin https://github.com/hwanginhyeok/-hermes-setup.git
   git branch -M main
   git pull origin main
   ```

## Related Files

- `~/sync_skills_from_repo.sh` - Sync script (created 2026-06-04)
- `~/.hermes/skills/.git/` - Git repository
- `references/model-update-patterns.md` - Model update workflow