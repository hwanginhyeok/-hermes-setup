# 텔레그램 PM-Bot 확장 패턴

## 구조

```
project-manager/
├── bot/
│   ├── pm_bot.py              # 메인 봇
│   └── extra_handlers.py      # 추가 명령 핸들러 (확장용)
├── docs/
│   └── PM-BOT-사용법.md        # 사용법 문서
└── restart_pm_bot.sh          # 봇 재시작 스크립트
```

## 확장 절차

### 1. 새 핸들러 함수 작성 (`bot/extra_handlers.py`)

```python
from telegram import Update
from telegram.ext import ContextTypes

async def cmd_newcommand(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """새 명령 설명"""
    # 권한 체크
    if not _authorized(update):
        return
    
    args = ctx.args
    # 로직 구현
    await update.message.reply_text("응답 메시지")
```

### 2. pm_bot.py에 import 추가

`from telegram.ext import filters,` 뒤에 추가:

```python
from bot.extra_handlers import cmd_newcommand
```

### 3. main() 함수에 핸들러 등록

```python
app.add_handler(CommandHandler("newcommand", cmd_newcommand))
```

### 4. 문서 업데이트

`docs/PM-BOT-사용법.md`에 사용법 추가

## ⚠️ pitfall: 직접 패치 금지

### 실패 사례 1: 이스케이프 문자 문제

```python
# ❌ 실패: python heredoc에서 \n\n 이스케이프 문제
content = f"async def cmd_add(...)\n\nasync def cmd_today(...)"
# 결과: SyntaxError: unexpected character after line continuation character
```

### 실패 사례 2: sed로 함수 끼워넣기

```bash
# ❌ 실패: import 순서 문제
sed -i '/from telegram.ext import (/,/filters,/a\
from bot.extra_handlers import cmd_add' pm_bot.py
# 결과: NameError: name 'cmd_add' is not defined (import가 호출보다 뒤에 위치)
```

### ✅ 올바른 방법: 별도 파일

이유:
1. 문법 에러 방지
2. import 순서 명확
3. 테스트 용이
4. 롤백 쉬움

## 재시작 스크립트 패턴

```bash
#!/bin/bash
BOT_DIR="$HOME/project-manager/bot"
PID_FILE="$HOME/.pm_logs/pm_bot.pid"
LOG_FILE="$HOME/.pm_logs/pm_bot.log"

# 기존 프로세스 종료
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        kill "$PID"
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

# 백그라운드 실행
cd "$BOT_DIR"
nohup python3 pm_bot.py >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
```

## 텔레그램 Conflict 에러

에러: `Conflict: terminated by other getUpdates request`

원인: 봇 인스턴스가 두 개 실행 중

해결:
```bash
# 모든 봇 프로세스 종료
pkill -f pm_bot.py

# 로그 파일 백업 (선택)
mv ~/.pm_logs/pm_bot.log ~/.pm_logs/pm_bot.log.old

# 재시작
bash ~/project-manager/restart_pm_bot.sh
```

## 추가된 명령 예시

### /add — 프로젝트 태스크 추가

```python
async def cmd_add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args
    if len(args) < 2:
        await update.message.reply_text("사용법: /add {프로젝트} {태스크명} [우선순위]")
        return
    
    project = args[0]
    task_name = " ".join(args[1:-1]) if len(args) > 2 else args[1]
    priority = args[-1].upper() if args[-1].upper() in ["P1", "P2", "P3"] else "P2"
    
    project_paths = {
        "bea": Path.home() / "be-a-studio",
        "stock": Path.home() / "stock",
        "insung": Path.home() / "insung_blog",
        "music": Path.home() / "music-lab",
        "hermes": Path.home() / "project-manager",
    }
    
    # ... 구현
```

### /auto — 자동화 작업 등록

```python
async def cmd_auto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args
    
    # /auto list 체크
    if len(args) == 1 and args[0] == "list":
        # 목록 반환
        return
    
    # 자동화 등록
    project = args[0]
    description = " ".join(args[1:])
    
    automation_file = PM_DIR / "automations" / f"{project}_{timestamp}.md"
    automation_file.write_text(automation_content)
```

## PM 세션 릴레이 메커니즘

**원리**:
1. 텔레그램 메시지 수신 (비-슬래시 텍스트)
2. tmux send-keys로 PM 세션에 입력
3. ===PM-END=== 마커까지 캡처
4. 텔레그램으로 응답 전송

**구현**:
```python
async def _relay_to_pm(message: str) -> str:
    async with PM_RELAY_LOCK:
        # 송신 직전 캡처
        before = _tmux_capture_full(PM_SESSION)
        baseline_len = len(before)
        
        # send-keys
        _tmux_send(PM_SESSION, message)
        
        # 마커까지 폴링
        deadline = time.monotonic() + PM_REPLY_TIMEOUT
        while time.monotonic() < deadline:
            current = _tmux_capture_full(PM_SESSION)
            if len(current) <= baseline_len:
                continue
            new_part = current[baseline_len:]
            idx = new_part.rfind(PM_END_MARKER)
            if idx >= 0:
                reply = new_part[:idx]
                cleaned = _strip_status_lines(reply).strip()
                return cleaned
```

**PM 응답 필수 조건**:
- 마지막 줄에 단독으로 `===PM-END===`
- statusline 노이즈 제거 (ctx:XX% 줄)
- 간결한 한국어 (5-15줄 권장)

## 참고 문서

- `~/project-manager/docs/PM-BOT-사용법.md` - 사용법
- `~/project-manager/bot/pm_bot.py` - 메인 봇
- `~/project-manager/bot/extra_handlers.py` - 추가 핸들러