import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from tools.scraper import FirecrawlScraperTool, JinaReaderTool

logger = logging.getLogger("raptorflow.crawler_pipeline")


@dataclass(frozen=True)
class CrawlPolicy:
    max_concurrent: int = 5
    timeout: int = 15
    max_content_length: int = 10000
    user_agent: str = "RaptorFlowResearch/3.0 (Industrial grade)"


@dataclass(frozen=True)
class ScrapeResult:
    url: str
    domain: str
    content: str
    title: str = ""
    source: str = ""


@dataclass(frozen=True)
class NormalizedContent:
    title: str
    content: str


class DiscoveryStage:
    def discover(self, urls: Iterable[str]) -> List[str]:
        seen = set()
        unique_urls = []
        for url in urls:
            if not url or url in seen:
                continue
            seen.add(url)
            unique_urls.append(url)
        return unique_urls


class FetchStage:
    async def fetch_html(
        self, url: str, session: aiohttp.ClientSession, policy: CrawlPolicy
    ) -> Optional[str]:
        try:
            async with session.get(url, timeout=policy.timeout) as response:
                if response.status != 200:
                    logger.warning(
                        "Failed to fetch %s: Status %s", url, response.status
                    )
                    return None
                return await response.text()
        except Exception as exc:
            logger.error("Error fetching %s: %s", url, exc)
            return None


class NormalizeStage:
    def normalize_html(self, html: str, policy: CrawlPolicy) -> NormalizedContent:
        soup = BeautifulSoup(html, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = "\n".join(chunk for chunk in chunks if chunk)
        return NormalizedContent(
            title=title, content=self.normalize_content(content, policy)
        )

    def normalize_content(self, content: str, policy: CrawlPolicy) -> str:
        cleaned = re.sub(r"\n{3,}", "\n\n", content).strip()
        if policy.max_content_length:
            return cleaned[: policy.max_content_length]
        return cleaned


class ExtractStage:
    def __init__(
        self,
        firecrawl: Optional[FirecrawlScraperTool] = None,
        jina: Optional[JinaReaderTool] = None,
    ):
        self.firecrawl = firecrawl or FirecrawlScraperTool()
        self.jina = jina or JinaReaderTool()

    async def extract(
        self,
        url: str,
        session: aiohttp.ClientSession,
        policy: CrawlPolicy,
        fetch_stage: FetchStage,
        normalize_stage: NormalizeStage,
        semaphore: asyncio.Semaphore,
    ) -> Optional[ScrapeResult]:
        async with semaphore:
            try:
                data = await self.firecrawl._execute(url)
                content = data.get("markdown") or data.get("content") if data else None
                if content:
                    return self._build_result(
                        url=url,
                        title=data.get("metadata", {}).get("title", ""),
                        content=normalize_stage.normalize_content(content, policy),
                        source="firecrawl",
                    )
            except Exception as exc:
                logger.warning("Firecrawl failed for %s, trying Jina: %s", url, exc)

            try:
                data = await self.jina._execute(url)
                if data and data.get("content"):
                    return self._build_result(
                        url=url,
                        title=data.get("title", ""),
                        content=normalize_stage.normalize_content(
                            data["content"], policy
                        ),
                        source="jina",
                    )
            except Exception as exc:
                logger.warning(
                    "Jina failed for %s, falling back to BeautifulSoup: %s", url, exc
                )

            html = await fetch_stage.fetch_html(url, session, policy)
            if not html:
                return None

            normalized = normalize_stage.normalize_html(html, policy)
            return self._build_result(
                url=url,
                title=normalized.title,
                content=normalized.content,
                source="fallback_bs4",
            )

    @staticmethod
    def _build_result(url: str, title: str, content: str, source: str) -> ScrapeResult:
        return ScrapeResult(
            url=url,
            domain=urlparse(url).netloc,
            title=title,
            content=content,
            source=source,
        )


class CrawlerPipeline:
    def __init__(
        self,
        discovery_stage: Optional[DiscoveryStage] = None,
        fetch_stage: Optional[FetchStage] = None,
        extract_stage: Optional[ExtractStage] = None,
        normalize_stage: Optional[NormalizeStage] = None,
    ):
        self.discovery_stage = discovery_stage or DiscoveryStage()
        self.fetch_stage = fetch_stage or FetchStage()
        self.extract_stage = extract_stage or ExtractStage()
        self.normalize_stage = normalize_stage or NormalizeStage()

    async def fetch(self, urls: List[str], policy: CrawlPolicy) -> List[ScrapeResult]:
        discovered = self.discovery_stage.discover(urls)
        if not discovered:
            return []

        headers = {"User-Agent": policy.user_agent}
        semaphore = asyncio.Semaphore(policy.max_concurrent)
        async with aiohttp.ClientSession(headers=headers) as session:
            tasks = [
                self.extract_stage.extract(
                    url,
                    session,
                    policy,
                    self.fetch_stage,
                    self.normalize_stage,
                    semaphore,
                )
                for url in discovered
            ]
            results = await asyncio.gather(*tasks)
        return [result for result in results if result]
