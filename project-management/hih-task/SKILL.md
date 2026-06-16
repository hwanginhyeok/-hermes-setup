---
name: hih-task
description: "프로젝트 태스크 브리핑 + 세션 정리 + git 커밋. 세션 시작/종료 모두 사용. Claude Code .claude/skills/hih-task와 동일."
user_invocable: true
---

# /hih-task

태스크를 브리핑하고 인터랙티브하게 관리한다.
태스크 정리(audit)는 `/hih-task-clear`, 메모리는 `/hih-memory`, git은 `/hih-git`.

## 스킬 위치

이 스킬은 `~/hih-skills/hih-task/`에 있으며 `~/.hermes/skills/hih-task`로 심볼릭 링크되어 있습니다.
관련 스킬들도 모두 `~/hih-skills/`에 있으니 참고하세요.

## 사용자 선호

- 간결한 한국어로 브리핑 (모바일 5-15줄 권장)
- 텔레그램 중계 시 마지막 줄에 `===PM-END===` 마커 단독 라인 출력
- 긴 내용은 핵심만 추리고 "자세히는 PC에서" 안내
- **"카리 살려서"** - 토큰 절약을 위해 불필요한 설명 생략, 결과 중심 전달

## 포트폴리오 구조 원칙

**프로젝트별 케이스 페이지** (비권장 - 역량 중심):
```
src/pages/cases/{project-slug}/index.astro
├── Hero 섹션 (한 줄 설명)
├── 프로젝트 기본 정보
│   ├── 기간 (start~end)
│   ├── 상태 (진행 중 / 완료 / 보류)
│   ├── 태그
├── 핵심 성과 (숫자로 표현)
├── 기술 스택
├── 링크 섹션 (버튼형)
│   ├── 프로젝트 홈페이지
│   ├── 데모/스크린샷
│   ├── API 문서
│   └── GitHub 링크
└── 관련 프로젝트
```

**탭 클릭 시 해당 사이트/데모 연결**
- 탭을 누르면 해당 프로젝트의 웹사이트/데모/문서로 이동

## 실행 순서


## Codex/GLM 리뷰워크플로우

### 용도
계획 세우기 또는 리뷰할 때 Codex/GLM을 사용하여 독립적인 제2/제3 의견을 받음.

### 전제 조건
1. Z_AI_API_KEY 설정됨 (GLM용)
2. Codex CLI 설치됨 (codex)
3. Git repo 초기화됨

### Step 1: 계획 제안
```bash
# 사용자가 "계획 세워봐" 또는 "리뷰해봐" 요청
# PM이 작업 범위 정의 후 Codex/GLM에 발송
```

### Step 2: Codex 계획 생성
```bash
# pane 1 (Claude Opus) - PM
TASK_PROMPT="계획 요청: $@"
codex --prompt "$TASK_PROMPT" --output /tmp/codex_plan.md
```

### Step 3: GLM 리뷰
```bash
# pane 2 (GLM) - 리뷰어
REVIEW_PROMPT="아래 계획을 리뷰:

$(cat /tmp/codex_plan.md)"
# GLM 세션에 전송 (tmux send-keys 또는 delegate_task)
```

### Step 4: PM 비교 검증
```bash
# Codex 계획 vs GLM 리뷰 vs PM 의견 비교
# 충돌 시 사용자에게 질문
```

### Step 5: 최종 계획 확정
```bash
# 3개 의견 종합하여 최종 계획서 작성
# CURRENT_TASK.md에 반영
```

### 사용 예
```bash
# hih-task에서 계획 요청 시
/hih-task "Codex/GLM 리뷰: MBD 시뮬레이터 구현 계획"

# 리뷰 요청 시
/hih-task "GLM 리뷰: commit abc123 diff 분석"
```

### 모델 선택 가이드
- **Codex**: 코드 생성 및 기술 계획
- **GLM 4.6**: 빠른 리뷰 및 의견 (초안)
- **GLM 5.0**: 깊은 분석 및 비판



### 1. 태스크 파일 읽기
- `TASK.md` — 인덱스
- `CURRENT_TASK.md` — 진행 중
- `PREPARED_TASK.md` — 예정 (P1만 상세, P2/P3 개수만)
- `FINISHED_TASK.md` — 최근 5개만

