"""
Pain Point Miner Agent - Discovers pain points from forums, reviews, and web sources.
"""

from typing import Dict, List, Optional
import logging
import asyncio

from backend.models.persona import ICPProfile
from backend.config.settings import get_settings
from backend.services.openai_client import openai_client
from backend.utils.cache import redis_cache

logger = logging.getLogger(__name__)
settings = get_settings()


class PainPointMinerAgent:
    """
    Mines pain points from various online sources.
    
    Responsibilities:
    - Search forums (Reddit, Quora) for pain points
    - Analyze review sites (G2, Trustpilot) for complaints
    - Extract triggers and objections
    - Update ICP with discovered pain points
    
    Note: This implementation uses LLM-based inference. In production,
    you'd integrate with actual APIs (Reddit API, web scraping, etc.)
    """
    
    def __init__(self):
        self.sources = ["Reddit", "Quora", "G2", "Trustpilot", "LinkedIn", "Twitter"]
    
    async def mine_pain_points(
        self,
        icp: ICPProfile,
        depth: str = "quick"  # "quick" or "deep"
    ) -> List[str]:
        """
        Mines pain points for a given ICP.
        
        Args:
            icp: ICP to research
            depth: "quick" (~800 tokens) or "deep" (~3K tokens)
            
        Returns:
            List of discovered pain points
        """
        logger.info(f"Mining pain points for: {icp.name} (depth: {depth})")
        
        # Check cache first
        cache_key = f"pain_points:{icp.id}:{depth}"
        cached_results = await redis_cache.get(cache_key)
        if cached_results:
            logger.info("Using cached pain points")
            return cached_results
        
        # Build research query
        research_query = self._build_research_query(icp)
        
        # Mine from different sources
        if depth == "deep":
            pain_points = await self._deep_research(research_query, icp)
        else:
            pain_points = await self._quick_research(research_query, icp)
        
        # Cache results for 7 days
        await redis_cache.set(cache_key, pain_points, ttl=7 * 24 * 3600)
        
        logger.info(f"Discovered {len(pain_points)} pain points")
        return pain_points
    
    async def extract_triggers(self, pain_points: List[str]) -> List[str]:
        """
        Extracts behavioral triggers from pain points.
        
        Args:
            pain_points: List of pain points
            
        Returns:
            List of triggers that prompt action
        """
        logger.info("Extracting behavioral triggers")
        
        trigger_prompt = f"""
Given these pain points, extract the specific triggers or events that would prompt someone to seek a solution:

Pain Points:
{self._format_list(pain_points)}

Triggers are specific events or thresholds that create urgency. Examples:
- "Missing quarterly targets for the 2nd time"
- "Team size doubled but productivity stayed flat"
- "Got burned by a bad vendor"
- "New competitor entered the market"

Extract 5-7 specific triggers from the pain points above. Return as a JSON array:
{{"triggers": ["trigger 1", "trigger 2", ...]}}
"""
        
        try:
            messages = [
                {"role": "system", "content": "You extract behavioral triggers from pain points."},
                {"role": "user", "content": trigger_prompt}
            ]
            
            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response)
            return result.get("triggers", [])
            
        except Exception as e:
            logger.error(f"Trigger extraction failed: {e}")
            return []
    
    def _build_research_query(self, icp: ICPProfile) -> str:
        """Builds a search query for the ICP."""
        query_parts = []
        
        if icp.demographics and icp.demographics.buyer_role:
            query_parts.append(icp.demographics.buyer_role)
        
        if icp.demographics and icp.demographics.industry:
            query_parts.append(icp.demographics.industry)
        
        if icp.pain_points:
            query_parts.append(icp.pain_points[0])
        
        return " ".join(query_parts)
    
    async def _quick_research(self, query: str, icp: ICPProfile) -> List[str]:
        """
        Quick research mode (~800 tokens).
        Uses LLM to infer likely pain points based on role and industry.
        """
        prompt = f"""
You are researching pain points for this customer profile:

Role: {icp.demographics.buyer_role if icp.demographics else 'Professional'}
Industry: {icp.demographics.industry if icp.demographics else 'General'}
Current Known Pain Points: {', '.join(icp.pain_points) if icp.pain_points else 'None'}

Based on your knowledge of this role and industry, infer 5-7 additional specific pain points they likely face.

Return as JSON array:
{{"pain_points": ["pain point 1", "pain point 2", ...]}}

Be specific and actionable. Focus on:
- Daily frustrations
- Process inefficiencies
- Resource constraints
- Technology gaps
- Market pressures
"""
        
        try:
            messages = [
                {"role": "system", "content": "You are a customer intelligence researcher."},
                {"role": "user", "content": prompt}
            ]
            
            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response)
            return result.get("pain_points", [])
            
        except Exception as e:
            logger.error(f"Quick research failed: {e}")
            return []
    
    async def _deep_research(self, query: str, icp: ICPProfile) -> List[str]:
        """
        Deep research mode (~3K tokens).
        Simulates searching multiple sources and synthesizing findings.
        
        In production, this would:
        1. Call Reddit API to search relevant subreddits
        2. Scrape G2/Trustpilot reviews
        3. Search Quora questions
        4. Analyze social media discussions
        """
        prompt = f"""
You are conducting deep customer research. Simulate searching these sources for pain points:

Sources: Reddit, Quora, G2 Reviews, Trustpilot, LinkedIn discussions, Twitter threads

Profile:
- Role: {icp.demographics.buyer_role if icp.demographics else 'Professional'}
- Industry: {icp.demographics.industry if icp.demographics else 'General'}
- Company Size: {icp.demographics.company_size if icp.demographics else 'Unknown'}
- Current Pain Points: {', '.join(icp.pain_points) if icp.pain_points else 'None'}

For each source, provide:
1. 2-3 specific pain points discovered
2. Example quote (simulated but realistic)
3. Frequency/severity indicator

Then synthesize into 10-15 unique, specific pain points.

Return as JSON:
{{
    "sources": [
        {{
            "source": "Reddit r/marketing",
            "pain_points": ["pain 1", "pain 2"],
            "example_quote": "quote",
            "frequency": "high|medium|low"
        }},
        ...
    ],
    "synthesized_pain_points": ["pain 1", "pain 2", ...]
}}

Be realistic - pain points should sound like real complaints from forums and reviews.
"""
        
        try:
            messages = [
                {"role": "system", "content": "You are a thorough customer intelligence researcher."},
                {"role": "user", "content": prompt}
            ]
            
            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response)
            
            # Log source findings for transparency
            for source in result.get("sources", []):
                logger.info(f"Source: {source.get('source')} - {source.get('frequency')} frequency")
            
            return result.get("synthesized_pain_points", [])
            
        except Exception as e:
            logger.error(f"Deep research failed: {e}")
            return []
    
    def _format_list(self, items: List[str]) -> str:
        """Formats a list for prompts."""
        return "\n".join([f"- {item}" for item in items])


# Global instance
pain_point_miner = PainPointMinerAgent()

