#!/bin/bash
# Git conflict resolution helper for rebase conflicts
# Usage: ./resolve-rebase-conflict.sh <project_path>

set -e

PROJECT_PATH="${1:-.}"
cd "$PROJECT_PATH"

echo "=== Git Rebase Conflict Resolution ==="
echo "Project: $(pwd)"
echo ""

# Check if we're in a rebase
if ! git status | grep -q "interactive rebase in progress\|rebasing"; then
    echo "ERROR: No rebase in progress"
    echo "Run 'git pull --rebase' first to trigger conflict"
    exit 1
fi

# Show conflicted files
echo "Conflicted files:"
git status | grep "both modified" | sed 's/.*both modified:   /  - /'
echo ""

# Prompt for resolution strategy
echo "Resolution options:"
echo "  1) Use local version (HEAD)"
echo "  2) Use remote version (incoming)"
echo "  3) Manual merge (edit files yourself)"
echo ""
read -p "Choose strategy [1/2/3]: " STRATEGY

case $STRATEGY in
    1)
        echo "Keeping local versions..."
        git status | grep "both modified" | sed 's/.*both modified:   //' | while read -r file; do
            git checkout --ours "$file"
            git add "$file"
            echo "  Resolved: $file (local)"
        done
        ;;
    2)
        echo "Keeping remote versions..."
        git status | grep "both modified" | sed 's/.*both modified:   //' | while read -r file; do
            git checkout --theirs "$file"
            git add "$file"
            echo "  Resolved: $file (remote)"
        done
        ;;
    3)
        echo "Manual merge selected. Please edit files:"
        git status | grep "both modified" | sed 's/.*both modified:   //' | while read -r file; do
            echo "  - $file"
        done
        echo ""
        echo "After editing, run:"
        echo "  git add <resolved-files>"
        echo "  git rebase --continue"
        exit 0
        ;;
    *)
        echo "ERROR: Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Continuing rebase..."
if ! git rebase --continue; then
    echo ""
    echo "ERROR: Rebase continue failed (likely editor issue)"
    echo "Run manually:"
    echo "  git commit -m 'Merge conflict resolution'"
    echo "  git rebase --continue"
    exit 1
fi

echo ""
echo "=== Rebase complete ==="
echo "Verify with: git status"
echo "Push with: git push"