### 2. 포트폴리오용 케이스 파일 생성
- 프로젝트별 `src/pages/cases/{project-slug}/index.astro` 생성
- 상세 내용: 기간, 핵심 성과, 기술 스택, 링크
- 포맷: Hero + 기본 정보 + 성과 + 기술 스택 + 링크 섹션

### 3. 기존 케이스 파일 갱신
- 내용 최신화
- 포트폴리오 `/capabilities/` 구조와 연결 고려

### 4. 브리핑 출력
```
## 프로젝트 케이스: {프로젝트명}

### 기본 정보
- 기간: {기간}
- 상태: {진행 중 / 완료 / 보류}

### 핵심 성과
- {숫자로 표현}

### 기술 스택
- {기술들}

### 링크
- [프로젝트 홈페이지](URL)
- [데모/스크린샷](URL)
- [API 문서](URL)
```

### 5. 태스크 파일 갱신
- `CURRENT_TASK.md` / `PREPARED_TASK.md` / `FINISHED_TASK.md` 갱신
**구조**
```
src/pages/cases/{project-slug}/index.astro
├── Hero 섹션 (한 줄 설명)
├── 프로젝트 기본 정보 (기간, 상태, 태그)
├── 핵심 성과 (숫자로 표현)
├── 기술 스택
├── 링크 섹션 (버튼형)
└── 관련 프로젝트
```

## 실행 순서


## Codex/GLM 리뷰워크플로우

### 용도
계획 세우기 또는 리뷰할 때 Codex/GLM을 사용하여 독립적인 제2/제3 의견을 받음.

### 전제 조건
1. Z_AI_API_KEY 설정됨 (GLM용)
2. Codex CLI 설치됨 (codex)
3. Git repo 초기화됨

### Step 1: 계획 제안
```bash
# 사용자가 "계획 세워봐" 또는 "리뷰해봐" 요청
# PM이 작업 범위 정의 후 Codex/GLM에 발송
```

### Step 2: Codex 계획 생성
```bash
# pane 1 (Claude Opus) - PM
TASK_PROMPT="계획 요청: $@"
codex --prompt "$TASK_PROMPT" --output /tmp/codex_plan.md
```

### Step 3: GLM 리뷰
```bash
# pane 2 (GLM) - 리뷰어
REVIEW_PROMPT="아래 계획을 리뷰:

$(cat /tmp/codex_plan.md)"
# GLM 세션에 전송 (tmux send-keys 또는 delegate_task)
```

### Step 4: PM 비교 검증
```bash
# Codex 계획 vs GLM 리뷰 vs PM 의견 비교
# 충돌 시 사용자에게 질문
```

### Step 5: 최종 계획 확정
```bash
# 3개 의견 종합하여 최종 계획서 작성
# CURRENT_TASK.md에 반영
```

### 사용 예
```bash
# hih-task에서 계획 요청 시
/hih-task "Codex/GLM 리뷰: MBD 시뮬레이터 구현 계획"

# 리뷰 요청 시
/hih-task "GLM 리뷰: commit abc123 diff 분석"
```

### 모델 선택 가이드
- **Codex**: 코드 생성 및 기술 계획
- **GLM 4.6**: 빠른 리뷰 및 의견 (초안)
- **GLM 5.0**: 깊은 분석 및 비판



### 1. 태스크 파일 읽기
프로젝트 루트에서:
- `TASK.md` — 인덱스
- `CURRENT_TASK.md` — 진행 중
- `PREPARED_TASK.md` — 예정
- `FINISHED_TASK.md` — 완료

### 2. 브리핑 출력
```
## 태스크 브리핑 — {프로젝트명}

### Current ({N}개)
| # | 태스크 | 시작일 | blocked | 비고 |
...

### Prepared ({N}개)
| # | 태스크 | 우선순위 | depends | 비고 |
... (P1만 표시, P2/P3는 개수만)

### Finished ({N}개)
최근 5개만 표시

### 조치 필요
- [ ] blocked 태스크 해결 방안
- [ ] prepared → current 전환 후보
- [ ] 아카이브 필요 여부
```

### 3. 태스크 관리 액션

