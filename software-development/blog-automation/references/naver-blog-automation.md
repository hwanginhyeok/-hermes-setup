# Naver Blog Automation - insung-blog Project Notes

Session-specific details from the insung-blog project at `/home/window11/insung_blog/`.

## Project Overview

**인성이프로젝트** — Naver blog operations automation system. Built comment bot, auto-publishing, AI writing, and Telegram control plane.

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Comment bot (AI comments + reply automation) | Complete |
| 2 | Auto-posting to Naver Blog | Complete |
| 3 | Telegram bot + Supabase control plane | Complete |
| 4 | Feedback loop (skill improvement) | Complete |

## Service Architecture

**Two systemd-managed services:**

| Service | Description | Port |
|---------|-------------|------|
| `blog-api` | FastAPI server (uvicorn) | 8001 |
| `blog-worker` | Command queue worker (command_worker.py) | — |

**Historical service:**
- `blog-telegram.service` — Disabled since 2026-04-11 (now uses direct API calls to `src/utils/telegram_notifier.py`)

## Key Directories & Files

```
/home/window11/insung_blog/
├── src/
│   ├── icloud/              # iCloud photo collection (to be added)
│   ├── content/             # AI content generation (to be added)
│   ├── storage/
│   │   └── supabase_client.py  # Supabase integration
│   └── utils/
│       └── telegram_notifier.py  # Telegram notifications
├── api_server.py            # FastAPI endpoints (1609 lines)
├── command_worker.py        # Background task queue
├── publisher_main.py        # Naver Blog publishing
├── main.py                  # Comment bot runner
├── CLAUDE.md                # Project documentation
├── .env                     # Secrets (ICLOUD_APPLE_ID, etc. to be added)
└── scripts/
    └── icloud_daily_agent.py  # Daily automation script (to be added)
```

## Existing API Endpoints (api_server.py)

Key endpoints for automation:

- `POST /generate` — Photo path + memo → AI draft generation
- `POST /publish` — Approved draft → publish to Naver Blog
- `GET /status` — Daily comment bot status
- `POST /comment/run` — Run comment bot once
- `POST /feedback` — Feedback → update writing skills

**New endpoints to add (from icloud integration plan):**
- `POST /icloud/draft` — iCloud photos → analyze → plan → draft
- `POST /icloud/publish` — Publish specific draft to Naver Blog

## Naver Blog Authentication

**Cookie-based authentication:**
- Cookies stored in `cookies/` directory
- Use `save_cookies.py` to refresh manually when login expires
- Periodic cookie refresh required due to 2FA and session expiration

**Cookie refresh procedure:**
```bash
cd /home/window11/insung_blog
source .venv/bin/activate
python save_cookies.py
```

## Debug Scripts

Project includes several debug scripts for troubleshooting Naver Blog selectors:

- `debug_publisher.py` — DOM analysis for publishing + screenshots
- `debug_comment_selector.py` — Comment DOM analysis
- `debug_comment_write.py` — Comment writing testing
- `debug_login.py` — Login flow testing
- `test_my_blog.py` — Bot testing
- `test_public_blog.py` — Public blog testing
- `test_real_comment.py` — Real comment posting test

## Supabase Integration

**Purpose:** Control plane for bot settings, comment tracking, and run logs

**Tables:**
- `pending_comments` — Awaiting approval comments
- `bot_settings` — Bot configuration
- `bot_run_log` — Execution history

**Integration:**
```python
from src.storage.supabase_client import resolve_token_to_user_sb
```

## Telegram Integration

**Pattern:** Single-direction notifications (admin only)

**Utility:**
```python
from src.utils.telegram_notifier import send_admin_notification

await send_admin_notification("Agent run complete")
```

