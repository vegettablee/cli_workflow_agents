# Price Detector Scraper

## Overview
A scraper that monitors TheRealReal for new listings by brand, researches comparable sold prices via sub-agents, and surfaces actionable buy signals. Integrated into an existing CLI tool that already includes an email agent.

## Scope
- **Phase 1:** TheRealReal only (Buyee deferred — harder due to Cloudflare + Yahoo Auctions JP complexity)
- **Phase 2:** Add Buyee, add "New Arrivals" feed alongside per-brand search

## Core Flow
1. Poll TheRealReal per-brand search sorted by newest — **httpx + session cookies** (no Playwright for scraping)
2. Ingest 1-3 new listings per poll cycle
3. For each listing (processed sequentially):
   a. Sub-agents fire in parallel — eBay/Grailed return sold comps
   b. **Image classification** — filter out bad/unclear comp images (pretrained model, runs locally)
   c. **Image similarity** (CLIP, runs locally) — drop comps that don't visually match the TRR listing image
   d. Verdict agent makes final verdict on remaining comps
4. Action based on verdict:
   - **Ignore** — store in log only
   - **Mark** — add to likes on personal TRR account, keep tracking price
   - **Notify immediately** — strong buy signal, alert user now

Note: TRR listings use professionally shot images and do not need classification or similarity filtering.

## Verdict Logic
- Threshold example: >30% below average sold comps = strong signal
- If insufficient research data found → route to manual review queue
- User can override sources per brand (decide which platforms to research)
- Verdict agent is a separate, dedicated agent — reinitialized per item (not kept alive across listings)

## Image Pipeline (Comp Filtering)
- Runs locally on desktop — no API costs
- **Step 1 — Image classification:** pretrained model (HuggingFace) filters out blurry, unclear, or miscategorized comp images from eBay/Grailed before similarity is run
- **Step 2 — Image similarity:** CLIP model compares remaining comp images against the TRR listing image; comps below the similarity threshold are dropped before verdict
- Threshold configurable per brand in `watchlist.json` (e.g., sneakers need tighter match than jackets)
- Only applies to eBay/Grailed sold comp images — TRR listings are professionally shot and skip this pipeline

## Research Sources (Sub-Agents)
- **eBay sold listings** — primary, free Finding API available
- **Vestiaire Collective** — better for luxury
- **Grailed** — better for streetwear
- **StockX** — sneakers + select bags only
- Source selection should be configurable per brand/category

## Brand Watchlist
- Defined in a config file (YAML or JSON)
- Per-brand optional filters: price ceiling, condition, size
- Low-volume brands: review everything, LLM just enriches
- High-volume brands: pre-filter before LLM to avoid unnecessary API calls

## Auto-Liking on TRR Account
- Playwright logs in with user credentials, clicks save/favorite
- Technically against TRR ToS — account ban risk is real but low at this volume
- Price drop notifications come from polling saved items (not a native webhook), ~30-60 min latency

## UI / Display
- Already using **Rich** for CLI output
- Stream events to console as they happen (no Textual needed)
- Display per item: image, listing details, research results per source, final verdict
- **Images:** use `chafa` for inline terminal rendering (`brew install chafa`)
  - Accepts URLs directly, no download needed
  - Falls back to `open <url>` (macOS Preview) for full-size view

```python
import subprocess

def show_image(url: str):
    subprocess.run(["chafa", url])
```

## Volume
- Target: 2-3 items per hour initially
- Low volume = low detection risk on TRR
- Experiment per brand as watchlist grows

## Storage
- SQLite for item tracking + price history
- Log table for ignored items
- Price snapshots over time to spot markdown patterns
- **Cloudflare R2** for image storage — S3-compatible, no egress fees, needed for manually reviewing listings to improve the pipeline over time

## Notifications
- Discord webhook, email, or Telegram bot for immediate alerts
- Manual review queue for low-confidence items

## Integration
- Plugs into existing CLI tool alongside email agent
- Match existing project structure and Rich console patterns when implementing

## Implementation Notes

### MVP Scope
- Ingest 1-3 listings per poll cycle (not just 1)
- Listings processed sequentially (listing 1 fully completes before listing 2 starts)
- Sub-agents within each listing run in parallel
- Async multi-listing support deferred to post-MVP

