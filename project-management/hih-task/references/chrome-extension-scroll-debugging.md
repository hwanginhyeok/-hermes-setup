# Chrome Extension Scroll Debugging — 네이버 피드 수집 병목

## 문제 패턴

- 이론적 상한: 100개 (`MAX_FEED_POSTS`)
- 실제 수집: ~19-20개에서 멈춤
- 여러 병목이 중첩되어 있었음

## 루트 코즈 3계층 (2026-05-14 확정)

### Layer 1: triggerNativeScroll 스크롤 미작동

**원인**: `triggerNativeScroll()`이 `WheelEvent` dispatch만 하고 실제 `window.scrollTo`는 마지막에 있지만 효과 없음. 네이버 모바일 피드는 `document.scrollingElement`에서 `window.scrollTo`로만 스크롤됨.

**실측** (browserbase):
- `window.scrollTo(0, scrollHeight)` 실행 → 13개 → 34개 → 69개로 증가
- `WheelEvent`만 dispatch → 0개 증가 (이벤트 리스너가 없음)

**수정**: `window.scrollTo`를 1순위로, wheel은 보강용으로 강등
```javascript
function triggerNativeScroll() {
  const prevY = window.scrollY;
  window.scrollTo(0, document.documentElement.scrollHeight); // 1순위
  document.dispatchEvent(new WheelEvent('wheel', {...}));    // 보강
  document.body.dispatchEvent(new WheelEvent('wheel', {...})); // 보강
  return { scrolled: window.scrollY > prevY, prevY, newY: window.scrollY };
}
```

**핵심**: `scrollTo` 직후 `sleep(1500)` 필요 — MutationObserver 설치 전에 DOM 로딩이 완료되는 것 방지

### Layer 2: API 경로 미스매치 (치명)

**원인**: 익스텐션이 `/comments/*` 호출 → 서버는 `/comment/*` → 전부 404 → `.catch(()=>{})`로 무시 → 잠금만 걸고 해제/결과보고 안 됨

| 익스텐션 (수정 전) | 서버 엔드포인트 | 상태 |
|---|---|---|
| `/comments/lock` POST | `/comment/lock-for-posting` | 404 |
| `/comments/${id}` POST | `/comment/post-result/${id}` | 404 |
| `/comments/${id}` DELETE | `/comment/unlock/${id}` | 404 |
| `/comments/ready` GET | `/comment/ready-to-post` | 404 |

**결과**: posting 상태 50건이 orphan로 잠김 (잠금만 걸고 해제 안 됨)

**예방 패턴**: 익스텐션↔서버 API 경로 변경 시 양쪽 동시 수정. `.catch(()=>{})`가 에러를 삼키므로 404가 조용히 발생함. 최소한 `console.warn` 로깅 필요.

### Layer 3: 로그인 가드 부재

**원인**: `runPostingLoop`에 로그인 사전체크 없음 → 쿠키 만료 상태에서 게시 시도 → `tryPost`는 가드 있지만 서버 잠금은 이미 실행됨 → posting orphan

**수정**: 루프 시작 전 `getNaverLoginStatus()` 가드 + finally에서 잔여 posting `unlock-all`

## 데드코드 오인 함정 (05-12 사례)

**증상**: `feed_collector.py` L34 `max_posts=20` 발견 → "이게 병목" 판정
**실제**: Python 봇서버는 이미 폐기(RETIRE-PW-EXECUTE). Chrome 확장 `extractFeedPosts()`가 실제 호출 경로.

**예방**:
1. 먼저 **실제 호출 경로** 추적 (systemd 상태, cron, 최근 로그)
2. 코드 발견 시 "이게 지금 실행되고 있나?" 검증 필수
3. FINISHED_TASK.md의 폐기 기록 확인

## Playwright 쪽도 동일 문제 (feed_collector.py)

`src/collectors/feed_collector.py`에도 스크롤 로직 없이 초기 DOM만 파싱 → ~20개 한계.
무한 스크롤 추가: `window.scrollTo` + `mouse.wheel` + noGrowthStreak 3회.
다만 이 파일은 현재 데드코드 (크롬 익스텐션이 수집 담당).

## VNC에서 Chrome 개발자 모드 실행

로컬 수정 후 실측하려면 Chrome에 개발자 버전을 로드해야 함. **zip 빌드/웹스토어 업로드 불필요.**

```bash
# VNC 디스플레이에서 Chrome 실행 (WSL TigerVNC :1)
# 반드시 terminal(background=true)로 실행 (nohup/disown은 차단됨)
DISPLAY=:1 google-chrome \
  --load-extension=/home/window11/insung_blog/chrome-extension-poc \
  --no-first-run --no-sandbox \
  chrome://extensions
```

**주의**:
- 웹스토어 버전과 충돌 → 웹스토어 버전을 먼저 비활성화
- `chrome://extensions` → 개발자 모드 ON → 확장 카드 🔄 새로고침 = 코드 변경 즉시 반영
- 서비스 워커 콘솔: 확장 카드의 "서비스 워커" 링크 → DevTools 열림
- **사용자가 "확장 업데이트 할까?" 물어보면** → 웹스토어 빌드 필요 없음. chrome://extensions에서 🔄만 누르면 됨

## 테스트 절차

1. 확장 로드 (개발자 모드) — 위 VNC 실행 또는 수동 chrome://extensions
2. 네이버 로그인 상태 확인 (NID_AUT 쿠키)
3. `/bot` → "이웃 새글 수집" 실행
4. `chrome://extensions` → 서비스 워커 → DevTools Console
5. `[FEED-SCROLL]` 로그로 라운드별 증가 확인:
   ```
   [FEED-SCROLL] initial parse: 18 posts
   [FEED-SCROLL] round=0 scroll={"scrolled":true,"prevY":0,"newY":2541}
   [FEED-SCROLL] round=0 posts=34 prev=18
   [FEED-SCROLL] round=1 posts=69 prev=34
   ```
6. `scrolled: true` 나오면 정상, `false`면 scrollTo가 안 먹는 것

## 파일 위치

- 크롬 익스텐션: `chrome-extension-poc/background.js`
  - `triggerNativeScroll()` ~L877
  - `extractFeedPosts()` ~L912
  - `runPostingLoop()` ~L572
- Playwright (데드): `src/collectors/feed_collector.py`
- 서버 API: `api_server.py` L853+ (`/comment/lock-for-posting`, `/comment/post-result/{id}`, `/comment/unlock-all`)
