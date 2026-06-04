#!/usr/bin/env python3
"""
PFD HTML 색상 분석 스크립트
BeautifulSoup 없이 regex만 사용하여 HTML 색상 코드를 분석합니다.

사용법:
    python analyze_pfd_colors.py [HTML_FILE_PATH]

예시:
    python analyze_pfd_colors.py SS500_PFD_생산공정도_V01_260310.html
"""

import re
import sys
from pathlib import Path
from datetime import datetime


def analyze_pfd_colors(html_file: Path):
    """PFD HTML 파일의 색상을 분석합니다."""
    
    if not html_file.exists():
        print(f"✗ 파일 없음: {html_file}")
        return
    
    print("=" * 80)
    print("PFD HTML 색상 분석")
    print("=" * 80)
    print(f"파일: {html_file}")
    print(f"크기: {html_file.stat().st_size:,} bytes")
    print(f"수정: {datetime.fromtimestamp(html_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # HTML 읽기
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 모든 Hex 색상 코드 추출
    all_colors = re.findall(r'#[0-9A-Fa-f]{6}', content)
    color_counts = {}
    for color in all_colors:
        color_counts[color] = color_counts.get(color, 0) + 1
    
    # 빈도순 정렬
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("[전체 색상 코드 (빈도순)]")
    print("-" * 80)
    for color, count in sorted_colors[:20]:
        print(f"  {color}: {count}회")
    
    # 노란색 계열 필터링
    print("\n[노란색 계열 분석]")
    print("-" * 80)
    
    yellowish = []
    for color, count in sorted_colors:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # 노란색 판단: R > 200, G > 200, B < 150
        if r > 200 and g > 200 and b < 150:
            yellowish.append((color, r, g, b, count))
    
    if yellowish:
        print(f"✓ {len(yellowish)}개 노란색 계열 발견:")
        for color, r, g, b, count in sorted(yellowish, key=lambda x: x[4], reverse=True):
            print(f"  {color} (RGB: {r}, {g}, {b}) — {count}회")
    else:
        print("  (노란색 계열 없음)")
    
    # One-E 관련 요소 검색
    print("\n[One-E 관련 요소 검색]")
    print("-" * 80)
    
    lines = content.split('\n')
    onee_lines = []
    
    for line_num, line in enumerate(lines, 1):
        if any(keyword in line for keyword in ['One-E', 'ONE-E', 'one-e', '완성품', '최종조립', '차량완성']):
            onee_lines.append((line_num, line.strip()))
    
    if onee_lines:
        print(f"✓ {len(onee_lines)}개 One-E 관련 라인 발견:")
        for line_num, line in onee_lines[:10]:
            print(f"  L{line_num}: {line[:100]}")
    else:
        print("  ⚠️ One-E Assembly 없음!")
        print("  → templates/one-e-assembly.html 참조하여 추가 필요")
    
    # Assembly 컬럼 색상 확인
    print("\n[Assembly 컬럼 색상]")
    print("-" * 80)
    
    # CSS 정의된 색상
    assy_colors = re.findall(
        r'\.assy-col\.[a-z-]+\{[^}]*border-color:#[0-9A-Fa-f]{6}[^}]*\}',
        content
    )
    
    if assy_colors:
        print("CSS 정의:")
        for color_def in assy_colors:
            print(f"  {color_def}")
    
    # 인라인 스타일 색상
    inline_colors = re.findall(
        r'assy-col[^>]*style="[^"]*border-color:#[0-9A-Fa-f]{6}[^"]*"',
        content
    )
    
    if inline_colors:
        print("\n인라인 스타일:")
        for color_def in inline_colors[:10]:
            print(f"  {color_def[:100]}")
    
    # 검사 심볼 색상 확인
    print("\n[검사 심볼 색상]")
    print("-" * 80)
    
    insp_patterns = re.findall(
        r'\.s-insp\{[^}]*background:#[0-9A-Fa-f]{6}[^}]*\}',
        content
    )
    
    if insp_patterns:
        print("검사 스텝 배경색:")
        for pattern in insp_patterns:
            print(f"  {pattern}")
    
    sym_insp_patterns = re.findall(
        r'\.sym-insp\{[^}]*background:#[0-9A-Fa-f]{6}[^}]*\}',
        content
    )
    
    if sym_insp_patterns:
        print("검사 심볼 배경색:")
        for pattern in sym_insp_patterns:
            print(f"  {pattern}")
    
    # 권장사항
    print("\n[권장사항]")
    print("-" * 80)
    
    # 사용자 색상 테마 확인
    if '#000000' in [c for c, _ in sorted_colors[:10]]:
        print("✓ 검정색(#000000) 사용됨 (사용자 tmux 테마 일치)")
    else:
        print("⚠️ 검정색(#000000) 사용 안 됨")
        print("  → 사용자 선호: 검정(#000000)을 One-E Assembly에 사용")
    
    # 노란색 확인
    if yellowish:
        print(f"⚠️ {len(yellowish)}개 노란색 계열 사용됨")
        print("  → 검사 심볼/스텝에 노란색이 사용됨")
        print("  → One-E Assembly는 검정(#000000) 사용 권장")


def main():
    if len(sys.argv) < 2:
        print("사용법: python analyze_pfd_colors.py [HTML_FILE_PATH]")
        print("\n예시:")
        print("  python analyze_pfd_colors.py SS500_PFD_생산공정도_V01_260310.html")
        sys.exit(1)
    
    html_file = Path(sys.argv[1])
    
    if not html_file.exists():
        print(f"✗ 파일 없음: {html_file}")
        sys.exit(1)
    
    analyze_pfd_colors(html_file)


if __name__ == "__main__":
    main()