사용자 요청에 따라:
- **"done #번호"** → CURRENT → FINISHED 이동 (완료일 자동 기입)
- **"start #번호"** → PREPARED → CURRENT 이동 (시작일 자동 기입)
- **"add 태스크명"** → PREPARED에 추가
- **"block #번호 사유"** → blocked 컬럼 업데이트
- **"archive"** → FINISHED → TASK_ARCHIVE/{YYYY-MM}.md 이동

### 4. 파일 포맷

#### TASK.md (인덱스)
```markdown
# {프로젝트명} 태스크

> Current: [CURRENT_TASK.md](CURRENT_TASK.md) | Prepared: [PREPARED_TASK.md](PREPARED_TASK.md) | Finished: [FINISHED_TASK.md](FINISHED_TASK.md)

## 요약
- Current: {N}개
- Prepared: {N}개 (P1: {n}, P2: {n}, P3: {n})
- Finished: {N}개
```

#### CURRENT_TASK.md
```markdown
# Current Tasks

| # | 태스크 | 시작일 | blocked | 비고 |
|---|--------|--------|---------|------|
```

#### PREPARED_TASK.md
```markdown
# Prepared Tasks

| # | 태스크 | 우선순위 | depends | 비고 |
|---|--------|:-------:|---------|------|
```

#### FINISHED_TASK.md
```markdown
# Finished Tasks

| # | 태스크 | 완료일 | 비고 |
|---|--------|--------|------|
```

### 5. 아카이브 규칙
- FINISHED 100개+ → 아카이브
- 월 이월 → 이전 달 아카이브
- 경로: `TASK_ARCHIVE/{YYYY-MM}.md`

### 6. 세션 정리 (옵션)
- 완료된 태스크 → FINISHED 이동
- 새 TODO → PREPARED 추가
- TASK.md 인덱스 갱신
- DIFFICULTY.md 기록 (2시간+ 삽질 시)
- git status 확인 → 의미 단위 커밋

### 7. 참고 자료
- Chrome Extension Scroll Debugging: `references/chrome-extension-scroll-debugging.md`
- 세션 크래시 복구 진단 상세: `references/pm-session-recovery.md`
- tmux 워커 풀 오케스트레이션 패턴: `references/tmux-worker-pool.md`
- PM 근본 원인 분석: 섹션 "PM 근본 원인 분석 (Root Cause Analysis)"
- tmux Hermes Pane 최적화: `references/tmux-hermes-pane-optimization.md` (2026-06-16)
- Notion 주간 페이지 생성 Cron 템플릿: `templates/weekly-page-creation-cron.md` (2026-06-16)

## PM 근본 원인 분석 (Root Cause Analysis)

PM 세션에서 문제 보고 시 READ → REVIEW → RE-DIRECT → REPORT 패턴을 따른다:

1. **READ** — 관련 문서/로그/DB 데이터 직접 조회
   - 코드: `read_file`, `search_files`로 하드코딩된 한도/셀렉터 확인
   - 로그: `journalctl`, `tail -f logs/*.log`
   - DB: Supabase 직조회 (`.venv/bin/python` + SDK)
   
2. **REVIEW** — 모순/이상/누락 짚어내기
   - 단순 요약 X, 진짜 RC 추적
   - "이게 문제로다" — 홈페이지 형식 vs 코드 한도 vs 알고리즘 구분
   
3. **RE-DIRECT** — 부족하면 재지시 또는 사용자 액션 요청
   - tmux send-keys로 세션에 전달
   - 사용자 실측 필요시 테스트 절차 제시
   
4. **REPORT** — 결론 + 다음 액션 제안
   - 옵션 A/B/C 형태로 제시 (공수/효과 포함)

**예시**: 댓글 수집 20건 병목 분석 (2026-05-12 ~ 05-14)
- READ: `feed_collector.py` L34 `max_posts=20` 하드코딩 발견 → **데드코드 오인 함정** (Python 봇서버는 이미 폐기)
- 사용자 정정: "파이썬 봇서버는 더이상 안쓰는걸로 아는데?" → 실제 호출 경로 재추적
- 재조사: Chrome 확장 `extractFeedPosts()` + `triggerNativeScroll()`이 실제 병목
- 실측 (browserbase): `window.scrollTo` → 13→34→69개 증가. `WheelEvent`만 → 0개 증가
- REVIEW: 다계층 병목 발견: (1) `triggerNativeScroll` wheel만 dispatch, scrollTo 안 됨 (2) API 경로 `/comments/*` vs `/comment/*` 미스매치 → 전부 404 → posting 50건 orphan (3) 로그인 가드 부재
- RE-DIRECT: 개발자 모드 확장 로드 + 서비스 워커 콘솔로 `[FEED-SCROLL]` 로그 실측
- REPORT: 3계층 동시 수정 (8727afe). 글 수집량 증가 확인.
- **교훈**: 다계층 병목. 1차 원인(scrollTo)만 고치고 끝내면 안 됨. API 경로/로그인/DB orphan까지 전수 조사 필요. 상세: `references/chrome-extension-scroll-debugging.md`

