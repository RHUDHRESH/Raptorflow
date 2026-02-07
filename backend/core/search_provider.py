import logging
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qsl, urlsplit, urlunsplit

import httpx

from core.config import get_settings
from core.search_native import NativeSearch

logger = logging.getLogger("raptorflow.search_provider")

TRACKING_QUERY_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "gclid",
    "fbclid",
    "igshid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
    "ref_url",
    "spm",
}


def normalize_url(url: str) -> str:
    if not url:
        return url
    trimmed = url.strip()
    if "://" not in trimmed:
        trimmed = f"https://{trimmed}"
    parsed = urlsplit(trimmed)
    scheme = parsed.scheme.lower() if parsed.scheme else "https"
    netloc = parsed.netloc.lower()
    if scheme == "http" and netloc.endswith(":80"):
        netloc = netloc[:-3]
    if scheme == "https" and netloc.endswith(":443"):
        netloc = netloc[:-4]
    query_items = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_PARAMS
    ]
    query_items.sort()
    query = "&".join(f"{k}={v}" for k, v in query_items) if query_items else ""
    return urlunsplit((scheme, netloc, parsed.path or "/", query, ""))


def dedupe_urls(urls: Iterable[str]) -> List[str]:
    seen = set()
    deduped = []
    for url in urls:
        normalized = normalize_url(url)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


@dataclass
class ProviderResult:
    urls: List[str]
    provider: str


class BaseSearchProvider:
    name = "base"

    def __init__(self, settings):
        self.settings = settings

    def is_available(self) -> bool:
        return True

    async def search(self, query: str, num_results: int = 5) -> ProviderResult:
        raise NotImplementedError


class NativeSearchProvider(BaseSearchProvider):
    name = "native"

    def __init__(self, settings):
        super().__init__(settings)
        self._native = NativeSearch()

    async def search(self, query: str, num_results: int = 5) -> ProviderResult:
        results = await self._native.query(query, limit=num_results)
        urls = [res.get("url", "") for res in results]
        return ProviderResult(urls=urls, provider=self.name)


class SerperSearchProvider(BaseSearchProvider):
    name = "serper"

    def __init__(self, settings, endpoint: str):
        super().__init__(settings)
        self.endpoint = endpoint
        self._client = httpx.AsyncClient(timeout=10.0)

    def is_available(self) -> bool:
        return bool(self.settings.SERPER_API_KEY)

    async def search(self, query: str, num_results: int = 5) -> ProviderResult:
        if not self.settings.SERPER_API_KEY:
            return ProviderResult(urls=[], provider=self.name)
        payload = {"q": query, "num": num_results}
        headers = {
            "X-API-KEY": self.settings.SERPER_API_KEY,
            "Content-Type": "application/json",
        }
        response = await self._client.post(self.endpoint, json=payload, headers=headers)
        if response.status_code != 200:
            logger.warning("Serper search failed: %s", response.status_code)
            return ProviderResult(urls=[], provider=self.name)
        data = response.json()
        urls = [item.get("link", "") for item in data.get("organic", [])]
        return ProviderResult(urls=urls, provider=self.name)


class SearchProviderRegistry:
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self._providers = self._build_providers()
        self._cursor = 0
        self._remaining_quotas = self._initialize_quotas()

    def _build_providers(self) -> List[BaseSearchProvider]:
        provider_settings = self.settings.SEARCH_PROVIDER_SETTINGS or {}
        order = self.settings.SEARCH_PROVIDER_ORDER or ["native"]
        providers: Dict[str, BaseSearchProvider] = {
            "native": NativeSearchProvider(self.settings),
            "serper": SerperSearchProvider(
                self.settings,
                provider_settings.get("serper", {}).get(
                    "endpoint", "https://google.serper.dev/search"
                ),
            ),
        }
        return [providers[name] for name in order if name in providers]

    def _initialize_quotas(self) -> Dict[str, Optional[int]]:
        quotas: Dict[str, Optional[int]] = {}
        for name, quota in (self.settings.SEARCH_PROVIDER_QUOTAS or {}).items():
            quotas[name] = quota
        return quotas

    def _next_candidates(self) -> Iterable[Tuple[int, BaseSearchProvider]]:
        if not self._providers:
            return []
        total = len(self._providers)
        return (
            (
                (self._cursor + offset) % total,
                self._providers[(self._cursor + offset) % total],
            )
            for offset in range(total)
        )

    def _has_quota(self, provider: BaseSearchProvider) -> bool:
        quota = self._remaining_quotas.get(provider.name)
        return quota is None or quota > 0

    def _consume_quota(self, provider: BaseSearchProvider) -> None:
        if provider.name not in self._remaining_quotas:
            return
        if self._remaining_quotas[provider.name] is None:
            return
        self._remaining_quotas[provider.name] = max(
            0, (self._remaining_quotas[provider.name] or 0) - 1
        )

    async def search(self, query: str, num_results: int = 5) -> List[str]:
        if not query:
            return []
        for index, provider in self._next_candidates():
            if not provider.is_available() or not self._has_quota(provider):
                continue
            try:
                result = await provider.search(query, num_results=num_results)
            except Exception as exc:
                logger.warning("Search provider %s failed: %s", provider.name, exc)
                continue
            urls = dedupe_urls(result.urls)
            if urls:
                self._consume_quota(provider)
                self._cursor = (index + 1) % len(self._providers)
                return urls
        return []
