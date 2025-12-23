import os
import logging
from typing import List, Dict, Any
from tavily import TavilyClient
from backend.core.base_tool import BaseRaptorTool, RaptorRateLimiter

logger = logging.getLogger("raptorflow.tools.search")

class TavilyMultiHopTool(BaseRaptorTool):
    """
    SOTA Multi-hop Search Tool.
    Performs deep research using Tavily's specialized AI search.
    """

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                logger.error("TAVILY_API_KEY missing from environment.")
                raise ValueError("TAVILY_API_KEY missing")
            self._client = TavilyClient(api_key=api_key)
        return self._client

    @property
    def name(self) -> str:
        return "tavily_search"

    @property
    def description(self) -> str:
        return (
            "A SOTA multi-hop search engine. Use this for deep factual research, "
            "competitive intelligence, and finding specific evidence. "
            "Input should be a detailed search query."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(
        self, query: str, search_depth: str = "advanced"
    ) -> List[Dict[str, Any]]:
        """
        Executes the deep search.
        """
        logger.info(f"Executing Tavily multi-hop search: {query}")
        # Tavily search is synchronous, we run in thread for SOTA async performance
        import asyncio

        response = await asyncio.to_thread(
            self.client.search, query=query, search_depth=search_depth, max_results=5
        )
        return response.get("results", [])

class PerplexitySearchTool(BaseRaptorTool):
    """
    SOTA Real-time Search Tool.
    Uses Perplexity for high-velocity news and trend extraction.
    """
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.url = "https://api.perplexity.ai/chat/completions"

    @property
    def name(self) -> str:
        return "perplexity_search"

    @property
    def description(self) -> str:
        return (
            "A SOTA real-time search engine. Use this for trending news, "
            "up-to-the-minute market shifts, and verifying recent facts. "
            "Input should be a factual query."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(self, query: str) -> str:
        """
        Executes search via Perplexity's completion API.
        """
        import aiohttp
        logger.info(f"Executing Perplexity real-time search: {query}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar-pro", # SOTA model for 2025
            "messages": [
                {"role": "system", "content": "Be precise and cite sources."},
                {"role": "user", "content": query}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise ValueError(f"Perplexity API failed ({resp.status}): {text}")
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
