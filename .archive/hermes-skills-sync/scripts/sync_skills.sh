#!/bin/bash
# Hermes 스킬 동기화 스크립트
# 사용: bash ~/.hermes/skills/devops/hermes-skills-sync/scripts/sync_skills.sh

set -e

GSTACK_REPO="$HOME/.claude/skills/gstack"
HERMES_SKILLS="$HOME/.hermes/skills"

echo "=== gstack 업데이트 ==="
cd "$GSTACK_REPO"
if [ ! -f VERSION ]; then
    echo "❌ VERSION 파일 없음"
    exit 1
fi

OLD_VER=$(cat VERSION)
echo "현재 버전: $OLD_VER"

git pull origin main
NEW_VER=$(cat VERSION)
echo "새 버전: $NEW_VER"

if [ "$OLD_VER" = "$NEW_VER" ]; then
    echo "⏭️ 이미 최신 버전"
    exit 0
fi

echo ""
echo "=== ~/.hermes/skills/에 복사 ==="
# 기존 gstack 스킬 백업
mkdir -p "$HERMES_SKILLS/backup"
mv "$HERMES_SKILLS"/gstack-* "$HERMES_SKILLS/backup/" 2>/dev/null || true

# 새로운 gstack 스킬 복사
cp -r "$GSTACK_REPO/.agents/skills/gstack-"* "$HERMES_SKILLS/"

echo "복사된 스킬 개수: $(ls -d "$HERMES_SKILLS"/gstack-* 2>/dev/null | wc -l)"

echo ""
echo "=== Git 커밋 ==="
cd "$HERMES_SKILLS"
git add gstack-*
git commit -m "chore: gstack 업데이트 (v$NEW_VER)

- v$OLD_VER → v$NEW_VER
- $(git -C "$GSTACK_REPO" diff --stat HEAD~1 HEAD | tail -1 | awk '{print $1, $2, $3}')"

git push origin main

echo ""
echo "✅ 완료: 노트북에서 'cd ~/.hermes/skills && git pull' 실행하세요"