**Environment variables:**
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_ADMIN_CHAT_ID`

## Environment Variables

**Current `.env` setup:**
- `API_SECRET_TOKEN` — FastAPI auth
- `ANTHROPIC_API_KEY` — Claude API (for AI writing)
- `TELEGRAM_BOT_TOKEN` — Telegram bot token
- `TELEGRAM_ADMIN_CHAT_ID` — Admin chat ID
- Supabase connection details
- Naver account credentials

**To add for iCloud integration:**
```
ICLOUD_APPLE_ID=your_email@example.com
ICLOUD_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App-specific password, NOT account password
```

## Naver Blog Selectors (as of 2026-05-10)

**Note:** These selectors change frequently. Always verify with `debug_publisher.py` before using in production.

**Publish page:**
- Title: `#title` (or similar, verify)
- Content: `#content` (or similar, verify)
- File upload: `#file-upload` (or similar, verify)
- Publish button: `#publish-button` (or similar, verify)

**Comment selectors** (different from post selectors):
- Comment input: Variable, verify with `debug_comment_selector.py`
- Submit button: Variable, verify with `debug_comment_selector.py`

## Service Management Commands

```bash
# Check status
systemctl --user status blog-api blog-worker

# Restart
systemctl --user restart blog-api blog-worker

# Check logs
journalctl --user -u blog-worker -n 50 --no-pager

# Check for duplicate processes
ps aux | grep command_worker | grep -v grep | wc -l  # Should be 1

# Fix duplicates (if > 1)
systemctl --user stop blog-worker && \
  pkill -f command_worker.py 2>/dev/null && \
  sleep 2 && \
  systemctl --user start blog-worker
```

**CRITICAL:**
- **NEVER** use `pkill -f command_worker.py` directly without stopping service first — systemd auto-restart causes conflicts
- Use `systemctl --user stop blog-worker` instead
- Don't restart `blog-telegram.service` — it's intentionally disabled

## Session Start Protocol (from CLAUDE.md)

### STEP 0 — Service Status Check
```bash
systemctl --user status blog-api blog-worker | grep -E "●|Active:"
```

### STEP 1 — Task Status Check
- Read `CURRENT_TASK.md`
- Read `PREPARED_TASK.md`

### STEP 2 — Briefing Report
- Recent completions
- Today's tasks
- Blockers

### STEP 3 — Direction Discussion
- Priority alignment with user

## AI Models Used

**Writing:** Claude Haiku-4-5-20251001 (via Anthropic API)
**Persona Analysis:** Claude Sonnet (via Anthropic API)
**Comments:** Ollama gemma3:4b (local LLM)
**Vision:** Claude Sonnet (for photo analysis, to be added)

## File Naming Conventions

- Drafts: `output/draft_{timestamp}.md`
- Screenshots: `.gstack-screenshots/*.png`
- Tests: `tests/test_*.py`
- Debug scripts: `debug_*.py`
- Skills: `.claude/skills/*.md`
- Rules: `.claude/rules/*.md`

## Common Pitfalls

1. **Cookie expiration:** Naver Blog sessions expire, requiring manual refresh via `save_cookies.py`
2. **DOM changes:** Naver Blog DOM changes frequently, breaking selectors. Always test with debug scripts.
3. **Service conflicts:** Multiple worker processes cause conflicts. Check with `ps aux | grep command_worker`.
4. **Selector confusion:** Comment selectors differ from post selectors. Don't mix them up.
5. **Feed collector 20-post limit (FIXED 2026-05-13):** `src/collectors/feed_collector.py` had no scroll logic — only parsed initial page (~20 posts). Fixed by adding `_scroll_and_parse()` with dual scroll (`window.scrollTo` + `page.mouse.wheel`) and no-growth-streak detection. Default `max_posts` raised from 20 → 100. See `references/chrome-extension-nextjs-patterns.md` for full pattern.
6. **Telegram bot confusion:** Current setup is single-direction (notifications only), not interactive bot.

## Workflows

### Comment Bot Workflow
1. `main.py` fetches recent posts from Naver Blog
2. AI generates comments based on post content + persona
3. Comments stored in Supabase `pending_comments`
4. User approves via Telegram/webhook
5. Approved comments posted to Naver Blog
6. Replies tracked for engagement

### Auto-Publishing Workflow
1. User provides photos + memo via API
2. `api_server.py` calls AI (Haiku) to generate draft
3. Draft saved for review
4. User approves via Telegram/webhook
5. `publisher_main.py` uses Playwright to post to Naver Blog
6. Success notification sent via Telegram

