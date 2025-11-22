"""
Synthesis Agent - Converts ambient discoveries into concrete campaign ideas.
"""

import structlog
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from backend.config.prompts import MASTER_SUPERVISOR_SYSTEM_PROMPT
from backend.services.openai_client import openai_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class SynthesisAgent:
    """
    Synthesizes insights into actionable campaign ideas.
    
    Takes:
    - Ambient discoveries (quick wins)
    - ICP tags and profiles
    - Market research insights
    
    Produces:
    - Concrete campaign proposals with rationale
    - Mini-plans (channels, assets, timeline)
    - Priority scores
    - Risk assessments
    
    Responsibilities:
    - Convert opportunities into campaigns
    - Recommend channels and content mix
    - Estimate effort and resource needs
    - Provide strategic rationale
    """
    
    def __init__(self):
        self.effort_levels = ["low", "medium", "high"]
        self.confidence_levels = ["low", "medium", "high"]
    
    async def synthesize_campaign_idea(
        self,
        opportunity: Dict[str, Any],
        icps: List[Dict],
        market_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes an opportunity into a concrete campaign proposal.
        
        Args:
            opportunity: Quick win or ambient discovery
            icps: Relevant ICPs
            market_context: Optional market insights
            
        Returns:
            Campaign proposal with mini-plan
        """
        correlation_id = get_correlation_id()
        logger.info(
            "Synthesizing campaign idea",
            opportunity_title=opportunity.get("title", "N/A"),
            num_icps=len(icps),
            correlation_id=correlation_id
        )
        
        # Build context
        icp_context = self._build_icp_context(icps)
        market_context_str = self._format_market_context(market_context) if market_context else ""
        
        prompt = f"""
You are a campaign strategist synthesizing an opportunity into an actionable campaign.

OPPORTUNITY:
Title: {opportunity.get('title', 'N/A')}
Description: {opportunity.get('description', 'N/A')}
Signal Type: {opportunity.get('signal_type', 'N/A')}
Why Now: {opportunity.get('why_now', 'N/A')}
Suggested Angles: {opportunity.get('campaign_angle', 'N/A')}

TARGET ICPS:
{icp_context}

{market_context_str}

Create a concrete campaign proposal:

1. **Campaign Concept**: Clear, compelling campaign name and one-line pitch
2. **Strategic Rationale**: Why this campaign will work (2-3 sentences)
3. **Mini-Plan**:
   - Recommended channels and why
   - Content assets needed (types, quantities)
   - Suggested timeline (days/weeks)
   - Estimated effort level (low/medium/high)
4. **Success Metrics**: What defines success
5. **Risks**: What could go wrong

Return JSON:
{{
    "campaign_name": "Catchy campaign name",
    "one_line_pitch": "What this campaign does",
    "strategic_rationale": "Why this will work",
    "recommended_channels": [
        {{
            "channel": "linkedin|twitter|email|blog",
            "why": "Reason for this channel",
            "priority": "primary|secondary"
        }}
    ],
    "content_requirements": [
        {{
            "type": "blog|email|social_post|video|infographic",
            "quantity": 5,
            "purpose": "What this content achieves"
        }}
    ],
    "timeline": {{
        "duration_days": 14,
        "phases": [
            {{
                "name": "Phase name",
                "duration_days": 7,
                "key_milestones": ["milestone 1", "milestone 2"]
            }}
        ]
    }},
    "effort_level": "low|medium|high",
    "estimated_hours": 40,
    "success_metrics": ["metric 1", "metric 2", "metric 3"],
    "risks": ["risk 1", "risk 2"],
    "confidence": "high|medium|low",
    "priority_score": 7.5
}}
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": MASTER_SUPERVISOR_SYSTEM_PROMPT + "\nYou synthesize opportunities into actionable campaigns."
                },
                {"role": "user", "content": prompt}
            ]
            
            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            
            import json
            campaign_proposal = json.loads(response)
            
            # Add metadata
            campaign_proposal["source_opportunity"] = opportunity.get("title", "N/A")
            campaign_proposal["synthesized_at"] = datetime.utcnow().isoformat()
            
            logger.info(
                "Campaign idea synthesized",
                campaign_name=campaign_proposal.get("campaign_name", "N/A"),
                effort=campaign_proposal.get("effort_level", "N/A"),
                confidence=campaign_proposal.get("confidence", "N/A"),
                correlation_id=correlation_id
            )
            
            return campaign_proposal
            
        except Exception as e:
            logger.error(f"Campaign synthesis failed: {e}")
            return self._fallback_campaign(opportunity)
    
    async def batch_synthesize(
        self,
        opportunities: List[Dict],
        icps: List[Dict],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes multiple opportunities in batch.
        
        Args:
            opportunities: List of quick wins
            icps: User's ICPs
            limit: Max campaigns to synthesize
            
        Returns:
            List of campaign proposals
        """
        correlation_id = get_correlation_id()
        logger.info(
            "Batch synthesizing campaigns",
            num_opportunities=len(opportunities),
            limit=limit,
            correlation_id=correlation_id
        )
        
        campaigns = []
        for opp in opportunities[:limit]:
            try:
                campaign = await self.synthesize_campaign_idea(opp, icps)
                campaigns.append(campaign)
            except Exception as e:
                logger.error(f"Failed to synthesize opportunity: {e}")
        
        # Sort by priority score
        campaigns.sort(
            key=lambda x: x.get("priority_score", 0),
            reverse=True
        )
        
        logger.info(
            "Batch synthesis completed",
            campaigns_created=len(campaigns),
            correlation_id=correlation_id
        )
        
        return campaigns
    
    async def compare_campaigns(
        self,
        campaigns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compares multiple campaign proposals and recommends priority.
        
        Args:
            campaigns: List of campaign proposals
            
        Returns:
            Comparison analysis with recommendations
        """
        if not campaigns:
            return {"error": "No campaigns to compare"}
        
        # Build comparison context
        campaign_summaries = "\n\n".join([
            f"Campaign {idx + 1}: {c.get('campaign_name', 'N/A')}\n"
            f"Effort: {c.get('effort_level', 'N/A')}\n"
            f"Priority Score: {c.get('priority_score', 'N/A')}\n"
            f"Pitch: {c.get('one_line_pitch', 'N/A')}"
            for idx, c in enumerate(campaigns)
        ])
        
        prompt = f"""
Compare these campaign proposals and recommend which to prioritize:

{campaign_summaries}

Consider:
- Strategic fit and impact
- Resource requirements
- Timeline and urgency
- Risk vs. reward

Return JSON:
{{
    "recommended_order": [1, 3, 2],
    "reasoning": "Why this priority order",
    "quick_wins": ["Campaign names that are quick wins"],
    "strategic_bets": ["Campaign names that are strategic bets"],
    "skip": ["Campaign names to skip and why"]
}}
"""
        
        try:
            messages = [
                {"role": "system", "content": "You compare and prioritize campaign proposals."},
                {"role": "user", "content": prompt}
            ]
            
            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            import json
            comparison = json.loads(response)
            
            return comparison
            
        except Exception as e:
            logger.error(f"Campaign comparison failed: {e}")
            return {"error": str(e)}
    
    def _build_icp_context(self, icps: List[Dict]) -> str:
        """Builds ICP context string."""
        if not icps:
            return "No ICPs provided"
        
        icp_lines = []
        for icp in icps[:3]:  # Top 3 ICPs
            name = icp.get("name", "Unknown")
            summary = icp.get("executive_summary", "N/A")[:150]
            pain_points = ", ".join(icp.get("pain_points", [])[:3])
            
            icp_lines.append(
                f"- {name}: {summary}\n  Pain Points: {pain_points}"
            )
        
        return "\n".join(icp_lines)
    
    def _format_market_context(self, market_context: Dict) -> str:
        """Formats market context."""
        if not market_context:
            return ""
        
        return f"""
MARKET CONTEXT:
{market_context.get('summary', 'N/A')}

Key Insights:
{chr(10).join(['- ' + i for i in market_context.get('key_insights', [])])}
"""
    
    def _fallback_campaign(self, opportunity: Dict) -> Dict[str, Any]:
        """Fallback campaign if synthesis fails."""
        return {
            "campaign_name": opportunity.get("title", "Campaign"),
            "one_line_pitch": opportunity.get("description", "")[:200],
            "strategic_rationale": "Based on current opportunity",
            "recommended_channels": [{"channel": "linkedin", "why": "Default", "priority": "primary"}],
            "content_requirements": [{"type": "blog", "quantity": 1, "purpose": "Awareness"}],
            "timeline": {"duration_days": 14, "phases": []},
            "effort_level": "medium",
            "estimated_hours": 20,
            "success_metrics": ["Engagement", "Reach"],
            "risks": ["Unknown"],
            "confidence": "low",
            "priority_score": 5.0,
            "error": "Synthesis failed, using fallback"
        }


# Global instance
synthesis_agent = SynthesisAgent()

