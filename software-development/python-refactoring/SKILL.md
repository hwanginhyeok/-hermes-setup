---
name: python-refactoring
description: "Python code refactoring and technical debt reduction — extract templates, consolidate duplicates, remove dead code, improve exception handling. For monolith reduction and codebase cleanup."
---

# Python Refactoring Skill

Systematic approaches to reducing technical debt in Python codebases. Focus on **safe, incremental refactoring** with verification at each step.

## Core Patterns

### 1. Inline Template Extraction

**When**: Large HTML/CSS/SQL strings embedded in Python files (500+ lines)

**Pattern**:
```
1. Identify inline templates (AN_TEMPLATE = """...""")
2. Extract to external files in design_library/templates/
3. Create loader function: load_legacy_template(category)
4. Replace direct assignment with function call
5. Verify: python3 -m py_compile + functional test
```

**Benefits**:
- Reduces monolith size (2,591→2,323 lines = 10% reduction)
- Separates concerns (code vs templates)
- Enables template versioning/review

**Example**: `card_engine.py` BAS-103
- Before: 142-line AN_TEMPLATE + 145-line DG_TEMPLATE inline
- After: `legacy_an/cover.html` + `legacy_dg/cover.html` + `load_legacy_template()`

**Pitfalls**:
- **Missing variable expansion**: Ensure Jinja2 variables (`{{photo_path}}`) are preserved
- **Path resolution**: Use `Path(__file__).parent` for relative template paths
- **Encoding**: Always specify `encoding='utf-8'` when reading templates

### 2. Duplicate Code Consolidation

**When**: Multiple scripts with identical logic (Playwright rendering, file I/O, API calls)

**Pattern**:
```
1. Find duplicate code: grep -h "def render" render_*.py | sort | uniq -c
2. Extract common logic to shared module (render_utils.py)
3. Create reusable functions with parameters
4. Replace call sites one by one
5. Keep original scripts as legacy/ until verification complete
```

**Benefits**:
- Single source of truth for bug fixes
- Easier testing (mock one module)
- Consistent error handling

**Example**: `render_utils.py` BAS-106
- Before: 4 scripts (mono_red/longblack/newneek/the_edit) each with identical Playwright boilerplate
- After: `render_html_files()`, `render_style_batch()`, `print_summary()` shared
- Created: `render_single_style.py` as unified entry point

**Pitfalls**:
- **Over-abstraction**: Don't consolidate code that looks similar but has subtle differences
- **Breaking changes**: Keep old APIs during transition period
- **Testing smoke**: Each consolidation needs functional verification

### 3. Legacy Code Removal

**When**: Dead code after migration (Notion→GDrive, v1→v2)

**Pattern**:
```
1. Confirm no active dependencies:
   grep -r "module_name" --include="*.py" --include="*.sh" scripts/ docs/
2. Move to legacy/ instead of immediate delete
3. Run full test suite (or smoke tests)
4. Remove from git tracking: git rm
5. Update documentation references
6. Delete legacy/ directory
```

**Benefits**:
- Reduces cognitive load (what's active vs what's dead)
- Smaller codebase = faster searches/reads
- Prevents accidental use of deprecated code

**Example**: `scripts/legacy/` BAS-108
- Deleted: notion_uploader.py (1,442 lines) + notion_polling.py (398 lines) + render_*.py (4 files)
- Verification: No imports/references in active codebase
- Total: 2,053 lines removed

**Pitfalls**:
- **Hidden dependencies**: Cron jobs, external scripts, documentation examples
- **Config files**: Check systemd services, Makefiles, shell scripts
- **Documentation**: Old examples in docs/specs/ that users might copy

### 4. Exception Handling Refactoring

**When**: Broad `except Exception` that catches everything (23+ instances)

**Pattern**:
```
1. Audit: grep -n "except Exception" file.py | wc -l
2. For each try-except, identify likely exceptions:
   - File I/O → OSError, FileNotFoundError, json.JSONDecodeError
   - External API → requests.RequestException, TimeoutError
   - Color math → ValueError, AttributeError
3. Replace with specific exceptions:
   try:
       json.load(f)
   except (json.JSONDecodeError, OSError) as e:
       # Handle specific error
4. Keep generic Exception only at top-level handlers
```

**Benefits**:
- Better error messages (specific vs "something went wrong")
- Easier debugging (stack traces point to real issue)
- Prevents silent failures (KeyError swallowed by broad catch)

**Example**: card_reviewer.py BAS-107 (23 instances)
- `json.load()` → `except (json.JSONDecodeError, OSError)`
- `colormath` ops → `except (ValueError, AttributeError, KeyError)`
- Keep broad exceptions only at request boundaries

**Pitfalls**:
- **Time intensive**: Each context requires analysis (23 instances = 1-2 hours)
- **Risk of over-narrowing**: Missing legitimate edge cases
- **Test coverage**: Need error injection tests for each exception path

## Verification Checklist

After each refactoring:

- [ ] Syntax check: `python3 -m py_compile module.py`
- [ ] Import test: `python3 -c "from module import function"`
- [ ] **Clear .pyc cache**: `find . -name "*.pyc" -delete && find . -name "__pycache__" -type d -exec rm -rf {} +` — stale cache can serve pre-refactoring code, especially when the change fixes a bug that existed in the cached version
- [ ] Smoke test: Run affected scripts with sample data
- [ ] Documentation update: Update docs/specs/ references
- [ ] Git commit: Atomic commits per refactoring (not mixed changes)

## Task-Driven Refactoring

**Approach**: Work through tasks by priority (P0 → P1 → P2)

**Example Sequence** (BAS-103~108):
1. **P0** (Critical): Inline template extraction → immediate size reduction
2. **P1** (High): Duplicate consolidation → maintainability improvement
3. **P1** (High): v1 removal after v2 verified → eliminate confusion
4. **P2** (Medium): Legacy cleanup → final cleanup pass
5. **P2** (Low): Exception handling → quality improvement (separate session)

**Benefits**:
- Early wins (P0/P1) demonstrate value
- Reduces risk (don't change everything at once)
- Easier to roll back if issues found

## Common Anti-Patterns

**Don't**:
- Delete code without verifying dependencies (use grep/git grep first)
- Consolidate code that's only coincidentally similar
- Refactor working critical systems without tests
- Mix refactoring with feature changes (atomic commits)
- Over-abstract into "god modules" that do everything

**Do**:
- Keep legacy/ during transition period
- Test each change independently
- Update documentation as you go
- Use descriptive function names (render_html_files not process)
- Add docstrings explaining the "why" not just the "what"

## References

- `references/be-a-studio-refactoring-2026-05.md` — Complete session transcript with before/after code examples
- `references/exception-handling-patterns.md` — Common exception types by context (JSON, HTTP, file I/O, etc.)
- `scripts/refactoring_smoke_test.py` — Verification script to run after refactoring