## 세션 크래시 후 상태 복구 (Session Recovery)

세션이 팅기거나 모델 전환으로 끊긴 후 "어제 하던 것 트래킹 + 이어서 진행" 요청이 들어오면 아래 순서로 상태를 재구성한다.

### 복구 데이터 소스 (우선순위 순)

| # | 소스 | 명령/경로 | 읽는 것 |
|---|------|-----------|---------|
| 1 | `daily_latest.json` | `~/.pm_logs/daily_latest.json` | git 현황, 태스크, cron 에러, unpushed, stale_tasks, broken_symlinks |
| 2 | `session_search` | 최근 5~10개 세션 | 세션 제목/시간으로 어제 작업 내역 파악 |
| 3 | `CURRENT_TASK.md` | 각 프로젝트 | 진행 중 태스크 + blocked 상태 |
| 4 | `git log` | 각 프로젝트 `--oneline -10` | 어제 커밋 내역 |
| 5 | `tmux list-sessions` | | 워커 풀(w1/w2/w3) 상태 — 어떤 워커가 어떤 프로젝트를 담당 중인지 |
| 6 | cron 에러 로그 | `~/.pm_logs/*.log`, `~/stock/logs/*.log` | ImportError, Conflict, rclone 실패 등 |

### 복구 워크플로우

1. **READ**: daily_latest.json + session_search + 각 프로젝트 CURRENT_TASK + git log 동시 읽기
2. **REVIEW**: 완료된 작업 / 끊긴 작업 / 미해결 이슈 분류
3. **PRIORITIZE**: 크론 장애(P0) > 기능 개발(P1) > 정리(P2) 순으로 분류
4. **TRIAGE 테이블 출력**: 사용자에게 번호 + 상태 + 원인 + 해결책 요약
5. **ACT**: 터미널 권한 있으면 직접 수정, 없으면 tmux 위임 또는 명령어 제공

### 자주 나오는 크론 에러 패턴

| 에러 | 원인 | 해결 |
|------|------|------|
| `ImportError: NumPy 1.x vs 2.x` | 시스템 matplotlib가 구 NumPy로 빌드 → pip NumPy 업그레이드 후 충돌 | `.venv`에서 `pip install --upgrade matplotlib` |
| `telegram.error.Conflict` | 같은 봇 토큰으로 여러 프로세스가 getUpdates 호출 | `ps aux | grep bot`으로 중복 확인 → 잔류 프로세스 kill + 서비스 재시작 |
| `rclone upload failed` | GDrive 원격 설정 만료 또는 경로 오류 | `rclone config reconnect gdrive:` — 아래 VNC 인증 절차 참조 |
| `name 'category' is not defined` | 데이터 구조 vs 코드 불일치 — `category` vs `brand` 필드명 차이 | **필드명 매핑 확인**: candidates JSON에는 `brand` 필드만 있음. `card_data.get("category")` 대신 `card_data.get("brand").lower()` 사용. .pyc 캐시 삭제 후 재실행: `find . -name "*.pyc" -delete && find . -name "__pycache__" -type d -exec rm -rf {} +` |

### rclone GDrive 토큰 갱신 (VNC 필요)

rclone 토큰 만료 시 구글 브라우저 인증이 필요하다. VNC 환경에서 수행:

```bash
# 1. rclone을 background로 실행 (VNC 디스플레이에 브라우저 팝업)
DISPLAY=:1 rclone config reconnect gdrive: &

# 2. VNC 화면에서 Chrome에 Google 로그인 창이 뜸 → 사용자가 인증

# 3. 완료 확인
rclone lsd gdrive:
```

