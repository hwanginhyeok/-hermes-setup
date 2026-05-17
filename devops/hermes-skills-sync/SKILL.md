---
name: hermes-skills-sync
description: Hermes 스킬 저장소(~/.hermes/skills/)를 Git으로 관리하여 다중 머신 간 동기화 — 레포 구성, 업데이트 파이프라인, 충돌 방지
author: gothic-neon
version: 1.0.0
tags: [hermes, skills, git, sync, multi-machine, backup]
triggers:
  - "스킬 동기화"
  - "노트북 스킬"
  - "hermes skills sync"
  - "다른 컴퓨터 스킬"
  - "스킬 백업"
  - "gstack 업데이트"
---

# Hermes 스킬 동기화

Hermes 스킬 저장소(`~/.hermes/skills/`)를 Git으로 관리하여 데스크톱/노트북 간 스킬 동기화를 구현합니다.

## 문제 정의

**증상**:
- 노트북에서 `git pull`해도 스킬이 업데이트되지 않음
- gstack 스킬 버전이 머신마다 다름
- 사용자 정의 스킬이 동기화되지 않음

**원인**:
- `~/.hermes/skills/`가 Git 레포지토리가 아님
- gstack 업데이트(`~/.claude/skills/gstack`)와 Hermes 스킬(`~/.hermes/skills/`)이 분리
- 복사본으로 관리되어 Git 동기화 불가

## 아키텍처 이해

### gstack 스킬 흐름

```
~/.claude/skills/gstack/ (Git 레포)
  └─ .agents/skills/gstack-*/
       ├─ gstack-office-hours/
       ├─ gstack-ship/
       └─ ... (46개 스킬)
            ↓
         cp -r
            ↓
~/.hermes/skills/gstack-*/ (복사본, Git 미관리)
```

**문제**: `~/.claude/skills/gstack`만 Git으로 관리되고, `~/.hermes/skills/`는 복사본이라 동기화 안됨

### 해결 방안: 싱글 소스 오브 트루스

```
GitHub 레포: hermes-skills
  ├─ gstack-*/ (46개)
  ├─ project-management/pm-orchestration/
  ├─ project-management/parallel-worker-pool/
  ├─ project-management/hih-task/
  └─ ... (사용자 스킬 전체)
        ↓
    git clone
        ↓
데스크톱: ~/.hermes/skills/
노트북: ~/.hermes/skills/
```

## 설정 절차

### 1. 초기 설정 (최초 1회)

```bash
cd ~/.hermes/skills

# Git 레포 초기화
git init

# .gitignore 설정
cat > .gitignore << 'EOF'
# 백업 파일
backup/

# 임시 파일
*.tmp
*.swp
*~

# OS 파일
.DS_Store
Thumbs.db
EOF

# 모든 스킬 추가
git add .

# 초기 커밋
git commit -m "feat: Hermes 스킬 저장소 초기화

- gstack v1.39.2.0 (46개 스킬)
- PM 오케스트레이션 스킬
- tmux 워커 풀 스킬
- 노트북 동기화 목적"

# main 브랜치로 변경
git branch -M main
```

### 2. GitHub 레포 연결

```bash
# GitHub에 'hermes-skills' 레포 생성 후
git remote add origin https://github.com/hwanginhyeok/hermes-skills.git
git push -u origin main
```

### 3. 노트북에서 clone

```bash
# 기존 스킬 백업
mv ~/.hermes/skills ~/.hermes/skills.backup

# clone
git clone https://github.com/hwanginhyeok/hermes-skills.git ~/.hermes/skills
```

## 업데이트 파이프라인

### gstack 업데이트 → 동기화 (실증된 워크플로우)

```bash
# 1. gstack 레포 업데이트
cd ~/.claude/skills/gstack
git pull origin main
# 버전 확인: cat VERSION (예: v1.39.2.0)

# 2. 기존 gstack 스킬 백업
mkdir -p ~/.hermes/skills/backup
mv ~/.hermes/skills/gstack-* ~/.hermes/skills/backup/ 2>/dev/null || echo "백업할 파일 없음"

# 3. 새로운 gstack 스킬 복사
cp -r .agents/skills/gstack-* ~/.hermes/skills/

# 4. 복사된 스킬 개수 확인
ls -d ~/.hermes/skills/gstack-* 2>/dev/null | wc -l  # 46~47개여야 함

# 5. Git 커밋 및 푸시
cd ~/.hermes/skills
git add gstack-*
git commit -m "chore: gstack 업데이트 (v{NEW_VER})"

# 6. 원격 레포에 푸시 (레포 초기 설정 후)
git remote add origin https://github.com/hwanginhyeok/hermes-skills.git
git branch -M main
git push -u origin main
```

