# Python 스크립트 작성 패턴

## execute_code vs Heredoc

### ⚠️ 문제점
- **heredoc**를 사용하여 복잡한 Python 코드를 터미널에 삽입하면 문자열 이스케이프 문제가 발생합니다.
- 특히 백스래시(`\`), 따옴표(`\n`), 달러(`$`) 같은 특수문자가 이스케이프로 인식되어 `\n` 이스케이프 문제를 일으킵니다.

### ✅ 올바른 방법
- **execute_code 도구 사용**: 간단한 Python 코드 스크립트는 `execute_code` 도구로 작성
- 완전한 Python 모듈로 만들어서 import/호출 가능하게 작성

### 예시

```python
# ❌ 잘못된 방법 (heredoc)
cat > ~/project-manager/bot/pm_bot.py << 'EOF'
async def cmd_add(...):
    ...
EOF'

# ✅ 올바른 방법 (execute_code)
execute_code("""
def main():
    print("Hello, World!")
""")

# 또는 직접 파일 write 사용
write_file(path="~/project-manager/bot/pm_bot.py", content=...)
```

## 주요 포인트
- 문자열 이스케이프 회피: `\\n` → 실제 개행문, `\\t` → 탭, `\\$` → 변수
- 복잡한 로직: 함수 정의는 execute_code로, 파일 쓰기는 write_file로 분리

---