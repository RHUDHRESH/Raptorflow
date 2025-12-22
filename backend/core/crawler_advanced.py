import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin, urlparse
import logging

class AdvancedCrawler:
    """
    Industrial-grade Crawler with Semantic extraction.
    Designed for SOTA Agentic Research.
    """
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.headers = {"User-Agent": "RaptorFlowResearch/3.0 (Enterprise grade)"}

    async def scrape_semantic(self, url: str) -> Optional[Dict[str, str]]:
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(url, timeout=20) as response:
                        if response.status != 200: return None
                        html = await response.text()
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 1. Extract Meta
                        title = soup.title.string if soup.title else ""
                        description = ""
                        meta_desc = soup.find("meta", attrs={"name": "description"})
                        if meta_desc: description = meta_desc.get("content", "")

                        # 2. Main Content Heuristic (Article extraction)
                        # We look for <article>, <main> or the div with most paragraphs
                        main_content = soup.find('main') or soup.find('article')
                        if not main_content:
                            # Heuristic: Find the div with the most p tags
                            divs = soup.find_all('div')
                            main_content = max(divs, key=lambda d: len(d.find_all('p'))) if divs else soup

                        # 3. Clean and return
                        for junk in main_content(["script", "style", "nav", "footer", "aside", "header"]):
                            junk.decompose()
                            
                        text = re.sub(r'\n+', '\n', main_content.get_text(separator=' ')).strip()
                        
                        return {
                            "url": url,
                            "title": title,
                            "description": description,
                            "content": text[:15000] # Industrial safety cap
                        }
            except Exception as e:
                logging.error(f"Failed to crawl {url}: {e}")
                return None

    async def batch_crawl(self, urls: List[str]) -> List[Dict[str, str]]:
        tasks = [self.scrape_semantic(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]
