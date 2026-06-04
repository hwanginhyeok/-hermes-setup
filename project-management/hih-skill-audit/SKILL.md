---
name: hih-skill-audit
description: |
  hih 스킬 라이브러리 체계적 리뷰 및 품질 관리. 스킬 구조, 네이밍, 메타데이터 표준화,
  중복 감지, 리팩토링 필요성 평가.
  
  Use when: "스킬 리뷰", "스킬 점검", "스킬 정리", "hih 스킬 현황"
user_invocable: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# /hih-skill-audit — hih 스킬 라이브러리 리뷰

hih 스킬들의 품질, 구조, 네이밍, 메타데이터를 체계적으로 리뷰합니다.

## 실행 시 동작

### 1. 스킬 목록 파악

```bash
# 설치된 hih 스킬 목록
ls -la ~/.hermes/skills/ | grep hih

# 스킬별 라인 수 확인
for dir in ~/.hermes/skills/hih-*; do echo "=== $dir ==="; wc -l "$dir/SKILL.md" 2>/dev/null || echo "No SKILL.md"; done

# 심링크 vs 로컬 구분
cd ~/.hermes/skills && for dir in hih-*; do [ -L "$dir" ] && echo "$dir → $(readlink -f $dir)"; done
```

### 2. 메타데이터 검증

```python
#!/usr/bin/env python3
from pathlib import Path
import re

skills_dir = Path("/home/window11/.hermes/skills")
issues = {'naming': [], 'frontmatter': [], 'structure': [], 'missing_meta': []}

for skill_path in sorted(skills_dir.glob("hih-*")):
    if not (skill_path / "SKILL.md").exists():
        issues['structure'].append(f"{skill_path.name}: No SKILL.md")
        continue
    
    content = (skill_path / "SKILL.md").read_text()
    
    # 1. 네이밍 부정합 체크
    name_match = re.search(r'name: ([^\n]+)', content.split('---')[1] if '---' in content[4:] else "")
    if name_match:
        declared_name = name_match.group(1).strip()
        if skill_path.name.replace('-', '-') != declared_name.replace('-', '_'):
            # hih-claude vs codex 같은 케이스 감지
            if 'claude' in skill_path.name.lower() and 'codex' in declared_name.lower():
                issues['naming'].append(f"{skill_path.name}: 폴더명 vs name: 불일치 ({declared_name})")
    
    # 2. frontmatter 체크
    if not content.startswith('---'):
        issues['frontmatter'].append(f"{skill_path.name}: No YAML frontmatter")
    else:
        if "user_invocable:" not in content[:500]:
            issues['missing_meta'].append(f"{skill_path.name}: user_invocable 미명시")
        
        if "allowed-tools:" not in content[:500] and skill_path.name in ['hih-clear', 'hih-git', 'hih-cron']:
            issues['missing_meta'].append(f"{skill_path.name}: allowed-tools 명시 권장")
    
    # 3. Use when 트리거 체크
    if "Use when:" not in content and "사용 타이밍:" not in content:
        if skill_path.name not in ["hih-dev", "hih-claude"]:
            issues['missing_meta'].append(f"{skill_path.name}: Use when/사용 타이밍 미명시")

# 결과 출력
for category, items in issues.items():
    if items:
        print(f"## {category.upper()}")
        for item in items:
            print(f"  ❌ {item}")
```

### 3. 중요도별 분류

```python
#!/usr/bin/env python3
# 중요도별 문제점 분석
critical_issues = []  # 기능 오류 (즉시 조치)
high_issues = []      # 기능 개선 필요
medium_issues = []    # 표준화 권장
low_issues = []       # 개선 제안

# CRITICAL: 네이밍 부정합, frontmatter 부재
# HIGH: 과도한 길이 (>300 lines), 코드 중복
# MEDIUM: 메타데이터 누락
# LOW: 문서 스타일 개선
```

### 4. 카테고리별 그룹핑

```python
categories = {
    '세션 관리': ['hih-task', 'hih-clear', 'hih-all-clear', 'hih-vnc'],
    '개발 워크플로우': ['hih-dev', 'hih-dual', 'hih-glm', 'hih-claude'],
    'Git': ['hih-git'],
    'Cron/자동화': ['hih-cron'],
    '사고 프레임워크': ['hih-fp', 'hih-ontology'],
    '지식 관리': ['hih-difficulty'],
}
```

### 5. 리팩토링 필요성 평가

