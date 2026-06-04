#!/bin/bash
#
# tmux 한글 입력 설정 스크립트
# 작성: 2026-05-25
#

set -e

echo "=========================================="
echo "  tmux 한글 입력 설정"
echo "=========================================="
echo ""

# 1. 한국어 로케일 설치 확인 및 활성화
echo "1️⃣ 한국어 로케일 활성화 중..."
if [ -f /etc/locale.gen ]; then
    # 주석 해제
    sudo sed -i 's/^# ko_KR.UTF-8 UTF-8/ko_KR.UTF-8 UTF-8/' /etc/locale.gen
    sudo locale-gen ko_KR.UTF-8
    sudo update-locale LANG=ko_KR.UTF-8
    echo "   ✅ 한국어 로케일 설치 완료"
else
    echo "   ⚠️ /etc/locale.gen 없음"
fi
echo ""

# 2. .bashrc에 로케일 설정 추가
echo "2️⃣ .bashrc에 로케일 설정 추가 중..."
if ! grep -q "export LANG=ko_KR.UTF-8" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# tmux 한글 입력 지원
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
export LC_CTYPE=ko_KR.UTF-8
EOF
    echo "   ✅ .bashrc에 로케일 설정 추가 완료"
else
    echo "   ℹ️ 이미 설정됨"
fi
echo ""

# 3. .tmux.conf에 UTF-8 설정 추가
echo "3️⃣ .tmux.conf에 UTF-8 설정 추가 중..."
if ! grep -q "set -ga terminal-overrides" ~/.tmux.conf; then
    # 기본 설정 뒤에 추가
    sed -i '/^set -g default-terminal "screen-256color"/a set -ga terminal-overrides ",*256col*:Tc"' ~/.tmux.conf
    echo "   ✅ .tmux.conf에 UTF-8 설정 추가 완료"
else
    echo "   ℹ️ 이미 설정됨"
fi
echo ""

# 4. 현재 세션에 로케일 적용
echo "4️⃣ 현재 세션에 로케일 적용 중..."
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
export LC_CTYPE=ko_KR.UTF-8
echo "   ✅ 현재 세션에 적용 완료"
echo ""

# 5. tmux 설정 재로드
echo "5️⃣ tmux 설정 재로드 중..."
if [ -n "$TMUX" ]; then
    tmux source-file ~/.tmux.conf
    echo "   ✅ tmux 설정 재로드 완료"
else
    echo "   ℹ️ tmux 세션 아님 (다음 시작 시 적용됨)"
fi
echo ""

echo "=========================================="
echo "  설정 완료!"
echo "=========================================="
echo ""
echo "📝 다음 단계:"
echo "  1. 현재 터미널에서 다음 명령 실행:"
echo "     export LANG=ko_KR.UTF-8"
echo "     export LC_ALL=ko_KR.UTF-8"
echo "     export LC_CTYPE=ko_KR.UTF-8"
echo ""
echo "  2. tmux 세션 재시작:"
echo "     tmux kill-server"
echo "     tmux new -s test"
echo ""
echo "  3. 한글 입력 테스트:"
echo "     안녕하세요!"
echo ""
echo "=========================================="