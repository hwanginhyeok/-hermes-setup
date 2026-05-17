# Chrome Extension + Next.js Integration Patterns

> Patterns from insung-blog project (2026-05-13 session). Covers version checking, infinite scroll handling, and extension-driven discovery.

---

## 1. Extension Version Checking (middleware-based)

**Problem:** Old extension versions cause errors but users get no update prompt.

**Solution:** Middleware intercepts ALL `/api/ext/*` routes in one place — no per-route modification needed.

### Architecture

```
Extension (background.js)
  → every apiFetch() sends X-Ext-Version header (from manifest)
  → reads X-Ext-Outdated response header
  → sets chrome.storage.local { extOutdated: true }
  → popup.js + ExtErrorBanner.tsx read flag → show outdated UI

Next.js (middleware.ts)
  → matcher includes /api/ext/:path*
  → reads X-Ext-Version from request
  → if semver < MIN_EXT_VERSION → sets X-Ext-Outdated + X-Ext-Min-Version headers
  → does NOT block the request (compatibility with old versions)
```

### Key Code Patterns

**background.js — version constant + header injection:**
```javascript
const EXT_VERSION = chrome.runtime.getManifest().version;

// In apiFetch:
headers: {
  'Authorization': `Bearer ${token}`,
  'X-Ext-Version': EXT_VERSION,
}

// After response:
if (resp.headers.get('X-Ext-Outdated') === 'true') {
  chrome.storage.local.set({ extOutdated: true, extMinVersion: resp.headers.get('X-Ext-Min-Version') });
}
```

**middleware.ts — semver check:**
```typescript
function cmpSemver(a: string, b: string): number {
  const pa = a.split(".").map(Number);
  const pb = b.split(".").map(Number);
  for (let i = 0; i < 3; i++) {
    if ((pa[i] || 0) < (pb[i] || 0)) return -1;
    if ((pa[i] || 0) > (pb[i] || 0)) return 1;
  }
  return 0;
}

// In middleware handler for /api/ext/*:
if (extVer && cmpSemver(extVer, MIN_EXT_VERSION) < 0) {
  res.headers.set("X-Ext-Outdated", "true");
}
res.headers.set("X-Ext-Min-Version", MIN_EXT_VERSION);
```

**Pitfall:** Do NOT modify 13+ individual route files. Use middleware instead.
**Pitfall:** `chrome.runtime.getManifest().version` must be called in background.js context, not in content scripts.

---

## 2. Infinite Scroll Handling (wheel events + network capture)

**Problem:** Naver FeedList ignores `window.scrollTo()` — infinite scroll only triggers on real user wheel/scroll events.

**Solution:** Three-phase approach — network capture + wheel event dispatch + API URL logging.

### Phase 1: Network Capture (install in page context)

```javascript
function installNetworkCapture() {
  if (window.__feedApiUrls) return;
  window.__feedApiUrls = [];
  const origFetch = window.fetch;
  window.fetch = function(...args) {
    const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
    if (url.includes('Feed') || url.includes('PostList')) {
      window.__feedApiUrls.push({ url, timestamp: Date.now() });
    }
    return origFetch.apply(this, args);
  };
  // Same for XMLHttpRequest.prototype.open
}
```

### Phase 2: Scroll Trigger (CORRECTED 2026-05-14)

**CRITICAL:** Initial implementation used `dispatchEvent(new WheelEvent(...))` as the primary method. This does NOT work — Naver ignores synthetic wheel events. `window.scrollTo()` IS the primary method that works.

**Why wheel-only failed (2026-05-14 debugging):**
- `dispatchEvent(new WheelEvent(...))` alone → 0 actual scroll, posts stayed at ~19
- `window.scrollTo(0, scrollHeight)` → immediate scroll, posts jumped to 69+ in testing
- Verified with `browser_scroll` (Playwright-level scroll) vs `triggerNativeScroll` (wheel-only) on the same page

**Correct implementation:**
```javascript
function triggerNativeScroll() {
  // ── 1. window.scrollTo FIRST (the only thing that actually scrolls) ──
  const prevY = window.scrollY;
  window.scrollTo(0, document.documentElement.scrollHeight);

  // ── 2. Wheel event as SUPPLEMENT (some SPAs listen for wheel to trigger lazy-load) ──
  const wheelOpts = { deltaY: 3000, deltaMode: 0, bubbles: true, cancelable: true };
  document.dispatchEvent(new WheelEvent('wheel', wheelOpts));
  document.body.dispatchEvent(new WheelEvent('wheel', wheelOpts));

  // ── 3. scrollTop on overflow containers (masonry, etc.) ──
  const containers = [
    document.querySelector('[class*="masonry"]'),
    document.querySelector('#container'),
    document.querySelector('.feed_area'),
    document.scrollingElement,
  ].filter(Boolean);
  for (const el of containers) {
    if (el.scrollHeight > el.clientHeight + 10) {
      el.scrollTop = el.scrollHeight;
    }
  }

  return { scrolled: window.scrollY > prevY, prevY, newY: window.scrollY };
}
```

