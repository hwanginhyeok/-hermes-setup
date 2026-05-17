# Be:A Studio — Card News Automation Architecture

> Last audited: 2026-05-13. Project path: `/home/window11/be-a-studio/`

## Overview

Be:A Studio is Be:Analogue's SNS card news automation engine. It collects content from RSS/YouTube feeds, processes it through GLM, renders HTML→PNG slides via Playwright, auto-reviews quality, and publishes to Instagram via Buffer.

**Scale:** ~30,000 lines Python | ~70 .py files | 13 signature design styles | 89 content sources

## Pipeline (11 stages, cron 05:30 daily)

```
run_daily.sh orchestrates:
1. daily_collector.py      — 69 YouTube + 21 RSS = 90 sources, ThreadPoolExecutor, dedup-merge
2. enrich_youtube.py       — YouTube transcript extraction (IP-blocked, description fallback)
3. enrich_news.py          — Article full-text extraction
4. enrich_summary.py       — 300~500 char summary generation
5. daily_curator.py        — Score-based curation + brand filter + CJK filter + relax mode
6. daily_planner.py        — Claude Sonnet CLI-based card planning (was GLM, switched 2026-05-14 for quality)
7. plan_to_prompt.py       — Bridge: plans/ → prompts/ for copywriter/renderer
8. content_copywriter.py   — GLM generates actual slide copy from plan
9. card_engine.py + render — Playwright HTML→PNG, variable N slides, 13 signature styles
10. card_reviewer.py       — 5-dimension auto-check (color, contrast, watermark, rhythm, tone) + GLM vision
11. GDrive upload + Telegram notification
```

### State Machine (pipeline_state.py)

```
planned → copied → rendered_v1 → reviewed → replanned → copied_v2 → rendered_v2 → editor_reviewed → approved
```

Each transition validates artifact file existence. Score < 80 triggers auto-replan (max 3 attempts).

### Key Files

| File | Lines | Role |
|------|-------|------|
| `scripts/card_engine.py` | 2,323 | Core rendering — Playwright HTML→PNG, loads templates from design_library |
| `scripts/card_reviewer.py` | 2,627 | Quality gates — LAB color, WCAG contrast, sequence check, GLM vision |
| `scripts/photo_resolver.py` | 1,506 | 4-stage photo fallback: OG→body→stock(pexels→unsplash→pixabay→wikimedia→flickr)→preset |
| `scripts/render_from_plan.py` | 1,164 | Plan-to-render bridge |
| `scripts/content_copywriter.py` | 905 | GLM copy generation with self-evaluation + auto-regeneration |
| `scripts/content_replanner.py` | 795 | 2nd loop replan when review score < 80 |
| `scripts/run_pipeline.py` | 559 | Pipeline orchestrator (v2, 2nd loop built-in) |
| `scripts/render_utils.py` | ~100 | Shared Playwright rendering utilities |
| `scripts/feed_health_check.py` | ~230 | RSS/YouTube feed health monitor (cron 06:00) |

### Content Sources (config/sources.yaml)

- **AN (Analogue):** lifestyle, wellness, slow living, reading — Korean YouTube + English RSS
- **DG (Digital):** AI, tech, automation, productivity — English RSS + Korean YouTube
- **an_dg:** Both brands (e.g., 교양_지식, Atlantic, Rest of World)

### Design Library

13 signature styles under `config/design_library/templates/`:
- **AN allowed:** scrapbook, gradient_drift, hybrid_3d, the_edit_minimal, uppity, newneek
- **DG allowed:** timeline, checklist, brutalist, infographic, the_edit_minimal
- Legacy AN/DG templates at `legacy_an/cover.html`, `legacy_dg/cover.html`
- `format_map.yaml` maps style names to renderer configs
- `color_engine.py` provides SharedPalette — photo-dominant color extraction

## Completed Code Quality Cleanup (2026-05-13)

These P0/P1 issues are now **RESOLVED**:

| Issue | Fix | Result |
|-------|-----|--------|
| card_engine.py 2,591-line monolith | Inline AN/DG templates → `legacy_an/`/`legacy_dg/` HTML files + `load_legacy_template()` | 2,323 lines (-268) |
| run_pipeline v1+v2 coexist | v1 moved to legacy/, v2 renamed to run_pipeline.py | -538 lines |
| 11 render scripts scattered | `render_utils.py` shared module + `render_single_style.py` unified entry point | 4 single-style scripts removed |
| legacy/ dead code (notion_uploader etc.) | Entire scripts/legacy/ directory removed | -2,053 lines |
| BAS-102 category vs brand bug | `card_data.get("category")` → `card_data.get("brand").lower()` | Fixed |

**Net code reduction: ~2,800 lines**

## Monitoring

### Feed Health Check (cron 06:00)
```bash
python3 scripts/feed_health_check.py              # Full check (RSS + YouTube)
python3 scripts/feed_health_check.py --rss-only    # RSS only
python3 scripts/feed_health_check.py --json        # JSON output
```
- Checks all 90 sources (21 RSS + 69 YouTube)
- Failure rate ≥30% → Telegram alert
- Results: `~/.pm_logs/feed_health_latest.json`

## Known Remaining Issues

| ID | Issue | Status |
|----|-------|--------|
| BAS-110 | Content Reservoir system — Obsidian vault + top-N% accumulation + reject analysis | Planned (P1) |
| BAS-107 | 38+ broad `except Exception` in card_reviewer (23) + photo_resolver (15) | Open (P2) |
| BAS-99 | YouTube transcript IP-blocked (description fallback partial) | Open (P3) |
| BAS-57 | Naver Blog self-publishing via Playwright | Open (P1) |

