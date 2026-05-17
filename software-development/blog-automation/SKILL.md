---
name: blog-automation
description: "Blog automation systems: content generation, scheduling, publishing, and comment management across platforms (Naver Blog, WordPress, etc.)."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [blog, automation, publishing, content-generation, naver-blog]
    related_skills: [writing-plans, subagent-driven-development]
---

# Blog Automation

Automated blog operations: content planning, AI-powered writing, scheduling, publishing, and comment management. Covers full-stack automation from ideation to engagement.

## Use Cases

- **iCloud Photo → Blog**: Daily photo collection → AI analysis → content planning → auto-publishing
- **Comment Bots**: AI-powered comment generation, reply automation, engagement tracking
- **Multi-platform Publishing**: Single source → Naver Blog, WordPress, Ghost, Hugo, etc.
- **Content Workflows**: Ideation → Draft → Review → Publish → Promote
- **SNS Integration**: Auto-post to Telegram, Twitter/X, Instagram after blog publish

## Architecture Patterns

### Classic Naver Blog Automation (insung-blog project)

**Tech Stack:**
- Python 3.12+ with async/await
- Playwright for browser automation (headless/headed)
- Claude API (Vision + Text generation)
- FastAPI for webhook/API endpoints
- Supabase for control plane (settings, logs)
- SQLite for local DB (comments, runs)
- Next.js 14 for web dashboard
- systemd for service management
- Telegram for notifications

**Core Services:**
```
blog-api.service      → FastAPI server (port 8001)
blog-worker.service   → Command queue worker
```

**Workflow:**
1. **Photo Collection**: Playwright → iCloud.com → download latest photos
2. **Content Analysis**: Claude Vision → analyze photos → generate topics/tags/memo
3. **Draft Generation**: Claude API → generate blog post from plan
4. **Publishing**: Playwright → Naver Blog → post content with images
5. **Notification**: Telegram → notify user of draft/review/publish

**Photo Collection Pipeline (WSL mount approach — production):**

iCloud Photos are mounted via WSL2 at `/mnt/c/Users/window11/Pictures/iCloud Photos/Photos/`. No web scraping needed — read files directly from the filesystem.

**Key Modules (insung-blog `src/photo/`):**
```
src/photo/__init__.py           → PhotoGroup + TopicIdea dataclasses
src/photo/exif_utils.py         → Pillow EXIF DateTime/GPS parsing, mtime fallback
src/photo/scanner.py            → PhotoScanner: scan_new_photos() + group_by_time_and_location()
src/photo/topic_planner.py      → TopicPlanner: Claude Vision analysis → topic ideas (1-3 per group)
src/photo/pipeline.py           → PhotoBlogPipeline orchestrator: scan → plan → notify → publish
scripts/photo_pipeline.py       → CLI: scan / plan / publish / status
```

**Pipeline Flow:**
```
iCloud Photos folder (WSL mount)
  → PhotoScanner.scan_new_photos() [SQLite state tracking, skip already-seen]
  → group_by_time_and_location() [EXIF DateTime + GPS haversine clustering]
  → TopicPlanner.plan_topics() [Claude Vision on representative 5 photos]
  → Telegram notification with topic choices
  → User picks topic via CLI
  → content_generator.generate_post() [existing module, reused]
  → publisher_main._run_publish() [existing module, reused]
```

**State DB:** `data/photo_state.db` (SQLite) — 4 tables: seen_photos, group_status, photo_groups, photo_topics

**CLI Usage:**
```bash
python scripts/photo_pipeline.py scan          # Scan for new photos, save groups
python scripts/photo_pipeline.py plan          # Scan + AI topic planning + Telegram notify
python scripts/photo_pipeline.py publish <id> <idx> [--memo "..."] [--dry-run]
python scripts/photo_pipeline.py status        # List pending (planned) groups
```

**Performance:** scan_new_photos() processes ~7,700 images in ~20s. First run requires bulk seen_photos seeding (~2 min for 7K+ images via executemany).

**Config (config/settings.py):**
```python
ICLOUD_PHOTO_DIR = Path("/mnt/c/Users/window11/Pictures/iCloud Photos/Photos/")
PHOTO_SCAN_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"})
PHOTO_GROUP_TIME_GAP_HOURS = 2        # Same group if within 2 hours
PHOTO_GROUP_LOCATION_RADIUS_M = 500   # Same group if within 500m GPS
PHOTO_GROUP_MIN_SIZE = 2              # Minimum photos per group
PHOTO_GROUP_MAX_SIZE = 30             # Maximum photos per group
```

