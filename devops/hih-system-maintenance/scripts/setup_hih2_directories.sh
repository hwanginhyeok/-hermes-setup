#!/bin/bash
#
# HIH_2 필수 디렉토리 구조 생성 스크립트
# Usage: bash setup_hih2_directories.sh
#

set -e

echo "=== HIH_2 Directory Structure Setup ==="
echo ""

# 프로젝트 루트 확인
if [ ! -f "CURRENT_TASK.md" ] || [ ! -f "CLAUDE.md" ]; then
    echo "Error: Not in HIH_2 project root"
    echo "Please run from /home/gint_pcd/projects/HIH_2/"
    exit 1
fi

# 필수 디렉토리 정의
REQUIRED_DIRS=(
    "HIH_Claude/cron_monitoring"
    "HIH_Claude/production_status"
    "HIH_Claude/standup_daily"
    "HIH_Claude/bom_dfme_check"
    "HIH_Claude/dfmea_status"
    "HIH_Claude/weekly"
)

echo "Creating required directories..."

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "  ✓ Created: $dir"
    else
        echo "  ○ Exists: $dir"
    fi
done

echo ""
echo "Verifying data files..."

DATA_FILES=(
    "HIH_Claude/데이터/parts_tracking.csv"
    "HIH_Claude/데이터/issues.csv"
    "HIH_Claude/데이터/dfmea_issue_status.csv"
)

for file in "${DATA_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ Found: $file"
    else
        echo "  ✗ Missing: $file"
    fi
done

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Verify data files exist"
echo "  2. Create cronjobs using skill: /hih-system-maintenance"
echo "  3. Test with: cronjob(action='run', job_id='...')"
