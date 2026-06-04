# Be:A Studio Refactoring Session (2026-05-13)

**Project:** be-a-studio (card news automation)
**Session Focus:** Phase 1.18 Code Quality Cleanup (BAS-103~108)
**Approach:** Priority-driven (P0 → P1 → P2)
**Result:** 4 tasks completed, 2,652 lines net reduction

## Tasks Completed

### BAS-103 (P0): Inline Template Extraction
**Problem:** `card_engine.py` had 2,591 lines with 142-line AN_TEMPLATE + 145-line DG_TEMPLATE inline
**Solution:** 
- Extracted templates to `config/design_library/templates/legacy_an/cover.html` and `legacy_dg/cover.html`
- Created `load_legacy_template(category)` function
- Changed `template_str = AN_TEMPLATE` to `template_str = load_legacy_template(category)`

**Code Change:**
```python
# Before (37-326 lines):
AN_TEMPLATE = """<!DOCTYPE html>
...
</html>"""

DG_TEMPLATE = """<!DOCTYPE html>
...
</html>"""

# Later in code:
if category in ("an",):
    template_str = AN_TEMPLATE  # ❌ 142-line inline string

# After (37-60 lines):
def load_legacy_template(category: str) -> str:
    template_map = {
        "an": "config/design_library/templates/legacy_an/cover.html",
        "dg": "config/design_library/templates/legacy_dg/cover.html",
    }
    template_path = Path(__file__).parent.parent / template_map[category]
    return template_path.read_text(encoding='utf-8')

# Later in code:
if category in ("an",):
    template_str = load_legacy_template(category)  # ✅ Clean function call
```

**Result:** 2,591 → 2,323 lines (268-line reduction, 10% shrinkage)

**Pitfalls Encountered:**
- ✅ **Resolved**: Jinja2 variables (`{{photo_path}}`) preserved correctly
- ✅ **Resolved**: Path resolution used `Path(__file__).parent.parent` for correct relative paths

### BAS-105 (P1): run_pipeline v1 Removal
**Problem:** v1 (538 lines) and v2 (559 lines) coexisted, causing confusion
**Solution:**
- Confirmed v2 is actively used (cron, imports, docs)
- Moved v1 to `scripts/legacy/run_pipeline.py.v1`
- Renamed v2 to `scripts/run_pipeline.py`

**Verification:**
```bash
grep -r "run_pipeline\.py" --include="*.py" scripts/ | grep -v "legacy"
# Only v2 usage found

grep -r "run_pipeline\.py" --include="*.sh" .
# No shell script usage (cron uses v2)
```

**Result:** v1 removed from active codebase (later deleted in BAS-108)

### BAS-106 (P1): Render Script Consolidation
**Problem:** 4 scripts (mono_red/longblack/newneek/the_edit) had identical Playwright boilerplate
**Solution:**
- Created `scripts/render_utils.py` with shared functions:
  - `render_html_files()` — Playwright screenshot loop
  - `render_style_batch()` — Single style batch rendering
  - `print_summary()` — Output formatting
- Created `scripts/render_single_style.py` as unified entry point
- Updated `scripts/render_batch.py` to use `render_utils.py`
- Moved 4 legacy scripts to `scripts/legacy/`

**Code Change:**
```python
# Before (4 files, ~35 lines each):
def render():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slides = sorted(TEMPLATE_DIR.glob("slide*.html"))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        for html_file in slides:
            num = html_file.stem.replace("slide", "")
            out_path = OUTPUT_DIR / f"slide{num}.png"
            page.goto(f"file://{html_file}")
            page.wait_for_timeout(500)
            page.screenshot(path=str(out_path), full_page=False)
        browser.close()

# After (shared in render_utils.py):
def render_html_files(browser, html_files, output_dir, file_pattern="slide", viewport=None, wait_ms=500):
    """Reusable rendering function"""
    output_dir.mkdir(parents=True, exist_ok=True)
    page = browser.new_page(viewport=viewport or {"width": 1080, "height": 1080})
    success = failed = 0
    for html_file in sorted(html_files):
        num = html_file.stem.replace(file_pattern, "")
        out_path = output_dir / f"{file_pattern}{num}.png"
        try:
            page.goto(f"file://{html_file.absolute()}")
            page.wait_for_timeout(wait_ms)
            page.screenshot(path=str(out_path), full_page=False)
            success += 1
        except Exception as e:
            print(f"  ✗ {out_path.name}: {e}")
            failed += 1
    page.close()
    return success, failed
```

**Result:** Eliminated 140+ lines of duplicate code across 4 files

**Pitfalls Encountered:**
- ✅ **Resolved**: File naming patterns differed (slide vs longblack_slide) → added `file_pattern` parameter
- ✅ **Resolved**: Viewport variations → parameterized with default

