"""
TRR Playwright test script — CDP connect approach.

Before running this script:
    1. Launch Chrome with remote debugging:
       /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-dev-profile"
    2. Log in to therealreal.com manually in that window.
    3. Navigate to the home page.
    4. Then run this script.

Setup (first time only):
    pip install playwright
    playwright install chromium
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        print("[*] Connecting to Chrome on port 9222...")
        print("    Make sure Chrome is running with: --remote-debugging-port=9222 --user-data-dir=\"$HOME/chrome-dev-profile\"")

        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            print("[error] Could not connect. Is Chrome running with --remote-debugging-port=9222?")
            return

        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        current_url = page.url
        print(f"[*] Connected. Current page: {current_url}")

        if "therealreal.com" not in current_url:
            print("[error] You must be on therealreal.com before running this script.")
            print("        Navigate to the home page in Chrome and try again.")
            await browser.close()
            return

        loop = asyncio.get_event_loop()
        confirm = await loop.run_in_executor(
            None,
            lambda: input("Are you logged in and on the home page? (y/n): ").strip().lower()
        )
        if confirm != "y":
            print("[abort] Exiting. Get logged in and on the home page first, then re-run.")
            await browser.close()
            return

        print("[confirmed] Proceeding...")


        ###### PLAYWRIGHT SCRIPT ######


        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
