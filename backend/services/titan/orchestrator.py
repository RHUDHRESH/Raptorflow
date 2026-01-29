import asyncio
import hashlib
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from tools.web_scraper import ContentType, ScrapingMethod, WebScraperTool

from ..core.supabase_mgr import get_supabase_client
from ..llm import LLMManager
from ..services.search.orchestrator import SOTASearchOrchestrator
from ..services.storage import get_enhanced_storage_service
from ..services.titan.multiplexer import SearchMultiplexer, SemanticRanker
from ..services.titan.scraper import IntelligentMarkdown, PlaywrightStealthPool

logger = logging.getLogger("raptorflow.services.titan.orchestrator")


class TitanMode(str, Enum):
    LITE = "LITE"
    RESEARCH = "RESEARCH"
    DEEP = "DEEP"


class LinkSignalScorer:
    """
    Scores links for research relevance using LLM reasoning.
    """

    def __init__(self, llm: LLMManager):
        self.llm = llm

    async def score_links(
        self, query: str, links: List[str], focus_areas: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Assigns a signal score (0-1) to each link.
        """
        if not links:
            return []

        # Deduplicate and limit
        links = list(set(links))[:30]

        focus_str = f" Focus areas: {', '.join(focus_areas)}" if focus_areas else ""
        links_str = "\n".join(
            [f"ID: {i} | URL: {link}" for i, link in enumerate(links)]
        )

        prompt = f"""You are a research signal optimizer.
Research Query: '{query}'
{focus_str}

Analyze these links and return a JSON list of IDs that are HIGHLY likely to contain deep factual data (pricing, technical docs, case studies, specific features).
Ignore: social media, login, terms, privacy, jobs, generic 'about' pages unless highly relevant.

Return only a JSON object like: {{"high_signal_ids": [0, 5, 12]}}

Links:
{links_str}"""

        try:
            response = await self.llm.generate(
                LLMRequest(
                    messages=[LLMMessage(role=LLMRole.USER, content=prompt)],
                    model="gemini-1.5-flash",
                    temperature=0.1,
                )
            )

            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()

            import json

            data = json.loads(content)
            high_signal_ids = data.get("high_signal_ids", [])

            return [links[idx] for idx in high_signal_ids if 0 <= idx < len(links)]
        except Exception as e:
            logger.error(f"Link scoring failed: {e}")
            # Fallback: simple keyword based heuristic
            keywords = [
                "pricing",
                "features",
                "docs",
                "case-study",
                "whitepaper",
                "product",
            ]
            return [l for l in links if any(k in l.lower() for k in keywords)][:5]


class CognitiveSynthesizer:
    """
    Distills raw research data into a structured JSON Intelligence Map.
    """

    def __init__(self, llm: LLMManager):
        self.llm = llm

    async def synthesize(
        self, query: str, data: List[Dict[str, Any]], mode: str
    ) -> Dict[str, Any]:
        """
        Performs multi-stage synthesis of gathered data.
        """
        if not data:
            return {"query": query, "intelligence": "No data found."}

        # Prepare context from data
        context_parts = []
        for i, item in enumerate(data):
            text = (
                item.get("text")
                or item.get("full_content")
                or item.get("snippet")
                or ""
            )
            context_parts.append(f"Source {i} [{item.get('url')}]: {text[:2000]}")

        context_str = "\n\n".join(context_parts)

        prompt = f"""You are a SOTA Market Intelligence Analyst.
Primary Objective: '{query}'
Research Mode: {mode}

Synthesize the following raw data into a high-density intelligence report.
Focus on: Unique mechanisms, pricing models, ICP segments, and competitive gaps.

Return a JSON object with this structure:
{{
  "summary": "...",
  "key_findings": ["...", "..."],
  "pricing_intelligence": {{ "detected": true/false, "details": "..." }},
  "competitive_landscape": "...",
  "market_map": {{ ... }}
}}

Data:
{context_str}"""

        try:
            response = await self.llm.generate(
                LLMRequest(
                    messages=[LLMMessage(role=LLMRole.USER, content=prompt)],
                    model="gemini-1.5-flash",
                    temperature=0.3,
                )
            )

            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()

            import json

            return json.loads(content)
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return {"summary": "Synthesis failed due to API error.", "error": str(e)}


class TitanOrchestrator:
    """
    Titan SOTA Intelligence Orchestrator.
    Handles multi-modal research from Lite search to Deep recursive scraping.
    """

    def __init__(self):
        self.settings = get_settings()
        self.llm = LLMManager()
        self.search_orchestrator = SOTASearchOrchestrator()
        self.multiplexer = SearchMultiplexer()
        self.ranker = SemanticRanker()
        self.scraper_tool = WebScraperTool()
        self.stealth_pool = PlaywrightStealthPool(max_contexts=5)
        self.markdown = IntelligentMarkdown()
        self.link_scorer = LinkSignalScorer(self.llm)
        self.synthesizer = CognitiveSynthesizer(self.llm)
        self.cache = CacheService()

    async def execute(
        self,
        query: str,
        mode: str = "LITE",
        focus_areas: Optional[List[str]] = None,
        max_results: int = 10,
        use_stealth: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute research based on the specified mode.
        """
        if mode not in TitanMode.__members__:
            raise ValueError(
                f"Invalid mode: {mode}. Must be one of {list(TitanMode.__members__.keys())}"
            )

        mode_enum = TitanMode(mode)

        logger.info(f"Executing Titan research in {mode_enum} mode for query: {query}")

        result = None
        if mode_enum == TitanMode.LITE:
            result = await self._execute_lite(query, max_results)
        elif mode_enum == TitanMode.RESEARCH:
            result = await self._execute_research(
                query, focus_areas, max_results, use_stealth
            )
        elif mode_enum == TitanMode.DEEP:
            result = await self._execute_deep(
                query, focus_areas, max_results, use_stealth
            )

        # 5. Storage & Persistence (Phases 5)
        if result and mode_enum != TitanMode.LITE:
            try:
                await self._store_intelligence(query, result)
            except Exception as e:
                logger.error(f"Failed to store intelligence: {e}")

        return result

    async def _store_intelligence(
        self, query: str, result: Dict[str, Any], workspace_id: str = "default"
    ):
        """
        Stores result in Supabase Storage and pgvector.
        """
        logger.info(f"Persisting intelligence for query: {query}")

        # 1. Store raw JSON in Supabase Storage
        filename = f"titan_intel_{hashlib.md5(query.encode()).hexdigest()[:10]}.json"
        try:
            # Prepare content
            json_content = json.dumps(result, indent=2).encode("utf-8")

            # Use enhanced storage service (lazy getter)
            from services.storage import get_enhanced_storage_service

            upload_res = await get_enhanced_storage_service().upload_file(
                file_content=json_content,
                filename=filename,
                workspace_id=workspace_id,
                content_type="application/json",
                user_id="titan_engine",
            )

            if upload_res["status"] == "success":
                logger.info(
                    f"Titan intelligence saved to Supabase: {upload_res['storage_path']}"
                )
            else:
                logger.warning(
                    f"Failed to save Titan intelligence to Supabase: {upload_res.get('error')}"
                )
        except Exception as e:
            logger.error(f"Supabase storage failed for Titan result: {e}")

        # 2. Inject chunks into pgvector (Supabase)
        intelligence = result.get("intelligence_map", {})
        if intelligence:
            try:
                summary = intelligence.get("summary", "")
                findings = " ".join(intelligence.get("key_findings", []))
                text_to_vectorize = (
                    f"Query: {query}\nSummary: {summary}\nFindings: {findings}"
                )

                # Use Supabase RPC for vector upsert if available
                # This assumes a 'match_documents' or similar RPC exists for vector search
                # and a 'documents' table for storage.
                supabase = get_supabase_client()

                # Simplified vector storage logic
                # In production, we'd generate embeddings first using vertex_ai_service
                await supabase.table("intelligence_vault").insert(
                    {
                        "workspace_id": workspace_id,
                        "query": query,
                        "summary": summary,
                        "full_intelligence": intelligence,
                        "source": "titan_sota",
                        "created_at": datetime.now().isoformat(),
                    }
                ).execute()

                logger.info("Titan intelligence indexed in Supabase")
            except Exception as e:
                logger.error(f"Vector storage failed for Titan result: {e}")

    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Simple text chunker."""
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    async def _execute_lite(self, query: str, max_results: int) -> Dict[str, Any]:
        """
        LITE mode: Fast search aggregation only.
        """
        try:
            results = await self.search_orchestrator.query(query, limit=max_results)
            return {
                "query": query,
                "mode": "LITE",
                "results": results,
                "count": len(results),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Lite research failed: {e}")
            return {
                "query": query,
                "mode": "LITE",
                "results": [],
                "error": str(e),
                "count": 0,
                "timestamp": datetime.now().isoformat(),
            }

    async def _scrape_with_escalation(
        self, url: str, use_stealth: bool = True
    ) -> Dict[str, Any]:
        """
        Escalation ladder: HTTP -> Playwright Stealth.
        """
        # Check Cache (TTL: 24h)
        cache_key = f"titan:scrape:{hashlib.md5(url.encode()).hexdigest()}"
        cached_val = await self.cache.redis.get_json(cache_key)
        if cached_val:
            logger.info(f"Titan Scrape Cache Hit: {url}")
            return cached_val

        if not use_stealth:
            try:
                result = await self.scraper_tool._execute(url=url, method="http")
                # Check if we got meaningful content
                content_list = result.get("content", {}).get("content", [])
                text = " ".join(
                    [
                        c.get("data", {}).get("text", "")
                        for c in content_list
                        if isinstance(c, dict)
                    ]
                )
                if len(text) > 500:
                    resp = {"url": url, "text": text, "method": "http"}
                    await self.cache.redis.set_json(cache_key, resp, ex=86400)
                    return resp
            except Exception:
                logger.debug(f"HTTP scrape failed for {url}, escalating...")

        # Escalation or Direct Stealth
        stealth_result = await self.stealth_pool.scrape_url(url)
        if stealth_result.get("status") == "success":
            clean_text = self.markdown.convert(stealth_result.get("html", ""))
            resp = {
                "url": url,
                "text": clean_text,
                "title": stealth_result.get("title"),
                "links": stealth_result.get("links"),
                "method": "playwright_stealth",
            }
            await self.cache.redis.set_json(cache_key, resp, ex=86400)
            return resp

        return {"url": url, "error": "All scraping methods failed", "status": "failed"}

    async def _execute_research(
        self,
        query: str,
        focus_areas: Optional[List[str]],
        max_results: int,
        use_stealth: bool,
    ) -> Dict[str, Any]:
        """
        RESEARCH mode: Multi-query search + semantic ranking + targeted scraping.
        """
        try:
            # 1. Multiplexed Search
            all_search_results = await self.multiplexer.execute_multiplexed(
                query, focus_areas, count=5
            )

            # 2. Semantic Ranking
            ranked_results = await self.rank_results(
                query, all_search_results, focus_areas
            )

            # 3. Scrape top results in parallel
            top_candidates = ranked_results[:5]
            scrape_tasks = [
                self._scrape_with_escalation(res.get("url"), use_stealth)
                for res in top_candidates
                if res.get("url")
            ]

            scraped_data = await asyncio.gather(*scrape_tasks, return_exceptions=True)

            enriched_results = []
            for i, res in enumerate(top_candidates):
                enrichment = scraped_data[i] if i < len(scraped_data) else None
                if isinstance(enrichment, dict) and "text" in enrichment:
                    res["full_content"] = enrichment["text"][:10000]
                    res["scrape_method"] = enrichment.get("method")

                enriched_results.append(res)

            # 4. Synthesize Intelligence Map
            intelligence_map = await self.synthesizer.synthesize(
                query, enriched_results, "RESEARCH"
            )

            return {
                "query": query,
                "mode": "RESEARCH",
                "results": enriched_results,
                "intelligence_map": intelligence_map,
                "count": len(enriched_results),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Research mode failed: {e}")
            return {
                "query": query,
                "mode": "RESEARCH",
                "error": str(e),
                "intelligence_map": {
                    "summary": "Synthesis failed due to API error.",
                    "details": str(e),
                },
                "results": [],
                "count": 0,
                "timestamp": datetime.now().isoformat(),
            }

    async def _execute_deep(
        self,
        query: str,
        focus_areas: Optional[List[str]],
        max_results: int,
        use_stealth: bool,
    ) -> Dict[str, Any]:
        """
        DEEP mode: High-concurrency discovery + recursive traversal.
        """
        try:
            # 1. Broad Multiplexed Search
            all_search_results = await self.multiplexer.execute_multiplexed(
                query, focus_areas, count=10
            )
            ranked_results = await self.rank_results(
                query, all_search_results, focus_areas
            )

            if not ranked_results:
                return {"query": query, "mode": "DEEP", "results": [], "count": 0}

            # 2. Parallel Recursive Traversal on top 2 domains
            top_urls = [r.get("url") for r in ranked_results[:2] if r.get("url")]

            traversal_results = await asyncio.gather(
                *[
                    self._recursive_traverse(query, url, focus_areas, depth=2)
                    for url in top_urls
                ],
                return_exceptions=True,
            )

            deep_data = [d for d in traversal_results if not isinstance(d, Exception)]

            # 3. Flatten and Synthesize
            all_pages = []
            for domain_res in deep_data:
                all_pages.extend(domain_res.get("pages", []))

            intelligence_map = await self.synthesizer.synthesize(
                query, all_pages, "DEEP"
            )

            return {
                "query": query,
                "mode": "DEEP",
                "results": ranked_results[:max_results],
                "deep_research_data": deep_data,
                "intelligence_map": intelligence_map,
                "count": len(ranked_results),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Deep research failed: {e}")
            return {
                "query": query,
                "mode": "DEEP",
                "error": str(e),
                "intelligence_map": {
                    "summary": "Recursive traversal failed.",
                    "details": str(e),
                },
                "results": [],
                "count": 0,
                "timestamp": datetime.now().isoformat(),
            }

    async def _recursive_traverse(
        self, query: str, start_url: str, focus_areas: List[str] = None, depth: int = 2
    ) -> Dict[str, Any]:
        """
        Breadth-First Search traversal with signal scoring.
        """
        visited = set()
        queue = [(start_url, 0)]
        results = []

        while queue and len(results) < 10:  # Safety limit for sync execution
            url, current_depth = queue.pop(0)
            if url in visited or current_depth > depth:
                continue

            visited.add(url)
            logger.info(f"Traversing: {url} at depth {current_depth}")

            # Scrape page
            scrape_res = await self._scrape_with_escalation(url, use_stealth=True)
            if scrape_res.get("status") == "failed":
                continue

            results.append(
                {
                    "url": url,
                    "text": scrape_res.get("text", "")[:5000],
                    "depth": current_depth,
                }
            )

            # Extract and score links if depth allows
            if current_depth < depth:
                links = scrape_res.get("links", [])
                if links:
                    # Filter for same domain to prevent runaway
                    domain = urlparse(start_url).netloc
                    same_domain_links = [
                        l for l in links if urlparse(l).netloc == domain
                    ]

                    high_signal_links = await self.link_scorer.score_links(
                        query, same_domain_links, focus_areas
                    )
                    for link in high_signal_links:
                        if link not in visited:
                            queue.append((link, current_depth + 1))

        return {"root_url": start_url, "pages": results}

    async def rank_results(
        self, query: str, results: List[Dict[str, Any]], focus_areas: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Helper to rank results."""
        return await self.ranker.rank_results(query, results, focus_areas)

    async def close(self):
        """Cleanup all resources."""
        await self.search_orchestrator.close()
        await self.scraper_tool.cleanup()
        await self.stealth_pool.close()
