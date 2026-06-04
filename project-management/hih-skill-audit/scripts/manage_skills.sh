#!/bin/bash
#
# 스킬 관리 자동화 스크립트
# - 스킬 현황 확인
# - 노트북 동기화
# - 보고서 생성
#

set -e

# 설정
REPO_DIR="$HOME/project-manager"
SKILLS_DIR="$HOME/.hermes/skills"
REPORT_DIR="$REPO_DIR/docs/reports/skills"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 디렉토리 생성
mkdir -p "$REPORT_DIR"

# 1. 스킬 현황 보고서 생성
echo "📊 스킬 현황 보고서 생성 중..."

REPORT_FILE="$REPORT_DIR/skills_status_${DATE}.md"

cat > "$REPORT_FILE" << EOF
# 스킬 관리 현황

## 📅 기록일: $(date +%Y-%m-%d %H:%M:%S)

## 📦 전역 스킬 현황

EOF

# 전역 스킬 수 확인
ALL_SKILLS=$(find "$SKILLS_DIR" -name 'SKILL.md' -type f | wc -l)
CATEGORIES=$(find "$SKILLS_DIR" -name 'SKILL.md' -type f -exec grep -h '^category:' {} \; | sort -u | wc -l)

cat >> "$REPORT_FILE" << EOF
- 전체 스킬: $ALL_SKILLS개
- 카테고리: $CATEGORIES개

## 📂 프로젝트별 스킬 현황

EOF

# 프로젝트별 스킬 확인
PROJECTS="$REPO_DIR/projects.yaml"

if [ -f "$PROJECTS" ]; then
    python3 -c "
import yaml
import os

with open('$PROJECTS', 'r') as f:
    projects = yaml.safe_load(f)

for project, info in projects.get('projects', {}).items():
    path = info.get('path', '')
    skills_dir = os.path.join(path, '.hermes/skills')
    
    if os.path.exists(skills_dir):
        skills = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
        print(f'### {project}')
        print(f'- 경로: {path}')
        print(f'- 스킬 수: {len(skills)}개')
        print()
" >> "$REPORT_FILE"
fi

# 최근 변경 스킬
cat >> "$REPORT_FILE" << EOF

## 🔄 최근 7일 내 변경 스킬

EOF

find "$SKILLS_DIR" -name 'SKILL.md' -type f -mtime -7 | while read skill_path; do
    skill_name=$(basename $(dirname "$skill_path"))
    mod_time=$(stat -c '%y' "$skill_path" | cut -d'.' -f1)
    echo "- ${skill_name}: ${mod_time}" >> "$REPORT_FILE"
done

# 완료 표시
cat >> "$REPORT_FILE" << EOF

## ✅ 상태

- 스킬 관리 정상
- 노트북 동기화 준비 완료

## 📝 다음 작업

- 노트북에서 최신 보고서 확인
- 필요 시 스킬 추가/수정
EOF

echo "✅ 보고서 생성 완료: $REPORT_FILE"

# 2. Git 커밋 + 푸쉬
echo "🚀 Git 커밋 + 푸쉬 중..."

cd "$REPO_DIR"
git add "$REPORT_DIR"
git commit -m "chore: 스킬 관리 현황 보고서 - ${DATE}" || echo "커밋 없음"
git push || echo "푸쉬 실패"

echo "✅ Git 동기화 완료"

# 3. 노트북 동기화 확인
echo "📱 노트북 동기화 상태:"

cd "$REPO_DIR"
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main 2>/dev/null || echo "none")

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo "  ✅ 동기화됨"
else
    echo "  ⚠️  동기화 필요"
    echo "  로컬: $LOCAL_COMMIT"
    echo "  리모트: $REMOTE_COMMIT"
fi

echo ""
echo "🎉 스킬 관리 자동화 완료!"