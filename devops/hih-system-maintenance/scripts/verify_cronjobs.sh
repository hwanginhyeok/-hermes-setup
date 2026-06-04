#!/bin/bash
# Cronjob Verification Script
# HIH_2 Cronjob 상태 자동 점검
# 사용법: ./scripts/verify_cronjobs.sh

set -e

echo "=== HIH_2 Cronjob Verification ==="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check cron output directory
CRON_OUTPUT_DIR="$HOME/.hermes/cron/output"

if [ ! -d "$CRON_OUTPUT_DIR" ]; then
    echo -e "${RED}❌ Cron output directory not found: $CRON_OUTPUT_DIR${NC}"
    echo "Run: mkdir -p $CRON_OUTPUT_DIR"
    exit 1
fi

echo -e "${GREEN}✅ Cron output directory exists${NC}"
echo ""

# List all job output directories
echo "=== Cronjob Output Directories ==="
JOB_COUNT=$(find "$CRON_OUTPUT_DIR" -maxdepth 1 -type d | tail -n +2 | wc -l)
echo "Total jobs with output: $JOB_COUNT"
echo ""

# Check each job
for job_dir in "$CRON_OUTPUT_DIR"/*; do
    if [ -d "$job_dir" ]; then
        JOB_ID=$(basename "$job_dir")
        echo "Job: $JOB_ID"
        
        # Latest output file
        LATEST_OUTPUT=$(ls -t "$job_dir"/*.md 2>/dev/null | head -1)
        
        if [ -z "$LATEST_OUTPUT" ]; then
            echo -e "  ${YELLOW}⚠️  No output files${NC}"
        else
            FILENAME=$(basename "$LATEST_OUTPUT")
            TIMESTAMP=$(echo "$FILENAME" | sed 's/\.md$//')
            echo -e "  ${GREEN}✅ Latest: $TIMESTAMP${NC}"
            
            # Check for errors
            if grep -q "## Error" "$LATEST_OUTPUT"; then
                echo -e "  ${RED}❌ Has errors${NC}"
                ERROR_MSG=$(grep -A 5 "## Error" "$LATEST_OUTPUT" | head -6)
                echo "  Error preview: $ERROR_MSG"
            else
                echo -e "  ${GREEN}✅ No errors${NC}"
            fi
        fi
        echo ""
    fi
done

# Check LLM provider
echo "=== LLM Provider Check ==="
if command -v hermes &> /dev/null; then
    PROVIDER_OUTPUT=$(hermes model list 2>&1 || true)
    if echo "$PROVIDER_OUTPUT" | grep -q "No provider selected"; then
        echo -e "${RED}❌ No LLM provider configured${NC}"
        echo "Run: hermes model"
    else
        echo -e "${GREEN}✅ LLM provider configured${NC}"
        echo "$PROVIDER_OUTPUT" | head -3
    fi
else
    echo -e "${YELLOW}⚠️  Hermes CLI not found${NC}"
fi
echo ""

# Check required directories
echo "=== Required Directories ==="
REQUIRED_DIRS=(
    "HIH_Claude/cron_monitoring"
    "HIH_Claude/production_status"
    "HIH_Claude/standup_daily"
    "HIH_Claude/bom_dfme_check"
    "HIH_Claude/dfmea_status"
    "HIH_Claude/weekly"
)

ALL_EXIST=true
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ $dir${NC}"
    else
        echo -e "${RED}❌ $dir (not found)${NC}"
        ALL_EXIST=false
    fi
done

if [ "$ALL_EXIST" = false ]; then
    echo ""
    echo "Run: mkdir -p HIH_Claude/{cron_monitoring,production_status,standup_daily,bom_dfme_check,dfmea_status,weekly}"
fi
echo ""

# Check data files
echo "=== Data Files ==="
DATA_FILES=(
    "HIH_Claude/데이터/parts_tracking.csv"
    "HIH_Claude/데이터/issues.csv"
    "HIH_Claude/데이터/dfmea_issue_status.csv"
)

for file in "${DATA_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(ls -lh "$file" | awk '{print $5}')
        echo -e "${GREEN}✅ $file ($SIZE)${NC}"
    else
        echo -e "${RED}❌ $file (not found)${NC}"
    fi
done
echo ""

echo "=== Verification Complete ==="