### Planned iCloud Workflow
1. Cron triggers `icloud_daily_agent.py` daily at 10:00 AM
2. Playwright logs into iCloud.com and downloads latest photo
3. Claude Vision analyzes photo → generates plan (title, topics, tags, memo)
4. AI generates draft from plan (reusing existing `/generate` endpoint)
5. Draft + plan sent to Telegram for user review
6. User approves → `/icloud/publish` endpoint posts to Naver Blog
7. Confirmation notification sent via Telegram

## Git Workflow

```bash
# Feature branches
git checkout -b feature/icloud-integration

# Commit frequently
git add src/icloud/ tests/
git commit -m "feat: add iCloud photo client"

# PR process (via GitHub)
```

## Project Documentation Files

- `CLAUDE.md` — Project overview, rules, service management, commands
- `CURRENT_TASK.md` — Current task status
- `PREPARED_TASK.md` — Prepared tasks queue
- `FINISHED_TASK.md` — Completed tasks
- `DIFFICULTY.md` — Technical debt and challenges
- `TASK.md` — Active task details
- `docs/plans/` — Implementation plans (including icloud integration)

## Tech Stack Details

- **Python:** 3.12+ with async/await, type hints (`str | None` syntax)
- **Playwright:** Browser automation (both headless and headed modes)
- **FastAPI:** REST API with CORS, Bearer auth
- **Claude API:** Haiku (writing), Sonnet (vision, persona), via Anthropic
- **Supabase:** PostgreSQL-based backend for control plane
- **SQLite:** Local database for comments and runs
- **Next.js:** 14, app router, deployed on Vercel
- **dotenv:** Environment variable management
- **systemd:** Process management for services

## Next.js Web Platform

**Location:** `apps/web/`
**Deployment:** Vercel
**Routes:** Dashboard, blog management, comment review

**Purpose:** Web interface for managing blog automation, viewing drafts, approving comments.

## Cron Automation (Hermes)

**Pattern:** Use Hermes cronjob system for scheduling
```bash
# In Hermes TUI
/cron create "every day at 10:00 AM"
# Then specify the script to run
```

**Alternative:** Traditional Linux cron
```bash
crontab -e
# Add: 0 10 * * * cd /home/window11/insung_blog && /home/window11/.venv/bin/python scripts/icloud_daily_agent.py
```

## Testing Strategy

- **Unit tests:** `tests/` directory using pytest
- **E2E tests:** Playwright-based browser tests
- **Smoke tests:** Run debug scripts to verify selectors work
- **Integration tests:** Test full workflow from photo to publish
- **Syntax validation:** `python -c "import py_compile; py_compile.compile('file.py', doraise=True)"`

## Daily Operations Checklist

- [ ] Check service status: `systemctl --user status blog-api blog-worker`
- [ ] Review Telegram notifications
- [ ] Check for cookie expiration (run `save_cookies.py` if needed)
- [ ] Review pending comments in Supabase
- [ ] Approve/reject drafts
- [ ] Monitor rate limits and platform compliance
- [ ] Review logs for errors: `journalctl --user -u blog-worker -n 50`

## Recovery Procedures

### If blog-worker crashes:
```bash
systemctl --user stop blog-worker
systemctl --user start blog-worker
```

### If cookies expire:
```bash
cd /home/window11/insung_blog
source .venv/bin/activate
python save_cookies.py
systemctl --user restart blog-api blog-worker
```

### If selectors break:
```bash
python debug_publisher.py
# Update selectors in publisher_main.py based on output
git commit -m "fix: update Naver Blog selectors"
systemctl --user restart blog-api blog-worker
```

## Integration with External Tools

- **n8n:** Workflow automation, calls FastAPI webhooks
- **Telegram:** Single-direction notifications via `src/utils/telegram_notifier.py`
- **Supabase:** Control plane for settings and state
- **Ollama:** Local LLM for comment generation (gemma3:4b model)
- **Claude:** Remote API for writing (Haiku) and vision (Sonnet)
