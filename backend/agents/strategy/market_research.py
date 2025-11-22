"""
Market Research Agent - Quick Insight and Deep Dossier modes for market intelligence.
"""

import structlog
from typing import Dict, List, Optional, Literal
import hashlib

from backend.config.prompts import MASTER_SUPERVISOR_SYSTEM_PROMPT
from backend.services.openai_client import openai_client
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class MarketResearchAgent:
    """
    Conducts market research in two modes.
    
    Quick Insight Mode (~800 tokens):
    - Fast turnaround for immediate questions
    - Single-shot LLM call
    - Cached for 7 days
    
    Deep Dossier Mode (~3K tokens):
    - Comprehensive analysis
    - Breaks complex questions into sub-queries
    - Synthesizes multiple data points
    - Cached for 14 days
    
    Responsibilities:
    - Answer market questions (trends, competitors, opportunities)
    - Provide competitive intelligence
    - Identify market gaps and positioning
    - Surface relevant case studies and benchmarks
    """
    
    def __init__(self):
        self.quick_insight_max_tokens = 800
        self.deep_dossier_max_tokens = 3000
    
    async def research(
        self,
        question: str,
        mode: Literal["quick", "deep"] = "quick",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Conducts market research.
        
        Args:
            question: Research question
            mode: "quick" or "deep"
            context: Additional context (industry, company size, etc.)
            
        Returns:
            Research findings with sources and confidence
        """
        correlation_id = get_correlation_id()
        logger.info(
            "Conducting market research",
            question=question[:100],
            mode=mode,
            correlation_id=correlation_id
        )
        
        # Check cache
        cache_key = self._generate_cache_key(question, mode, context)
        cached = await redis_cache.get(cache_key)
        if cached:
            logger.info("Returning cached research", correlation_id=correlation_id)
            return cached
        
        # Conduct research
        if mode == "quick":
            findings = await self._quick_insight(question, context)
        else:
            findings = await self._deep_dossier(question, context)
        
        # Cache results
        ttl = 604800 if mode == "quick" else 1209600  # 7 or 14 days
        await redis_cache.set(cache_key, findings, ttl=ttl)
        
        logger.info(
            "Market research completed",
            mode=mode,
            confidence=findings.get("confidence", "N/A"),
            correlation_id=correlation_id
        )
        
        return findings
    
    async def _quick_insight(
        self,
        question: str,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Quick insight mode - single LLM call.
        """
        context_str = self._format_context(context) if context else ""
        
        prompt = f"""
You are a market research analyst providing quick, actionable insights.

QUESTION: {question}

{context_str}

Provide a concise, data-informed answer in ~600 words covering:
1. Direct answer to the question
2. Key supporting data points or trends
3. Practical implications
4. Recommended next steps

Format as JSON:
{{
    "answer": "Direct answer in 2-3 sentences",
    "key_findings": ["finding 1", "finding 2", "finding 3"],
    "trends": ["trend 1", "trend 2"],
    "implications": "What this means for the business",
    "next_steps": ["action 1", "action 2"],
    "confidence": "high|medium|low",
    "sources_consulted": ["source type 1", "source type 2"]
}}
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a market research expert providing quick, actionable insights."
                },
                {"role": "user", "content": prompt}
            ]
            
            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.4,
                max_tokens=self.quick_insight_max_tokens,
                response_format={"type": "json_object"}
            )
            
            import json
            findings = json.loads(response)
            findings["mode"] = "quick"
            
            return findings
            
        except Exception as e:
            logger.error(f"Quick insight failed: {e}")
            return self._fallback_findings(question, "quick")
    
    async def _deep_dossier(
        self,
        question: str,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Deep dossier mode - breaks into sub-queries.
        """
        # Step 1: Break down the question
        sub_queries = await self._decompose_question(question)
        
        # Step 2: Research each sub-query
        sub_findings = []
        for sub_q in sub_queries[:4]:  # Max 4 sub-queries
            finding = await self._research_sub_query(sub_q, context)
            sub_findings.append(finding)
        
        # Step 3: Synthesize findings
        synthesis = await self._synthesize_findings(question, sub_findings)
        
        synthesis["mode"] = "deep"
        synthesis["sub_queries"] = sub_queries
        
        return synthesis
    
    async def _decompose_question(self, question: str) -> List[str]:
        """
        Breaks complex question into sub-queries.
        """
        prompt = f"""
Break this complex market research question into 3-4 simpler sub-questions:

QUESTION: {question}

Return JSON:
{{
    "sub_questions": ["sub-q 1", "sub-q 2", "sub-q 3"]
}}
"""
        
        try:
            messages = [
                {"role": "system", "content": "You decompose complex research questions."},
                {"role": "user", "content": prompt}
            ]
            
            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response)
            return result.get("sub_questions", [question])
            
        except Exception as e:
            logger.error(f"Question decomposition failed: {e}")
            return [question]  # Fallback to original question
    
    async def _research_sub_query(
        self,
        sub_query: str,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Researches a single sub-query.
        """
        context_str = self._format_context(context) if context else ""
        
        prompt = f"""
Research this specific question:

{sub_query}

{context_str}

Provide focused insights in JSON:
{{
    "answer": "Direct answer",
    "data_points": ["data 1", "data 2"],
    "confidence": "high|medium|low"
}}
"""
        
        try:
            messages = [
                {"role": "system", "content": "You provide focused research insights."},
                {"role": "user", "content": prompt}
            ]
            
            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.4,
                max_tokens=600,
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Sub-query research failed: {e}")
            return {"answer": "Unable to research", "data_points": [], "confidence": "low"}
    
    async def _synthesize_findings(
        self,
        original_question: str,
        sub_findings: List[Dict]
    ) -> Dict[str, Any]:
        """
        Synthesizes sub-findings into comprehensive answer.
        """
        findings_summary = "\n\n".join([
            f"Q: {f.get('question', 'N/A')}\nA: {f.get('answer', 'N/A')}"
            for f in sub_findings
        ])
        
        prompt = f"""
Synthesize these research findings into a comprehensive market dossier:

ORIGINAL QUESTION: {original_question}

FINDINGS:
{findings_summary}

Create a comprehensive synthesis in JSON:
{{
    "executive_summary": "2-3 paragraph synthesis",
    "key_insights": ["insight 1", "insight 2", "insight 3", "insight 4"],
    "competitive_landscape": "Overview of competition",
    "opportunities": ["opportunity 1", "opportunity 2"],
    "threats": ["threat 1", "threat 2"],
    "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
    "confidence": "high|medium|low",
    "gaps": "What we don't know yet"
}}
"""
        
        try:
            messages = [
                {"role": "system", "content": "You synthesize market research into actionable intelligence."},
                {"role": "user", "content": prompt}
            ]
            
            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.5,
                max_tokens=self.deep_dossier_max_tokens,
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return self._fallback_findings(original_question, "deep")
    
    def _format_context(self, context: Dict) -> str:
        """Formats context dict into string."""
        parts = []
        if context.get("industry"):
            parts.append(f"Industry: {context['industry']}")
        if context.get("company_size"):
            parts.append(f"Company Size: {context['company_size']}")
        if context.get("geography"):
            parts.append(f"Geography: {context['geography']}")
        if context.get("additional"):
            parts.append(f"Additional Context: {context['additional']}")
        
        return "\n".join(parts) if parts else ""
    
    def _generate_cache_key(
        self,
        question: str,
        mode: str,
        context: Optional[Dict]
    ) -> str:
        """Generates cache key from inputs."""
        context_str = str(sorted(context.items())) if context else ""
        combined = f"{question}:{mode}:{context_str}"
        hash_obj = hashlib.sha256(combined.encode())
        return f"market_research:{hash_obj.hexdigest()}"
    
    def _fallback_findings(self, question: str, mode: str) -> Dict[str, Any]:
        """Fallback findings if research fails."""
        return {
            "answer": f"Unable to fully research: {question}",
            "key_findings": ["Research incomplete due to error"],
            "confidence": "low",
            "mode": mode,
            "error": True
        }


# Global instance
market_research = MarketResearchAgent()

