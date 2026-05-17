---
name: multi-repo-git-consolidation
description: "Git consolidation across multiple repositories: status aggregation, commit batching, push coordination"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Git, Multi-repo, Consolidation, Status, Batch, Push]
    related_skills: [github-pr-workflow, github-repo-management]
---

# Multi-Repository Git Consolidation

Consolidate git operations across multiple repositories. Useful for:
- PM-style multi-project health checks
- Batch committing/pushing before reboots or deployments
- Aggregating uncommitted file reports
- Comparing git configurations across repos

## Core Workflow

### 1. Aggregate Status Across All Repos

```bash
# If you have a projects.yaml registry (like project-manager)
for proj in $(yq eval '.projects[].path' projects.yaml); do
  echo "=== $proj ==="
  cd "$proj" 2>/dev/null && git status -sb && git log -1 --oneline
  echo ""
done

# Manual list alternative
for proj in stock insung_blog physical_AI_rs500 music-lab; do
  echo "=== $proj ==="
  cd "/home/window11/$proj" 2>/dev/null && git status -sb && git log -1 --oneline
  echo ""
done
```

### 2. Check Remote Configuration

```bash
# Verify all repos have remotes configured
for proj in stock insung_blog physical_AI_rs500; do
  echo "=== $proj ==="
  cd "/home/window11/$proj" && git remote -v 2>/dev/null || echo "NO GIT"
  echo ""
done
```

### 3. Batch Push (with Confirmation)

```bash
# DRY RUN first - see what would be pushed
for proj in stock insung_blog music-lab; do
  cd "/home/window11/$proj" && git push --dry-run --all && git push --dry-run --tags
done

# Actual push (only after dry run confirms)
for proj in stock insung_blog music-lab; do
  cd "/home/window11/$proj" && git push --all && git push --tags
done
```

## Report Format

After aggregation, present a concise report:

```
총 N개 프로젝트 중 uncommitted 파일:
  ⚠️ 프로젝트명: N파일 (마지막 커밋: N일 전)
  ⚠️ 프로젝트명: N파일 (마지막 커밋: 오늘)
  ✅ 프로젝트명: 0파일 (N일 전)
```

## Pitfalls

### Avoid Silent Failures
```bash
# BAD - silent on missing directories
for proj in $LIST; do
  cd "/path/$proj" && git push  # fails silently if cd fails
done

# GOOD - explicit checking
for proj in $LIST; do
  if [ -d "/path/$proj" ]; then
    cd "/path/$proj" && git push
  else
    echo "SKIP: $proj (not found)"
  fi
done
```

### Cross-Machine Merge Conflicts (Rebase Pattern)

When projects are edited on multiple machines (laptop vs desktop), you'll encounter push rejections:

```bash
# Symptom: push rejected with "fetch first" or "non-fast-forward"
error: could not push some refs to 'https://github.com/hwanginhyeok/HIH_2.git'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally.
```

**Resolution Workflow:**

```bash
# Option 1: Rebase (cleaner history, preserves linear timeline)
cd /home/window11/HIH_2
git pull --rebase
git push

# Option 2: If rebase conflicts occur (automatic merge failed)
cd /home/window11/포트폴리오  # example conflicted repo
git pull --rebase
# CONFLICT detected: CURRENT_TASK.md, FINISHED_TASK.md, TASK.md

# Step 1: Check conflict status
git status
# Output: "both modified: CURRENT_TASK.md"

# Step 2: Read conflicted files to understand divergences
# Look for conflict markers: <<<<<<< HEAD, =======, >>>>>>> <commit-hash>
read_file CURRENT_TASK.md  # or cat directly

# Step 3: Manually merge - choose strategy:
#   - Keep HEAD version (local)
#   - Keep incoming version (remote)
#   - Merge both (union)
# Write merged file:
write_file CURRENT_TASK.md  # with merged content

# Step 4: Stage resolved files
git add CURRENT_TASK.md FINISHED_TASK.md TASK.md

# Step 5: Continue rebase (may trigger editor for commit message)
git rebase --continue
# If editor fails: use -m flag
git commit -m "Merge conflict resolution - 집/노트북 병합"
git rebase --continue

# Step 6: Push successful merge
git push
```

**Common Conflict Patterns:**

1. **Task list divergence**: One machine added new tasks, another completed different ones
   - Strategy: Union merge + manual de-duplication
   - Check task IDs to avoid duplicates

2. **Same file, different sections**: Edits don't overlap
   - Strategy: Manual merge keeping both changes

3. **Metadata updates**: Dates, counts, status lines
   - Strategy: Take most recent, manually verify counts

**Prevention:**
- Pull before starting work on a machine: `git pull --rebase`
- Commit frequently to reduce divergence window
- Use task IDs consistently across machines

### HIH_2 Pattern - Sync Before Commit
Some projects may be edited on multiple machines (e.g., laptop vs desktop):
- Check git log for recent commits from other locations
- Verify last commit author/timestamp
- Pull before pushing if cross-machine editing is detected
- **Alert threshold**: >1000 uncommitted files likely indicates cross-machine sync issue