### Folder Structure
```
src/
  scraper/                          # scraper-specific display, logging, and state layer
    __init__.py
    /dashboard
      dashboard.py                    # Rich Live layout (stats, agent status, anomalies)
      tui.py                          # Textual pre-launch config screen
    /logging
      logging_manager.py              # anomaly detection, logging management
    /stats
      stats.py                        # stats generation + DB query helpers for display
    scraper_state.py                # scraper-specific session state
  automation/
    agents/
      agent_manager.py              # scraper agents added here (orchestrator, research)
      scraper/
        orchestrator_agent.py       # coordinates workflow + makes final verdict (ignore / mark / approve)
        research/
          ebay.py                   # autonomous — adjusts search queries on poor results
          grailed.py
          vestiaire.py
          stockx.py
        image/
          classifier.py             # pretrained HuggingFace model — filters bad/unclear comp images
          similarity.py             # CLIP model — drops comps that don't visually match TRR listing
    workflows/
      scraper/
        scraper_workflow.py         # scraper orchestration + sequential flow
    tools/
      scraper/
        trr_scraper.py              # TheRealReal Playwright polling
        auto_liker.py               # Playwright TRR auto-liker
    db/
      scraper/
        schema.py                   # SQLite schema (separate from email DB)
        queries.py                  # scraper DB queries
    session_state.py                # cross-workflow coordinator, initializes scraper_state on scraper startup
watchlist.json                      # brand watchlist + per-brand filters
```

### Integration Points into Existing Code
- `src/TUI/commands.py` — add `scraper` command route
- `src/automation/agents/agent_manager.py` — add scraper agent properties (same lazy-init pattern)
- `src/automation/session_state.py` — initializes `scraper_state.py` on scraper startup; stays lean, delegates all scraper-specific state to `src/scraper/scraper_state.py`

### Commands
- `scraper` — start the scraper (blocking), opens Textual config screen first, then Rich live dashboard
- `scraper pause <source>` — pause a specific research source (e.g., `scraper pause ebay`)
- `scraper continue <source>` — resume a paused source
- `scraper kill <source>` — permanently disable a source for the current session
- `scraper kill all` — full shutdown, kills orchestrator and all sub-agents

### Stop Control
- Uses a `.scraper_control` file polled by the running process
- Second terminal writes commands to this file to control the running scraper
- **Paused agent behavior:** subsequent listings in the same session treat the paused source as missing (no research contribution)
- **End of session:** if a paused agent had gathered data before being paused, that data is passed to the orchestrator; if it had nothing, it contributes nothing

### Config (watchlist.json)
- Brand watchlist with per-brand filters: price ceiling, condition, size
- Per-brand source selection (which of eBay, Grailed, Vestiaire, StockX to use)
- Sub-agent timeout: cut-off time per research conclusion (e.g., 10 minutes) — partial results get batched into verdict on timeout
- Rate limiting: items per hour

### Dashboard (Rich Live)
- Per-brand stats: `[Ignore: _ | Mark: _ | Approved: _]`
- Per-source report cards: `[eBay: fail/succeed | Grailed: fail/succeed | ...]`
- Agent status panel: shows active/paused/killed state per source
- Anomaly alerts: same product appearing repeatedly, brand with no new items in 24h
- Agent shutdown events indicated in real-time

### Pre-Launch UI (Textual)
- Config screen before scraper starts
- Sliders/toggles for: rate limits, source-to-brand assignments, per-brand filters

### TRR Scraping Approach
Playwright is avoided entirely for scraping due to bot detection (navigator.webdriver flags, CDP timing fingerprints, CAPTCHA). Instead:

- **Session cookies** extracted programmatically from a Chrome debug profile using `browser-cookie3`
- Chrome launched once manually with remote debugging for login:
  ```
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-dev-profile"
  ```
- `httpx` makes all requests with those cookies attached — server sees normal authenticated HTTP requests, no browser fingerprints

**Two-page structure handled differently:**

1. **Listings page** (e.g. brand search sorted by newest):
   - TRR embeds a JSON-LD `ItemList` block in the HTML for SEO
   - Lightweight parser (BeautifulSoup) extracts name, URL, and image for each listing
   - No LLM needed here — structure is reliable and standardized

2. **Detail page** (individual listing):
   - HTML is noisier with repeated fields and inconsistent structure
   - Lightweight parser grabs relevant chunks (description, condition, size blocks)
   - HTML chunk passed to **extraction agent** (LLM) which returns structured JSON
   - More resilient to TRR layout changes than brittle CSS selectors

**Agent pipeline per listing (all reinitialized per item — never kept alive across listings):**
```
listings page → parse JSON-LD → product URLs
   ↓ per URL
detail page → lightweight parse → HTML chunk
→ [extraction agent] structured listing fields
→ [research agent] eBay sold comps
→ [verdict agent] buy / watch / pass + reasoning
→ store in DB
```

### Credentials
- TRR login credentials stored in `.env`
- Chrome debug profile path: `$HOME/chrome-dev-profile`

### Notifications
- iMessage push notifications deferred (added last in pipeline)
- Terminal output always primary
