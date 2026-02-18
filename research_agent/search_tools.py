from __future__ import annotations

import asyncio
import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .research_log import Source


class SearchToolError(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolSearchResult:
    tool_name: str
    query: str
    sources: List[Source]
    error: Optional[str] = None
    latency_ms: Optional[int] = None


def _truncate(s: str, n: int) -> str:
    s2 = s.strip()
    if len(s2) <= n:
        return s2
    return s2[: max(0, n - 3)].rstrip() + "..."


def _dedupe_by_url(sources: Iterable[Source], limit: int) -> List[Source]:
    seen: set[str] = set()
    out: List[Source] = []
    for s in sources:
        url = s.url.strip()
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(s)
        if len(out) >= limit:
            break
    return out


class AsyncHTTPClient:
    def __init__(self, *, timeout_s: float = 20.0) -> None:
        self._timeout_s = float(timeout_s)
        self._aiohttp = None
        self._session = None
        try:
            import aiohttp  # type: ignore

            self._aiohttp = aiohttp
        except Exception:
            self._aiohttp = None

    async def __aenter__(self) -> "AsyncHTTPClient":
        if self._aiohttp is not None:
            timeout = self._aiohttp.ClientTimeout(total=self._timeout_s)
            self._session = self._aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        if self._session is not None:
            async with self._session.get(url, headers=headers) as resp:
                text = await resp.text()
                if resp.status >= 400:
                    raise SearchToolError(f"HTTP {resp.status}: {text[:300]}")
                return json.loads(text)
        return await asyncio.to_thread(self._get_json_sync, url, headers)

    async def post_json(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        if self._session is not None:
            async with self._session.post(url, json=payload, headers=headers) as resp:
                text = await resp.text()
                if resp.status >= 400:
                    raise SearchToolError(f"HTTP {resp.status}: {text[:300]}")
                return json.loads(text)
        return await asyncio.to_thread(self._post_json_sync, url, payload, headers)

    def _get_json_sync(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        req = urllib.request.Request(url, headers=headers or {}, method="GET")
        with urllib.request.urlopen(req, timeout=self._timeout_s) as resp:
            data = resp.read().decode("utf-8", errors="replace")
            return json.loads(data)

    def _post_json_sync(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        body = json.dumps(payload).encode("utf-8")
        hdrs = {"Content-Type": "application/json"}
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
        with urllib.request.urlopen(req, timeout=self._timeout_s) as resp:
            data = resp.read().decode("utf-8", errors="replace")
            return json.loads(data)


class SearchTool:
    name: str

    def is_configured(self) -> bool:
        return True

    async def search(
        self, _http: AsyncHTTPClient, _query: str, *, num_results: int = 5
    ) -> List[Source]:
        _ = num_results
        raise NotImplementedError


class ExaSearchTool(SearchTool):
    name = "exa"

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        search_type: str = "auto",
        max_text_chars: int = 800,
    ) -> None:
        self._api_key = api_key or os.environ.get("EXA_API_KEY")
        self._search_type = search_type
        self._max_text_chars = int(max_text_chars)

    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def search(
        self, http: AsyncHTTPClient, query: str, *, num_results: int = 5
    ) -> List[Source]:
        if not self._api_key:
            raise SearchToolError("EXA_API_KEY is not set")
        url = "https://api.exa.ai/search"
        payload: Dict[str, Any] = {
            "query": query,
            "type": self._search_type,
            "num_results": int(num_results),
            "contents": {"text": {"maxCharacters": self._max_text_chars}},
        }
        headers = {"x-api-key": self._api_key}
        data = await http.post_json(url, payload, headers=headers)
        results = data.get("results") or []
        out: List[Source] = []
        for r in results:
            try:
                u = str(r.get("url") or "").strip()
                if not u:
                    continue
                title = str(r.get("title") or "")
                snippet = str(r.get("text") or r.get("summary") or "")
                score = r.get("score")
                published = r.get("publishedDate") or r.get("published")
                out.append(
                    Source(
                        url=u,
                        title=_truncate(title, 200),
                        snippet=_truncate(snippet, 400),
                        score=float(score) if isinstance(score, (int, float)) else None,
                        published=str(published) if published else None,
                        tool=self.name,
                    )
                )
            except Exception:
                continue
        return _dedupe_by_url(out, int(num_results))


class GoogleCSESearchTool(SearchTool):
    name = "google"

    def __init__(
        self, *, api_key: Optional[str] = None, cx: Optional[str] = None
    ) -> None:
        self._api_key = api_key or os.environ.get("GOOGLE_CSE_API_KEY")
        self._cx = cx or os.environ.get("GOOGLE_CSE_CX")

    def is_configured(self) -> bool:
        return bool(self._api_key and self._cx)

    async def search(
        self, http: AsyncHTTPClient, query: str, *, num_results: int = 5
    ) -> List[Source]:
        if not (self._api_key and self._cx):
            raise SearchToolError("GOOGLE_CSE_API_KEY/GOOGLE_CSE_CX are not set")
        params = {
            "key": self._api_key,
            "cx": self._cx,
            "q": query,
            "num": min(10, max(1, int(num_results))),
        }
        url = "https://www.googleapis.com/customsearch/v1?" + urllib.parse.urlencode(
            params
        )
        data = await http.get_json(url)
        items = data.get("items") or []
        out: List[Source] = []
        for it in items:
            try:
                u = str(it.get("link") or "").strip()
                if not u:
                    continue
                out.append(
                    Source(
                        url=u,
                        title=_truncate(str(it.get("title") or ""), 200),
                        snippet=_truncate(str(it.get("snippet") or ""), 400),
                        tool=self.name,
                    )
                )
            except Exception:
                continue
        return _dedupe_by_url(out, int(num_results))


class SerpAPISearchTool(SearchTool):
    name = "serpapi"

    def __init__(
        self, *, api_key: Optional[str] = None, engine: str = "google"
    ) -> None:
        self._api_key = api_key or os.environ.get("SERPAPI_API_KEY")
        self._engine = engine

    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def search(
        self, http: AsyncHTTPClient, query: str, *, num_results: int = 5
    ) -> List[Source]:
        if not self._api_key:
            raise SearchToolError("SERPAPI_API_KEY is not set")
        params = {
            "api_key": self._api_key,
            "engine": self._engine,
            "q": query,
            "num": int(num_results),
        }
        url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)
        data = await http.get_json(url)
        organic = data.get("organic_results") or []
        out: List[Source] = []
        for it in organic:
            try:
                u = str(it.get("link") or "").strip()
                if not u:
                    continue
                out.append(
                    Source(
                        url=u,
                        title=_truncate(str(it.get("title") or ""), 200),
                        snippet=_truncate(
                            str(
                                it.get("snippet")
                                or it.get("snippet_highlighted_words")
                                or ""
                            ),
                            400,
                        ),
                        tool=self.name,
                    )
                )
            except Exception:
                continue
        return _dedupe_by_url(out, int(num_results))


class ToolRunner:
    def __init__(
        self,
        tools: Sequence[SearchTool],
        *,
        max_concurrency: int = 6,
        per_request_timeout_s: float = 20.0,
    ) -> None:
        self._tools = list(tools)
        self._sem = asyncio.Semaphore(max(1, int(max_concurrency)))
        self._timeout_s = float(per_request_timeout_s)

    @property
    def tools(self) -> List[SearchTool]:
        return list(self._tools)

    def configured_tools(self) -> List[SearchTool]:
        return [t for t in self._tools if t.is_configured()]

    async def run_one(
        self,
        http: AsyncHTTPClient,
        tool: SearchTool,
        query: str,
        *,
        num_results: int = 5,
    ) -> ToolSearchResult:
        async with self._sem:
            start = time.time()
            try:
                sources = await asyncio.wait_for(
                    tool.search(http, query, num_results=num_results),
                    timeout=self._timeout_s,
                )
                latency_ms = int((time.time() - start) * 1000)
                return ToolSearchResult(
                    tool_name=tool.name,
                    query=query,
                    sources=sources,
                    latency_ms=latency_ms,
                )
            except Exception as e:
                latency_ms = int((time.time() - start) * 1000)
                return ToolSearchResult(
                    tool_name=tool.name,
                    query=query,
                    sources=[],
                    error=str(e),
                    latency_ms=latency_ms,
                )

    async def run(
        self,
        http: AsyncHTTPClient,
        queries: Sequence[str],
        *,
        tools: Optional[Sequence[SearchTool]] = None,
        num_results: int = 5,
    ) -> List[ToolSearchResult]:
        use_tools = list(tools) if tools is not None else self.configured_tools()
        tasks: List[asyncio.Task[ToolSearchResult]] = []
        for q in queries:
            q2 = str(q).strip()
            if not q2:
                continue
            for t in use_tools:
                tasks.append(
                    asyncio.create_task(
                        self.run_one(http, t, q2, num_results=num_results)
                    )
                )
        if not tasks:
            return []
        return list(await asyncio.gather(*tasks))


def merge_tool_results(
    results: Sequence[ToolSearchResult], *, top_k: int = 8
) -> Tuple[List[Source], Dict[str, Any]]:
    all_sources: List[Source] = []
    tool_errors: Dict[str, Any] = {}
    for r in results:
        all_sources.extend(r.sources)
        if r.error:
            tool_errors.setdefault(r.tool_name, []).append(
                {"query": r.query, "error": r.error, "latency_ms": r.latency_ms}
            )
    return _dedupe_by_url(all_sources, int(top_k)), {"errors": tool_errors}
