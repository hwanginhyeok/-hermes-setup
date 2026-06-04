#!/usr/bin/env python3
"""
월간 보고 아카이빙 + 최적화 제안
- 이전 달 보고 → archived/로 이동
- 최신 달 daily/ 폴더 유지
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path.home() / ".hermes" / "session_reports"
ARCHIVE_DIR = BASE_DIR / "archived"
DAILY_DIR = BASE_DIR / "daily"


def archive_previous_month():
    """이전 달 보고를 archived/로 이동"""
    current_month = datetime.now().strftime("%Y-%m")
    
    # 아카이브 폴더 생성
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 이전 달 디렉토리 확인
    if ARCHIVE_DIR.exists():
        for d in sorted(ARCHIVE_DIR.glob("20*")):
            if d.name == current_month:
                continue  # 현재 달은 스킵
        
            # 이미 아카이브에 있으면 패스
            target = ARCHIVE_DIR / d.name
            if not target.exists():
                shutil.move(str(d), str(target))
                print(f"📦 아카이빙: {d.name} → archived/")
            else:
                print(f"  ⏭ 이미 존재함: {target}")
    
    # daily/ 폴더에 남은 오래된 폴더 정리
    for d in DAILY_DIR.glob("20*"):
        if d.is_dir():
            # 현재 달이 아니면 archived로 이동
            if not d.name.startswith(current_month):
                target = ARCHIVE_DIR / d.name
                if not target.exists():
                    shutil.move(str(d), str(target))
                    print(f"  📦 {d.name} → archived/")


def optimize_reports():
    """보고 최적화 제안 분석"""
    print("\n## 최적화 제안 분석")
    print("=" * 50)
    
    # daily/ 폴더의 최신 보고 확인
    if not DAILY_DIR.exists():
        print("❌ daily/ 폴더 없음")
        return
    
    latest_reports = sorted(DAILY_DIR.glob("summary_*.md"))[-5:] if DAILY_DIR.glob("summary_*.md") else []
    
    if not latest_reports:
        print("❌ 최신 보고 없음")
        return
    
    # 키워드 빈도 분석
    keywords = {}
    for report in latest_reports:
        with open(report, 'r', encoding='utf-8') as f:
            content = f.read()
            # 주요 키워드 빈도
            for kw in ["댓글", "봇", "테스트", "배포", "확장", "쿠키"]:
                count = content.count(kw)
                if count > 0:
                    keywords[kw] = keywords.get(kw, 0) + count
    
    # 빈도순 정렬
    sorted_kw = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    
    print("\n📊 키워드 빈도 (최근 5개 보고)")
    for kw, count in sorted_kw[:10]:
        print(f"  {kw}: {count}회")
    
    # 키워드 기반 최적화 제안
    print("\n💡 최적화 제안")
    
    if keywords.get("댓글", 0) > 5:
        print("  🤖 댓글 봇 관련 작업이 많음 → 전용 스킬 생성 고려")
    
    if keywords.get("테스트", 0) > 5:
        print("  🧪 테스트 작업이 많음 → 테스트 자동화 강화")
    
    if keywords.get("쿠키", 0) > 3:
        print("  🍪 쿠키 갱신 관련 작업이 많음 → 쿠키 자동 갱신 스케줄 확인")
    
    if keywords.get("배포", 0) > 3:
        print("  🚀 배포 관련 작업이 많음 → 배포 파이프라인 강화")


def main():
    """메인 실행"""
    print("📅 월간 보고 아카이빙 + 최적화 제안")
    print(f"현재 달: {datetime.now().strftime('%Y-%m')}")
    print("=" * 50)
    
    # 아카이빙
    archive_previous_month()
    
    # 최적화 제안
    optimize_reports()
    
    print("\n" + "=" * 50)
    print("✅ 완료")


if __name__ == "__main__":
    main()