**주의**: rclone 프로세스를 중간에 kill하면 인증 플로우가 끊김. 사용자가 VNC에서 인증 완료할 때까지 기다릴 것.

### 참고 자료
- 세션 복구 진단 상세: `references/pm-session-recovery.md`
- Chrome Extension Scroll Debugging: `references/chrome-extension-scroll-debugging.md`
- Be:A Studio 파이프라인 트러블슈팅: `references/be-a-studio-pipeline-troubleshooting.md`
- PM 근본 원인 분석: 섹션 "PM 근본 원인 분석 (Root Cause Analysis)"

## 워커 풀 아키텍처 (2026-05-13 개편)

프로젝트별 고정 세션 폐지. PM + w1/w2/w3 워커 풀로 운영.

```
PM  — 오케스트레이터. 읽기/리뷰/재지시.
w1  — 워커 1. PM이 프로젝트 할당.
w2  — 워커 2. 병렬 작업용.
w3  — 워커 3. 필요시 추가.
```

### 워커 할당
```bash
# 할당 (C-u로 버퍼 클리어 필수)
tmux send-keys -t w1 C-u
tmux send-keys -t w1 "source ~/.bashrc && cd ~/PROJECT && claude --add-dir ~/PROJECT --add-dir ~/project-manager" Enter

# 프롬프트 확인 (sleep 10 후)
tmux capture-pane -t w1 -p | tail -3   # ❯ 프롬프트 확인

# 해제
tmux send-keys -t w1 "/exit" Enter
```

### 세션 상태 체크
```bash
python3 ~/project-manager/pm.py sessions   # 워커별 ctx/모델/프로젝트
```

### 워커 ctx 소모 관리
- ctx 90%+ + 세션 시간 긴 경우 → `/clear`로 리셋 후 재지시
- `/clear` 전 커밋 여부 반드시 확인 (uncommitted 날아갈 수 있음)
- `/clear` 후 재지시 시 이전 컨텍스트 없으니 핵심만 짧게

상세: `references/tmux-worker-pool.md`

## 주의
- PM 세션에서는 읽기만. 수정 지시는 워커(w1/w2/w3)에 `tmux send-keys`로 전달.
- 터미널 권한이 차단되면 RE-DIRECT만 하고 사용자에게 명령어를 제공한다.
- **워커 경계 준수**: 각 워커는 한 번에 하나의 프로젝트만. 전환 시 claude 재시작 필수.
## Chrome 확장 스크롤 디버깅 패턴 (인성이블로그 2026-05-14)

네이버 피드 스크롤이 안 먹는 증상 → 수집량이 19~20건에서 멈춤.

### 원인 계층
1. **Playwright vs 익스텐션 혼동**: `feed_collector.py`(Playwright)는 데드코드. 실제 수집은 Chrome 익스텐션 `background.js`의 `extractFeedPosts()`가 담당.
2. **triggerNativeScroll 함정**: `WheelEvent` dispatch만 하고 `window.scrollTo()` 미실행 → 이벤트가 실제 스크롤 트리거 안 함.
3. **API 경로 미스매치**: 익스텐션 `/comments/*` → 서버 `/comment/*` (복수/단수 차이) → 전부 404 → `.catch(()=>{})` 로 에러 무시 → `posting` 상태 50건 orphan.

### 디버그 절차
```bash
# 1. 어떤 코드가 실제 수집하는지 먼저 확인
grep -n 'extractFeedPosts\|parseFeedInPage\|triggerNativeScroll' chrome-extension-poc/background.js

# 2. 브라우저에서 직접 스크롤 테스트
# chrome://extensions → 서비스 워커 콘솔 → 수집 실행 → [FEED-SCROLL] 로그 확인

# 3. API 경로 일치 확인
grep -n "apiFetch.*comment" chrome-extension-poc/background.js  # 익스텐션 호출 경로
grep -n "app\.\(post\|get\|put\).*comment" api_server.py        # 서버 엔드포인트
```

### 수정 패턴
```js
// triggerNativeScroll — scrollTo 1순위, wheel은 보강
function triggerNativeScroll() {
  const prevY = window.scrollY;
  window.scrollTo(0, document.documentElement.scrollHeight);
  // wheel 이벤트 보강...
  return { scrolled: window.scrollY !== prevY, ... };
}
```

