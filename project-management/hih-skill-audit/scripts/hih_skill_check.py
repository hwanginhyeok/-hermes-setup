#!/usr/bin/env python3
"""
hih 스킬 자동 검증 스크립트
스킬의 네이밍, frontmatter, 구조, 메타데이터를 자동으로 검증
"""

import os
import sys
from pathlib import Path
import re
from datetime import datetime

def check_skills(skills_dir=None):
    """스킬 검증"""
    if skills_dir is None:
        skills_dir = Path.home() / ".hermes" / "skills"
    else:
        skills_dir = Path(skills_dir)

    if not skills_dir.exists():
        print(f"❌ 스킬 디렉토리 없음: {skills_dir}")
        return False

    # 문제점 저장
    issues = {
        'critical': [],  # 기능 오류 (즉시 조치)
        'high': [],      # 기능 개선 필요
        'medium': [],    # 표준화 권장
        'low': [],       # 개선 제안
        'info': []       # 정보만
    }

    # hih 스킬만
    hih_skills = sorted(skills_dir.glob("hih-*"))

    if not hih_skills:
        print(f"⚠️  hih 스킬 없음: {skills_dir}")
        return True

    print(f"📊 {len(hih_skills)}개 hih 스킬 검증 시작...\n")

    for skill_path in hih_skills:
        if not skill_path.is_dir() and not skill_path.is_symlink():
            continue

        skill_name = skill_path.name
        skill_md = skill_path / "SKILL.md"

        # SKILL.md 존재 확인
        if not skill_md.exists():
            issues['critical'].append(f"{skill_name}: SKILL.md 부재")
            continue

        try:
            content = skill_md.read_text()
            lines = content.split('\n')
        except Exception as e:
            issues['critical'].append(f"{skill_name}: 읽기 실패 ({e})")
            continue

        # 1. 네이밍 부정합 체크
        frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            name_match = re.search(r'name: ([^\n]+)', frontmatter)
            if name_match:
                declared_name = name_match.group(1).strip().lower()
                # hih-claude vs codex 같은 케이스
                if 'claude' in skill_name and 'codex' in declared_name:
                    issues['critical'].append(
                        f"{skill_name}: 네이밍 부정합 (폴더={skill_name}, name={declared_name})"
                    )

        # 2. frontmatter 체크
        if not content.startswith('---'):
            issues['critical'].append(f"{skill_name}: YAML frontmatter 부재")
        else:
            # user_invocable 체크
            if "user_invocable:" not in content[:500]:
                issues['medium'].append(f"{skill_name}: user_invocable 미명시")

            # allowed-tools 체크
            if "allowed-tools:" not in content[:500]:
                if skill_name in ['hih-clear', 'hih-git', 'hih-cron', 'hih-task']:
                    issues['medium'].append(f"{skill_name}: allowed-tools 명시 권장")

        # 3. Use when 트리거 체크
        if "Use when:" not in content and "사용 타이밍:" not in content:
            if skill_name not in ["hih-dev", "hih-claude", "hih-codex"]:
                issues['low'].append(f"{skill_name}: Use when/사용 타이밍 미명시")

        # 4. 길이 체크
        line_count = len(lines)
        if line_count > 400:
            issues['high'].append(f"{skill_name}: 과도한 길이 ({line_count} lines, >400)")
        elif line_count > 300:
            issues['medium'].append(f"{skill_name}: 긴 스킬 ({line_count} lines, >300)")

        # 5. 섹션 구조 체크
        if "## 실행 시 동작" not in content and "## 실행 순서" not in content:
            if skill_name not in ["hih-dev", "hih-claude", "hih-dual", "hih-glm"]:
                issues['info'].append(f"{skill_name}: 표준 실행 섹션 부재")

    # 리포트 출력
    print("=" * 60)
    print("📋 검증 결과")
    print("=" * 60)

    total_issues = 0
    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        items = issues[severity]
        if items:
            icon = {
                'critical': '🚨',
                'high': '⚠️ ',
                'medium': 'ℹ️ ',
                'low': '💡',
                'info': '📌'
            }[severity]
            print(f"\n{icon} {severity.upper()} ({len(items)}건)")
            for item in items:
                print(f"  - {item}")
            total_issues += len(items)

    print("\n" + "=" * 60)
    if total_issues == 0:
        print("✅ 모든 스킬이 정상입니다!")
    else:
        print(f"총 {total_issues}개 문제점 발견")
    print("=" * 60)

    return total_issues == 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="hih 스킬 자동 검증")
    parser.add_argument(
        "--skills-dir",
        default=None,
        help="스킬 디렉토리 (기본: ~/.hermes/skills)"
    )
    args = parser.parse_args()

    success = check_skills(args.skills_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
