#!/bin/bash
# Multi-repo git status aggregator
# Usage: ./git-status-scan.sh [project_root]

PROJECT_ROOT="${1:-/home/window11}"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Git Status Consolidation Report                        ║"
echo "╠════════════════════════════════════════════════════════╣"
echo ""

# Find all git repos
total_repos=0
uncommitted_repos=0
declare -A uncommitted_counts

while IFS= read -r -d '' git_dir; do
  repo_dir=$(dirname "$git_dir")
  repo_name=$(basename "$repo_dir")
  cd "$repo_dir" || continue

  # Get status
  uncommitted=$(git status --porcelain 2>/dev/null | wc -l)
  branch=$(git branch --show-current 2>/dev/null)
  last_commit=$(git log -1 --format="%cr (%h)" 2>/dev/null)
  remote=$(git remote get-url origin 2>/dev/null || echo "NO_REMOTE")

  total_repos=$((total_repos + 1))

  if [ "$uncommitted" -gt 0 ]; then
    echo "  ⚠️  $repo_name [$branch]"
    echo "     Uncommitted: $uncommitted files"
    echo "     Last: $last_commit"
    echo "     Remote: $remote"
    echo ""
    uncommitted_counts[$repo_name]=$uncommitted
    uncommitted_repos=$((uncommitted_repos + 1))
  else
    echo "  ✅ $repo_name [$branch]"
    echo "     Last: $last_commit"
    echo "     Remote: $remote"
    echo ""
  fi

done < <(find "$PROJECT_ROOT" -maxdepth 2 -name ".git" -type d -print0 2>/dev/null)

echo "─────────────────────────────────────────────────────────"
echo "  총 $total_repos개 레포지토리"
echo "  ⚠️  $uncommitted_repos개 레포지토리에 uncommitted 파일"
echo ""

# Show repos with most uncommitted files (threshold > 10)
if [ $uncommitted_repos -gt 0 ]; then
  echo "─────────────────────────────────────────────────────────"
  echo "  🚨 긴급 커밋 필요 (10+파일):"
  for repo in "${!uncommitted_counts[@]}"; do
    count=${uncommitted_counts[$repo]}
    if [ "$count" -ge 10 ]; then
      echo "     $repo: $count 파일"
    fi
  done | sort -t: -k2 -rn
  echo ""
fi
