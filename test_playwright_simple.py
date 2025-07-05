#!/usr/bin/env python3
import asyncio
import os

from playwright.async_api import async_playwright


async def test_playwright():
    print("🚀 Starting simple Playwright test...")

    try:
        print("1. Starting Playwright...")
        playwright = await async_playwright().start()
        print("✅ Playwright started successfully")

        print("2. Launching browser...")
        browser = await playwright.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        print("✅ Browser launched successfully")

        print("3. Creating context...")
        context = await browser.new_context()
        print("✅ Context created successfully")

        print("4. Creating page...")
        page = await context.new_page()
        print("✅ Page created successfully")

        print("5. Setting timeout...")
        await page.set_default_timeout(10000)
        print("✅ Timeout set successfully")

        print("6. Navigating to a simple page...")
        await page.goto("https://example.com")
        print("✅ Navigation successful")

        print("7. Getting page title...")
        title = await page.title()
        print(f"✅ Page title: {title}")

        print("8. Closing browser...")
        await browser.close()
        print("✅ Browser closed successfully")

        print("9. Stopping Playwright...")
        await playwright.stop()
        print("✅ Playwright stopped successfully")

        print("🎉 All tests passed! Playwright is working correctly.")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        print(f"Exception details:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    # Set the browsers path
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/home/king/.cache/ms-playwright"

    result = asyncio.run(test_playwright())
    if result:
        print("✅ Test completed successfully")
    else:
        print("❌ Test failed")