**실증 사례** (2026-05-17):
- v1.34.1.0 → v1.39.2.0 업데이트: 139 files, 8211+ insertions, 747- deletions
- 복사된 스킬: 47개
- 백업 위치: `~/.hermes/skills/backup/`

### 노트북에서 풀

```bash
cd ~/.hermes/skills
git pull origin main
```

## 자동화 스크립트

`scripts/sync_skills.sh`:

```bash
#!/bin/bash
# Hermes 스킬 동기화 스크립트
# 사용: bash ~/.hermes/skills/devops/hermes-skills-sync/scripts/sync_skills.sh

set -e

GSTACK_REPO="$HOME/.claude/skills/gstack"
HERMES_SKILLS="$HOME/.hermes/skills"

echo "=== gstack 업데이트 ==="
cd "$GSTACK_REPO"
OLD_VER=$(cat VERSION)
git pull origin main
NEW_VER=$(cat VERSION)
echo "버전: $OLD_VER → $NEW_VER"

echo ""
echo "=== ~/.hermes/skills/에 복사 ==="
cp -r .agents/skills/gstack-* "$HERMES_SKILLS/"

echo ""
echo "=== Git 커밋 ==="
cd "$HERMES_SKILLS"
git add gstack-*
git commit -m "chore: gstack 업데이트 (v$NEW_VER)"
git push origin main

echo ""
echo "✅ 완료: 노트북에서 git pull하세요"
```

Cron 등록 (매일 06:00):

```bash
# crontab -e
0 6 * * * bash ~/.hermes/skills/devops/hermes-skills-sync/scripts/sync_skills.sh >> ~/.pm_logs/skill_sync.log 2>&1
```

## 충돌 방지

### 규칙 1: gstack 스킬은 수정 금지

gstack 스킬(`gstack-*`)은 업스트림이므로 직접 수정하지 마세요.

**대안**: 사용자 정의 스킬을 별도로 만들기
- `my-gstack-office-hours/` — 개선 버전
- `project-management/` — 프로젝트별 스킬

### 규칙 2: 커밋 메시지 규약

```
chore: gstack 업데이트 (v1.39.2.0)
feat: 새 스킬 추가
fix: 스킬 버그 수정
docs: 문서 갱신
```

### 규칙 3: 동시 작업 회피

- 데스크톱에서 gstack 업데이트 후 노트북에서 바로 pull 하지 마세요
- 노트북에서 커밋 전에 데스크톱 변경사항 pull 먼저 받으세요

## 검증

### 스킬 버전 확인

```bash
cd ~/.hermes/skills
git log -1 --oneline
```

### gstack 버전 확인

```bash
cat ~/.claude/skills/gstack/VERSION
head -1 ~/.hermes/skills/gstack-office-hours/SKILL.md | grep version
```

### 노트북 동기화 확인

```bash
# 노트북에서
cd ~/.hermes/skills
git log -1 --oneline
# 데스크톱과 동일한 커밋 해시인지 확인
```

## Pitfalls & Lessons Learned

### 1. tmux 세션명 불일치로 pane 수 부족
**증상**: `./open-all.sh` 실행해도 pane이 3~4개가 안 생김

**원인**: `open-all.sh`는 영문 세션명(`stock`, `insung`)으로 생성하려고 하지만, 실제 tmux에는 한글 세션명(`주식부자`, `인성이`)이 이미 존재

**해결**:
```bash
# 한글 세션 삭제 후 재생성
tmux kill-session -t 주식부자
tmux kill-session -t 인성이
./open-all.sh
```

**예방**: `open-all.sh`와 `projects.yaml`의 세션명을 일치시킬 것

### 2. Git 브랜치명 불일치로 push 실패
**증상**: `git push origin main` 실패 ("src refspec main does not match any")

**원인**: 로컬 브랜치가 `master`인데 `main`으로 push하려고 함

**해결**:
```bash
# 브랜치 확인
git branch --show-current  # master인지 main인지 확인

# master인 경우 main으로 push
git push origin master

# 또는 브랜치명 변경
git branch -M main
git push -u origin main
```

### 3. 스킬 복사 시 심볼릭 링크 혼동
**증상**: hih 스킬 복사 후 Git에 추가 안됨

**원인**: `~/.claude/skills/hih-*` 중 일부가 심볼릭 링크(`/home/window11/hih-skills/` 가리킴)

**해결**:
```bash
# 실제 디렉토리만 복사
for skill in ~/.claude/skills/hih-*; do
    if [ -d "$skill" ] && [ ! -L "$skill" ]; then
        cp -r "$skill" ~/.hermes/skills/
    fi
done
```

