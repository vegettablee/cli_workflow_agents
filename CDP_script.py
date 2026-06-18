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

from patchright.async_api import async_playwright, Browser

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


async def fetch_html(url: str, browser: Browser) -> str:
    """Navigate to url in the existing browser context and return rendered HTML."""
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else await context.new_page()

    print(f"[*] Navigating to: {url}")
    await page.goto(url)
    await asyncio.sleep(3)

    html = await page.content()
    print(f"[+] Fetched {len(html):,} bytes")
    return html


async def main():
    browser = await connect()
    if not browser:
        print("[-] Not connected.")
        return
    print("[+] Connected. Keeping session alive (Ctrl+C to exit).")

    disconnected = asyncio.Event()
    browser.on("disconnected", lambda _=None: disconnected.set())

    try:
        await disconnected.wait()
        print("[-] Browser disconnected.")
    except Exception as e:
        print(f"[error] {e}")


if __name__ == "__main__":
    asyncio.run(main())
