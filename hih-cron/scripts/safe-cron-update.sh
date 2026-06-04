#!/bin/bash
# crontab 안전 변경 스크립트
# 백업 + 미리보기 + 문법검증 + 롤백 포함
#
# Usage:
#   ./safe-cron-update.sh /tmp/crontab_new.txt
#   ./safe-cron-update.sh /tmp/crontab_new.txt --dry-run

set -euo pipefail

# 색상 출력
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 인자 확인
NEW_CRON_FILE="${1:-}"
DRY_RUN="${2:-}"

if [ ! -f "$NEW_CRON_FILE" ]; then
    echo -e "${RED}❌ 파일 없음: $NEW_CRON_FILE${NC}"
    echo "Usage: $0 <crontab_file> [--dry-run]"
    exit 1
fi

# 1. 백업 생성
BACKUP_DIR="/tmp/cron_backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/crontab_backup_$TIMESTAMP.txt"

echo -e "${YELLOW}## 1. 백업 생성${NC}"
crontab -l > "$BACKUP_FILE" 2>/dev/null || true
echo -e "${GREEN}✅ 백업 완료: $BACKUP_FILE${NC}"
ORIGINAL_LINES=$(wc -l < "$BACKUP_FILE")
echo "   백업 줄 수: $ORIGINAL_LINES"
echo ""

# 2. 미리보기
echo -e "${YELLOW}## 2. 새 crontab 미리보기${NC}"
NEW_LINES=$(wc -l < "$NEW_CRON_FILE")
echo "   새 파일 줄 수: $NEW_LINES (+$((NEW_LINES - ORIGINAL_LINES))줄)"
echo ""
diff "$BACKUP_FILE" "$NEW_CRON_FILE" || true
echo ""

# 3. 문법 검증
echo -e "${YELLOW}## 3. 문법 검증${NC}"

# 비어있는 줄만 있는지 확인
if [ "$(grep -v '^[[:space:]]*$' "$NEW_CRON_FILE" | wc -l)" -eq 0 ]; then
    echo -e "${RED}❌ 파일이 비어있거나 주석만 있음${NC}"
    exit 1
fi

# cron 문법 기본 검증 (5개 필드 + 명령어)
SYNTAX_ERRORS=0
while IFS= read -r line; do
    # 주석/빈줄 무시
    [[ "$line" =~ ^# ]] && continue
    [[ -z "${line// }" ]] && continue
    
    #cron 필드 개수 확인 (최소 5개 시간 필드 + 명령어)
    FIELD_COUNT=$(echo "$line" | awk '{print NF}')
    if [ "$FIELD_COUNT" -lt 6 ]; then
        echo -e "${RED}⚠️  필드 부족 ($FIELD_COUNT < 6): $line${NC}"
        ((SYNTAX_ERRORS++))
    fi
done < "$NEW_CRON_FILE"

if [ $SYNTAX_ERRORS -gt 0 ]; then
    echo -e "${RED}❌ 문법 오류 $SYNTAXANGES건 발견${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 문법 검증 통과${NC}"
echo ""

# 4. Dry-run이면 여기서 종료
if [ "$DRY_RUN" == "--dry-run" ]; then
    echo -e "${YELLOW}## Dry-run 모드 - 적용하지 않음${NC}"
    echo ""
    echo "## 적용 예정 명령어"
    echo "crontab $NEW_CRON_FILE"
    echo ""
    echo "## 롤백 명령어 (필요 시)"
    echo "crontab $BACKUP_FILE"
    exit 0
fi

# 5. 적용
echo -e "${YELLOW}## 4. crontab 적용${NC}"
if crontab "$NEW_CRON_FILE"; then
    echo -e "${GREEN}✅ crontab 적용 완료${NC}"
else
    echo -e "${RED}❌ crontab 적용 실패${NC}"
    echo ""
    echo "## 롤백 명령어"
    echo "crontab $BACKUP_FILE"
    exit 1
fi
echo ""

# 6. 검증
echo -e "${YELLOW}## 5. 검증${NC}"
CURRENT_LINES=$(crontab -l | wc -l)
echo "   적용 후 줄 수: $CURRENT_LINES"
echo ""

# cron 데몬 상태 확인
if systemctl is-active --quiet cron; then
    echo -e "${GREEN}✅ cron 데몬: active (running)${NC}"
else
    echo -e "${RED}⚠️  cron 데몬: not active${NC}"
fi
echo ""

echo -e "${GREEN}## 완료${NC}"
echo ""
echo "## 롤백 명령어 (필요 시)"
echo "crontab $BACKUP_FILE"
echo ""
echo "## 백업 파일"
echo "$BACKUP_FILE"
