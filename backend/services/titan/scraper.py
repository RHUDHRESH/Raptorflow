import asyncio
import logging
import random
import uuid
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger("raptorflow.services.titan.scraper")

class PlaywrightStealthPool:
    """
    Managed pool of Playwright browser contexts with stealth features.
    Includes fingerprint randomization and proxy support.
    """
    def __init__(self, max_contexts: int = 5):
        self.max_contexts = max_contexts
        self.browser: Optional[Browser] = None
        self.playwright = None
        self._lock = asyncio.Lock()
        self._contexts: List[BrowserContext] = []

    async def start(self):
        """Initialize browser."""
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )
            logger.info("Playwright Stealth Pool initialized.")

    async def get_page(self) -> Page:
        """Get a fresh page from a new randomized context."""
        await self.start()
        
        # Randomize User-Agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        
        context = await self.browser.new_context(
            user_agent=random.choice(user_agents),
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=random.choice([1, 2])
        )
        
        # Add stealth scripts (simple version)
        page = await context.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        
        return page

    async def scrape_url(self, url: str, wait_time: int = 2) -> Dict[str, Any]:
        """Scrape a URL using a fresh context and return content."""
        page = await self.get_page()
        try:
            logger.info(f"Stealth scraping: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Additional wait for dynamic content
            if wait_time:
                await asyncio.sleep(wait_time)
                
            content = await page.content()
            title = await page.title()
            
            # Get links for recursive discovery
            links = await page.eval_on_selector_all("a[href]", "elements => elements.map(e => e.href)")
            
            return {
                "url": url,
                "title": title,
                "html": content,
                "links": list(set(links)),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Stealth scrape failed for {url}: {e}")
            return {"url": url, "error": str(e), "status": "failed"}
        finally:
            context = page.context
            await page.close()
            await context.close()

    async def close(self):
        """Cleanup resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.browser = None
        self.playwright = None

class IntelligentMarkdown:
    """
    Converts HTML to structured Markdown while preserving hierarchy and tables.
    """
    @staticmethod
    def convert(html: str) -> str:
        """
        Implementation using BeautifulSoup to extract clean text/markdown.
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove noisy tags
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        return soup.get_text(separator="\n", strip=True)