**CRITICAL: Add sleep AFTER scrollTo, BEFORE MutationObserver installation.** Without this, MutationObserver may miss the DOM changes because scrollTo + lazy-load render completes before observer is attached:

```javascript
// In scroll loop:
const [scrollInfo] = await chrome.scripting.executeScript({
  target: { tabId: tab.id },
  func: triggerNativeScroll,
});
console.log(`[FEED-SCROLL] scroll=${JSON.stringify(scrollInfo?.result)}`);
await sleep(1500);  // CRITICAL: wait for lazy-load render BEFORE observer
// THEN install MutationObserver...
```

### Phase 3: Capture API URLs for Future Optimization

After scrolling, extract captured URLs and store in `chrome.storage.local`. On next run, can skip DOM parsing entirely and call API directly.

**Pitfall:** Wheel-only `dispatchEvent` does NOT trigger Naver's lazy-load. `window.scrollTo()` is the working method.
**Pitfall:** Must `await sleep(1500+)` between scrollTo and MutationObserver to catch DOM changes.
**Pitfall:** `dispatchEvent(new WheelEvent(...))` only works when injected via `chrome.scripting.executeScript` — not from popup or service worker directly.

### Playwright Server-Side Feed Collector (`feed_collector.py`)

**Problem (2026-05-13):** Playwright-based `src/collectors/feed_collector.py` had NO scroll logic — only parsed initial page load. Naver FeedList shows ~20 posts initially, so only 20 posts were ever collected despite `max_posts=100` being passed by `feed_commenter.py`.

**Root cause:** `_parse_feed()` ran a single `page.evaluate()` to extract links, then returned. No `window.scrollTo()` or `page.mouse.wheel()` calls.

**Fix — `_scroll_and_parse()` pattern:**
```python
async def _scroll_and_parse(page, my_blog_ids, max_posts):
    seen: set[str] = set()
    all_posts: list[dict] = []
    no_growth_streak = 0

    # Initial parse
    links = await _parse_all_links(page)
    new_posts = _extract_posts_from_links(links, my_blog_ids, max_posts, seen)
    all_posts.extend(new_posts)

    for round_num in range(1, MAX_SCROLL_ROUNDS + 1):
        if len(all_posts) >= max_posts:
            break

        # Dual scroll (Playwright supports both, unlike extension)
        await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        await asyncio.sleep(SCROLL_PAUSE_SEC)
        await page.mouse.wheel(0, 800)  # Extra push for lazy-load
        await asyncio.sleep(1.0)

        links = await _parse_all_links(page)
        new_posts = _extract_posts_from_links(links, my_blog_ids, max_posts, seen)

        if not new_posts:
            no_growth_streak += 1
            if no_growth_streak >= NO_GROWTH_LIMIT:  # Default 3
                break
        else:
            no_growth_streak = 0
            all_posts.extend(new_posts)

    return all_posts[:max_posts]
```

**Key differences from extension scroll:**
| Aspect | Extension (background.js) | Playwright (feed_collector.py) |
|--------|--------------------------|-------------------------------|
| `scrollTo()` | Ignored by Naver SPA | Works (Playwright is a real browser) |
| Wheel events | `dispatchEvent(new WheelEvent(...))` via `executeScript` | `page.mouse.wheel(0, 800)` (native) |
| Growth detection | `allPosts.length` comparison | `no_growth_streak` counter (3 consecutive empty = stop) |
| Max rounds | `MAX_SCROLL_ROUNDS = 20` | `MAX_SCROLL_ROUNDS = 15` |
| Pause | `sleep(2000)` | `SCROLL_PAUSE_SEC = 2.0` + extra 1.0s after wheel |

**Pitfall:** `max_posts` default was 20 in `feed_collector.py` — changed to 100. The caller (`feed_commenter.py`) already passed 100 but the collector's single-parse-only behavior was the bottleneck.
**Pitfall:** `_extract_posts_from_links()` must check `len(text) <= 5` — Naver feed includes thumbnail `<a>` tags with empty/short text that match the blog URL pattern but are not real posts.

---