**Cron:** `0 9 * * * cd /home/window11/insung_blog && .venv/bin/python scripts/photo_pipeline.py plan`

**Deprecated:** `src/icloud/icloud_client.py` (Playwright web scraping approach) — replaced by WSL mount. Remove during cleanup.

### Multi-Platform Pattern

**When to Use:** Managing multiple blogs with shared content

```
┌─────────────┐
│   Source    │ (Photos, Notes, Ideas)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Planner   │ (AI planning, topic selection)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Generator  │ (AI writing, formatting)
└──────┬──────┘
       │
       ├─────────┬─────────┬─────────┐
       ▼         ▼         ▼         ▼
  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
  │ Naver  │ │Wordpress│ │ Ghost  │ │ Hugo   │
  │  Blog  │ │        │ │        │ │        │
  └────────┘ └────────┘ └────────┘ └────────┘
```

**Implementation:**
- Abstract `Publisher` interface with platform-specific implementations
- Unified content model (Markdown with frontmatter)
- Platform-specific formatters (HTML, MD, etc.)
- Unified scheduling (cron, webhooks, event-driven)

## Platform-Specific Integration

### Naver Blog

**Authentication:**
- Login cookies stored in `cookies/` directory
- Periodic cookie refresh required (2FA detection)
- Use `save_cookies.py` to refresh manually when login expires

**Publishing Flow:**
```python
# publisher_main.py pattern
from playwright.async_api import async_playwright

async def publish_post(title: str, content: str, images: List[str]):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 1. Load cookies
        await page.context.add_cookies(cookies)
        
        # 2. Navigate to blog write page
        await page.goto("https://blog.naver.com/post/write")
        
        # 3. Fill title and content
        await page.fill("#title", title)
        await page.fill("#content", content)
        
        # 4. Upload images (if any)
        for img in images:
            await page.set_input_files("#file-upload", img)
            await page.wait_for_timeout(1000)
        
        # 5. Publish
        await page.click("#publish-button")
        await page.wait_for_url("**/blog.naver.com/*")
        
        await browser.close()
```

**Selectors Change:** Naver Blog DOM changes frequently. Use `debug_publisher.py` to inspect current selectors before updating production code.

**Comments:**
- Comments require different auth (sometimes separate login)
- Comment selectors are different from post selectors
- Use `debug_comment_selector.py` for DOM analysis

### WordPress (Self-hosted)

**Approach:**
- REST API (preferred): `/wp-json/wp/v2/posts`
- XML-RPC (legacy, still used by Jetpack)
- Playwright (fallback for complex plugins)

```python
import requests

def publish_wordpress(site_url: str, title: str, content: str, api_token: str):
    url = f"{site_url}/wp-json/wp/v2/posts"
    headers = {"Authorization": f"Bearer {api_token}"}
    data = {
        "title": title,
        "content": content,
        "status": "publish"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

### Ghost / Jekyll / Hugo

**Approach:**
- Git-based workflow: push markdown files → CI/CD → deploy
- Use frontmatter for metadata (title, tags, date, slug)

```markdown
---
title: "Post Title"
tags: ["tech", "tutorial"]
date: 2026-05-10
slug: post-title
---

Content here...
```

**Automation:**
```python
def create_hugo_post(content_dir: str, title: str, body: str, tags: List[str]):
    from datetime import datetime
    from pathlib import Path
    
    slug = title.lower().replace(" ", "-")
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-{slug}.md"
    filepath = Path(content_dir) / filename
    
    frontmatter = f"""---
title: "{title}"
tags: {tags}
date: {date_str}
---

{body}
"""
    
    filepath.write_text(frontmatter)
    return filepath
