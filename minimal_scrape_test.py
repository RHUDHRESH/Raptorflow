import asyncio

from playwright.async_api import async_playwright


async def test_scrape():
    print("Starting scrape test...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.wikipedia.org")

        # Get page title
        title = await page.title()
        print(f"Page title: {title}")

        # Take screenshot
        await page.screenshot(path="scrape_test_screenshot.png")
        print("Screenshot saved to scrape_test_screenshot.png")

        await browser.close()
        print("Scrape test completed successfully!")


asyncio.run(test_scrape())