### posting orphan 복구
```python
# posting 상태 stuck 건들 approved로 롤백
sb.table("pending_comments").update({"status": "approved"}) \
  .eq("user_id", uid).eq("status", "posting").execute()
```
- **프로젝트 세션 경계 준수**: 각 프로젝트 세션은 해당 프로젝트만 다룬다. 다른 프로젝트 이슈가 나오면 메모만 하고 해당 프로젝트 세션에서 처리하도록 안내. 사용자가 정정하면 즉시 돌아갈 것.

## 함정 — Chrome 확장 수정 후 실측
## 함정 — Chrome 확장 수정 후 실측
**사용자가 "확장 업데이트/빌드 해야 해?" 물어보면 → 아니요.** 개발자 모드로 로드된 확장은 `chrome://extensions` → 🔄 새로고침만 하면 코드 변경이 즉시 반영됨. zip 빌드/웹스토어 업로드는 배포용이지 실측용이 아님.

**핵심 확인**: 서비스 워커 콘솔에서 `chrome.runtime.getManifest().version` 입력 → 수정된 버전이 나와야 함. 구버전이면 리로드가 안 된 것.

**VNC 자동화 제약**:
- TigerVNC 창관리자가 `_NET_ACTIVE_WINDOW` 미지원 → `xdotool windowactivate` 실패
- 대신 `google-chrome "URL"` 로 새 탭 열기 (기존 세션에 자동 연결)
- Chrome 백그라운드 실행은 반드시 `terminal(background=true)` 사용 (nohup/disown 차단됨)

## PM 오케스트레이터 시스템 정밀 분석 (2026-05-15)

PM 시스템 전체를 정밀 분석하여 현재 상태와 개선 기회를 체계적으로 파악하는 프레임워크.

### 분석 항목

#### 1. 구조적 건전성 (Structural Integrity)
- **PM 본체**: 파일 수 (MD 209개), git 크기 (6.9M), 심링크 상태
- **tmux 세션**: 10개 세션 정상 작동 (PM + 7 프로젝트 + hermes + 기타)
- **파일 구조**: CLAUDE.md/TASK/PREPARED/FINISHED 4단계 체계 준수
- **심링크**: `docs/projects/`에서 각 프로젝트 문서 연결 완료 여부

**검증 명령어**:
```bash
# PM 본체 상태
find ~/project-manager -name "*.md" | wc -l
du -sh ~/project-manager/.git
tmux list-sessions -F "#{session_name}: #{session_windows} windows"

# 심링크 건강
find -L ~/project-manager/docs/projects -type l ! -readable 2>/dev/null
```

#### 2. 운영 효율성 (Operational Efficiency)

**잘 작동하는 부분**:
- `pm.py status` - 통합 현황 (git, task, disk 한눈에)
- `pm.py health` - 건강 진단 (용량/의심항목/gitignore/venv)
- `pm.py validate` - 태스크 일관성 검증
- cron 관리 - 최근 35일+ dead job 정리로 가벼워짐

**개선 필요 영역**:

1. **태스크 요약 자동 동기 부재**
   - 증상: 인성이 TASK.md says "Current 5개" → 실제 CURRENT_TASK.md는 3개
   - 원인: 자식 프로젝트가 CURRENT_TASK 업데이트해도 TASK.md 요약을 수동으로 갱신해야 함
   - 영향: PM이 `pm.py tasks`로 전체 현황 보더라도 개별 프로젝트 내부 불일치를 못 잡음
   - 해결 방향: 자식 프로젝트에서 CURRENT_TASK 변경 시 TASK.md 요약도 자동 갱신하는 hook 추가

2. **블로커 시각화 부족**
   - 증상: `pm.py tasks`에서 블로커를 보여주지만, 어디서 막혔는지 한눈에 안 들어옴
   - 원인: 블로커별 의존성 맵(DAG)이 없어서 해소 순서 판단 어려움
   - 영향: P1 태스크가 P2 블로커로 막혀있는지, 외부 의존성인지 파악 늦음
   - 해결 방향: 의존성 그래프 시각화 (graphviz DOT 출력)

