# Example: Post-Commit Critical Review Report

This example shows the structure and format for post-commit critical reviews used for PM handoff.

## Example Structure

```
# <Project> Code Review Report

**Commit**: <commit_hash>
**Date**: YYYY-MM-DD HH:MM:SS
**Reviewer**: Hermes Agent
**Project**: <Project name>

---

## CRITICAL (배포 차단)

### 1. <Title of critical issue>

**문제**:
- Description of the problem
- Code location (file:line)
- Specific evidence

**위험도**: HIGH/MEDIUM/LOW
- Explanation of why this is critical

**위치**:
- `path/to/file` lines X-Y

---

### 2. <Another critical issue>

...same structure...

---

## INFORMATIONAL (개선 권고)

### 1. <Title of informational issue>

**내용**:
- Description of the improvement area

**권고**:
- Specific recommendation

---

## OK (잘 된 부분)

### 1. <What went well>

- Description of good practice followed
- Location in code
- `path/to/file` line X

---

## 종합 평가

**<One-line summary verdict>**
```

## Real Example: BAS-REFORM-1b Review

From session 2026-05-10 where Be:A Studio content pipeline reform Step 1b was reviewed:

**Task:** newneek AN 전용 확정 — DG에서 제거, _edit_minimal 공용 유지

**Key findings:**
- CRITICAL: 스타일 명명 불일치 지속 - 파일 간 불일치 (_edit_minimal vs the_edit_minimal)
  - format_map.yaml: AN alternates line 7 `_edit_minimal`, DG alternates line 19 `_edit_minimal`, DG quote line 25 `the_edit_minimal`
  - content_planner.py: _AN_STYLES, _DG_STYLES 모두 `the_edit_minimal`
  - 위험도: HIGH - YAML/PY 간 명칭 다름 → runtime 매칭 실패
- CRITICAL: 스타일 명명 불일치 - format_map.yaml 내부 혼재
  - 위험도: MEDIUM-HIGH - 동일 스타일이 다른 이름으로 취급될 가능성
- INFORMATIONAL: 주석과 실제 이름 불일치 확인
- OK: DG에서 newneek 완전 제거 (alternates, slide_types)
- OK: AN에서 newneek 유지
- OK: content_planner.py에서 _DG_STYLES 업데이트

**Format used:**
- CRITICAL sections: 문제, 위험도, 위치
- INFORMATIONAL sections: 내용, 권고
- OK sections: 확인된 구현
- One-line verdict: "newneek 중복 해결 완료했으나, _edit_minimal 명명 불일치가 지속되어 배포 차단 필요."

---

## Real Example: BAS-REFORM-2 Review

From session 2026-05-10 where photo_keyword 영어화 구현 검증 was performed:

**Task:** photo_keyword 영어 구체 명사구 강제 — 추상어 금지

**Key findings:**
- CRITICAL: 한글 자모 범위 오타 위험 — CJK 감지 불완전
  - `_has_cjk(text: str)` function: '㄰' <= c <= '㆏' 범위는 맞으나 주석과 코드 불일치
  - 일본어 히라가나(3040~309F), 가타카나(30A0~30FF) 미포함
  - 위험도: MEDIUM-HIGH - CJK 감지 불완전으로 한국어 키워드 누락 가능
  - 개선 권고: ord() 기반 명확한 범위 체크로 변경
- INFORMATIONAL: 일본어 가나 범위 미포함 — 한글+한자로 충분하지만 명시 필요
- OK: validate_photo_keywords() 로직 구현 (한글 음절, 한글 자모, CJK 범위)
- OK: content_planner 프롬프트 AN/DG 예시 완전 포함
- OK: validate_photo_keywords() 실제 호출 확인 (save_final_json line 544)
- OK: 검증 실패 시 경고만 하고 계속 진행 (블로킹 아님)

**Format used:**
- CRITICAL sections: 문제, 위험도, 개선 권고
- INFORMATIONAL sections: 내용
- OK sections: 확인된 구현
- One-line verdict: "photo_keyword 영어화 구현은 잘 되어 있으나, CJK 감지 로직의 주석/코드 불일치와 가나 범위 미포함으로 인해 CRITICAL 1건 발생으로 배포 차단 권장."

---

## Common Checklist Patterns

When user provides specific checklist items like:

```
체크:
1. validate_photo_keywords() — 한국어 감지 로직이 실제로 CJK 범위 커버하는지
2. content_planner 프롬프트 변경이 AN/DG 예시를 모두 포함하는지
3. copywriter에서 validate가 실제로 호출되는지 (dead code 아닌지)
4. 검증 실패 시 경고만 하고 계속 진행하는지, 아니면 블로킹하는지
```

Each checklist item must be systematically verified:

1. Read the actual code implementation (e.g., `scripts/content_copywriter.py`)
2. Trace the call chain to verify functions are actually called
3. Check the prompt generation logic (e.g., `scripts/content_planner.py`)
4. Verify actual execution paths (not just theoretical)

## Important: Constraint Enforcement

**NEVER read ~/.claude/ or user config files.**

Example constraint from user:
```
[중요] ~/.claude/ 파일 읽지 마라. 저장소 코드만.
```

This means:
- ✅ READ: `/home/window11/be-a-studio/config/design_library/format_map.yaml`
- ✅ READ: `/home/window11/be-a-studio/scripts/content_planner.py`
- ❌ DON'T READ: `~/.claude/config.yaml`
- ❌ DON'T READ: `~/.claude/profiles/pm/config.yaml`

Always verify the repository path structure and only read project files.