### BAS-108 (P2): Legacy Directory Cleanup
**Problem:** `scripts/legacy/` contained 2,053 lines of dead code
**Solution:**
- Verified no dependencies: `grep -r "notion_uploader|notion_polling" --include="*.py" scripts/ | grep -v legacy`
- Deleted entire directory: `rm -rf scripts/legacy/`
- Updated TASK.md to reflect cleanup

**Files Deleted:**
- notion_uploader.py (1,442 lines) — Notion→GDrive migration complete
- notion_polling.py (398 lines) — No longer needed
- render_mono_red.py (35 lines) — Replaced by render_single_style.py
- render_longblack.py (35 lines)
- render_newneek.py (66 lines)
- render_the_edit.py (77 lines)
- run_pipeline.py.v1 (538 lines)

**Result:** 2,053 lines removed, legacy/ directory deleted

## Data Structure Bug Discovery (BAS-102 Recurrence)

**Problem:** 05-13 05:30 cron failed with `name 'category' is not defined` in all 5 planning attempts

**Root Cause Analysis:**
1. **Assumption:** FINISHED_TASK.md said "488/494행 category 미정의 → 438행 try 직전에 card_data.get('category','') 추가"
2. **Reality:** Code was correct (437行 had `category = card_data.get("category", "")`)
3. **Real Issue:** Candidates JSON uses `brand` field, NOT `category` field

**Data Structure Mismatch:**
```json
// Actual candidates JSON structure:
{
  "brand": "an",              // ✅ EXISTS
  "category_kr": "스타트업_경제교양",  // ✅ EXISTS (display name)
  // "category": "an"        // ❌ DOES NOT EXIST
}
```

**Fix Applied:**
```python
# Before:
category = card_data.get("category", "")  # Returns "" (empty string)

# After:
brand = card_data.get("brand", "").lower()  # Returns "an" or "dg"
category = brand  # Alias for downstream compatibility
```

**Prevention:** Added `references/be-a-studio-data-structures.md` to blog-automation skill

## Verification Commands Used

### Syntax Check
```bash
python3 -m py_compile scripts/card_engine.py scripts/render_utils.py scripts/render_single_style.py scripts/render_batch.py
```

### Functional Test
```bash
cd /home/window11/be-a-studio
python3 -c "
from scripts.card_engine import load_legacy_template
an_tpl = load_legacy_template('an')
dg_tpl = load_legacy_template('dg')
print(f'✅ AN: {len(an_tpl)} chars, DG: {len(dg_tpl)} chars')
"
```

### Dependency Check
```bash
grep -r "run_pipeline\.py" --include="*.py" --include="*.sh" scripts/ docs/
```

### Data Structure Inspection
```python
import json
from pathlib import Path
candidates = json.loads(Path("content_queue/daily_candidates/20260512.json").read_text())
print(f"Keys: {list(candidates[0].keys())}")
print(f"Has 'category': {'category' in candidates[0]}")
print(f"Has 'brand': {'brand' in candidates[0]}")
```

## Outcomes

### Code Metrics
- **Total deleted:** 2,859 lines (v1 + legacy + duplicates)
- **Total added:** 207 lines (render_utils.py + render_single_style.py)
- **Net reduction:** 2,652 lines
- **Files modified:** 6
- **Files created:** 5
- **Files deleted:** 7

### Quality Improvements
1. ✅ **Reduced monolith**: card_engine.py 10% smaller
2. ✅ **Eliminated confusion**: v1 vs v2 no longer coexists
3. ✅ **DRY principle**: Render code consolidated
4. ✅ **Cleaner repo**: 2,053 lines of dead code removed
5. ✅ **Data clarity**: Documented actual JSON schemas

### Remaining Work (P2)
- **BAS-107**: Exception handling refactoring (23 instances in card_reviewer.py, 15 in photo_resolver.py)
  - **Recommendation:** Separate session (1-2 hours focused work)
  - **Approach:** Audit → Identify specific exceptions → Replace one-by-one → Test

## Lessons Learned

1. **Verify assumptions**: FINISHED_TASK.md said fix was applied, but actual data structure differed
2. **Trust but verify**: Code looked correct, but runtime behavior showed mismatch
3. **Inspect real data**: Always examine actual JSON/files before coding
4. **Document schemas**: Added data structures reference to prevent recurrence
5. **Priority-driven approach**: P0/P1 completed first, P2 deferred appropriately

## References

- **blog-automation skill**: `references/be-a-studio-data-structures.md` (new)
- **hih-task skill**: Updated cron error patterns with category/brand bug
- **python-refactoring skill**: This document added as reference
