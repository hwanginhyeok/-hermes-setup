---
name: hermes-agent-skill-authoring
description: "Author in-repo SKILL.md: frontmatter, validator, structure."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, authoring, hermes-agent, conventions, skill-md]
    related_skills: [writing-plans, requesting-code-review]
---

# Authoring Hermes-Agent Skills (in-repo)

## Overview

There are two places a SKILL.md can live:

1. **User-local:** `~/.hermes/skills/<maybe-category>/<name>/SKILL.md` — personal, not shared. Created via `skill_manage(action='create')`.
2. **In-repo (this skill is about this case):** `/home/bb/hermes-agent/skills/<category>/<name>/SKILL.md` — committed, shipped with the package. Use `write_file` + `git add`. `skill_manage(action='create')` does NOT target this tree.

## When to Use

- User asks you to add a skill "in this branch / repo / commit"
- You're committing a reusable workflow that should ship with hermes-agent
- You're editing an existing skill under `/home/bb/hermes-agent/skills/` (use `patch` for small edits, `write_file` for rewrites; `skill_manage` still works for patch on in-repo skills, but not for `create`)

## Required Frontmatter

Source of truth: `tools/skill_manager_tool.py::_validate_frontmatter`. Hard requirements:

- Starts with `---` as the first bytes (no leading blank line).
- Closes with `\n---\n` before the body.
- Parses as a YAML mapping.
- `name` field present.
- `description` field present, ≤ **1024 chars** (`MAX_DESCRIPTION_LENGTH`).
- Non-empty body after the closing `---`.

Peer-matched shape used by every skill under `skills/software-development/`:

```yaml
---
name: my-skill-name               # lowercase, hyphens, ≤64 chars (MAX_NAME_LENGTH)
description: Use when <trigger>. <one-line behavior>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, descriptive, tags]
    related_skills: [other-skill, another-skill]
---
```

`version` / `author` / `license` / `metadata` are NOT enforced by the validator, but every peer has them — omit and your skill sticks out.

## Size Limits

- Description: ≤ 1024 chars (enforced).
- Full SKILL.md: ≤ 100,000 chars (enforced as `MAX_SKILL_CONTENT_CHARS`, ~36k tokens).
- Peer skills in `software-development/` sit at **8-14k chars**. Aim for that range. If you're pushing past 20k, split into `references/*.md` and reference them from SKILL.md.

## Peer-Matched Structure

Every in-repo skill follows roughly:

```
# <Title>

## Overview
One or two paragraphs: what and why.

## When to Use
- Bulleted triggers
- "Don't use for:" counter-triggers

## <Topic sections specific to the skill>
- Quick-reference tables are common
- Code blocks with exact commands
- Hermes-specific recipes (tests via scripts/run_tests.sh, ui-tui paths, etc.)

## Common Pitfalls
Numbered list of mistakes and their fixes.

## Verification Checklist
- [ ] Checkbox list of post-action verifications

## One-Shot Recipes (optional)
Named scenarios → concrete command sequences.
```

Not every section is mandatory, but `Overview` + `When to Use` + actionable body + pitfalls are the minimum for the skill to feel like a peer.

## Directory Placement

```
skills/<category>/<skill-name>/SKILL.md
```

Categories currently in repo (confirm with `ls skills/`): `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `leisure`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`.

Pick the closest existing category. Don't invent new top-level categories casually.

## Workflow

1. **Survey peers** in the target category:
   ```
   ls skills/<category>/
   ```
   Read 2-3 peer SKILL.md files to match tone and structure.
2. **Check validator constraints** in `tools/skill_manager_tool.py` if unsure.
3. **Draft** with `write_file` to `skills/<category>/<name>/SKILL.md`.
4. **Validate locally**:
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<category>/<name>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. **Git add + commit** on the active branch.
6. **Note:** the CURRENT session's skill loader is cached — `skill_view` / `skills_list` will not see the new skill until a new session. This is expected, not a bug.

## Cross-Referencing Other Skills

`metadata.hermes.related_skills` unions both trees (`skills/` in-repo and `~/.hermes/skills/`) at load time. You CAN reference a user-local skill from an in-repo skill, but it won't resolve for other users who clone the repo fresh. Prefer referencing only in-repo skills from in-repo skills. If a frequently-referenced skill lives only in `~/.hermes/skills/`, consider promoting it to the repo.

## Editing Existing In-Repo Skills

- **Small fix (typo, added pitfall, tightened trigger):** `skill_manage(action='patch', name=..., old_string=..., new_string=...)` works fine on in-repo skills.
- **Major rewrite:** `write_file` the whole SKILL.md. `skill_manage(action='edit')` also works but requires supplying the full new content.
- **Adding supporting files:** `write_file` to `skills/<category>/<name>/references/<file>.md`, `templates/<file>`, or `scripts/<file>`. `skill_manage(action='write_file')` also works and enforces the references/templates/scripts/assets subdir allowlist.
- **Always commit** the edit — in-repo skills are source, not runtime state.

## Common Pitfalls

1. **Using `skill_manage(action='create')` for an in-repo skill.** It writes to `~/.hermes/skills/`, not the repo tree. Use `write_file` for in-repo creation.

2. **Leading whitespace before `---`.** The validator checks `content.startswith("---")`; any leading blank line or BOM fails validation.

3. **Description too generic.** Peer descriptions start with "Use when ..." and describe the *trigger class*, not the one task. "Use when debugging X" > "Debug X".

4. **Forgetting the author/license/metadata block.** Not validator-enforced, but every peer has it; omitting makes the skill look half-finished.

5. **Writing a skill that duplicates a peer.** Before creating, `ls skills/<category>/` and open 2-3 peers. Prefer extending an existing skill to creating a narrow sibling.

