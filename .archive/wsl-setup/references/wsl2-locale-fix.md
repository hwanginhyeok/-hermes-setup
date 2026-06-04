# WSL2 Locale Fix Session History

## Session: 2026-05-25 - tmux 한글 입력 안 됨

### Initial State
- LANG: C.UTF-8 (한국어 로케일 없음)
- LC_CTYPE: (비어있음)
- tmux conf: UTF-8 terminal-overrides 누락
- 설치된 로케일: C, C.utf8, POSIX (ko_KR.UTF-8 없음)

### Problem Diagnosis
```bash
# 로케일 확인
locale -a
# 결과: C, C.utf8, POSIX (한국어 없음)

# tmux 설정 확인
cat ~/.tmux.conf | grep terminal-overrides
# 결과: 없음

# 환경변수 확인
echo $LANG $LC_CTYPE
# 결과: C.UTF-8 (empty)
```

### Resolution Applied

1. **시스템 로케일 활성화** (sudo 필요):
   ```bash
   sudo sed -i 's/^# ko_KR.UTF-8 UTF-8/ko_KR.UTF-8 UTF-8/' /etc/locale.gen
   sudo locale-gen ko_KR.UTF-8
   sudo update-locale LANG=ko_KR.UTF-8
   ```

2. **사용자 레벨 환경변수** (.bashrc):
   ```bash
   export LANG=ko_KR.UTF-8
   export LC_ALL=ko_KR.UTF-8
   export LC_CTYPE=ko_KR.UTF-8
   ```

3. **tmux UTF-8 설정** (.tmux.conf):
   ```bash
   set -g default-terminal "screen-256color"
   set -ga terminal-overrides ",*256col*:Tc"
   ```

4. **현재 세션 적용**:
   ```bash
   export LANG=ko_KR.UTF-8
   export LC_ALL=ko_KR.UTF-8
   export LC_CTYPE=ko_KR.UTF-8
   ```

5. **tmux 재시작**:
   ```bash
   tmux kill-server
   tmux new -s test
   ```

### Verification
```bash
# 로케일 확인
locale -a | grep ko_KR
# 결과: ko_KR.UTF-8

# tmux 내부에서 한글 입력 테스트
안녕하세요!
# 결과: 정상 입력됨
```

### Lessons Learned

1. **locale 설정 범위**: 시스템(locale-gen) vs 사용자(.bashrc) vs 현재 세션(export)
2. **tmux 재시작 필수**: 설정 변경 후 현재 tmux 세션에는 적용되지 않음. 반드시 kill 후 재생성
3. **sudo 분리**: .bashrc/.tmux.conf는 불필요하지만 locale-gen은 sudo 필수
4. **terminal-overrides 중요**: 이 설정 없으면 UTF-8이 제대로 동작하지 않음

### Created Files

- `~/scripts/tmux-korean-setup.sh` - 전체 설정 스크립트 (sudo 포함)

### User Feedback

- "there were a local file but why it removed ??" - 사용자가 기존 설정 파일이 있다고 기억함
- 실제로는 백업 파일(.tmux.conf.dark.backup, .tmux.conf.light)만 존재했음
- 새로운 setup 스크립트 생성 및 적용 필요