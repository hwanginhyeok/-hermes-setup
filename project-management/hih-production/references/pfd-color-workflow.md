# PFD HTML 색상 분석 워크플로우

## 문제 상황

사용자가 "색깔 변경이 아직도 안됐다. 원익 분석 제대로 하고 수정방안 잡자. 지금 약간 노랑 계열이야."라고 보고 (2026-05-28).

## 분석 절차

### 1단계: HTML 파일 직접 확인

```bash
# 최신 PFD HTML 파일 찾기
find /home/gint_pcd/projects/HIH_2/HIH_Claude/산출물/04_PFD -name "*.html" -type f -mtime -7

# 파일 수정일 확인
ls -lt SS500_PFD_*.html | head -5
```

### 2단계: 색상 코드 추출 (BeautifulSoup 없이)

**주의**: BeautifulSoup 미설치 시 regex로 HTML 분석

```python
import re
from pathlib import Path

html_file = Path("SS500_PFD_생산공정도_V01_260310.html")

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 모든 Hex 색상 코드 추출
all_colors = re.findall(r'#[0-9A-Fa-f]{6}', content)
color_counts = {}
for color in all_colors:
    color_counts[color] = color_counts.get(color, 0) + 1

# 빈도순 정렬
sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)

for color, count in sorted_colors[:15]:
    print(f"{color}: {count}회")
```

### 3단계: 노란색 계열 필터링

```python
# 노란색 판단: R > 200, G > 200, B < 150
yellowish = []
for color, count in sorted_colors:
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    
    if r > 200 and g > 200 and b < 150:
        yellowish.append((color, r, g, b, count))

print("노란색 계열:")
for color, r, g, b, count in yellowish:
    print(f"  {color} (RGB: {r}, {g}, {b}): {count}회")
```

### 4단계: One-E Assembly 검색

```python
# One-E/완성품 관련 라인 찾기
lines = content.split('\n')
onee_lines = []

for line_num, line in enumerate(lines, 1):
    if any(keyword in line for keyword in ['One-E', 'ONE-E', 'one-e', '완성품', '최종조립', '차량완성']):
        onee_lines.append((line_num, line.strip()))

if onee_lines:
    print("One-E 관련 라인:")
    for line_num, line in onee_lines[:15]:
        print(f"  L{line_num}: {line[:100]}")
else:
    print("⚠️ One-E Assembly 없음!")
```

### 5단계: Assembly 컬럼 색상 확인

```python
# assy-col 클래스의 색상 추출
assy_colors = re.findall(
    r'\.assy-col\.[a-z-]+\{[^}]*border-color:#[0-9A-Fa-f]{6}[^}]*\}',
    content
)

# 인라인 스타일의 border-color 추출
inline_colors = re.findall(
    r'assy-col[^>]*style="[^"]*border-color:#[0-9A-Fa-f]{6}[^"]*"',
    content
)

print("CSS 정의:")
for color_def in assy_colors:
    print(f"  {color_def}")

print("\n인라인 스타일:")
for color_def in inline_colors[:10]:
    print(f"  {color_def[:100]}")
```

## 발견된 문제 (2026-05-28)

1. **One-E Assembly 누락**: HTML 파일에 One-E Assembly가 존재하지 않음
2. **노란색 계열 사용**: 검사 심볼(`.sym-insp`)과 스텝(`.s-insp`)이 `#ffeaa7` 사용
3. **경고 색상**: `#fdcb6e`가 warn 상태용으로 사용됨

## 수정 방안

### 1. One-E Assembly 추가

```python
# VHA 영역 다음에 One-E 추가
vha_pattern = r'(</div>\n\n<div style="text-align:center;font-size:1\.5em;color:#0984e3;margin:5px 0">↓</div>)'

one_e_html = '''
<!-- ONE-E ASSEMBLY -->
<div class="assy-col" style="border-color:#000000;border-width:3px">
  <span class="badge" style="background:#000000;color:#fff">최종완성품</span>
  <div class="assy-title" style="background:#000000;color:#fff">One-E</div>
  <div class="assy-sub">완성차량 (Speed Sprayer SS500)</div>
  ...
</div>
'''

modified_content = re.sub(vha_pattern, r'\1\n\n' + one_e_html, content)
```

### 2. 색상 사용자 취향에 맞춤

사용자 tmux 테마 참조 (`~/.tmux.conf`):
- 주요 텍스트: `#000000` (검정)
- 비활성: `#333333` (진한 회색)
- accent: `#2563eb` (포인트 블루)

### 3. 백업 후 수정

```python
# 백업 생성
backup_path = html_file.with_suffix('.html.backup')
with open(backup_path, 'w', encoding='utf-8') as f:
    f.write(original_content)

# 수정된 파일 저장
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(modified_content)
```

## 검증

브라우저에서 열어서 확인:

```bash
cmd.exe /c start "" "$(wslpath -w 'SS500_PFD_생산공정도_V01_260310.html')"
```

## 핵심 교훈

1. **BeautifulSoup 미설치 시 regex 사용**: `bs4` 모듈 없어도 HTML 색상 분석 가능
2. **사용자 색상 취향 확인**: tmux 테마 등 사용자 설정 파일 참조
3. **백업 필수**: 수정 전 항상 `.backup` 파일 생성
4. **One-E Assembly 누락 확인**: Sub-Assy만 있고 완성품 없는지 확인
