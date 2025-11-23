"""
Ambient Search Agent - Runs daily background scans for timely opportunities.
"""

import structlog
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4

from backend.config.prompts import MASTER_SUPERVISOR_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class AmbientSearchAgent:
    """
    Continuously monitors environment for marketing opportunities.
    
    Monitors:
    - External signals: News, trends, Google Trends, industry events
    - Internal signals: Customer emails, support tickets, sales calls
    - Competitive moves: Competitor announcements, campaigns
    - Seasonal events: Holidays, industry conferences
    
    Responsibilities:
    - Run daily background scans
    - Identify timely opportunities matched to ICPs
    - Surface "quick wins" - time-sensitive campaign ideas
    - Store suggestions in quick_wins table with ICP tags
    """
    
    def __init__(self):
        self.signal_types = [
            "trending_topic",
            "breaking_news",
            "seasonal_event",
            "competitor_move",
            "customer_feedback",
            "industry_shift"
        ]
    
    async def run_daily_scan(
        self,
        workspace_id: UUID,
        icps: List[Dict[str, Any]],
        user_industry: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Runs daily ambient scan for opportunities.
        
        Args:
            workspace_id: User's workspace
            icps: User's ICPs for matching
            user_industry: User's industry for relevance filtering
            
        Returns:
            List of discovered opportunities (quick wins)
        """
        correlation_id = get_correlation_id()
        logger.info(
            "Running daily ambient scan",
            workspace_id=workspace_id,
            num_icps=len(icps),
            correlation_id=correlation_id
        )
        
        opportunities = []
        
        # Scan external signals
        external_opps = await self._scan_external_signals(user_industry)
        opportunities.extend(external_opps)
        
        # Scan internal signals
        internal_opps = await self._scan_internal_signals(workspace_id)
        opportunities.extend(internal_opps)
        
        # Match opportunities to ICPs
        matched_opportunities = await self._match_to_icps(opportunities, icps)
        
        # Store in database
        await self._store_opportunities(workspace_id, matched_opportunities)
        
        logger.info(
            "Ambient scan completed",
            opportunities_found=len(matched_opportunities),
            correlation_id=correlation_id
        )
        
        return matched_opportunities
    
    async def _scan_external_signals(
        self,
        industry: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Scans external environment for signals.
        In production, this would call real APIs (Google Trends, news APIs, etc.)
        For now, we simulate with LLM.
        """
        industry_context = f" in the {industry} industry" if industry else ""
        
        prompt = f"""
You are monitoring the external environment for marketing opportunities{industry_context}.

Identify 3-5 current trends, events, or opportunities happening RIGHT NOW that could be leveraged for marketing campaigns.

Consider:
- Trending topics on social media
- Recent news or industry developments
- Upcoming seasonal events (next 30 days)
- Cultural moments or holidays
- Industry conferences or events

Return JSON:
{{
    "opportunities": [
        {{
            "title": "Opportunity title",
            "signal_type": "trending_topic|breaking_news|seasonal_event|industry_shift",
            "description": "What's happening",
            "why_now": "Why this is timely",
            "expires_at": "YYYY-MM-DD (when opportunity expires)",
            "potential_channels": ["channel1", "channel2"],
            "suggested_content_angles": ["angle 1", "angle 2"]
        }}
    ]
}}
"""
        
        try:
            messages = [
                {"role": "system", "content": "You are an opportunity scanner monitoring external signals."},
                {"role": "user", "content": prompt}
            ]
            
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.8,  # Higher for creative opportunities
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response)
            
            opportunities = result.get("opportunities", [])
            
            # Add metadata
            for opp in opportunities:
                opp["source"] = "external_scan"
                opp["discovered_at"] = datetime.now(timezone.utc).isoformat()
            
            return opportunities
            
        except Exception as e:
            logger.error(f"External signal scan failed: {e}")
            return []
    
    async def _scan_internal_signals(
        self,
        workspace_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Scans internal signals (customer feedback, support tickets).
        """
        try:
            # Fetch recent support feedback
            feedback_records = await supabase_client.fetch_all(
                "support_feedback",
                filters={"workspace_id": str(workspace_id)}
            )
            
            if not feedback_records:
                return []
            
            # Sample recent feedback
            recent_feedback = feedback_records[:10]
            feedback_text = "\n".join([
                f"- {f.get('message', 'N/A')[:200]}"
                for f in recent_feedback
            ])
            
            prompt = f"""
Analyze this customer feedback for content opportunities:

{feedback_text}

Identify 2-3 content or campaign opportunities based on:
- Common questions or pain points
- Feature requests that could be marketed
- Success stories or wins
- Objections that need addressing

Return JSON:
{{
    "opportunities": [
        {{
            "title": "Opportunity title",
            "signal_type": "customer_feedback",
            "description": "What customers are saying",
            "why_now": "Why this matters now",
            "potential_content": ["content idea 1", "content idea 2"]
        }}
    ]
}}
"""
            
            messages = [
                {"role": "system", "content": "You analyze customer feedback for marketing opportunities."},
                {"role": "user", "content": prompt}
            ]
            
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response)
            opportunities = result.get("opportunities", [])
            
            for opp in opportunities:
                opp["source"] = "internal_signals"
                opp["discovered_at"] = datetime.now(timezone.utc).isoformat()
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Internal signal scan failed: {e}")
            return []
    
    async def _match_to_icps(
        self,
        opportunities: List[Dict],
        icps: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Matches opportunities to relevant ICPs.
        """
        if not opportunities or not icps:
            return opportunities
        
        # Create ICP summary
        icp_summaries = "\n".join([
            f"- {icp.get('name', 'Unknown')}: {icp.get('executive_summary', 'N/A')[:150]}, Tags: {', '.join(icp.get('tags', [])[:5])}"
            for icp in icps[:5]
        ])
        
        for opp in opportunities:
            prompt = f"""
Match this opportunity to relevant ICPs:

OPPORTUNITY:
{opp.get('title', 'N/A')}: {opp.get('description', 'N/A')}

ICPS:
{icp_summaries}

Return JSON:
{{
    "matched_icp_names": ["ICP name 1", "ICP name 2"],
    "relevance_reasoning": "Why this matches these ICPs",
    "campaign_angle": "How to position this for these ICPs"
}}
"""
            
            try:
                messages = [
                    {"role": "system", "content": "You match opportunities to ICPs."},
                    {"role": "user", "content": prompt}
                ]
                
                response = await vertex_ai_client.chat_completion(
                    messages=messages,
                    temperature=0.4,
                    response_format={"type": "json_object"}
                )
                
                import json
                match_result = json.loads(response)
                
                opp["matched_icps"] = match_result.get("matched_icp_names", [])
                opp["relevance_reasoning"] = match_result.get("relevance_reasoning", "")
                opp["campaign_angle"] = match_result.get("campaign_angle", "")
                
            except Exception as e:
                logger.error(f"ICP matching failed for opportunity: {e}")
                opp["matched_icps"] = []
        
        return opportunities
    
    async def _store_opportunities(
        self,
        workspace_id: UUID,
        opportunities: List[Dict]
    ) -> None:
        """
        Stores opportunities in quick_wins table.
        """
        for opp in opportunities:
            try:
                quick_win_data = {
                    "id": str(uuid4()),
                    "workspace_id": str(workspace_id),
                    "title": opp.get("title", "Untitled Opportunity"),
                    "description": opp.get("description", ""),
                    "signal_type": opp.get("signal_type", "unknown"),
                    "source": opp.get("source", "ambient_scan"),
                    "matched_icp_names": opp.get("matched_icps", []),
                    "campaign_angle": opp.get("campaign_angle", ""),
                    "expires_at": opp.get("expires_at"),
                    "status": "new",
                    "discovered_at": opp.get("discovered_at", datetime.now(timezone.utc).isoformat())
                }
                
                await supabase_client.insert("quick_wins", quick_win_data)
                
            except Exception as e:
                logger.error(f"Failed to store opportunity: {e}")
    
    async def get_active_opportunities(
        self,
        workspace_id: UUID,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retrieves active (non-expired) opportunities.
        """
        try:
            # Fetch all quick wins for workspace
            opportunities = await supabase_client.fetch_all(
                "quick_wins",
                filters={"workspace_id": str(workspace_id)}
            )
            
            # Filter non-expired
            now = datetime.now(timezone.utc)
            active = [
                opp for opp in opportunities
                if not opp.get("expires_at") or 
                datetime.fromisoformat(opp["expires_at"]) > now
            ]
            
            # Sort by discovered_at (newest first)
            active.sort(
                key=lambda x: x.get("discovered_at", ""),
                reverse=True
            )
            
            return active[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get active opportunities: {e}")
            return []


# Global instance
ambient_search = AmbientSearchAgent()