3. **cron health 모니터링 부재**
   - 증상: be-a-studio cron 간헐적 segfault → PM이 자동 감지 못 함
   - 원인: 각 cron 로그의 마지막 timestamp를 체크하는 모니터링 없음
   - 영향: 24h+ 멈춰있어도 사용자가 수동으로 발견해야 암
   - 해결 방향: `pm.py cron-health` 서브커맨드 추가 (각 로그 timestamp 체크 → 24h+ 멈추면 알림)

#### 3. PM 역할 수행 효율성 (Orchestration Efficiency)

**READ 단계** (데이터 직조회):
- ✅ 데이터 직조회 도구 풍부 (Supabase, git, logs)
- ✅ 심링크로 빠른 문서 접근
- ⚠️ 프로젝트별 CURRENT_TASK를 일일이 열어야 함 → `pm.py tasks`로 일부 해결
- ⚠️ daily_latest.json (20K)이 존재하지만 생성 메커니즘 불명확 (daily_report.py는 35일+ dead로 제거됨)

**REVIEW 단계** (모순/이상/누락 짚어내기):
- ✅ uncommitted 파일 감지 (현재 3개: 인성이 2, be-a-studio 1)
- ✅ validate로 태스크 불일치 감지 (TASK.md vs CURRENT_TASK.md)
- ⚠️ "지시 vs 실행 갭 리뷰"가 완전 수동 → 커밋 해시 있으면 매번 git show로 hunk 확인 필요

**RE-DIRECT 단계** (재지시):
- ✅ tmux send-keys로 지시 전달 가능
- ⚠️ 현재 active pane을 모르면 send-keys 타겟 불확실
- 영향: PM이 w1/w2/w3 중 어디에 작업을 지시해야 할지 트래커 부족

**VERIFY 단계** (검증):
- ⚠️ L2 hunk 검증이 완전 수동
- ⚠️ 산출물 확인(ls, ffprobe, DB query)도 수동
- 해결 방향: `pm.py verify <commit-hash>`로 자동 검증 스크립트 추가

#### 4. 아키텍처 개선 기회 (Architectural Improvements)

**A. 병렬 워커 활용도**
- 현재: tmux 세션 = 프로젝트 고정, pane2~ = 병렬 슬롯
- 문제: 병렬 활용 패턴이 수동으로만 작동
- 개선: `pm.py parallel <project> --workers 3 --file list` 래퍼로 자동 분배

**B. 태스크 의존성 관리**
- 현재: PREPARED_TASK에 `depends` 컬럼 있지만, 의존성 해소가 자동이 아님
- 문제: 부모 태스크 완료 → 자식 `depends` 갱신 수동
- 개선: 간단한 의존성 그래프 + 자동 의존 해제 스크립트

**C. 리포트 자동화**
- 현황: daily_report.py, weekly_report.py가 35일+ dead로 제거됨
- 그러나 주간 리포트(20K)는 여전히 생성됨 → 어떤 메커니즘으로?
- 개선: 리포트 생성 경로 명확화 후 PM health 통합

### 우선순위 제언

**즉시 실행 (low-hanging fruit)**:
1. 태스크 요약 자동 갱신: 자식 프로젝트에서 CURRENT_TASK 변경 시 TASK.md 요약도 업데이트하는 hook
2. uncommitted 파일 정리: 현재 3개(인성이 2, be-a-studio 1) 커밋
3. 블로커 집계: `pm.py blocked`로 전체 블로커 + 원인 + 해소 액션 한눈에 보기

**중기 (high-value)**:
4. cron health 모니터: 각 cron 로그의 마지막 timestamp 체크 → 24h+ 멈추면 알림
5. 지시-실행 갭 자동 검증: 커밋 메시지에서 태스크 ID 파싱 → 관련 파일 hunk 추출 → PM이 리뷰
6. 의존성 그래프: PREPARED_TASK의 depends로 DOT graph 생성 → 블로커 체인 시각화

**장기 (architectural)**:
7. PM 대시보드 웹 인터페이스: 현재 TUI지만, 웹에서 접근하면 모바일에서도 PM 가능
8. 자식 세션 결과 자동 수집: 각 프로젝트 세션이 완료 보고를 PM DB에 직접写入 → PM이 READ 단계 스킵 가능

### 참고 자료
- PM 시스템 전체 분석: `references/pm-system-analysis-20260515.md`
