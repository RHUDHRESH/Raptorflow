"""
Market Research Agent - Quick Insight and Deep Dossier modes for market intelligence.
"""

import structlog
from typing import Dict, List, Optional, Literal, Any
import hashlib
from datetime import datetime

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
    - Analyze competitive positioning and differentiation
    - Validate data sources and provide references
    """

    def __init__(self):
        self.quick_insight_max_tokens = 800
        self.deep_dossier_max_tokens = 3000

        # Data sources we can reference
        self.data_sources = {
            "internal": ["supabase_icps", "supabase_campaigns", "supabase_analytics"],
            "market_knowledge": ["llm_training_data", "industry_reports", "market_trends"],
            "competitive": ["public_competitor_data", "positioning_analysis"]
        }
    
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

    async def analyze_competitive_positioning(
        self,
        company_description: str,
        industry: str,
        target_audience: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes competitive positioning for a company.

        Args:
            company_description: Description of the company/product
            industry: Industry or market segment
            target_audience: Optional target audience description

        Returns:
            Competitive analysis with positioning, competitors, and differentiation
        """
        correlation_id = get_correlation_id()
        logger.info(
            "Analyzing competitive positioning",
            industry=industry,
            correlation_id=correlation_id
        )

        # Check cache
        import hashlib
        cache_key = f"competitive_positioning:{hashlib.sha256(f'{company_description}:{industry}'.encode()).hexdigest()}"
        cached = await redis_cache.get(cache_key)
        if cached:
            logger.info("Returning cached competitive analysis")
            return cached

        # Build analysis prompt
        target_context = f"\nTarget Audience: {target_audience}" if target_audience else ""

        prompt = f"""
You are a competitive intelligence analyst. Analyze the competitive landscape and positioning.

COMPANY: {company_description}
INDUSTRY: {industry}{target_context}

Provide a comprehensive competitive analysis:

1. **Market Landscape**: Overview of the competitive environment
2. **Key Competitors**: Identify 3-5 main competitors and their positioning
3. **Competitive Gaps**: Market gaps and underserved needs
4. **Differentiation Opportunities**: How this company can differentiate
5. **Positioning Recommendations**: Recommended market positioning

Return JSON:
{{
    "market_landscape": {{
        "market_size": "Description of market size and growth",
        "key_trends": ["trend 1", "trend 2", "trend 3"],
        "competitive_intensity": "low|medium|high",
        "barriers_to_entry": ["barrier 1", "barrier 2"]
    }},
    "competitors": [
        {{
            "name": "Competitor name or type",
            "positioning": "How they position themselves",
            "strengths": ["strength 1", "strength 2"],
            "weaknesses": ["weakness 1", "weakness 2"],
            "market_share": "estimated share if known"
        }}
    ],
    "gaps_and_opportunities": [
        {{
            "gap": "Underserved need or market gap",
            "opportunity": "How to capitalize on this gap",
            "difficulty": "low|medium|high"
        }}
    ],
    "differentiation_strategy": {{
        "primary_differentiator": "Main point of differentiation",
        "supporting_differentiators": ["secondary point 1", "secondary point 2"],
        "positioning_statement": "Recommended one-line positioning",
        "target_segment_focus": "Which segment to focus on"
    }},
    "data_sources": ["source 1", "source 2"],
    "confidence": "high|medium|low"
}}
"""

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a competitive intelligence expert with deep market knowledge. Provide data-informed analysis."
                },
                {"role": "user", "content": prompt}
            ]

            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.4,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            import json
            analysis = json.loads(response)

            # Add metadata
            analysis["industry"] = industry
            analysis["analyzed_at"] = datetime.utcnow().isoformat()

            # Cache results (14 days for competitive analysis)
            await redis_cache.set(cache_key, analysis, ttl=1209600)

            logger.info(
                "Competitive analysis completed",
                num_competitors=len(analysis.get("competitors", [])),
                confidence=analysis.get("confidence"),
                correlation_id=correlation_id
            )

            return analysis

        except Exception as e:
            logger.error(f"Competitive analysis failed: {e}")
            return self._fallback_competitive_analysis()

    def _fallback_competitive_analysis(self) -> Dict[str, Any]:
        """Fallback competitive analysis if LLM call fails."""
        return {
            "market_landscape": {
                "market_size": "Unable to determine",
                "key_trends": ["Analysis incomplete"],
                "competitive_intensity": "medium",
                "barriers_to_entry": []
            },
            "competitors": [],
            "gaps_and_opportunities": [],
            "differentiation_strategy": {
                "primary_differentiator": "Unable to determine",
                "supporting_differentiators": [],
                "positioning_statement": "Analysis incomplete",
                "target_segment_focus": "Unknown"
            },
            "data_sources": [],
            "confidence": "low",
            "error": True
        }

    async def get_market_opportunities(
        self,
        industry: str,
        icp_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Identifies market opportunities based on industry and ICP.

        Args:
            industry: Industry or market segment
            icp_data: Optional ICP profile data

        Returns:
            Market opportunities with prioritization
        """
        correlation_id = get_correlation_id()

        # Build context from ICP
        icp_context = ""
        if icp_data:
            pain_points = icp_data.get("pain_points", [])
            if pain_points:
                icp_context = f"\nTarget Customer Pain Points: {', '.join(pain_points[:5])}"

        question = f"What are the top market opportunities in {industry} for the next 12 months?{icp_context}"

        # Use deep research mode for opportunities
        findings = await self.research(
            question=question,
            mode="deep",
            context={"industry": industry}
        )

        # Enhance with opportunity structure
        opportunities = {
            "industry": industry,
            "opportunities": findings.get("key_insights", []),
            "trends": findings.get("trends", []) if "trends" in findings else [],
            "recommendations": findings.get("recommendations", []),
            "confidence": findings.get("confidence", "medium"),
            "sources": findings.get("sources_consulted", self.data_sources["market_knowledge"]),
            "analyzed_at": datetime.utcnow().isoformat()
        }

        return opportunities


# Global instance
market_research = MarketResearchAgent()

