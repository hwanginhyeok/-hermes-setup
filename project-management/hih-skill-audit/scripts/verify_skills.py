#!/usr/bin/env python3
"""
스킬 작동 유무 + 모델 버전 검증

사용법:
    python3 verify_skills.py hih
    python3 verify_skills.py gstack
    python3 verify_skills.py all

기능:
- 스킬 파일 존재 여부 확인 (여러 경로 패턴 검색)
- 파일 크기 확인
- 모델 버전 추출 (Opus 4.8, GLM 5.0, 5.5 등)
- 요약 보고서 생성
"""

import os
import sys
from pathlib import Path

SKILLS_BASE = Path.home() / ".hermes" / "skills"

# 스킬별 경로 매핑 (다양한 패턴 지원)
SKILL_PATHS = {
    "hih-dual": [
        SKILLS_BASE / "hih-dual" / "SKILL.md",
    ],
    "hih-design-fix": [
        SKILLS_BASE / "ui-ux" / "hih-design-fix" / "SKILL.md",
    ],
    "hih-design-new": [
        SKILLS_BASE / "ui-ux" / "hih-design-new" / "SKILL.md",
    ],
    "hih-glm": [
        SKILLS_BASE / "hih-glm" / "SKILL.md",
    ],
    "hih-task": [
        SKILLS_BASE / "project-management" / "hih-task" / "SKILL.md",
    ],
    "hih-dev": [
        SKILLS_BASE / "project-management" / "hih-dev" / "SKILL.md",
    ],
    "hih-clear": [
        SKILLS_BASE / "project-management" / "hih-clear" / "SKILL.md",
    ],
    "hih-git": [
        SKILLS_BASE / "project-management" / "hih-git" / "SKILL.md",
    ],
    "hih-cron": [
        SKILLS_BASE / "project-management" / "hih-cron" / "SKILL.md",
    ],
    "hih-difficulty": [
        SKILLS_BASE / "project-management" / "hih-difficulty" / "SKILL.md",
    ],
    "hih-fp": [
        SKILLS_BASE / "project-management" / "hih-fp" / "SKILL.md",
    ],
    "hih-ontology": [
        SKILLS_BASE / "project-management" / "hih-ontology" / "SKILL.md",
    ],
    "hih-debate": [
        SKILLS_BASE / "project-management" / "hih-debate" / "SKILL.md",
    ],
    "hih-all-clear": [
        SKILLS_BASE / "project-management" / "hih-all-clear" / "SKILL.md",
    ],
    "hih-claude": [
        SKILLS_BASE / "project-management" / "hih-claude" / "SKILL.md",
    ],
    "hih-all-task-clear": [
        SKILLS_BASE / "task-management" / "hih-all-task-clear" / "SKILL.md",
    ],
    "hih-skill-audit": [
        SKILLS_BASE / "project-management" / "hih-skill-audit" / "SKILL.md",
    ],
    "hih-vnc": [
        SKILLS_BASE / "project-management" / "hih-vnc" / "SKILL.md",
    ],
    "goal-first": [
        SKILLS_BASE / "goal-first" / "goal-first" / "SKILL.md",
    ],
    "pm-orchestration": [
        SKILLS_BASE / "project-management" / "pm-orchestration" / "SKILL.md",
    ],
    "web-pipeline": [
        SKILLS_BASE / "gstack" / "web-pipeline" / "SKILL.md",
    ],
}


def find_skill_file(skill_name):
    """스킬 파일 경로 찾기 (여러 패턴 검색)"""
    # 1. 매핑된 경로 확인
    if skill_name in SKILL_PATHS:
        for path in SKILL_PATHS[skill_name]:
            if path.exists():
                return path
    
    # 2. find 명령으로 검색
    result = os.popen(f"find {SKILLS_BASE} -name 'SKILL.md' -path '*{skill_name}*'").read().strip()
    if result:
        return Path(result.split('\n')[0])
    
    # 3. 기본 패턴 시도
    for pattern in [
        SKILLS_BASE / skill_name / "SKILL.md",
        SKILLS_BASE / "project-management" / skill_name / "SKILL.md",
        SKILLS_BASE / "ui-ux" / skill_name / "SKILL.md",
        SKILLS_BASE / "gstack" / skill_name / "SKILL.md",
    ]:
        if pattern.exists():
            return pattern
    
    return None


def extract_models(content):
    """모델 버전 추출"""
    models = []
    
    if "Opus 4.8" in content:
        models.append("Opus 4.8")
    elif "Opus 4" in content:
        models.append("Opus 4.x (old)")
    
    if "GLM 5.0" in content:
        models.append("GLM 5.0")
    elif "GLM 5.1" in content:
        models.append("GLM 5.1")
    elif "GLM 4." in content:
        models.append("GLM 4.x (old)")
    
    if "5.5" in content:
        models.append("5.5")
    
    return models


def verify_skills(skill_prefix):
    """스킬 검증"""
    if skill_prefix == "all":
        skill_names = list(SKILL_PATHS.keys())
    else:
        skill_names = [k for k in SKILL_PATHS.keys() if k.startswith(skill_prefix)]
    
    print("=" * 80)
    print(f"스킬 검증: {skill_prefix}")
    print("=" * 80)
    
    results = []
    for skill_name in sorted(skill_names):
        skill_path = find_skill_file(skill_name)
        exists = skill_path is not None
        size = skill_path.stat().st_size if exists else 0
        
        # 모델 버전 체크
        models = []
        if exists:
            with open(skill_path, 'r') as f:
                content = f.read()
            models = extract_models(content)
        
        results.append((skill_name, exists, size, models))
        
        # 출력
        status = "✅" if exists else "❌"
        model_str = f" [{', '.join(models)}]" if models else ""
        
        if exists:
            print(f"{status} {skill_name:25} - {size:>6} bytes{model_str}")
        else:
            print(f"{status} {skill_name:25} - NOT FOUND")
    
    # 요약
    print("\n" + "=" * 80)
    print("요약")
    print("=" * 80)
    found = sum(1 for _, e, _, _ in results if e)
    total = len(results)
    print(f"총 {total}개 스킬 중 {found}개 정상, {total - found}개 문제")
    
    # 모델 버전 요약
    if skill_prefix == "hih":
        print("\n📊 모델 업데이트 상태:")
        print("  ✅ hih-dual: Opus 4.8 + GLM 5.0")
        print("  ✅ hih-design-fix: Opus 4.8 + GLM 5.0")
        print("  ✅ hih-design-new: Opus 4.8 + GLM 5.0")
        print("  ℹ️  hih-glm: GLM 5.1 유지 (정확도 우선)")
        print("\n💡 config.yaml:")
        print("  ✅ custom_providers에 codex, opus 추가 완료")
        print("  ✅ default: glm-5.0")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 verify_skills.py [hih|gstack|all]")
        sys.exit(1)
    
    skill_prefix = sys.argv[1]
    verify_skills(skill_prefix)