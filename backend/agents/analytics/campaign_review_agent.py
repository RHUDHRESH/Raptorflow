"""
Campaign Review Agent - Generates post-mortem reports for completed campaigns.
Summarizes performance, learnings, and recommendations for future campaigns.
"""

import json
import structlog
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.supabase_client import supabase_client
from backend.models.campaign import MoveDecision
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class CampaignReviewAgent:
    """
    Generates comprehensive post-mortem reports for campaigns.
    Captures learnings, ROI analysis, and recommendations.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
    
    async def generate_post_mortem(
        self,
        workspace_id: UUID,
        move_id: UUID,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive campaign review.
        
        Args:
            workspace_id: User's workspace
            move_id: Completed campaign ID
            
        Returns:
            Post-mortem report dict
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Generating campaign post-mortem", move_id=move_id, correlation_id=correlation_id)
        
        # Fetch campaign data
        move_data = await supabase_client.fetch_one(
            "moves",
            {"id": str(move_id), "workspace_id": str(workspace_id)}
        )
        
        if not move_data:
            raise ValueError(f"Move {move_id} not found")
        
        # Fetch all metrics
        metrics_data = await supabase_client.fetch_all(
            "metrics_snapshot",
            {"workspace_id": str(workspace_id), "move_id": str(move_id)}
        )
        
        # Fetch decisions made during campaign
        decisions = await supabase_client.fetch_all(
            "move_decisions",
            {"move_id": str(move_id)}
        )
        
        # Fetch anomalies
        anomalies = await supabase_client.fetch_all(
            "move_anomalies",
            {"move_id": str(move_id)}
        )
        
        # Generate report using AI
        report = await self._generate_report(
            move_data,
            metrics_data,
            decisions,
            anomalies,
            correlation_id
        )
        
        # Store report
        await supabase_client.insert("campaign_reports", {
            "workspace_id": str(workspace_id),
            "move_id": str(move_id),
            "report": report,
            "generated_at": datetime.utcnow().isoformat()
        })
        
        return report
    
    async def _generate_report(
        self,
        move_data: Dict,
        metrics_data: List[Dict],
        decisions: List[Dict],
        anomalies: List[Dict],
        correlation_id: str
    ) -> Dict[str, Any]:
        """Uses AI to generate comprehensive post-mortem."""
        
        # Calculate overall metrics
        total_impressions = sum(m.get("metrics", {}).get("impressions", 0) for m in metrics_data)
        total_engagement = sum(m.get("metrics", {}).get("engagement", 0) for m in metrics_data)
        total_clicks = sum(m.get("metrics", {}).get("clicks", 0) for m in metrics_data)
        
        summary_stats = {
            "total_impressions": total_impressions,
            "total_engagement": total_engagement,
            "total_clicks": total_clicks,
            "engagement_rate": total_engagement / total_impressions if total_impressions > 0 else 0,
            "ctr": total_clicks / total_impressions if total_impressions > 0 else 0
        }
        
        prompt = f"""Generate a comprehensive post-mortem report for this marketing campaign.

**Campaign Overview**:
- Name: {move_data.get('name')}
- Goal: {move_data.get('goal')}
- Duration: {move_data.get('start_date')} to {move_data.get('end_date')}
- Channels: {', '.join(move_data.get('channels', []))}
- Status: {move_data.get('status')}

**Performance Summary**:
{json.dumps(summary_stats, indent=2)}

**Decisions Made** ({len(decisions)} total):
{json.dumps(decisions[:5], indent=2)}

**Anomalies Detected** ({len(anomalies)} total):
{json.dumps(anomalies, indent=2)}

**Report Structure**:
Generate a JSON report with:
1. executive_summary (3-4 sentences)
2. performance_highlights (top 3 wins)
3. challenges_faced (top 3 issues)
4. key_learnings (5-7 insights)
5. roi_analysis (estimated value delivered)
6. best_performing_content (what worked)
7. worst_performing_content (what didn't)
8. recommendations_future (5 actionable tips)
9. overall_grade (A+ to F with rationale)

Be specific, data-driven, and actionable.
"""
        
        messages = [
            {"role": "system", "content": "You are a senior marketing analyst creating campaign post-mortems. Be thorough, honest, and actionable."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use creative model for comprehensive narrative
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="creative",
                temperature=0.5,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            
            report = json.loads(llm_response)
            report["campaign_id"] = str(move_data["id"])
            report["campaign_name"] = move_data["name"]
            report["generated_at"] = datetime.utcnow().isoformat()
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}", correlation_id=correlation_id)
            return {
                "error": str(e),
                "executive_summary": "Report generation failed due to an error."
            }
    
    async def extract_learnings(
        self,
        workspace_id: UUID,
        timeframe_days: int = 90,
        correlation_id: str = None
    ) -> List[str]:
        """
        Extracts key learnings across all recent campaigns.
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Extracting cross-campaign learnings", correlation_id=correlation_id)
        
        cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)
        
        # Fetch all completed moves
        moves = await supabase_client.fetch_all(
            "moves",
            {"workspace_id": str(workspace_id), "status": "completed"}
        )
        
        # Fetch their reports
        reports = []
        for move in moves:
            report_data = await supabase_client.fetch_one(
                "campaign_reports",
                {"move_id": move["id"]}
            )
            if report_data:
                reports.append(report_data["report"])
        
        if not reports:
            return ["No completed campaigns to analyze yet."]
        
        # Synthesize learnings
        prompt = f"""Analyze these {len(reports)} campaign reports and extract 10 key learnings.

**Reports**:
{json.dumps([r.get("key_learnings", []) for r in reports], indent=2)}

Output as JSON array of learning statements. Make them specific, actionable, and pattern-based.
"""
        
        messages = [
            {"role": "system", "content": "You are a marketing strategist identifying patterns across campaigns."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="reasoning",
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            learnings = json.loads(llm_response)
            if not isinstance(learnings, list):
                learnings = [learnings]
            
            return learnings
            
        except Exception as e:
            logger.error(f"Failed to extract learnings: {e}", correlation_id=correlation_id)
            return ["Failed to synthesize learnings."]


campaign_review_agent = CampaignReviewAgent()



