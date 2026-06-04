#!/bin/bash
# hih 스킬 빠른 점검 스크립트
# 사용법: bash scripts/hih_skill_quick_check.sh

echo "=== hih 스킬 빠른 점검 ==="
echo ""

# 1. 스킬 개수
SKILL_COUNT=$(ls -d ~/.hermes/skills/hih-* 2>/dev/null | wc -l)
echo "📦 설치된 스킬: $SKILL_COUNT개"

# 2. No SKILL.md
NO_SKILL_MD=$(for dir in ~/.hermes/skills/hih-*; do [ ! -f "$dir/SKILL.md" ] && echo "$dir"; done)
if [ -n "$NO_SKILL_MD" ]; then
    echo "❌ SKILL.md 없음:"
    echo "$NO_SKILL_MD"
else
    echo "✅ 모든 스킬에 SKILL.md 존재"
fi

# 3. No frontmatter
NO_FRONTMATTER=$(for dir in ~/.hermes/skills/hih-*; do file="$dir/SKILL.md"; if [ -f "$file" ] && ! head -1 "$file" | grep -q '---'; then echo "$(basename $dir)"; fi; done)
if [ -n "$NO_FRONTMATTER" ]; then
    echo "❌ Frontmatter 없음:"
    echo "$NO_FRONTMATTER"
else
    echo "✅ 모든 스킬에 Frontmatter 존재"
fi

# 4. 네이밍 부정합 (hih-claude vs codex)
NAMING_MISMATCH=$(grep -l "name: codex" ~/.hermes/skills/hih-*/SKILL.md 2>/dev/null | xargs -I{} dirname {} | xargs basename)
if [ -n "$NAMING_MISMATCH" ]; then
    echo "⚠️  네이밍 부정합:"
    for skill in $NAMING_MISMATCH; do
        declared=$(grep "^name:" "$HOME/.hermes/skills/$skill/SKILL.md" | head -1 | cut -d' ' -f2)
        echo "  - $skill: name: $declared"
    done
else
    echo "✅ 네이밍 정합"
fi

# 5. 과도한 길이 (>300 lines)
LONG_SKILLS=$(for dir in ~/.hermes/skills/hih-*; do file="$dir/SKILL.md"; if [ -f "$file" ]; then lines=$(wc -l < "$file"); if [ "$lines" -gt 300 ]; then echo "$(basename $dir): $lines lines"; fi; fi; done)
if [ -n "$LONG_SKILLS" ]; then
    echo "⚠️  과도한 길이 (>300 lines):"
    echo "$LONG_SKILLS"
else
    echo "✅ 모든 스킬 적정 길이"
fi

echo ""
echo "=== 점검 완료 ==="
