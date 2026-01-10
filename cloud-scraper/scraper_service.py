"""
Production-ready Cloud Run Scraper Service
Enhanced with Playwright, OCR, color extraction, and compliance
"""

import asyncio
import io
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx
import structlog
from bs4 import BeautifulSoup
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from playwright.async_api import async_playwright

# Try to import OCR, but make it optional
try:
    import pytesseract

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ Tesseract not available - OCR functionality disabled")

# Google Cloud imports - will be mocked for local testing
try:
    from google.cloud import pubsub_v1, storage
    from google.cloud.logging import Client as LoggingClient

    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    print("⚠️ Google Cloud libraries not available - using local mode")

# Configure structured logging
try:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
except Exception as e:
    print(f"⚠️ Structlog configuration failed: {e}")
    # Fallback to basic logging
    logging.basicConfig(level=logging.INFO)
    structlog.configure(processors=[structlog.dev.ConsoleRenderer()])

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(title="Raptorflow Cloud Scraper", version="1.0.0")

# Initialize Google Cloud clients
storage_client = None
publisher = None
logging_client = None

# Check if we're in local mode
LOCAL_MODE = os.getenv("LOCAL_MODE", "false").lower() == "true"

if LOCAL_MODE or not GOOGLE_CLOUD_AVAILABLE:
    print("🔧 Running in local mode - using mock services")

    # Create mock clients for local testing
    class MockStorageClient:
        def __init__(self):
            self.local_storage = {}

        def bucket(self, name):
            return MockBucket(name, self.local_storage)

    class MockBucket:
        def __init__(self, name, storage_dict):
            self.name = name
            self.storage = storage_dict

        def blob(self, filename):
            return MockBlob(filename, self.name, self.storage)

        def list_blobs(self, prefix=None):
            return []

    class MockBlob:
        def __init__(self, filename, bucket_name, storage_dict):
            self.filename = filename
            self.bucket_name = bucket_name
            self.storage = storage_dict
            self.public_url = f"http://localhost:8080/mock-storage/{filename}"

        def upload_from_string(self, content, content_type=None):
            key = f"{self.bucket_name}/{self.filename}"
            self.storage[key] = {
                "content": content,
                "content_type": content_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            print(f"📁 Local storage: Saved {key} ({len(content)} bytes)")

        def download_as_text(self):
            key = f"{self.bucket_name}/{self.filename}"
            if key in self.storage:
                return self.storage[key]["content"]
            raise FileNotFoundError(f"File {self.filename} not found")

        def exists(self):
            key = f"{self.bucket_name}/{self.filename}"
            return key in self.storage

        def make_public(self):
            pass

    class MockPubSubClient:
        def __init__(self):
            self.messages = []

        def topic_path(self, project_id, topic_name):
            return f"projects/{project_id}/topics/{topic_name}"

        def publish(self, topic_path, data):
            message_id = f"msg-{len(self.messages)}"
            self.messages.append(
                {
                    "id": message_id,
                    "topic": topic_path,
                    "data": data,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            print(f"📨 Local Pub/Sub: Published message to {topic_path}")

            class MockFuture:
                def result(self):
                    return message_id

            return MockFuture()

    class MockLoggingClient:
        def setup_logging(self):
            print("📝 Local logging: Setup complete")

    # Use mock clients
    storage_client = MockStorageClient()
    publisher = MockPubSubClient()
    logging_client = MockLoggingClient()
    logging_client.setup_logging()

else:
    # Use real Google Cloud clients
    try:
        storage_client = storage.Client()
        publisher = pubsub_v1.PublisherClient()
        logging_client = LoggingClient()
        logging_client.setup_logging()
        logger.info("Google Cloud clients initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize Google Cloud clients", error=str(e))
        print("⚠️ Falling back to local mode due to Google Cloud initialization failure")
        LOCAL_MODE = True

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "raptorflow-481505")
BUCKET_NAME = os.getenv("BUCKET_NAME", "raptorflow-scraped-data")
TOPIC_NAME = os.getenv("TOPIC_NAME", "scraping-results")
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10000000"))  # 10MB


class EnhancedScraper:
    """Enhanced scraper with Playwright, OCR, and color extraction"""

    def __init__(self):
        self.timeout = 30000  # 30 seconds
        self.user_agent = "RaptorflowCloudScraper/1.0"

    async def scrape_with_playwright(
        self, url: str, user_id: str, legal_basis: str = "user_request"
    ) -> Dict[str, Any]:
        """Main scraping method using Playwright"""
        start_time = datetime.now(timezone.utc)

        try:
            async with async_playwright() as p:
                # Launch browser with optimized settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                    ],
                )

                context = await browser.new_context(
                    user_agent=self.user_agent, viewport={"width": 1920, "height": 1080}
                )

                page = await context.new_page()

                # Navigate and wait for content
                await page.goto(url, wait_until="networkidle", timeout=self.timeout)
                await page.wait_for_timeout(3000)  # Wait for JS execution

                # Extract basic content
                title = await page.title()
                content = await page.content()

                # Extract readable text
                readable_text = await page.evaluate("document.body.innerText")

                # Extract brand colors and styling
                styles = await page.evaluate(
                    """
                    () => {
                        const computed = getComputedStyle(document.body);
                        const links = document.querySelectorAll('link[rel="stylesheet"]');
                        const meta = document.querySelector('meta[name="theme-color"]');

                        return {
                            background: computed.backgroundColor,
                            color: computed.color,
                            accent: computed.accentColor,
                            theme_color: meta ? meta.content : null,
                            font_family: computed.fontFamily,
                            stylesheet_count: links.length
                        };
                    }
                """
                )

                # Extract structured data
                structured_data = await page.evaluate(
                    """
                    () => {
                        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                        return Array.from(scripts).map(script => {
                            try {
                                return JSON.parse(script.textContent);
                            } catch (e) {
                                return null;
                            }
                        }).filter(Boolean);
                    }
                """
                )

                # Take screenshot for OCR
                screenshot = await page.screenshot(full_page=True, type="png")

                # Perform OCR on screenshot
                ocr_text = await self._perform_ocr(screenshot)

                # Extract images
                images = await page.evaluate(
                    """
                    () => {
                        const imgs = Array.from(document.querySelectorAll('img'));
                        return imgs.slice(0, 10).map(img => ({
                            src: img.src,
                            alt: img.alt || '',
                            width: img.width,
                            height: img.height
                        }));
                    }
                """
                )

                await browser.close()

                # Parse HTML with BeautifulSoup for additional extraction
                soup = BeautifulSoup(content, "html.parser")

                # Extract meta tags
                meta_tags = {}
                for meta in soup.find_all("meta"):
                    name = meta.get("name") or meta.get("property")
                    content = meta.get("content")
                    if name and content:
                        meta_tags[name] = content

                # Create result
                result = {
                    "url": url,
                    "user_id": user_id,
                    "timestamp": start_time.isoformat(),
                    "title": title,
                    "content_length": len(content),
                    "readable_text": readable_text[:5000],  # Truncate for storage
                    "styles": styles,
                    "structured_data": structured_data,
                    "meta_tags": meta_tags,
                    "images": images,
                    "ocr_text": ocr_text[:2000],  # Truncate for storage
                    "screenshot_url": await self._upload_screenshot(screenshot, url),
                    "legal_basis": legal_basis,
                    "processing_time": (
                        datetime.now(timezone.utc) - start_time
                    ).total_seconds(),
                    "status": "success",
                }

                # Store result in Cloud Storage
                await self._store_result(result)

                # Publish to Pub/Sub
                await self._publish_result(result)

                return result

        except Exception as e:
            logger.error("Scraping failed", url=url, user_id=user_id, error=str(e))
            return {
                "url": url,
                "user_id": user_id,
                "timestamp": start_time.isoformat(),
                "status": "error",
                "error": str(e),
                "processing_time": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
            }

    async def _perform_ocr(self, screenshot_bytes: bytes) -> str:
        """Perform OCR on screenshot"""
        if not OCR_AVAILABLE:
            logger.info("OCR not available - skipping text extraction from images")
            return ""

        try:
            image = Image.open(io.BytesIO(screenshot_bytes))
            # Convert to grayscale for better OCR
            gray_image = image.convert("L")
            # Perform OCR
            text = pytesseract.image_to_string(gray_image, lang="eng")
            return text.strip()
        except Exception as e:
            logger.warning(
                "OCR failed - Tesseract not available or other error", error=str(e)
            )
            return ""

    async def _upload_screenshot(self, screenshot_bytes: bytes, url: str) -> str:
        """Upload screenshot to Cloud Storage"""
        try:
            bucket = storage_client.bucket(BUCKET_NAME)
            filename = f"screenshots/{hash(url)}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.png"
            blob = bucket.blob(filename)
            blob.upload_from_string(screenshot_bytes, content_type="image/png")
            blob.make_public()
            return blob.public_url
        except Exception as e:
            logger.warning("Failed to upload screenshot", error=str(e))
            return ""

    async def _store_result(self, result: Dict[str, Any]) -> str:
        """Store scraping result in Cloud Storage"""
        try:
            bucket = storage_client.bucket(BUCKET_NAME)
            filename = f"results/{result['user_id']}/{hash(result['url'])}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            blob = bucket.blob(filename)
            blob.upload_from_string(
                json.dumps(result, default=str), content_type="application/json"
            )
            return filename
        except Exception as e:
            logger.warning("Failed to store result", error=str(e))
            return ""

    async def _publish_result(self, result: Dict[str, Any]) -> None:
        """Publish result to Pub/Sub"""
        try:
            topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
            data = json.dumps(result, default=str).encode("utf-8")
            future = publisher.publish(topic_path, data)
            logger.info("Result published to Pub/Sub", message_id=future.result())
        except Exception as e:
            logger.warning("Failed to publish result", error=str(e))


# Initialize scraper
scraper = EnhancedScraper()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/scrape")
async def scrape_url(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """Main scraping endpoint"""
    url = request.get("url")
    user_id = request.get("user_id")
    legal_basis = request.get("legal_basis", "user_request")

    if not url or not user_id:
        raise HTTPException(status_code=400, detail="URL and user_id are required")

    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL")

    # Check content length
    if len(url) > MAX_CONTENT_LENGTH:
        raise HTTPException(status_code=400, detail="URL too long")

    # Log the request
    logger.info("Scraping request received", url=url, user_id=user_id)

    # Perform scraping
    result = await scraper.scrape_with_playwright(url, user_id, legal_basis)

    return JSONResponse(content=result)


@app.get("/scrape/{task_id}")
async def get_scrape_result(task_id: str):
    """Get scraping result by task ID"""
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"results/{task_id}.json")

        if not blob.exists():
            raise HTTPException(status_code=404, detail="Result not found")

        content = blob.download_as_text()
        result = json.loads(content)

        return JSONResponse(content=result)

    except Exception as e:
        logger.error("Failed to get result", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve result")


@app.get("/stats")
async def get_scraping_stats():
    """Get scraping statistics"""
    try:
        bucket = storage_client.bucket(BUCKET_NAME)

        # Count results
        blobs = list(bucket.list_blobs(prefix="results/"))
        total_results = len(blobs)

        # Count screenshots
        screenshots = list(bucket.list_blobs(prefix="screenshots/"))
        total_screenshots = len(screenshots)

        return {
            "total_results": total_results,
            "total_screenshots": total_screenshots,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error("Failed to get stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
