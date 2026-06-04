---
name: wsl-setup
description: WSL (Windows Subsystem for Linux) 환경 설정 및 문제 해결 - locale, tmux 한글 입력, systemd, GPU, 성능 최적화
tags: [wsl, ubuntu, locale, tmux, gpu, systemd]
---

# WSL Setup & Troubleshooting

WSL(Windows Subsystem for Linux) 환경에서 발생하는 설정 문제를 진단하고 해결합니다.

## Trigger Scenarios

- 터미널/tmux에서 한글 입력이 안 될 때
- locale 관련 에러 발생 시
- WSL 성능이 느릴 때
- systemd 서비스가 동작하지 않을 때
- GPU 접근이 안 될 때 (Ollama, ML)

## Key Problems & Solutions

### 1. 한글 입력 안 됨 (tmux)

**증상**: tmux 세션에서 한글 입력이 불가능하거나 깨짐

**원인**:
- 한국어 로케일(ko_KR.UTF-8) 미설치
- .tmux.conf에 UTF-8 terminal-overrides 설정 누락
- 로케일 환경변수(LANG, LC_ALL, LC_CTYPE) 미설정

**해결**:

1. 한국어 로케일 설치 (sudo 필요):
```bash
sudo sed -i 's/^# ko_KR.UTF-8 UTF-8/ko_KR.UTF-8 UTF-8/' /etc/locale.gen
sudo locale-gen ko_KR.UTF-8
sudo update-locale LANG=ko_KR.UTF-8
```

2. .bashrc에 환경변수 추가:
```bash
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
export LC_CTYPE=ko_KR.UTF-8
```

3. .tmux.conf에 UTF-8 설정 추가:
```bash
set -g default-terminal "screen-256color"
set -ga terminal-overrides ",*256col*:Tc"
```

4. 현재 세션에 적용:
```bash
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
export LC_CTYPE=ko_KR.UTF-8
tmux source-file ~/.tmux.conf
```

5. tmux 세션 재시작:
```bash
tmux kill-server
tmux new -s test
```

**스크립트**: `scripts/tmux-korean-setup.sh` 사용 가능

### 2. systemd 서비스 동작 안 함

**증상**: `systemctl start` 명령이 실패하거나 서비스가 자동 시작 안 됨

**해결**: `/etc/wsl.conf`에 systemd 활성화
```ini
[boot]
systemd=true
```

WSL 재시작 (PowerShell):
```powershell
wsl --shutdown
```

### 3. GPU 접근 불가

**증상**: `nvidia-smi` 실행 실패, Ollama이 CPU에서만 실행

**확인**:
```bash
nvidia-smi
# Should show GPU info
```

**해결**: Windows에서 NVIDIA WSL 드라이버 설치 (Linux가 아님)
- https://developer.nvidia.com/cuda/wsl

### 5. Windows CLI 툴 WSL에서 접근

**증상**: Windows에 설치된 CLI (xai, etc.)가 WSL에서 실행 안 됨

**원인**:
- Windows CLI 툴은 Windows PATH에만 등록
- WSL PATH에 Windows CLI 경로 포함되어 있어도 별도 바이너리 필요

**해결**:

**PowerShell에서 설치 확인**:
```powershell
Get-Command xai -ErrorAction SilentlyContinue | Select-Object Source,Version
```

**WSL에서 Windows CLI 실행**:
```bash
# PowerShell 통해서 실행
powershell.exe -Command "xai --version"

# 또는 cmd.exe 통해서 실행
cmd.exe /c "xai --version"
```

**Windows CLI가 Linux 호환 버전인지 확인**:
- x.ai CLI: 현재 Windows 전용
- OpenAI CLI: Linux/Windows 모두 지원

**권장**: WSL에서는 Linux 전용 CLI 툴 사용 권장

### 6. 성능 최적화

**팁**:
- 모델 파일을 Linux home(~/.ollama/models/)에 저장 - /mnt/c/ 접근 느림
- GPU 앱 닫기 - WSL이 Windows와 VRAM 공유
- Network: Ollama은 localhost:11434에서 Windows에서도 접근 가능

## Diagnostic Commands

```bash
# WSL 버전 확인
uname -a | grep microsoft

# Ubuntu 버전 확인
cat /etc/os-release | grep "NAME\\|VERSION"

# 로케일 확인
locale -a | grep ko_KR

# tmux 설정 확인
cat ~/.tmux.conf | grep terminal-overrides

# systemd 확인
systemctl --user status

# Windows CLI 툴 확인
powershell.exe -Command "Get-Command xai -ErrorAction SilentlyContinue | Select-Object Source"
```

## References

- `scripts/tmux-korean-setup.sh` - tmux 한글 입력 설정 스크립트
- `references/wsl2-locale-fix.md` - 세션별 문제 해결 기록
- `references/wsl2-gpu-troubleshooting.md` - GPU 접근 문제 해결

## Pitfalls
**Pitfalls**:
- **locale 설정 후 즉시 tmux에서 확인하지 말 것**: 현재 세션에는 적용되지 않음. 반드시 tmux 재시작 필요
- **Windows 드라이버 vs Linux 드라이버**: GPU 문제는 Windows 쪽에서 WSL 드라이버 설치해야 함 (apt install 아님)
- **파일 시스템 성능 차이**: ~/.ollama/models/를 Linux home에 저장 (Windows /mnt/c/ 느림)
- **sudo 필요 여부**: locale-gen은 sudo 필요하지만 .bashrc/.tmux.conf 설정은 불필요
- **Windows CLI 툴 설치 명령은 사용자가 직접 실행**: curl | bash 같은 설치 명령은 BLOCKED 발생. 설치 방법만 제공
- **Windows CLI 툴과 WSL 호환성**: Windows에 설치된 CLI는 WSL에서 `xai --version`로 바로 실행 안 됨. PowerShell 호출 필요
- **WSL에서 CLI 툴 설치**: Linux 호환 버전 확인 후 WSL 내부에서 설치 권장