6. **Expecting the current session to see the new skill.** It won't. The skill loader is initialized at session start. Verify in a fresh session or via `skill_view` using the exact path.

7. **Linking to skills that don't exist in-repo.** `related_skills: [some-user-local-skill]` works for you but breaks for other clones. Prefer only in-repo links.

8. **Patch fails on complex YAML frontmatter.** `skill_manage(action='patch')` can fail with "malformed patch" or YAML parsing errors when:
   - Frontmatter contains multi-line strings with quotes (e.g., `description: "Use when \"XYZ\"...`)
   - Old/new_string includes YAML frontmatter sections
   - Frontmatter has special formatting (colons, dashes, brackets) that confuse diff parser
   
   **Workaround:** For edits involving frontmatter or complex YAML, use `skill_manage(action='edit')` or `write_file` to rewrite the full SKILL.md instead of patching. Only use `patch` for body-only changes (text after the closing `---`).

## Skill Review and Audit

When reviewing a collection of skills for quality, consistency, and maintenance issues, use this systematic framework. A **reusable Python template** is available at `references/skill-review-template.py`.

### 1. Automated Health Check

Quick scan using the template:
```bash
python3 ~/.hermes/skills/software-development/hermes-agent-skill-authoring/references/skill-review-template.py --pattern "hih-*"
```

Or inline for targeted checks:

```python
#!/usr/bin/env python3
from pathlib import Path
import re

skills_dir = Path("~/.hermes/skills").expanduser()

# Basic stats
for skill_path in sorted(skills_dir.glob("hih-*")):
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ {skill_path.name}: No SKILL.md")
        continue
    
    content = skill_md.read_text()
    lines = len(content.split('\n'))
    
    # Frontmatter check
    if not content.startswith('---'):
        print(f"⚠️  {skill_path.name}: Missing YAML frontmatter")
    
    # Naming consistency
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        fm = frontmatter_match.group(1)
        if f"name: {skill_path.name}" not in fm:
            print(f"⚠️  {skill_path.name}: Folder name != frontmatter name")
```

### 2. Common Issue Categories

**CRITICAL (Functional Errors)**
- Folder name ≠ frontmatter `name:` field
- Missing YAML frontmatter entirely
- Description > 1024 chars (validator will reject)

**HIGH (Maintainability)**
- File > 300 lines (consider splitting into `references/` or `scripts/`)
- Hardcoded bash scripts in body (move to `scripts/`)
- Duplicate content across multiple skills

**MEDIUM (Standardization)**
- Missing `allowed-tools:` field
- Missing `user_invocable:` field
- No "Use when:" or "사용 타이밍:" trigger
- Inconsistent section structure

**LOW (Polish)**
- Missing `version:` / `author:` / `license:` (not enforced but peer-standard)
- Empty `related_skills:` when related skills exist
- Weak description (doesn't start with trigger class)

### 3. Refactoring Patterns

**Splitting Large Skills (>300 lines)**

```
skill-name/
├── SKILL.md          # Core: overview, when-to-use, pitfalls
├── scripts/
│   └── helper.py     # Complex logic extracted
└── references/
    └── api-notes.md  # Session-specific docs, API quirks
```

Before:
```markdown
## Step 3: Complex Bash Loop

```bash
# 50 lines of bash here
```
```

After:
```markdown
## Step 3: Complex Bash Loop

```bash
scripts/skill-name/setup-env.sh
```

See `scripts/setup-env.sh` for implementation details.
```

**Standardizing Frontmatter**

Minimum viable:
```yaml
---
name: skill-name
description: Use when <trigger>. <one-line>.
user_invocable: true
---
```

Full peer-matched:
```yaml
---
name: skill-name
description: Use when <trigger>. <one-line>.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [short, tags]
    related_skills: [other-skill]
allowed-tools:
  - Bash
  - Read
  - Write
---
```

### 4. Review Prioritization

Use P0/P1/P2/P3 framework for action items:

- **P0 (Immediate)**: CRITICAL issues that break functionality (15-30 min)
- **P1 (Weekly)**: HIGH issues impacting maintainability (1-2 hours)
- **P2 (Monthly)**: MEDIUM standardization gaps (30 min)
- **P3 (Time-permitting)**: LOW polish items (20 min)

### 5. Review Checklist Per Skill

- [ ] Folder name matches `name:` in frontmatter
- [ ] YAML frontmatter present and valid
- [ ] `description` ≤ 1024 chars
- [ ] `allowed-tools` specified (if applicable)
- [ ] "Use when:" or equivalent trigger present
- [ ] File ≤ 300 lines (or split plan exists)
- [ ] No hardcoded scripts in body (moved to `scripts/`)
- [ ] `## Common Pitfalls` section exists
- [ ] `related_skills` references are accurate

## Verification Checklist

- [ ] File is at `skills/<category>/<name>/SKILL.md` (not in `~/.hermes/skills/`)
- [ ] Frontmatter starts at byte 0 with `---`, closes with `\n---\n`
- [ ] `name`, `description`, `version`, `author`, `license`, `metadata.hermes.{tags, related_skills}` all present
- [ ] Name ≤ 64 chars, lowercase + hyphens
- [ ] Description ≤ 1024 chars and starts with "Use when ..."
- [ ] Total file ≤ 100,000 chars (aim for 8-15k, max 300 lines before splitting)
- [ ] Structure: `# Title` → `## Overview` → `## When to Use` → body → `## Common Pitfalls` → `## Verification Checklist`
- [ ] `related_skills` references resolve in-repo (or are explicitly OK to be user-local)
- [ ] `git add skills/<category>/<name>/ && git commit` completed on the intended branch