### Content Planner: Claude CLI Integration (2026-05-14)

**Change:** `content_planner.py` now calls Claude Sonnet via CLI subscription instead of GLM API.

```python
# Replacement pattern (in process_single_card):
proc = subprocess.run(
    ["claude", "-p", "--model", "sonnet", prompt],
    capture_output=True, text=True, timeout=120,
    env={**os.environ, "HOME": os.environ.get("HOME", "/home/window11")},
)
response_text = proc.stdout.strip()
```

**Also fixed:** `sanitize_for_planning()` was only passing `summary` (1,400 chars) to planner. Now includes `full_text` or `transcript` (up to 17,000+ chars):

```python
"full_text": data.get("content", {}).get("full_text", "") or data.get("transcript", ""),
```

**Impact:** Deeper content analysis → more slides → better quality. GLM `call_glm` import kept as fallback.

## Common Operational Issues

### rclone GDrive Token Expiry
- **Symptom:** `couldn't fetch token - maybe it has expired? - refresh with "rclone config reconnect gdrive:": oauth2: "invalid_grant"`
- **When:** OAuth token expires or is revoked. Happens every few weeks.
- **Fix:** `rclone config reconnect gdrive:` (interactive, requires browser auth)
- **Impact:** Pipeline completes render but GDrive upload silently fails. Cards still exist locally in `rendered/`.

### noVNC Remote Access (for Obsidian / VNC)
- **Setup:** `websockify --web /usr/share/novnc 6080 localhost:5901` (background)
- **URL (Tailscale Funnel):** `https://desktop-plq9e0i.tailec5aa6.ts.net` — root path proxies to noVNC
- **Do NOT use** `localhost:6080` or IP addresses — user accesses remotely via Tailscale hostname
- **Use case:** Remote browser access to WSL desktop for Obsidian, rclone auth, or any GUI task
- **rclone auth in VNC:** Run `DISPLAY=:1 rclone config reconnect gdrive:` as background process. Auth URL appears in stderr (`http://127.0.0.1:53682/auth?state=...`). User opens browser inside VNC to complete Google OAuth. Verify with `rclone ls gdrive: --max-depth 1`.

### enrich_news.py Segfault
- **Symptom:** `Segmentation fault (core dumped)` during cron run (05:30)
- **When:** Intermittent — not every run. Likely Python/C extension memory issue
- **Impact:** Pipeline halts after enrichment, no curation/planning/rendering
- **Workaround:** Manual re-run `bash scripts/run_daily.sh` succeeds on retry
- **Fix status:** Not root-caused. Consider running enrich_news.py in subprocess with retry logic

## Content Queue Structure

```
content_queue/
├── daily_raw/           # YYYYMMDD.json per day
├── daily_candidates/    # Curated items (5/day)
├── daily_seen.json      # Dedup tracker
├── plans/               # Per-card plan markdown (v1, v2)
├── prompts/             # JSON prompts for renderer
├── slides/              # Final slide JSON (_final.json)
├── photos/              # Downloaded photos
├── photos_used.json     # Photo dedup tracker
├── reviews/             # card_id_review.json per card
├── editor_review/       # Editor review markdown
├── pipeline_state.json  # State machine state
└── drafts/              # Temporary drafts
```

## Content Reservoir (BAS-110)

Obsidian vault at `content-vault/` for accumulated content curation:

```
content-vault/
├── Inbox/          ← Today's collection (unscored)
├── Reservoir/      ← Top N% quality — accumulated over time
├── Rejected/       ← Discarded items + reject reason
├── Published/      ← Published items with card_id
├── Dashboard/      ← Dataview SQL-like queries + Kanban drag-and-drop
├── Analysis/       ← Rejected item pattern analysis
├── Templates/      ← Content item note template
└── attachments/
```

**Pipeline extension:** `reservoir_ingest.py` (collect→note), `reservoir_scorer.py` (GLM score), `reservoir_picker.py` (user selection CLI)

**Obsidian launch (WSL):**
```bash
cd ~/apps/squashfs-root && APPDIR=$PWD DISPLAY=:1 ./obsidian --no-sandbox --disable-gpu
```

## Working with Be:A Studio

### Quick Health Check
```bash
cd ~/be-a-studio
ls content_queue/daily_raw/ | tail -5   # Check recent collection
ls rendered/ | tail -10                   # Check recent renders
git log --oneline -5                      # Recent activity
python3 -m pytest tests/ --tb=no -q      # Test suite
cat ~/.pm_logs/feed_health_latest.json   # Feed health
```

### Key Environment Variables
- `GLM_API_KEY` / `Z_AI_API_KEY` — GLM API for content processing
- `UNSPLASH_ACCESS_KEY`, `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `FLICKR_API_KEY` — Stock photo APIs
- `BEA_BOT_TOKEN`, `BEA_CHAT_ID` — Telegram bot
- `BUFFER_IG_CHANNEL_ID` — Buffer Instagram channel
- `TG_BOT_TOKEN`, `TG_CHAT_ID` — Telegram alert notifications (feed health)

### Rules (.claude/rules/llm-workflow.md)
- Sonnet 4.6: code implementer (pane 1)
- GLM 5.1: independent reviewer (pane 2)
- Korean concise responses. No unnecessary explanations.
- Batch operations → delegate to Agent tool