| 스킬 | 라인 수 | 리팩토링 필요성 | 조치 |
|------|---------|-----------------|------|
| hih-glm | 401 | 🔴 HIGH | scripts/ 분리 |
| hih-dual | 286 | 🔴 HIGH | scripts/ 분리 |
| hih-dev | 238 | 🟡 MEDIUM | frontmatter 추가 |
| hih-cron | 213 | 🟢 OK | - |
| hih-all-clear | 185 | 🟢 OK | - |

## 리포트 형식

```
## hih 스킬 리뷰 - 중요도별 문제점

### 🚨 CRITICAL (기능 오류 - 즉시 조치 필요)
1. **{skill}**: {issue}
   - 문제: {detail}
   - 영향: {impact}
   - 해결: {fix}

### ⚠️ HIGH (기능 개선 필요)
...

### ℹ️ MEDIUM (표준화 권장)
...

### 💡 LOW (개선 제안)
...
```

## 액션 아이템 관리

우선순위: P0 (즉시) > P1 (주간) > P2 (월간) > P3 (타임퍼밋)

```python
actions = [
    {
        'priority': 'P0',
        'action': 'hih-claude 네이밍 수정',
        'estimate': '10분',
        'steps': ['1. mv ...', '2. ...'],
        'blocking': '아니오'
    },
    # ...
]
```

## Pitfalls

1. **네이밍 부정합**: 폴더명과 SKILL.md의 `name:`이 다르면 사용자 혼동 유발
   - 사례: hih-claude 폴더인데 내용은 Codex용
   - 해결: 폴더명 변경 또는 내용 재작성

2. **frontmatter 누락**: hih-dev처럼 YAML이 없으면 메타데이터를 읽을 수 없음
   - 해결: 최상단에 `---`로 감싼 YAML 추가

3. **과도한 길이**: 300+ lines이면 유지보수 어려움
   - 해결: scripts/ 또는 references/로 코드 분리

4. **allowed-tools 미명시**: Bash 등 필수 툴이 없으면 에이전트가 권한을 모름
   - 해결: `allowed-tools: [Bash, Read, Write, Edit]` 추가

5. **Use when 누락**: 트리거가 없으면 스킬 라우팅 어려움
   - 해결: `Use when: "키워드1", "키워드2"` 추가

6. **스킬 호출 모니터링 누락**: 스킬 호출이 agent.log나 gateway.log에 명시적으로 기록되지 않음
   - 현재 상황: 로그 파일이 있지만 스킬 이름/타임스탬프가 기록되지 않음
   - 영향: 실시간 스킬 사용 추적 불가, 스킬 사용 빈도 분석 불가
   - 임시 해결: `tail -f ~/.hermes/logs/agent.log | grep -i 'skill'` (현재는 기록 없어 빈 결과)
   - 영구 해결: 스킬 호출 시 로그에 "SKILL_CALLED: {skill_name} {timestamp}" 기록하는 헬스훅 추가

## 스킬 관리 자동화

### Cron 기반 스킬 상태 모니터링 (2026-06-02)

사용자 요청: "스킬들 호출되는거 모니터링이 되고 있나?" → 현재 불가 확인 → 자동화 구현

**자동화 기능**:
- 매일 08:00 스킬 현황 확인
- 전역 스킬 + 프로젝트별 스킬 현황 보고서 생성
- 최근 7일 내 변경 스킬 추적
- Git 자동 커밋 + 푸쉬
- 노트북 동기화 상태 확인

**스크립트**: `scripts/manage_skills.sh`

**Cron 설정**:
```bash
# 스킬 관리 (매일 08:00)
0 8 * * * /home/window11/scripts/manage_skills.sh >> /home/window11/.pm_logs/manage_skills.log 2>&1
```

**보고서 위치**: `docs/reports/skills/skills_status_YYYY-MM-DD.md`

**노트북 사용 방법**:
1. GitHub에서 project-manager 클론
2. 보고서 확인 (`docs/reports/skills/`)
3. 필요 시 스킬 추가/수정
4. 자동으로 매일 08:00 동기화

## 검증 사례

