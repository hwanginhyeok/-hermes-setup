# 사용자 색상 취향 (tmux Dark Mono 테마 기반)

## tmux 테마 색상 추출

사용자의 `~/.tmux.conf`에서 추출한 색상 팔레트 (Dark Mono Theme):

```tmux
# 색상 팔레트 (Dark Mono)
bg_main    = #ffffff    (상태바 배경 - 순백)
bg_active  = #f0f0f0    (활성 윈도우 탭)
fg_dim     = #333333    (비활성 텍스트 - 진한 회색)
fg_mid     = #000000    (보조 텍스트 - 검정)
fg_dark    = #000000    (주요 텍스트 - 순수 검정)
accent     = #2563eb    (포인트 블루)
```

## 사용자 명시적 선호

- **주요 텍스트/강조**: `#000000` (순수 검정)
- **비활성 텍스트**: `#333333` (진한 회색)
- **Accent/포인트**: `#2563eb` (포인트 블루)
- **배경**: `#ffffff` (순백)

## PFD 적용 색상

사용자의 tmux 테마를 PFD HTML에 적용:

| 용도 | 색상 | Hex 코드 |
|------|------|---------|
| One-E Assembly (완성품) | 검정 | `#000000` |
| 완료/확보 상태 | 녹색 | `#00b894` |
| 부분 확보/경고 | 노랑 | `#fdcb6e` |
| 블로커/위험 | 빨강 | `#e17055` |
| 해당없음 | 회색 | `#b2bec3` |
| 배경 (상태바) | 순백 | `#ffffff` |
| 활성 탭 배경 | 옅은 회색 | `#f0f0f0` |
| Accent/포인트 | 포인트 블루 | `#2563eb` |

## 중요: 사용자 피드백

사용자가 "검정색 지정해줘봐"라고 명시적으로 요청함 (2026-05-28 세션).

이는 tmux 테마의 `fg_dark = #000000`과 일치함.

## 적용 예시

```python
# One-E Assembly 색상 (검정)
ONE_E_BORDER = '#000000'
ONE_E_TITLE = '#000000'
ONE_E_BADGE = '#000000'

# 상태별 색상
OK_BORDER = '#00b894'      # 완료
WARN_BORDER = '#fdcb6e'    # 경고
NG_BORDER = '#e17055'      # 블로커
GRAY_BORDER = '#b2bec3'    # 회색
```

## 중요: 두 가지 색상 영역 구분

사용자가 "색상", "색깔"을 언급할 때 두 가지 영역이 있음:

### 1. Hermes Agent 터미널 출력 색상
- **대상**: tmux 내에서 Hermes가 출력하는 메시지 색상
- **영향 요소**: ANSI escape codes, tmux 테마 설정
- **사용자 기대**: 검정(#000000) 텍스트 on 흰색(#ffffff) 배경
- **문제시**: 사용자가 "노란색으로 보인다"고 불만 제기

### 2. 프로젝트 아티팩트 색상
- **대상**: PFD HTML, CSS, 시각화 파일 등
- **영향 요소**: HTML/CSS 코드, color mapping 변수
- **사용자 기대**: tmux 테마와 일관성 (검정 accent, 흰색 배경)
- **문제시**: Assembly 카드 색상, 배지 색상 등

### 확인 방법

사용자가 "색상 변경"을 요청할 때:

```bash
# 1. 대상 확인 (가장 먼저)
"어느 색상을 말씀하는가요?
   - 제 터미널 출력 색상인가요?
   - PFD HTML의 Assembly 색상인가요?"

# 2. tmux 테마 확인 (터미널 출력인 경우)
cat ~/.tmux.conf | grep -A 10 '색상 팔레트'

# 3. HTML 색상 확인 (아티팩트인 경우)
grep -o '#[0-9A-Fa-f]\{6\}' SS500_PFD_*.html | sort | uniq -c
```

### 관련 세션 기록

- `references/color-confusion-debugging-session-20260528.md` — 색상 대상 오해 디버깅 사례