```

## Content Generation Pipeline

### Photo-Driven Workflow (iCloud — implemented)

**Approach:** WSL2 mounts iCloud Photos as a regular filesystem. No scraping, no API auth, no 2FA.

**Pattern:**
1. **Scan**: `PhotoScanner` reads `/mnt/c/Users/window11/Pictures/iCloud Photos/Photos/`, tracks seen files in SQLite, returns only new photos
2. **Group**: EXIF DateTime + GPS clusters photos into logical groups (same day + 2hr gap + 500m radius)
3. **Analyze**: `TopicPlanner` sends representative 5 photos to Claude Vision, gets scene analysis
4. **Plan**: Analysis + metadata → 1-3 `TopicIdea` objects (title, angle, category, confidence)
5. **Notify**: Telegram message with topic choices and CLI commands
6. **Publish**: User picks topic → `content_generator.generate_post()` → `publisher_main._run_publish()`

**Example Plan Structure:**
```json
{
    "title": "데스크탑 세팅 공유",
    "topics": ["하드웨어", "소프트웨어", "개발 환경"],
    "tags": ["tech", "setup", "dev-tools"],
    "memo": "개발자 친구들에게 공유하는 스타일, CLI 툴 위주로 설명",
    "tone": "friendly"
}
```

### Text-Only Workflow

**Pattern:**
1. **Ideation**: User provides keyword, topic, or inspiration
2. **Research**: Web search → gather context, quotes, examples
3. **Outline**: Generate structured outline with H1/H2/H3
4. **Draft**: Fill in sections with AI writing
5. **Optimize**: SEO, readability, tone adjustment
6. **Publish**: Platform-specific formatting and posting

## Comment Automation

### Comment Generation

**Pattern:**
```python
async def generate_comment(post: dict, persona: str = "helpful_expert") -> str:
    prompt = f"""
    블로그 글: {post['title']}
    내용 요약: {post['summary']}
    태그: {post['tags']}
    
    페르소나: {persona}
    당신은 이 글을 읽은 독자입니다. 자연스러운 댓글을 작성해주세요.
    너무 칭찬만 하지 말고, 질문이나 인사이트를 포함해주세요.
    """
    
    # Claude API call
    response = await claude_client.messages.create(...)
    return response.content[0].text
```

### Comment Bots (insung-blog pattern)

**Architecture:**
- `main.py`: Main comment bot runner
- `src/comment/commenter.py`: Comment generation logic
- `src/storage/supabase_client.py`: Comment tracking (pending, published)
- `command_worker.py`: Background task queue for comment jobs

**Workflow:**
1. **Target Selection**: Fetch recent posts from Naver Blog
2. **Context Gathering**: Extract title, tags, content preview
3. **Comment Generation**: AI → generate relevant comments
4. **Review**: Store in Supabase `pending_comments`
5. **Publishing**: User approval → post to Naver Blog
6. **Reply Tracking**: Monitor replies to bot comments

**Anti-Detection:**
- Rate limiting: 1 comment per N minutes
- Rotation: Multiple personas, varied comment length
- Natural language: Avoid repetitive patterns, use conversational tone

## Scheduling & Automation

### Cron Integration (Hermes)

**Setup:**
```bash
# Hermes TUI에서 설정
/cron create "every day at 10:00 AM"

# 프롬프트:
"""
매일 오전 10시에 /home/window11/insung_blog/scripts/daily_agent.py 실행
실행 결과를 텔레그램으로 보고
"""
```

**Agent Script Pattern:**
```python
#!/usr/bin/env python3
"""
Daily blog automation agent
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

async def main():
    # 1. Collect content
    # 2. Analyze & plan
    # 3. Generate draft
    # 4. Report to user
    # 5. Wait for approval
    # 6. Publish
    
    await report_to_telegram("Agent run complete")

if __name__ == "__main__":
    asyncio.run(main())
```

### Webhook Triggers

**Pattern:**
```python
# api_server.py
from fastapi import FastAPI

app = FastAPI()

@app.post("/webhook/photo-upload")
async def on_photo_upload(photo_url: str):
    # Trigger content pipeline
    plan = await analyze_photo(photo_url)
    draft = await generate_draft(plan)
    await save_for_review(draft)
```

**n8n Integration:**
- n8n HTTP Request node → FastAPI `/webhook/*` endpoints
- Workflow automation: n8n orchestrates, Hermes executes AI tasks

## Notification & Review

### Telegram Notifications

**Pattern:**
```python
# src/utils/telegram_notifier.py
from telegram import Bot

async def send_admin_notification(message: str):
    bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    chat_id = os.environ["TELEGRAM_ADMIN_CHAT_ID"]
    await bot.send_message(chat_id=chat_id, text=message)
```

**Approval Workflow:**
```python
# Send draft
await send_admin_notification(f"""
📝 New Draft Ready

Title: {draft['title']}
Preview: {draft['content'][:200]}...