- 2026-06-02: 모델 업데이트 + 스킬 작동 유무 검증 완료
  - 업데이트된 모델: GLM 5.0, Opus 4.8, Codex 5.5
  - 업데이트된 스킬: hih-dual, hih-design-fix, hih-design-new
  - config.yaml 업데이트: custom_providers에 codex, opus 추가
  - 검증 방법: Python으로 스킬 경로, 파일 존재, 모델 버전 자동 확인
  - 발견된 패턴:
    - 스킬은 여러 경로에 분산 가능 (직접 경로, 카테고리 하위 경로)
    - find 명령 + pathlib로 실제 경로 찾는 패턴
    - config.yaml 검증 시 전역과 profile 모두 확인 필요
  - 자동화: scripts/verify_skills.py로 검증 자동화
  - Git 동기화: https://github.com/hwanginhyeok/-hermes-setup
  - 노트북 사용: ~/sync_skills_from_repo.sh 스크립트 제공

- 2026-05-25: hih 스킬 13개 리뷰 완료
  - 발견: CRITICAL 2건, HIGH 2건, MEDIUM 3건
  - 조치: hih-claude 스킬 재작성 (Claude Code용)
  - hih-claude: 243 lines, YAML frontmatter 포함, allowed-tools 명시
  - 신규: hih-debate 스킬 생성 (다중 AI 토론 시스템)
    - 372 lines SKILL.md + 298 lines Python orchestrator + 117 lines topics
    - 3라운드 구조: 입장 제시 → 비판 → 재반박 → 시너지sis
    - 테스트 완료: "인공지능이 의식을 가질 수 있는가?" 주제로 시뮬레이션 성공

## Use when

- "스킬 리뷰", "스킬 점검", "스킬 정리", "hih 스킬 현황"
- "스킬 품질 관리", "스킬 리팩토링"
- 스킬 라이브러리 체계적 개선 필요 시
## 관련 파일

- **references/hih-skills-structure.md**: 스킬 구조 표준
- **references/hih-skills-audit-2026-05-25.md**: 2026-05-25 리뷰 상세 기록
  - 발견된 문제점 (CRITICAL 2건, HIGH 2건, MEDIUM 3건)
  - hih-debate 신규 스킬 생성 기록
  - 리뷰 방법론과 교훈
- **references/hih-claude-rewrite-2026-05-25.md**: hih-claude 스킬 재작성 기록
- **references/model-update-patterns.md**: 모델 업데이트 패턴 (2026-06-02 추가)
  - 스킬 파일 업데이트 방법
  - config.yaml 업데이트 패턴
  - 검증 패턴 (경로 찾기, 모델 버전 확인)
  - 관련 사례 (GLM 5.0, Opus 4.8, Codex 5.5 업데이트)
- **references/skill-sync-pattern.md**: 스킬 동기화 패턴 (2026-06-04 추가)
  - Git 기반 크로스 디바이스 동기화 (desktop ↔ notebook)
  - GitHub 레포: https://github.com/hwanginhyeok/-hermes-setup
  - 싱크 스크립트: ~/sync_skills_from_repo.sh
  - 사례: 2026-06-04 모델 업데이트 후 동기화 완료

- **scripts/manage_skills.sh**: 스킬 관리 자동화 스크립트 (2026-06-02 추가)
  - 기능: 스킬 현황 확인 + 보고서 생성 + Git 동기화 + 노트북 동기화
  - 실행: 매일 08:00 cron 자동 실행
  - 보고서: `docs/reports/skills/skills_status_YYYY-MM-DD.md`

- **scripts/hih_skill_check.py**: 자동 검증 스크립트
  ```bash
  # 실행 방법
  python3 ~/.hermes/skills/project-management/hih-skill-audit/scripts/hih_skill_check.py

  # 또는
  cd ~/.hermes/skills && python3 project-management/hih-skill-audit/scripts/hih_skill_check.py
  ```

  기능:
  - 네이밍 부정합 검출
  - frontmatter 누락 검출
  - 메타데이터 검증
  - 길이 체크 (>300 lines 경고)
  - 중요도별 분류 (CRITICAL > HIGH > MEDIUM > LOW)

- **scripts/verify_skills.py**: 스킬 작동 유무 + 모델 버전 검증 (2026-06-02 추가)
  ```bash
  # 사용법
  python3 ~/.hermes/skills/project-management/hih-skill-audit/scripts/verify_skills.py hih
  python3 ~/.hermes/skills/project-management/hih-skill-audit/scripts/verify_skills.py gstack

  # 또는
  cd ~/.hermes/skills/project-management/hih-skill-audit/scripts
  python3 verify_skills.py hih
  ```

  기능:
  - 스킬 파일 존재 여부 확인 (여러 경로 패턴 검색)
  - 파일 크기 확인
  - 모델 버전 추출 (Opus 4.8, GLM 5.0, 5.5 등)
  - 요약 보고서 생성
