import asyncio
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from llm import LLMManager, LLMMessage, LLMRequest, LLMRole
from redis.cache import CacheService
from services.search.orchestrator import SOTASearchOrchestrator

logger = logging.getLogger("raptorflow.services.titan.multiplexer")


class SearchMultiplexer:
    """
    Multiplexes a single research query into multiple variations and executes them in parallel.
    """

    def __init__(self):
        self.search_orchestrator = SOTASearchOrchestrator()
        self.llm = LLMManager()
        self.cache = CacheService()

    async def generate_variations(
        self, query: str, focus_areas: List[str] = None, count: int = 5
    ) -> List[str]:
        """
        Generates query variations using LLM.
        """
        focus_str = f" Focusing on: {', '.join(focus_areas)}" if focus_areas else ""
        prompt = f"""Generate {count} unique, search-engine optimized query variations for: '{query}'.{focus_str}
Return only a JSON list of strings."""

        try:
            response = await self.llm.generate(
                LLMRequest(
                    messages=[LLMMessage(role=LLMRole.USER, content=prompt)],
                    model="gemini-1.5-flash",  # Fast & Cheap for multiplexing
                    temperature=0.7,
                )
            )

            # Simple JSON extraction
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            variations = eval(content)  # Use json.loads in production
            if not isinstance(variations, list):
                return [query]
            return variations[:count]
        except Exception as e:
            logger.error(f"Failed to generate query variations: {e}")
            return [query]

    async def execute_multiplexed(
        self, query: str, focus_areas: List[str] = None, count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generates and executes variations in parallel.
        """
        # Check cache (TTL: 24h)
        cache_key = f"titan:search:{hashlib.md5(f'{query}:{focus_areas}:{count}'.encode()).hexdigest()}"
        cached_val = await self.cache.redis.get_json(cache_key)
        if cached_val:
            logger.info(f"Titan Search Cache Hit: {query}")
            return cached_val

        variations = await self.generate_variations(query, focus_areas, count)
        logger.info(f"Executing {len(variations)} search variations for: {query}")

        tasks = [self.search_orchestrator.query(v, limit=10) for v in variations]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge and deduplicate
        all_results = []
        seen_urls = set()
        for engine_results in results:
            if isinstance(engine_results, list):
                for res in engine_results:
                    url = res.get("url", "").split("?")[0].rstrip("/")
                    if url and url not in seen_urls:
                        all_results.append(res)
                        seen_urls.add(url)

        # Set cache
        await self.cache.redis.set_json(cache_key, all_results, ex=86400)

        return all_results


class SemanticRanker:
    """
    Ranks search results by relevance to the query and focus areas using Gemini Flash.
    """

    def __init__(self):
        self.llm = LLMManager()

    async def rank_results(
        self, query: str, results: List[Dict[str, Any]], focus_areas: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Ranks results using LLM reasoning.
        """
        if not results:
            return []

        if len(results) > 20:
            results = results[:20]  # Limit for LLM context

        focus_str = f" Focus areas: {', '.join(focus_areas)}" if focus_areas else ""

        # Prepare a condensed list for the LLM to rank
        candidates = []
        for i, res in enumerate(results):
            candidates.append(
                f"ID: {i} | Title: {res.get('title')} | Snippet: {res.get('snippet')}"
            )

        candidates_str = "\n".join(candidates)

        prompt = f"""You are a high-precision research ranker.
Query: '{query}'
{focus_str}

Analyze the following search results and rank them by relevance.
Return only a JSON list of IDs in order of most relevant to least relevant.
Example: [3, 0, 1, 2]

Results:
{candidates_str}"""

        try:
            response = await self.llm.generate(
                LLMRequest(
                    messages=[LLMMessage(role=LLMRole.USER, content=prompt)],
                    model="gemini-1.5-flash",
                    temperature=0.1,  # Low temperature for consistent ranking
                )
            )

            content = response.content.strip()
            # Clean JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            import json

            ranked_ids = json.loads(content)

            ranked_results = []
            for idx in ranked_ids:
                if isinstance(idx, int) and 0 <= idx < len(results):
                    ranked_results.append(results[idx])

            # Add any missing results at the end
            seen_ids = set(ranked_ids)
            for i, res in enumerate(results):
                if i not in seen_ids:
                    ranked_results.append(res)

            return ranked_results
        except Exception as e:
            logger.error(f"Semantic ranking failed: {e}")
            return results
