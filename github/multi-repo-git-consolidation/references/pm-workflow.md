# PM Git Consolidation Workflow

## Context: project-manager System

The PM (Project Manager) orchestrates 8+ projects. Each has:
- A git repo (GitHub: hwanginhyeok/*)
- A tmux session
- A CURRENT_TASK.md task file
- Services (e.g., blog-api, music-bot)

## Standard PM Git Health Check

### Step 1: Overview with pm.py

```bash
python3 pm.py status
```

Output shows:
- Project disk usage
- Uncommitted file counts
- Last commit date
- Active task counts
- Blockers

### Step 2: Detailed Status per Project

```bash
cd /home/window11/project-manager
for proj in stock insung_blog physical_AI_rs500 physical_AI_Engiuniverse my-politics-stats music-lab HIH_2 포트폴리오 knowledge-base be-a-studio; do
  echo "=== $proj ==="
  if [ -d "/home/window11/$proj" ]; then
    cd "/home/window11/$proj"
    git status -sb
    git log -1 --oneline
    echo ""
  fi
done
```

### Step 3: Remote Configuration Verification

```bash
for proj in stock insung_blog physical_AI_rs500 physical_AI_Engiuniverse my-politics-stats music-lab HIH_2 포트폴리오 knowledge-base be-a-studio; do
  echo "=== $proj ==="
  if [ -d "/home/window11/$proj" ]; then
    cd "/home/window11/$proj"
    git remote -v 2>/dev/null || echo "NO GIT"
    echo ""
  fi
done
```

### Step 4: Configuration Comparison (Hermes Example)

```bash
# Check for git management
cd /home/window11/.hermes && git remote -v 2>/dev/null || echo "NO GIT"

# Compare configs
diff ~/.hermes/config.yaml /path/to/hermes-eval/.hermes/config.yaml

# Check specific settings
cat ~/.hermes/config.yaml | grep -A5 "custom_providers:"
cat /path/to/hermes-eval/.hermes/config.yaml | grep -A5 "custom_providers:"
```

## Critical Alert Thresholds

- **HIH_2 > 1000 uncommitted**: Likely cross-machine sync issue (laptop vs desktop)
- **Any project > 30 days since last commit**: Stale project, possible archival
- **be-a-studio with uncommitted**: Active video editing project, prioritize

## Report Template

```
## Git 정리 보고서

### 전체 현황
총 10개 프로젝트 중 uncommitted 파일:
  ⚠️ 프로젝트명: N파일 (마지막 커밋: N일 전)
  ✅ 프로젝트명: 0파일 (N일 전)

### 원격 저장소 설정
- hwanginhyeok/repo1
- hwanginhyeok/repo2
...

### Hermes 설정 비교 (if applicable)
| 항목 | 설정1 | 설정2 |
|------|-------|-------|
| 모델 | ... | ... |

### 권장 사항
1. 긴급 커밋 필요: [프로젝트명] N파일
2. 정기 커밋 권장: [프로젝트명]
```

## Known Project Quirks

### HIH_2
- **Pattern**: Laptop vs Desktop editing
- **Symptom**: 6669 uncommitted files
- **Action**: Check git log for recent commits, verify sync before committing

### be-a-studio
- **Type**: Video editing project
- **Pattern**: Large binary files (Premiere/AE project files)
- **Caution**: Don't add large binaries to git without .gitignore rules

### 자율주행 / 포트폴리오
- **Status**: 보류 (paused)
- **Note**: effort_level=low, cron may still be active

## Commands Reference

```bash
# Quick uncommitted count
git status --porcelain | wc -l

# Show branch + ahead/behind
git status -sb

# Last commit info
git log -1 --oneline

# Remote URLs
git remote -v

# Find git repos in parent dir
find /home/window11 -maxdepth 2 -name ".git" -type d
```