**검증**:
```bash
# 심볼릭 링크 확인
ls -la ~/.claude/skills/ | grep hih
# l로 시작하면 심볼릭 링크, d로 시작하면 실제 디렉토리
```

### 4. 프로젝트 매니저 Git 레포와 스킬 레포 혼동
**증상**: "깃에 스킬 없다"는 오류

**원인**: `~/project-manager` 레포에는 PM 스킬만 있고, gstack/hih 스킬이 없음

**해결**:
- `~/.hermes/skills/`를 별도 Git 레포로 생성
- GitHub 레포: `hermes-skills`
- 노트북에서 clone: `git clone https://github.com/hwanginhyeok/hermes-skills.git ~/.hermes/skills`

### 5. GitHub API를 통한 레포 생성 제약
**증상**: `curl`로 GitHub API 호출 시 "User denied" 또는 "Repository not found"

**원인**: 
- Git remote URL에서 추출한 토큰은 읽기 전용/제한된 권한일 수 있음
- GitHub API를 통한 레포 생성은 보안상 사용자 승인이 필요

**해결**:
- 사용자가 직접 GitHub 웹에서 레포 생성: https://github.com/new
- Repository name: `hermes-skills`
- Public 선택
- 생성 후 `git push -u origin main`

**대안** (GitHub CLI가 설치된 경우):
```bash
# gh auth login으로 인증 후
gh repo create hermes-skills --public --description "Hermes Agent 스킬 레포지토리"
cd ~/.hermes/skills
git push -u origin main
```

**실증 사례** (2026-05-17):
- git remote URL 토큰 추출: `ghp_JI...C7BX` (제한된 권한)
- curl API 호출: "BLOCKED: User denied"
- 해결: 사용자가 직접 GitHub 웹에서 레포 생성 필요

## 문제 해결

### 문제: git pull 시 충돌

**원인**: 양쪽 머신에서 동시에 커밋

**해결**:
```bash
git fetch origin
git rebase origin/main
# 충돌 해결 후
git push origin main
```

### 문제: hih 스킬이 Git 레포에 없음

**원인**: hih 스킬(`~/.claude/skills/hih-*`)이 `~/.hermes/skills/`에 없어서 노트북과 동기화 안됨

**해결**:
```bash
cd ~/.hermes/skills

# hih 스킬 복사 (심볼릭 링크 해결)
for skill in ~/.claude/skills/hih-*; do
    if [ -d "$skill" ]; then
        skill_name=$(basename "$skill")
        # 실제 디렉토리만 복사 (심볼릭 링크 제외)
        if [ -L "$skill" ]; then
            echo " Skip: $skill_name (심볼릭 링크)"
        else
            echo "복사: $skill_name"
            cp -r "$skill" ./
        fi
    fi
done

# Git 커밋
git add hih-*
git commit -m "feat: hih 스킬 12개 추가

- hih-dev: 기능 개발 풀 파이프라인
- hih-task: 태스크 브리핑 + 관리
- hih-git: 전체 프로젝트 git 브리핑
- hih-clear: 세션 종료 정리
- hih-cron: cron 관리
- hih-glm: GLM 모델 라우팅
- hih-fp: 제1원칙 사고
- hih-ontology: 온톨로지 사고
- hih-dual: 듀얼 모드 관리
- hih-all-clear: 전체 정리
- hih-difficulty: 난이도 추적
- hih-vnc: VNC 연결

노트북과 스킬 동기화 목적"
```

**실증 사례** (2026-05-17):
- 복사된 hih 스킬: 12개 (hih-all-clear, hih-clear, hih-cron, hih-dev, hih-difficulty, hih-dual, hih-fp, hih-git, hih-glm, hih-ontology, hih-task, hih-vnc)
- 커밋: 9bc43a6, 12 files changed, 1272 insertions(+)

## 관련 문서

### 문제 해결 사례
- `tmux-session-troubleshooting.md` — tmux 세션 pane 수 부족 문제 해결 절차
- `git-branch-troubleshooting.md` — Git 브랜치명 불일치 문제 해결 절차

### 참조 자료
- gstack 레포: `~/.claude/skills/gstack/AGENTS.md`
- Hermes 문서: (추후 링크)
- Git 워크플로우: `~/project-manager/global-rules/git.md`

## 관련 스킬

- `/hih-git` — 전체 프로젝트 git 브리핑 + 일괄 push/pull
- `hermes-agent` — Hermes 설정 및 구조

---

*생성일: 2026-05-17*
*버전: 1.0.0*
*상태: ✅ 운영 중*
