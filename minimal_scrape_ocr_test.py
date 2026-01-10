import asyncio
import io

import pytesseract
from PIL import Image
from playwright.async_api import async_playwright

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
)


async def test_scrape_and_ocr():
    print("Starting scrape and OCR test...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.wikipedia.org")

        # Take screenshot
        screenshot = await page.screenshot(type="png")
        print("Screenshot captured")

        # Perform OCR
        image = Image.open(io.BytesIO(screenshot))
        gray_image = image.convert("L")
        ocr_text = pytesseract.image_to_string(gray_image)
        print("OCR Results:\n" + ocr_text[:500] + "...")

        await browser.close()
        print("Test completed successfully!")


asyncio.run(test_scrape_and_ocr())