## 3. Extension-Driven Discovery (search → candidates)

**Problem:** Server-side Naver search requires API keys + cookies. Extension has direct browser access (no auth needed for search.naver.com).

**Solution:** Extension performs search, extracts blogger IDs, sends candidates to server API.

### Architecture

```
Extension (background.js)
  → discoverBloggersByKeywords(keywords)
  → for each keyword: open search.naver.com tab
  → parseSearchResultsInPage() extracts blog IDs from href patterns
  → POST /api/ext/discover/candidates { bloggers: [...] }

Server (route.ts)
  → Deduplicate against neighbor_candidates + neighbors tables
  → upsert new candidates with relevance_score
  → Return { accepted, skipped }
```

### Search Result Parsing (in-page)

```javascript
function parseSearchResultsInPage() {
  const links = document.querySelectorAll('a[href]');
  const seen = new Set();
  const bloggers = [];
  for (const a of links) {
    const match = a.getAttribute('href')?.match(/blog\.naver\.com\/([a-zA-Z0-9_-]+)\/(\d{10,})/);
    if (!match || seen.has(match[1])) continue;
    seen.add(match[1]);
    bloggers.push({ blog_id: match[1], title: (a.textContent || '').trim().slice(0, 200) });
  }
  return bloggers;
}
```

### Anti-Bot Measures
- Max 5 keywords per run
- 2-4 second random delay between keywords
- Tab created/destroyed per keyword (fresh context)
- `credentials: 'omit'` on direct fetches

**Pitfall:** `search.naver.com` results are SPA-rendered. Must wait 3s after `waitForTabLoad` for JS hydration.
**Pitfall:** Dedup MUST check both `neighbor_candidates` AND `neighbors` tables — a blogger might already be an approved neighbor.

---

## General Pattern: Middleware > Per-Route Modification

When adding cross-cutting concerns to ext API routes (version checking, rate limiting, logging), prefer Next.js `middleware.ts` over modifying individual route files:

```typescript
// middleware.ts
if (pathname.startsWith("/api/ext")) {
  const res = NextResponse.next();
  // Add headers, check versions, log, etc.
  return res;
}
// matcher: [...otherPaths, "/api/ext/:path*"]
```

This avoids touching 13+ route files and ensures all future routes are covered automatically.

---

## 4. API Path Convention: `/comment/*` (singular) — Critical Pitfall

**Bug found 2026-05-14:** Extension `background.js` used `/comments/*` (plural) but server `api_server.py` registers `/comment/*` (singular). Every result-reporting call was silently 404-ing via `.catch(()=>{})`, causing:

1. **Lock succeeds** → status becomes `posting`
2. **Result report fails** (404, caught silently) → status stays `posting` forever
3. **50 rows stuck in `posting` state** — invisible to `ready-to-post` (which filters `approved`)
4. **Unlock on error also fails** → no recovery path

### Correct API path mapping

| Extension call (WRONG) | Server endpoint (CORRECT) |
|------------------------|--------------------------|
| `/comments/lock` | `/comment/lock-for-posting` |
| `/comments/${id}` POST | `/comment/post-result/${id}` |
| `/comments/${id}` DELETE | `/comment/unlock/${id}` |
| `/comments/ready` | `/comment/ready-to-post` |

### Prevention rules

1. **Path convention:** Server uses `/comment/*` (singular). Always match.
2. **Never `.catch(()=>{})` on critical state changes** — at minimum log the error.
3. **Test the full lifecycle:** lock → post → report result → unlock. A single 404 in the chain breaks state.
4. **Add finally-cleanup:** In `runPostingLoop`, the `finally` block must call `/comment/unlock-all` for any comments still in `posting` state (interrupted loop, crash, etc.).
5. **Login guard before posting:** Check `getNaverLoginStatus()` before entering the posting loop. Without login, `tryPost()` returns `notLoggedIn` but by then lock is already acquired.

### Posting state machine

```
pending → approved → posting → posted/failed
                  ↑                    ↑
                  └── unlock-all ──────┘  (finally cleanup)
```

- `approved` → `posting`: `/comment/lock-for-posting`
- `posting` → `posted`: `/comment/post-result/{id}` (success=true)
- `posting` → `failed`: `/comment/post-result/{id}` (success=false)
- `posting` → `approved`: `/comment/unlock-all` (cleanup orphaned locks)
- **Orphaned `posting` rows** → use SQL: `UPDATE pending_comments SET status='approved' WHERE status='posting'` (may hit UNIQUE constraint if a newer row exists for same post_url — in that case, DELETE the orphan instead)
