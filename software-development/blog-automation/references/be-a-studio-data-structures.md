# Be:A Studio Data Structures Reference

**Purpose:** Document actual data structures used in be-a-studio pipeline to prevent field name mismatches like the `category` vs `brand` bug (BAS-102, 2026-05-13).

## Candidates JSON Structure

**Location:** `content_queue/daily_candidates/YYYYMMDD.json`

**Produced by:** `daily_curator.py` → selects top 5 items from enriched news/YouTube

**Actual Schema:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=...",
  "title": "Video Title",
  "description": "Video description...",
  "thumbnail": "https://i.ytimg.com/vi/...",
  "published_at": "2026-05-12T10:00:00Z",
  "channel_name": "Channel Name",
  "channel_id": "UC...",
  "source_type": "youtube" | "rss",
  "brand": "an" | "dg",                    // ✅ EXISTS - Use this!
  "category_kr": "스타트업_경제교양",      // ✅ EXISTS - Korean category name
  "transcript": "...",                     // Transcript text (if available)
  "transcript_lang": "en" | "ko",
  "transcript_length": 1234,
  "has_transcript": true,
  "full_text": "...",                      // Article full text (RSS only)
  "has_full_text": true,
  "summary": "...",                        // AI-generated summary (300-500 chars)
  "content": {
    "key_facts": ["fact1", "fact2"]       // Extracted key facts
  },
  "verdict": "recommend" | "review" | "not_recommended",
  "total_score": 8.5,                      // 0-10 scale
  "transformable": true,
  "depth": "high" | "medium" | "low",
  "universality": 0.8,
  "brand_fit": 9.0,
  "reason": "Reason for verdict",
  "suggested_frame": "Suggested angle",
  "plan_data": {},                         // Placeholder for plan
  "an_axis": "Connect" | "Nature" | "Other" // 5-axis for An brand
}
```

**⚠️ CRITICAL:** 
- Field is **`brand`** (values: "an", "dg"), **NOT `category`**
- `category_kr` is the Korean display name, not the code
- `content_planner.py` must use `card_data.get("brand", "").lower()`

## Plan File Structure

**Location:** `content_queue/plans/{CARD_ID}_v1.md`

**Produced by:** `content_planner.py` (process_single_card)

**Frontmatter:**
```yaml
---
card_id: "AN-20260512-01"
brand: "an"
category: "교양_지식"
style: "scrapbook"
slide_count: 6
created_at: "2026-05-12T10:30:00+09:00"
source_url: "https://www.youtube.com/watch?v=..."
source_title: "Video Title"
---
```

**Content:** Markdown with YAML tables for slide planning

## Common Pitfalls

### 1. Category vs Brand Mismatch

**Symptom:** `NameError: name 'category' is not defined`

**Root Cause:** 
```python
# ❌ WRONG
category = card_data.get("category", "")  # Returns "" (empty string)

# ✅ CORRECT
brand = card_data.get("brand", "").lower()  # Returns "an" or "dg"
category = brand  # Alias for compatibility
```

**Why:** Candidates JSON uses `brand` field, not `category`. The `category_kr` field is for display only.

**Prevention:** 
- Always verify actual JSON structure before coding
- Use `execute_code` or `python3 -c` to inspect real data
- Check multiple sample items to ensure consistency

### 2. .pyc Cache Staleness

**Symptom:** Code changes not reflected in cron execution

**Fix:**
```bash
find /home/window11/be-a-studio -name "*.pyc" -delete
find /home/window11/be-a-studio -name "__pycache__" -type d -exec rm -rf {} +
```

**Prevention:** Add to pre-commit hook or cron script

## Verification Commands

### Inspect Candidates JSON
```python
import json
from pathlib import Path

candidates = json.loads(Path("content_queue/daily_candidates/20260512.json").read_text())
print(f"Total: {len(candidates)}")
print(f"Keys: {list(candidates[0].keys())}")
print(f"Brand field: {candidates[0].get('brand')}")
print(f"Has 'category': {'category' in candidates[0]}")
```

### Test Content Planner
```python
import sys
sys.path.insert(0, 'scripts')

mock_data = {
    'id': 'TEST-001',
    'content': {
        'title': 'Test',
        'summary': 'A' * 100,
    },
    'brand': 'an'  # ✅ Use 'brand', not 'category'
}

from content_planner import process_single_card
result = process_single_card(mock_data, dry_run=True)
```

## Related Files

- **Source:** `scripts/daily_curator.py` - produces candidates JSON
- **Consumer:** `scripts/content_planner.py` - reads candidates JSON
- **Schema Definition:** Not formally defined - inferred from code
- **Documentation Update Needed:** Consider adding JSON Schema validation

## When to Update This Reference

1. **Schema Changes:** When `daily_curator.py` output structure changes
2. **Field Additions:** When new fields are added to candidates JSON
3. **Bug Fixes:** When data structure bugs are found and fixed
4. **New Consumers:** When new scripts read from candidates JSON

**Maintenance:** Review quarterly or when pipeline stages are modified.
