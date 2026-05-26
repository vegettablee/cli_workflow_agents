# Price Detector Scraper

## Overview
A scraper that monitors TheRealReal for new listings by brand, researches comparable sold prices via sub-agents, and surfaces actionable buy signals. Integrated into an existing CLI tool that already includes an email agent.

## Scope
- **Phase 1:** TheRealReal only (Buyee deferred — harder due to Cloudflare + Yahoo Auctions JP complexity)
- **Phase 2:** Add Buyee, add "New Arrivals" feed alongside per-brand search

## Core Flow
1. Poll TheRealReal per-brand search sorted by newest
2. New item found → extract listing details + image URL
3. Launch concurrent sub-agents to research sold comps
4. LLM analyzes description + comp data → verdict
5. Action based on verdict:
   - **Ignore** — store in log only
   - **Mark** — add to likes on personal TRR account, keep tracking price
   - **Notify immediately** — strong buy signal, alert user now

## Verdict Logic
- Threshold example: >30% below average sold comps = strong signal
- If insufficient research data found → route to manual review queue
- User can override sources per brand (decide which platforms to research)

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

## Notifications
- Discord webhook, email, or Telegram bot for immediate alerts
- Manual review queue for low-confidence items

## Integration
- Plugs into existing CLI tool alongside email agent
- Match existing project structure and Rich console patterns when implementing

## Implementation Notes

### MVP Scope
- Sequential flow only: poll one TRR listing → fire sub-agents → verdict → repeat
- Async multi-listing support deferred to post-MVP

### Folder Structure
```
src/
  scraper/
    __init__.py
    orchestrator.py       # scraper-specific orchestrator
    dashboard.py          # Rich Live layout (stats, agent status, anomalies)
    tui.py                # Textual pre-launch config screen
    db.py                 # SQLite schema + queries (separate from email DB)
    config.py             # watchlist.json loader
    agents/
      verdict_agent.py    # LLM: ignore / mark / approve
      research/
        ebay.py
        grailed.py
        vestiaire.py
        stockx.py
    tools/
      trr_scraper.py      # TheRealReal polling
      auto_liker.py       # Playwright auto-liker
  automation/
    agents/
      agent_manager.py    # scraper agents added here (verdict, research)
watchlist.json            # brand watchlist + per-brand filters
```

### Integration Points into Existing Code
- `src/TUI/commands.py` — add `scraper` command route
- `src/automation/agents/agent_manager.py` — add scraper agent properties (same lazy-init pattern)

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

### Credentials
- TRR login credentials stored in `.env`

### Notifications
- iMessage push notifications deferred (added last in pipeline)
- Terminal output always primary
