# Git 브랜치명 불일치 문제 해결

## 문제 발생 (2026-05-17)

**증상**: `git push origin main` 실패

**에러 메시지**:
```
error: src refspec main does not match any
error: failed to push some refs to https://github.com/hwanginhyeok/project-manager.git
```

## 원인 분석

### 1. 브랜치명 불일치

**로컬 브랜치**: `master`
**원격 레포**: `origin/main` 존재
**시도한 명령**: `git push origin main`

**결과**: 로컬에 `main` 브랜치가 없어서 push 실패

### 2. 확인 방법

```bash
# 현재 브랜치 확인
git branch --show-current  # 출력: master

# 원격 브랜치 확인
git branch -r  # 출력: origin/master
```

## 해결 방법

### 방법 1: master 브랜치로 push (즉시 해결)

```bash
git push origin master
```

**결과**:
```
To https://github.com/hwanginhyeok/project-manager.git
   e14a601..54e0164  master -> origin/master
```

### 방법 2: 브랜치명을 main으로 변경

```bash
# 로컬 브랜치명 변경
git branch -M main

# main 브랜치로 push
git push -u origin main
```

**추천**: GitHub 최신 트렌드에 맞춰 `main` 사용

### 방법 3: 원격 브랜치명 변경

```bash
# 원격 브랜치명 변경 (GitHub 웹에서 또는 아래 명령)
git branch -m master main
git push -u origin main
git push origin --delete master  # 원격 master 브랜치 삭제
```

## 예방 조치

### 1. 초기 설정 시 main 브랜치로 시작

```bash
# Git 레포 초기화
git init

# 첫 커밋 후 main 브랜치로 변경
git branch -M main

# 원격 레포 추가
git remote add origin https://github.com/username/repo.git

# main으로 push
git push -u origin main
```

### 2. 전역 기본 브랜치 설정

```bash
# Git 2.28+에서 기본 브랜치를 main으로 설정
git config --global init.defaultBranch main

# 이후 새로운 레포는 자동으로 main 브랜치로 생성
git init  # main 브랜치로 생성됨
```

### 3. 브랜치명 확인 습관화

```bash
# push 전 항상 브랜치 확인
git branch --show-current

# 원격 브랜치 확인
git branch -r
```

## 관련 문서

- Git 공식 문서: [Branching](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell)
- GitHub 가이드: [Renaming a branch](https://github.com/github/renaming)

## 실증 사례

### 사례 1: project-manager 레포

**문제**: `git push origin main` 실패

**해결**:
```bash
git branch --show-current  # master
git push origin master     # 성공
```

**결과**: `e14a601..54e0164  master -> origin/master`

### 사례 2: hermes-skills 레포

**문제**: 신규 레포 생성 시 브랜치명 미정

**해결**:
```bash
git init
git add .
git commit -m "feat: Hermes 스킬 저장소 초기화"
git branch -M main
git remote add origin https://github.com/hwanginhyeok/hermes-skills.git
git push -u origin main
```

**결과**: ✅ 성공

---

*해결일: 2026-05-17*
*상태: ✅ 해결됨*