Approve? /approve_{draft_id}
Reject? /reject_{draft_id}
""")

# Handle response (via Telegram bot or webhook)
if command == f"/approve_{draft_id}":
    await publish_draft(draft_id)
```

## Debugging & Troubleshooting

### Common Issues

**1. Login Expired**
- Symptom: Playwright redirects to login page
- Fix: Run `save_cookies.py` to refresh cookies
- Prevention: Schedule cookie refresh weekly

**2. DOM Selectors Changed**
- Symptom: `playwright` timeout errors, element not found
- Fix: Run debug scripts (e.g., `debug_publisher.py`, `debug_comment_selector.py`)
- Prevention: Monitor Naver Blog changes, run weekly smoke tests

**3. Rate Limiting**
- Symptom: Comments not posting, account flagged
- Fix: Increase delays between actions, use multiple accounts
- Prevention: Respect platform limits, vary timing

**4. API Token Issues**
- Symptom: 401 Unauthorized from Claude API
- Fix: Update `.env` with new API key
- Prevention: Rotate keys periodically

### Debug Scripts

**DOM Analysis:**
```python
# debug_publisher.py
from playwright.async_api import async_playwright

async def analyze_publish_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://blog.naver.com/post/write")
        
        # Print all buttons
        buttons = await page.locator("button").all()
        for btn in buttons:
            print(await btn.inner_text())
        
        # Print all inputs
        inputs = await page.locator("input").all()
        for inp in inputs:
            print(await inp.get_attribute("name") or await inp.get_attribute("id"))
```

**Comment Testing:**
```python
# test_my_blog.py
import pytest

@pytest.mark.asyncio
async def test_fetch_recent_posts():
    from src.naver.client import NaverClient
    client = NaverClient()
    posts = await client.fetch_recent_posts(count=5)
    assert len(posts) == 5
    assert all("title" in p for p in posts)
```

## Service Management (systemd)

**Pattern:**
```bash
# Status check
systemctl --user status blog-api blog-worker

# Restart
systemctl --user restart blog-api blog-worker

# Logs
journalctl --user -u blog-worker -n 50 --no-pager

# Multiple instance check (avoid conflicts)
ps aux | grep command_worker | grep -v grep | wc -l  # Should be 1
```

**Common Pitfalls:**
- **NEVER** `pkill -f command_worker.py` — systemd auto-restarts causing conflicts
- Use `systemctl --user stop blog-worker` instead
- Check for stale tmux sessions before restarting services

## Pipeline Monitoring & Health Checks

### Feed Health Monitoring (BAS-97-FU-6 pattern)

**Pattern:** Cron-based health check for content sources with Telegram alerting. Runs daily after collection so failures are caught before next run.

```python
# Core pattern from feed_health_check.py
def check_rss_feed(name, url):
    req = Request(url, headers={"User-Agent": "BeAStudio/1.0"})
    resp = urlopen(req, timeout=15)
    body = resp.read(500)
    return {"ok": len(body) >= 50 and b"<" in body}  # Sanity check: non-empty XML
```

**Key decisions:**
- YouTube channels checked via `feeds/videos.xml?channel_id=XXX` (no API key needed)
- Failure rate threshold 30% before alerting (avoid noise from 1-2 transient failures)
- Results persisted to `~/.pm_logs/feed_health_latest.json` for historical tracking

### Code Quality Refactoring (BAS-103~108 pattern)

When reducing technical debt in a content pipeline:

1. **Inline templates → files**: Extract HTML strings from monolith scripts into `design_library/templates/`, add loader function
2. **Duplicate scripts → shared module**: Common Playwright rendering code → `render_utils.py`
3. **v1/v2 coexistence → rename**: Move v1 to legacy, rename v2 as main, update docs
4. **Dead code → delete entirely**: Migrated to GDrive? Remove `legacy/` completely, don't keep around
5. **Field name bugs → inspect real data first**: Always `python3 -c` the actual JSON before writing field access code

### Project Session Focus (Pitfall)

When working in a specific project session (e.g., be-a-studio), **stay in that project's context**. If a user mentions another project's issue, note it but don't start investigating there. The user will address other projects in their own sessions.

## Planning & Implementation

### Using writing-plans Skill

For complex blog automation features, always use `writing-plans` skill to create detailed implementation plans before coding.

**Pattern:**
1. Load `writing-plans` skill
2. Create plan with bite-sized tasks (2-5 min each)
3. Include exact file paths, complete code, verification steps
4. Execute via `subagent-driven-development` skill

**Example Plan Structure:**
```markdown
# [Feature Name] Implementation Plan

> For Hermes: Use subagent-driven-development skill to implement.

**Goal:** [One sentence]

**Architecture:** [2-3 sentences]

**Tech Stack:** [Key technologies]

---

### Task 1: [Descriptive Name]

**Objective:** What this task accomplishes

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `existing/file.py:45-67`

**Step 1: Write failing test**
[Code]

**Step 2: Run test**
[Command]
Expected: FAIL

**Step 3: Implement**
[Code]

**Step 4: Run test**
[Command]
Expected: PASS

**Step 5: Commit**
[Command]
```

## Content Reservoir Pattern (BAS-110)

Accumulate curated content over time instead of processing daily batches immediately. Top N% by quality score are kept in a "reservoir" for user selection; rejected items are logged with reasons for quality analysis.

### Why

Daily pipeline collects ~94 items but only 5% (5 items) get used. The rest are discarded. A reservoir:
- Preserves high-quality content for later use
- Lets users pick topics they care about (not just what GLM chose today)
- Tracks what was published where, and what was rejected and why
- Enables series/theme curation ("AI week", "wellness month")

### Architecture

```
Daily collection (94 items)
  → GLM quality scoring (0-10)
  → Top 20% (~19 items) → Reservoir (accumulate)
  → Bottom 80% (~75 items) → Rejected log (with reason)
  
Reservoir (accumulated)
  → User picks via Obsidian / CLI / Telegram
  → Planned → Rendered → Published
  → Publish history tracked

Rejected analysis
  → "Why was this rejected?" → Score/reason/category/source stats
  → "This source consistently scores low" → Source quality audit
```

### Obsidian as Content Management Interface

**Vault structure:**
```
content-vault/
├── Inbox/          ← Today's collection (unscored)
├── Reservoir/      ← Top N% — accumulated
├── Rejected/       ← Discarded + reason
├── Published/      ← Published with card_id
├── Dashboard/      ← Dataview queries + Kanban board
├── Analysis/       ← Rejected item analysis
├── Templates/      ← Note template with frontmatter schema
└── attachments/
```

**Each content item is a markdown note with frontmatter:**
```yaml
---
id: SRC-20260514-001
title: "AI 에이전트가 바꾸는 개발 워크플로우"
source: "TechCrunch"
source_type: rss
brand: dg
category: 테크_AI_개발
quality_score: 8.5
status: inbox        # inbox → reservoir → selected → planned → rendered → published
tags: [AI, 개발]
collected: 2026-05-14
---
```

**Dataview queries** enable SQL-like filtering: `TABLE quality_score FROM "Reservoir" WHERE brand = "dg" SORT quality_score DESC`. **Kanban plugin** provides drag-and-drop status management.

**Python automation writes notes** (reservoir_ingest.py creates markdown files). Obsidian provides the reading/browsing/selection interface.

### Key Decisions
- **Not all content stored** — only top N% (configurable, default 20%). User's explicit correction: "전부 저장은 아님. 상위 몇프로만 누적 저장"
- **Rejected items are logged** — with reason string for analysis, not silently discarded
- **Obsidian AppImage in WSL** — extract with `--appimage-extract` (no FUSE needed), run with `APPDIR=$PWD DISPLAY=:1 ./obsidian --no-sandbox --disable-gpu`
- **Dual mode** — automatic (GLM picks 5) + manual (user picks from reservoir). Coexist.
- **rclone GDrive token expiry** — `rclone config reconnect gdrive:` required every few weeks. Pipeline renders complete but uploads silently fail. Check for `invalid_grant` in logs.
- **noVNC + Tailscale for remote access** — `websockify --web /usr/share/novnc 6080 localhost:5901` proxies VNC 5901. Access via Tailscale Funnel HTTPS: `https://desktop-plq9e0i.tailec5aa6.ts.net` (root path proxies to 6080). **Do NOT use IP:port or localhost URLs** — user accesses remotely via Tailscale hostname.
- **rclone OAuth in VNC** — `DISPLAY=:1 rclone config reconnect gdrive:` opens browser inside VNC where user can authenticate. URL appears in stderr: `http://127.0.0.1:53682/auth?state=...`. If browser doesn't open automatically, open it manually inside VNC. **Run as background process** (`terminal(background=true)`) so it stays alive while user authenticates. **Don't kill the process** — wait for user to complete auth, then verify with `rclone ls gdrive: --max-depth 1`.
- **rclone auth is user-performed** — The agent opens the process and provides the URL, but the user MUST complete the Google OAuth login themselves. The agent cannot and should not attempt to automate the login click sequence. Just open `DISPLAY=:1 rclone config reconnect gdrive:` as a background process and tell the user to check VNC.
- **Verify auth with:** `rclone ls gdrive: --max-depth 1` — if it lists files, auth succeeded.
- **Tailscale serve map** (current): `/` → noVNC 6080, `/bas` → BAS 8877, `/insung` → insung_blog 8001, `/dashboard` → dashboard 8766, `:8443` → insung_blog 8002, `:8766` → dashboard 8766, `:8877` → BAS 8899

### Render Pipeline Entry Points (be-a-studio)

**CRITICAL — common confusion point:**

```bash
# CORRECT — renders from plan file (what run_daily.sh uses)
python3 scripts/render_from_plan.py --card-id AN-20260514-01

# WRONG — card_engine.py does NOT accept --card-id / --date flags
python3 scripts/card_engine.py --card-id AN-20260514-01 --date 20260514  # ERROR
```

`card_engine.py` is the low-level renderer (called by render_from_plan.py internally). The correct orchestration entry point for rendering from a plan file is `render_from_plan.py`.

**Always verify by checking run_daily.sh before calling render scripts manually:**
```bash
grep -A5 "card_engine\|렌더" scripts/run_daily.sh | head -20
```

---

### LLM Switching in Content Pipeline (GLM → Claude CLI)

**When to switch from API-based LLM to Claude CLI subscription:**
- User wants higher quality planning/generation than GLM provides
- Claude Max subscription active (no per-token cost)
- Need longer context (full_text/transcript up to 17K+ chars)

**Pattern — calling Claude CLI from Python (STDIN method — MUST use this):**
```python
import subprocess, os

proc = subprocess.run(
    ["claude", "-p", "--model", "sonnet"],
    input=prompt,                    # ← stdin, NOT positional arg
    capture_output=True, text=True, timeout=300,
    env={**os.environ, "HOME": os.environ.get("HOME", "/home/window11")},
)
response_text = proc.stdout.strip()
if not response_text:
    stderr_msg = proc.stderr.strip()[:200] if proc.stderr else "없음"
    print(f"⚠️ Claude 빈 응답 (stderr: {stderr_msg})")
```

**Key pitfalls:**
- **STDIN, NOT positional arg** — `claude -p --model sonnet` + `input=prompt`. Passing prompt as CLI arg (`claude -p --model sonnet PROMPT`) hits OS argument length limits with long prompts (8K+ chars) and silently truncates or errors.
- `timeout=300` not 120 — Sonnet with 17K transcript takes 2-3 min. 120s causes consistent timeouts.
- `claude -p` (non-interactive print mode) — always use `-p` for scripted calls.
- `--model sonnet` — explicit model, don't rely on default.
- Don't remove `glm_client` import — keep as fallback.
- Claude CLI must be logged in (`claude` interactive session works).
- Check stderr on empty stdout — stderr shows auth errors, model errors, etc.

### Content Pipeline Data Flow Bug Pattern

**Problem:** Content planner receives only 1,400-char summary but 17,000-char transcript/full_text is available. Result: shallow plans, too few slides, weak content.

**Root cause:** `sanitize_for_planning()` function strips fields before sending to LLM. Always check what data is actually available vs what's being passed.

**Debugging pattern:**
```bash
# Check actual data sizes in candidates JSON
cd /home/window11/be-a-studio && python3 -c "
import json
c = json.loads(open('content_queue/daily_candidates/DATE.json').read())
for item in c:
    print(f'{item[\"card_id\"]}: transcript={len(item.get(\"transcript\",\"\"))}자, summary={len(item.get(\"summary\",\"\"))}자, full_text={len(item.get(\"full_text\",\"\"))}자')
"
```

**Fix 1 — sanitize_for_planning():** Include full text sources:
```python
"full_text": data.get("content", {}).get("full_text", "") or data.get("transcript", ""),
```

**Fix 2 — daily_planner transcript injection:** The `plan_data` dict is extracted from `item["plan_data"]` which may not carry the transcript from the top-level item. Inject explicitly:
```python
# After: plan_data["id"] = card_id
if not plan_data.get("content", {}).get("full_text"):
    transcript = item.get("transcript", "") or item.get("full_text", "")
    if transcript:
        plan_data.setdefault("content", {})["full_text"] = transcript
```

**Lesson:** Before blaming LLM quality, verify the LLM is actually receiving all available data. Check `sanitize_*` or `prepare_*` functions that sit between raw data and LLM calls. Also check the aggregator/orchestrator (daily_planner) — it may strip data when constructing plan_data from the raw item.

## Best Practices

### Security

- **Never hardcode** API keys, passwords, or tokens in source code
- Use `.env` for secrets (gitignored)
- Rotate tokens regularly
- Use app-specific passwords where available (e.g., iCloud app passwords)
- Store cookies securely (encrypted if possible)

### Content Quality

- **Always review** AI-generated content before publishing
- Use persona tuning to match your voice
- A/B test different prompts for best results
- Track engagement metrics to refine strategy

### Platform Compliance

- **Respect rate limits** on all platforms
- Follow terms of service
- Don't spam — quality over quantity
- Use natural language patterns in automation
- Rotate timing to avoid detection

### Maintainability

- **Document all** platform-specific selectors (they change frequently)
- Keep debug scripts in `scripts/` for future troubleshooting
- Use type hints and async/await consistently
- Write tests for critical paths
- Commit frequently with descriptive messages

## Project Structure Template

```
blog-automation/
├── .env                      # Secrets (gitignored)
├── .env.example              # Template
├── CLAUDE.md                 # Project overview, rules
├── requirements.txt          # Python dependencies
├── main.py                   # Main bot runner
├── api_server.py             # FastAPI endpoints
├── command_worker.py         # Background queue worker
├── src/
│   ├── photo/                # Photo pipeline (scanner, planner, pipeline)
│   ├── ai/                   # AI generation (content_generator, memo_parser)
│   ├── neighbor/             # Neighbor discovery
│   ├── commenter/            # Comment generation
│   ├── handlers/             # Command handlers
│   ├── storage/              # DB clients (Supabase, SQLite)
│   └── utils/                # Telegram, logger, helpers
├── scripts/                  # Utility scripts
├── tests/                    # Pytest tests
├── cookies/                  # Browser cookies (gitignored)
├── logs/                     # Runtime logs
└── docs/
    └── plans/                # Implementation plans
```

## References & Templates

### Project-Specific References

**`references/be-a-studio-data-structures.md`** — **CRITICAL**: Actual JSON schemas used in be-a-studio pipeline. Documents the `candidates` JSON structure (field names, types, examples). **Prevents field name bugs** like the `category` vs `brand` mismatch (BAS-102, 2026-05-13). Contains verification commands and common pitfalls. **Always inspect this before modifying pipeline stages.**

**`references/be-a-studio-architecture.md`** — Be:A Studio card news automation: 11-stage pipeline (RSS→GLM→render→review→publish), 13 signature design styles, state machine, feed health monitoring (cron 06:00), code quality refactoring patterns (inline template extraction, render script consolidation, dead code removal), content queue structure, environment variables, and working procedures. **Updated 2026-05-13** with completed P0/P1 cleanup results. Use when working on be-a-studio or similar card/news automation systems.

**`references/naver-blog-automation.md`** — Detailed Naver Blog integration notes from the insung-blog project:
- Service architecture and management (systemd)
- Existing API endpoints (api_server.py, 1609 lines)
- Debug scripts for DOM analysis
- Cookie-based authentication and refresh procedures
- Supabase integration for control plane
- Telegram notification patterns
- Session start protocols and recovery procedures
- Common pitfalls and troubleshooting

**Use this reference when:**
- Working on Naver Blog automation
- Debugging selector issues
- Understanding the insung-blog project structure
- Setting up similar blog automation systems

**`references/experience-campaigns-schema.md`** — `experience_campaigns` 테이블 컬럼/수집 현황/null 비율/API 엔드포인트/프론트엔드 구조. 체험단 탭 개선 시 참조.

**`references/chrome-extension-nextjs-patterns.md`** — Chrome Extension + Next.js integration patterns from insung-blog:
- **Extension version checking** — middleware-based (not per-route): X-Ext-Version header → middleware semver check → X-Ext-Outdated response header → chrome.storage flag → popup/ExtErrorBanner outdated UI
- **Infinite scroll handling** — why `scrollTo()` fails on Naver FeedList + 3-phase fix: network capture (fetch/XHR interception) → wheel event dispatch → API URL logging for future optimization
- **Extension-driven discovery** — extension performs search.naver.com queries (no auth needed), extracts blogger IDs, POSTs to /api/ext/discover/candidates, server deduplicates and stores
- **API path convention pitfall** — Server uses `/comment/*` (singular), extension had `/comments/*` (plural). Every result-reporting call silently 404'd, causing 50 rows stuck in `posting` state. Always verify extension API paths match server route registration.
- **Login guard for posting** — `runPostingLoop` must check `getNaverLoginStatus()` before locking. Without this, lock succeeds but `tryPost` immediately fails, orphaning `posting` state.
- **finally-cleanup pattern** — `runPostingLoop`'s finally block must call `/comment/unlock-all` for leftover `posting` rows (interrupted loops, crashes).

### Neighbor System Investigation (2026-05-14)

**DB state for letter_hih (user 50c16052)**:
- Total neighbors: 259 — but 서로이웃(mutual): **0**, 일방(one_way): **0**, discovered: 242, None: 17
- `auto_neighbor_request`: **False** (not sending any neighbor requests)
- `max_neighbor_requests_per_day`: 10 (not used since auto is off)
- All neighbor_requests rows: status `cancelled` (from March 2026 test)

**Impact**: FeedList.naver shows 이웃 새글, but with 0 서로이웃 the feed shows 추천 피드 (Recommendation.naver redirect when not logged in, or generic recommendations). This limits comment collection volume regardless of scroll fixes.

**Query pattern for Supabase neighbor investigation**:
```bash
cd /home/window11/insung_blog && source .venv/bin/activate && set -a && source .env && set +a && python3 << 'PYEOF'
import sys, os; sys.path.insert(0, "."); os.chdir(".")
from dotenv import load_dotenv; load_dotenv()
from src.storage.supabase_client import get_supabase
sb = get_supabase()
uid = "50c16052-77b3-4c33-b1d9-acecc23e4806"
from collections import Counter
types = sb.table("neighbors").select("neighbor_type").eq("user_id", uid).execute()
print(Counter(r.get("neighbor_type","null") for r in types.data))
PYEOF
```

**Key files**:
- Neighbor visitor: `src/neighbor/neighbor_visitor.py` — `auto_request` setting controls automatic neighbor requests during visits
- Neighbor requester: `src/neighbor/neighbor_requester.py` — `send_neighbor_request()` via Playwright
- Settings: `bot_settings.auto_neighbor_request` / `bot_settings.max_neighbor_requests_per_day`
- Extension: `chrome-extension-poc/background.js` — `EXT-NEIGHBOR-REQUEST` (서로이웃 신청 확장, 코드 완료, 실측 대기)

**Key insight:** When adding cross-cutting concerns to ext API routes (versioning, rate limiting, logging), use Next.js `middleware.ts` with `/api/ext/:path*` matcher — avoids touching 13+ individual route files.

**Use this reference when:**
- Adding version checking or rate limiting to extension APIs
- Handling sites that ignore programmatic scrollTo (use wheel events instead)
- Building extension-driven search/discovery features
- Integrating Chrome extension with Next.js backend

### Starter Template

**`references/reverse-geocoding-apis.md`** — Reverse geocoding APIs for converting GPS coordinates to place names (OSM, Kakao, VWorld, Naver). Includes Python integration patterns, API comparison table, and fix for inaccurate location display in photo pipeline (raw coords → "송파구 잠실동").

**`templates/daily-agent-script.py`** — Ready-to-use template for daily automation agents:
- Complete skeleton with collect → analyze → generate → report phases
- Telegram notification integration
- Error handling and logging
- Timeout management
- Placeholder TODO sections for customization

**How to use:**
```bash
# Copy to your project
cp ~/.hermes/skills/software-development/blog-automation/templates/daily-agent-script.py \
   /home/window11/your_project/scripts/your-agent.py

# Modify the TODO sections
# Update imports to match your project structure
# Add environment variables to .env

# Make executable
chmod +x /home/window11/your_project/scripts/your-agent.py

# Test
python /home/window11/your_project/scripts/your-agent.py

# Set up cron in Hermes
/cron create "every day at 10:00 AM"
# Then specify the script path
```
