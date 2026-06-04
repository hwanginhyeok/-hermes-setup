#!/usr/bin/env python3
"""
Skill Review and Audit Template

Usage: python3 skill-review-template.py [--skill-dir ~/.hermes/skills] [--pattern "hih-*"]

Generates a structured report of skill health issues with prioritized action items.
"""

from pathlib import Path
import re
import argparse
from collections import defaultdict

def analyze_skill(skill_path):
    """Analyze a single skill and return issues dict."""
    issues = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': []
    }
    
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        issues['critical'].append("No SKILL.md file")
        return issues
    
    content = skill_md.read_text()
    lines = content.split('\n')
    
    # CRITICAL: Naming consistency
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        fm = frontmatter_match.group(1)
        name_match = re.search(r'name:\s*(\S+)', fm)
        if name_match:
            fm_name = name_match.group(1)
            if fm_name != skill_path.name:
                issues['critical'].append(
                    f"Folder name '{skill_path.name}' != frontmatter name '{fm_name}'"
                )
    else:
        issues['critical'].append("Missing YAML frontmatter")
    
    # CRITICAL: Description length
    desc_match = re.search(r'description:\s*(.+)', content[:2000])
    if desc_match:
        desc = desc_match.group(1).strip('"').strip("'")
        if len(desc) > 1024:
            issues['critical'].append(f"Description too long: {len(desc)} chars (max 1024)")
    
    # HIGH: File size
    if len(lines) > 300:
        issues['high'].append(f"File too long: {len(lines)} lines (consider splitting)")
    
    # HIGH: Hardcoded scripts
    if content.count('```bash') > 5:
        issues['high'].append(
            f"Multiple bash blocks ({content.count('```bash')}) - consider moving to scripts/"
        )
    
    # MEDIUM: Missing metadata
    if 'allowed-tools:' not in content:
        issues['medium'].append("Missing allowed-tools field")
    
    if 'user_invocable:' not in content:
        issues['medium'].append("Missing user_invocable field")
    
    if 'Use when:' not in content and '사용 타이밍:' not in content:
        issues['medium'].append("Missing 'Use when:' trigger")
    
    # LOW: Peer standards
    if 'version:' not in content:
        issues['low'].append("Missing version field")
    
    if 'author:' not in content:
        issues['low'].append("Missing author field")
    
    if '## Common Pitfalls' not in content:
        issues['low'].append("Missing Common Pitfalls section")
    
    return issues

def categorize_skills(skills_dir, pattern="*"):
    """Categorize skills by function."""
    categories = defaultdict(list)
    
    for skill_path in sorted(skills_dir.glob(pattern)):
        if not skill_path.is_dir():
            continue
        if not (skill_path / "SKILL.md").exists():
            continue
        
        content = (skill_path / "SKILL.md").read_text()
        
        # Heuristic categorization
        if any(word in content.lower() for word in ['session', 'task', 'clear', 'vnc']):
            categories['session-management'].append(skill_path.name)
        elif any(word in content.lower() for word in ['dev', 'dual', 'glm', 'reviewer', 'builder']):
            categories['development-workflow'].append(skill_path.name)
        elif any(word in content.lower() for word in ['git', 'commit', 'push']):
            categories['git'].append(skill_path.name)
        elif any(word in content.lower() for word in ['cron', 'schedule', 'automation']):
            categories['automation'].append(skill_path.name)
        elif any(word in content.lower() for word in ['ontology', 'fp', 'thinking', 'framework']):
            categories['thinking-frameworks'].append(skill_path.name)
        else:
            categories['other'].append(skill_path.name)
    
    return categories

def generate_report(skills_dir, pattern="*"):
    """Generate full skill review report."""
    all_issues = defaultdict(lambda: defaultdict(list))
    total_lines = 0
    skill_count = 0
    
    for skill_path in sorted(skills_dir.glob(pattern)):
        if not skill_path.is_dir():
            continue
        
        skill_count += 1
        issues = analyze_skill(skill_path)
        
        # Count lines
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            total_lines += len(skill_md.read_text().split('\n'))
        
        # Group issues by severity
        for severity, items in issues.items():
            if items:
                all_issues[severity][skill_path.name] = items
    
    # Print report
    print("# Skill Review Report\n")
    print(f"**Analyzed:** {skill_count} skills")
    print(f"**Total lines:** {total_lines:,}")
    print(f"**Average:** {total_lines // skill_count if skill_count else 0} lines/skill\n")
    
    print("---\n")
    
    # CRITICAL
    if all_issues['critical']:
        print("## 🚨 CRITICAL Issues (Immediate Action Required)\n")
        for skill, issues_list in all_issues['critical'].items():
            for issue in issues_list:
                print(f"**{skill}**: {issue}")
        print()
    
    # HIGH
    if all_issues['high']:
        print("## ⚠️ HIGH Priority (Maintainability)\n")
        for skill, issues_list in all_issues['high'].items():
            for issue in issues_list:
                print(f"**{skill}**: {issue}")
        print()
    
    # MEDIUM
    if all_issues['medium']:
        print("## ℹ️ MEDIUM (Standardization)\n")
        for skill, issues_list in all_issues['medium'].items():
            for issue in issues_list:
                print(f"**{skill}**: {issue}")
        print()
    
    # LOW
    if all_issues['low']:
        print("## 💡 LOW (Polish)\n")
        for skill, issues_list in all_issues['low'].items():
            for issue in issues_list:
                print(f"**{skill}**: {issue}")
        print()
    
    # Category breakdown
    print("---\n")
    print("## Category Breakdown\n")
    categories = categorize_skills(skills_dir, pattern)
    for cat, skills in categories.items():
        if skills:
            print(f"**{cat}**: {', '.join(skills)}")

def main():
    parser = argparse.ArgumentParser(description="Review and audit Hermes skills")
    parser.add_argument(
        '--skill-dir',
        default='~/.hermes/skills',
        help='Path to skills directory'
    )
    parser.add_argument(
        '--pattern',
        default='*',
        help='Glob pattern to match skills (default: all)'
    )
    
    args = parser.parse_args()
    skills_dir = Path(args.skill_dir).expanduser()
    
    if not skills_dir.exists():
        print(f"❌ Skills directory not found: {skills_dir}")
        return 1
    
    generate_report(skills_dir, args.pattern)
    return 0

if __name__ == '__main__':
    exit(main())
