# WSL 환경 OAuth 작동 방식

## OAuth 리다이렉트 원리

Google OAuth는 **로컬 서버 없이도 작동**합니다:

1. 브라우저에서 OAuth URL 열기
2. Google 로그인 + 권한 승인
3. **브라우저 주소창에서 `redirect_uri`로 리다이렉트**
4. 주소창 전체 URL 복사 → `/auth-code`에 전달

## WSL에서의 작동 방식

### ❌ 오해
- "포트 3000에 서버를 띄워야 한다" (X)
- "localhost:1이 안 열린다" (X)
- "WSL 네트워킹 문제다" (X)

### ✅ 실제 방식
**OAuth는 브라우저의 주소창만 사용**합니다:

1. OAuth URL에 `redirect_uri=http://localhost:3000` 포함
2. 권한 승인 후 Google은 브라우저 주소창으로 리다이렉트
3. **주소창 URL을 복사** → 전체 URL 전달

### 예시

**권한 승인 화면:**
```
구글 계정이 http://localhost:3000/?code=4/0A...&scope=... 로
리다이렉트됩니다.
```

**브라우저 주소창:**
```
http://localhost:3000/?code=4/0A...&scope=...
```

**→ 이 전체 URL을 복사해서 터미널에 붙여넣기!**

## WSL에서의 실제 작동 순서

### STEP 1: OAuth URL 생성
```bash
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url
```

### STEP 2: 브라우저에서 열기
- WSL에서는 Windows 브라우저 사용 (기본적으로 URL 클릭 시 자동 열림)
- 또는 URL 복사해서 Windows 브라우저 주소창에 붙여넣기

### STEP 3: 권한 승인
- Google 계정 로그인
- 요청된 권한 확인 (Gmail, Calendar, Drive, etc.)
- "허용" 클릭

### STEP 4: 리다이렉트 URL 복사
**중요!**
- 포트 3000에 서버가 떠 있을 필요 없음
- 단지 브라우저 주소창에 나타난 URL을 복사하면 됨
- "http://localhost:3000/?code=..." 전체를 복사

### STEP 5: auth-code 교환
```bash
python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-code "http://localhost:3000/?code=4/0A...&scope=..."
```

## 포트 3000이 왜 나올까?

setup.py의 기본 설정이 `http://localhost:3000`입니다:

```python
REDIRECT_URI = "http://localhost:3000"
```

이것은:
- **리다이렉트 URI 식별자** (Google OAuth 표준)
- 포트 번호 자체는 중요하지 않음
- 실제로 서버가 떠 있을 필요 없음

## WSL 네트워킹

### Windows 브라우저 접근
- `http://localhost:3000` → Windows 브라우저에서 바로 접근 가능
- `http://127.0.0.1:3000` → Windows에서도 접근 가능

### WSL에서 curl 테스트
```bash
curl http://localhost:3000  # 3000번 포트가 사용 중인지만 확인
# 실제로는 서버가 없어도 에러 안 남음 (Connection refused)
```

## 정리

### ✅ 올바른 이해
- OAuth는 포트 서버가 필요 없음
- 브라우저 주소창에서 리다이렉트 URL 복사만 하면 됨
- WSL에서도 Windows 브라우저 자동 열림 (URL 클릭 시)

### ❌ 오해
- "포트 서버를 띄워야 한다"
- "포트가 안 열려서 안 된다"
- "WSL 네트워킹 문제다"

## 다른 OAuth 스킬과의 차이

| 스킬 | 리다이렉트 방식 |
|------|---------------|
| google-workspace | 브라우저 주소창 (서버 불필요) |
| music-lab (YouTube) | 서비스 계정 인증 (다른 방식) |

music-lab은 Google OAuth가 아니라 YouTube API별 인증이므로 다른 방식 사용합니다.
