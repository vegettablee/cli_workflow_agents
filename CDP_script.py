"""
TRR catalog downloader — patchright CDP approach.

Before running:
    1. Launch Chrome with remote debugging:
        full terminal command(run from MAIN REPO DIRECTORY):
       open -a "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir=$HOME/chrome-dev-profile
    2. Log into therealreal.com in that window.
    3. Run this script.

Dependencies:
    pip install patchright
    patchright install chrome
"""

import asyncio
from datetime import date
from pathlib import Path

from patchright.async_api import async_playwright, Browser

from src.scraper.url_builder.builder import catalog_url

CATALOG_DIR = Path("db/html/catalog")
CDP_URL = "http://localhost:9222"


async def connect() -> Browser | None:
    try:
        p = await async_playwright().start()
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        print(f"[*] Connected to Chrome on {CDP_URL}")
        return browser
    except Exception as e:
        print(f"[error] Could not connect to Chrome: {e}")
        return None


async def is_connected() -> bool:
    try:
        p = await async_playwright().start()
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        await browser.close()
        return True
    except Exception:
        return False


async def fetch_html(url: str, browser: Browser) -> Path | None:
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else await context.new_page()

    print(f"[*] Navigating to: {url}")
    await page.goto(url)
    await asyncio.sleep(3)

    html = await page.content()

    today = date.today().strftime("%Y-%m-%d")
    filename = CATALOG_DIR / f"{brand.replace(' ', '_')}_{today}.html"
    filename.write_text(html, encoding="utf-8")

    print(f"[+] Saved {len(html):,} bytes -> {filename}")
    return filename


async def main():
    browser = await connect()
    if not browser:
        return

    brand = input("Brand (e.g. undercover): ").strip().lower()
    await fetch_catalog(brand, browser)
    await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
