#!/usr/bin/env python3
"""
hih 스킬 라이브러리 체계적 리뷰 스크립트

사용법:
    python3 scripts/hih_skill_audit.py

출력:
    - 중요도별 문제점 리포트
    - 카테고리별 현황
    - 액션 아이템
"""

from pathlib import Path
import re
from typing import Dict, List

def audit_hih_skills() -> Dict:
    """hih 스킬들 체계적 리뷰"""
    skills_dir = Path("/home/window11/.hermes/skills")
    
    issues = {
        'critical': [],   # 기능 오류 (즉시 조치)
        'high': [],       # 기능 개선 필요
        'medium': [],     # 표준화 권장
        'low': []         # 개선 제안
    }
    
    skills_summary = []
    
    for skill_path in sorted(skills_dir.glob("hih-*")):
        if not (skill_path / "SKILL.md").exists():
            issues['critical'].append({
                'skill': skill_path.name,
                'issue': 'No SKILL.md',
                'impact': '스킬을 로드할 수 없음',
                'fix': 'SKILL.md 생성'
            })
            continue
        
        content = (skill_path / "SKILL.md").read_text()
        lines = len(content.split('\n'))
        is_symlink = skill_path.is_symlink()
        
        # 스킬 요약
        skills_summary.append({
            'name': skill_path.name,
            'lines': lines,
            'is_symlink': is_symlink
        })
        
        # 1. CRITICAL: 네이밍 부정합
        name_match = re.search(r'name: ([^\n]+)', content[content.find('---')+3:content.find('---', 4)] if '---' in content[4:] else "")
        if name_match:
            declared_name = name_match.group(1).strip()
            # hih-claude vs codex 같은 케이스
            if 'claude' in skill_path.name.lower() and 'codex' in declared_name.lower():
                issues['critical'].append({
                    'skill': skill_path.name,
                    'issue': '네이밍 부정합',
                    'detail': f'폴더명은 {skill_path.name}인데 name: {declared_name}',
                    'impact': '사용자 혼동 유발, 검색 불가',
                    'fix': '폴더명 변경 또는 내용 재작성'
                })
        
        # 2. CRITICAL: frontmatter 부재
        if not content.startswith('---'):
            issues['critical'].append({
                'skill': skill_path.name,
                'issue': 'Frontmatter 부재',
                'detail': 'YAML frontmatter가 없음',
                'impact': '메타데이터를 읽을 수 없음',
                'fix': '최상단에 YAML frontmatter 추가'
            })
        
        # 3. HIGH: 과도한 길이
        if lines > 300:
            issues['high'].append({
                'skill': skill_path.name,
                'issue': f'과도한 길이 ({lines} lines)',
                'detail': '유지보수 어려움, 코드 중복',
                'impact': '수정 시 side effect risk',
                'fix': 'scripts/ 또는 references/로 분리 권장'
            })
        
        # 4. MEDIUM: allowed-tools 미명시
        if "allowed-tools:" not in content[:500]:
            if skill_path.name in ['hih-clear', 'hih-git', 'hih-cron']:
                issues['medium'].append({
                    'skill': skill_path.name,
                    'issue': 'allowed-tools 미명시',
                    'detail': 'Bash 등 필수 툴이 명시되지 않음',
                    'fix': "allowed-tools: [Bash, Read, Write, Edit] 추가"
                })
        
        # 5. LOW: Use when 누락
        if "Use when:" not in content and "사용 타이밍:" not in content:
            if skill_path.name not in ["hih-dev"]:
                issues['low'].append({
                    'skill': skill_path.name,
                    'issue': 'Use when 트리거 미명시',
                    'detail': '스킬 라우팅 시 참조 어려움',
                    'fix': '"Use when:" 또는 "사용 타이밍:" 추가'
                })
    
    return {
        'issues': issues,
        'summary': skills_summary
    }


def print_report(audit_result: Dict):
    """리포트 출력"""
    issues = audit_result['issues']
    summary = audit_result['summary']
    
    print("# hih 스킬 리뷰 - 중요도별 문제점\n")
    
    # CRITICAL
    if issues['critical']:
        print("## 🚨 CRITICAL (기능 오류 - 즉시 조치 필요)\n")
        for i, issue in enumerate(issues['critical'], 1):
            print(f"{i}. **{issue['skill']}**: {issue['issue']}")
            print(f"   - 문제: {issue.get('detail', issue.get('issue', ''))}")
            print(f"   - 영향: {issue['impact']}")
            print(f"   - 해결: {issue['fix']}")
            print()
    
    # HIGH
    if issues['high']:
        print("## ⚠️  HIGH (기능 개선 필요)\n")
        for i, issue in enumerate(issues['high'], 1):
            print(f"{i}. **{issue['skill']}**: {issue['issue']}")
            print(f"   - 문제: {issue['detail']}")
            print(f"   - 영향: {issue['impact']}")
            print(f"   - 해결: {issue['fix']}")
            print()
    
    # MEDIUM (상위 5개만)
    if issues['medium']:
        print("## ℹ️  MEDIUM (표준화 권장)\n")
        for i, issue in enumerate(issues['medium'][:5], 1):
            print(f"{i}. **{issue['skill']}**: {issue['issue']}")
            print(f"   - 문제: {issue['detail']}")
            print(f"   - 해결: {issue['fix']}")
            print()
        if len(issues['medium']) > 5:
            print(f"   ... 외 {len(issues['medium']) - 5}건\n")
    
    # LOW (상위 3개만)
    if issues['low']:
        print("## 💡 LOW (개선 제안)\n")
        for i, issue in enumerate(issues['low'][:3], 1):
            print(f"{i}. **{issue['skill']}**: {issue['issue']}")
            print(f"   - 문제: {issue['detail']}")
            print(f"   - 해결: {issue['fix']}")
            print()
        if len(issues['low']) > 3:
            print(f"   ... 외 {len(issues['low']) - 3}건\n")
    
    # 통계
    print("---\n")
    total_issues = sum(len(v) for v in issues.values())
    print(f"총 문제점: {total_issues}건")
    print(f"  - CRITICAL: {len(issues['critical'])}건")
    print(f"  - HIGH: {len(issues['high'])}건")
    print(f"  - MEDIUM: {len(issues['medium'])}건")
    print(f"  - LOW: {len(issues['low'])}건")
    
    # 스킬 요약
    print("\n## 스킬 요약\n")
    local_skills = [s for s in summary if not s['is_symlink']]
    symlink_skills = [s for s in summary if s['is_symlink']]
    
    print(f"로컬 스킬: {len(local_skills)}개")
    for skill in local_skills:
        print(f"  📁 {skill['name']}: {skill['lines']} lines")
    
    print(f"\n심링크 스킬: {len(symlink_skills)}개")
    for skill in symlink_skills:
        print(f"  🔗 {skill['name']}: {skill['lines']} lines")


if __name__ == "__main__":
    result = audit_hih_skills()
    print_report(result)