### Git Status Parsing
`git status -sb` gives you:
- Branch name and ahead/behind info
- Uncommitted counts (not raw file counts)

For raw file counts:
```bash
git status --porcelain | wc -l
```

### yq Dependency
Many project-manager workflows depend on `yq`:
```bash
# Install if missing
sudo snap install yq  # OR
pip install yq
```

## Tools Integration

### project-manager CLI
If using the project-manager system:
```bash
python3 pm.py status      # Aggregated status dashboard
python3 pm.py health      # Directory health diagnosis
```

### Git Config Comparison
Compare git configs across environments:
```bash
diff ~/.hermes/config.yaml /path/to/hermes-eval/.hermes/config.yaml
```

## Reference Material

- **references/pm-workflow.md** - Complete PM git consolidation workflow with project-manager system specifics
- **references/merge-conflict-resolution-case-study.md** - Real-world cross-machine conflict resolution transcript (포트폴리오 project 2026-05-12)
- **templates/pm-report.md** - Korean report template for git status summaries
- **scripts/git-status-scan.sh** - Automated script for scanning and aggregating git status across repos
- **scripts/resolve-rebase-conflict.sh** - Helper script for automated conflict resolution during rebase

## Examples

### Complete PM Git Consolidation (End-to-End)

**Scenario**: User requests "git 정리해보자" - consolidate all project repos and push to GitHub

```bash
# Phase 1: READ - Get overview
python3 pm.py status
# Output: Shows 10 projects with uncommitted counts

# Phase 2: DETAILED STATUS - Per-project inspection
for proj in stock insung_blog physical_AI_rs500 physical_AI_Engiuniverse my-politics-stats music-lab HIH_2 포트폴리오 knowledge-base be-a-studio; do
  echo "=== $proj ==="
  cd "/home/window11/$proj" 2>/dev/null
  git status -sb
  git log -1 --oneline
  echo ""
done

# Phase 3: VERIFY REMOTES
for proj in stock insung_blog physical_AI_rs500 physical_AI_Engiuniverse my-politics-stats music-lab HIH_2 포트폴리오 knowledge-base be-a-studio; do
  echo "=== $proj ==="
  cd "/home/window11/$proj" 2>/dev/null
  git remote -v 2>/dev/null || echo "NO GIT"
  echo ""
done

# Phase 4: BATCH COMMIT (all uncommitted changes)
for proj in stock insung_blog physical_AI_rs500 physical_AI_Engiuniverse my-politics-stats music-lab HIH_2 포트폴리오 knowledge-base be-a-studio; do
  echo "=== Committing $proj ==="
  cd "/home/window11/$proj" 2>/dev/null
  git add -A
  git commit -m "$(date +'%Y-%m-%d') Git 정리 - PM 자동화"
  echo ""
done

# Phase 5: BATCH PUSH (handle conflicts)
for proj in stock insung_blog physical_AI_rs500 physical_AI_Engiuniverse my-politics-stats music-lab HIH_2 포트폴리오 knowledge-base be-a-studio; do
  echo "=== Pushing $proj ==="
  cd "/home/window11/$proj" 2>/dev/null
  git push
  # If push fails, see "Cross-Machine Merge Conflicts" section
  echo ""
done

# Phase 6: VERIFY FINAL STATE
python3 pm.py status
# Expected: "✅ 전체 정상" (all clean)
```

**Report format (Korean):**
```
## Git 정리 완료 최종 보고

### 결과 요약
**전부 완료 (10/10)** ✅
- 프로젝트1: ✅ 커밋 + push
- 프로젝트2: ✅ 커밋 + push
...

### 충돌 해결
- 프로젝트: ✅ 충돌 수동 병합 + rebase + push
  - CURRENT_TASK.md: 집 B1-01 + 노트북 4-5/4-7 병합
  - FINISHED_TASK.md: 38개 태스크 유지
  - TASK.md: 최종 수정일 갱신

### 최종 상태
- uncommitted 파일: 0
- 모든 프로젝트 GitHub와 동기화 완료
```

### PM Health Check (from this session)
```bash
# 1. Get overview
python3 pm.py status

# 2. Detailed status per project
for proj in stock insung_blog physical_AI_rs500; do
  echo "=== $proj ==="
  cd "/home/window11/$proj"
  git status -sb
  git log -1 --oneline
  echo ""
done

# 3. Check remotes
for proj in stock insung_blog; do
  cd "/home/window11/$proj" && git remote -v
done

# 4. Identify critical uncommitted repos (e.g., HIH_2 with 6669 files)
```

### Pre-Reboot Safety Push
```bash
# 1. Check all repos
for dir in */; do
  if [ -d "$dir/.git" ]; then
    echo "=== $dir ==="
    cd "$dir"
    git status --short
    cd ..
  fi
done

# 2. Push all safe repos
for dir in */; do
  if [ -d "$dir/.git" ]; then
    cd "$dir"
    echo "Pushing $dir..."
    git push --all
    cd ..
  fi
done
```
