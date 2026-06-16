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

from patchright.async_api import async_playwright

from src.scraper.url_builder.builder import catalog_url

CATALOG_DIR = Path("db/html/catalog")


async def download_catalog(brand: str) -> Path:
    async with async_playwright() as p:
        print("[*] Connecting to Chrome on port 9222...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")

        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        url = catalog_url(brand)
        print(f"[*] Navigating to: {url}")
        await page.goto(url)
        # await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)

        html = await page.content()

        today = date.today().strftime("%Y-%m-%d")
        filename = CATALOG_DIR / f"{brand.replace(' ', '_')}_{today}.html"
        filename.write_text(html, encoding="utf-8")

        print(f"[+] Saved {len(html):,} bytes -> {filename}")
        await browser.close()
        return filename


if __name__ == "__main__":
    brand = input("Brand (e.g. undercover): ").strip().lower()
    asyncio.run(download_catalog(brand))
