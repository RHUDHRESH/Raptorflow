"""
Insight Agent - Analyzes metrics to generate actionable insights.
Identifies underperforming channels, suggests pivots, and detects anomalies.
"""

import json
import structlog
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.supabase_client import supabase_client
from backend.models.campaign import MoveAnomaly
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class InsightAgent:
    """
    Analyzes performance data and generates strategic insights.
    Uses AI to identify patterns, anomalies, and opportunities.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
    
    async def analyze_performance(
        self,
        workspace_id: UUID,
        move_id: UUID,
        time_period_days: int = 30,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Analyzes campaign performance and generates insights.
        
        Args:
            workspace_id: User's workspace
            move_id: Campaign to analyze
            time_period_days: Lookback period
            
        Returns:
            Insights dict with recommendations
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Analyzing performance", move_id=move_id, correlation_id=correlation_id)
        
        # Fetch historical metrics
        cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
        metrics_data = await supabase_client.fetch_all(
            "metrics_snapshot",
            {"workspace_id": str(workspace_id), "move_id": str(move_id)}
        )
        
        # Filter by date
        recent_metrics = [
            m for m in metrics_data 
            if datetime.fromisoformat(m["collected_at"]) >= cutoff_date
        ]
        
        if not recent_metrics:
            return {
                "status": "insufficient_data",
                "message": "Not enough data to generate insights"
            }
        
        # Use AI to analyze
        insights = await self._generate_insights(recent_metrics, correlation_id)
        
        # Detect anomalies
        anomalies = await self._detect_anomalies(move_id, recent_metrics, correlation_id)
        
        # Store anomalies
        for anomaly in anomalies:
            await supabase_client.insert("move_anomalies", anomaly.model_dump())
        
        return {
            "insights": insights,
            "anomalies": [a.model_dump() for a in anomalies],
            "analyzed_period_days": time_period_days,
            "data_points": len(recent_metrics)
        }
    
    async def _generate_insights(
        self,
        metrics_data: List[Dict],
        correlation_id: str
    ) -> List[Dict[str, str]]:
        """Uses AI to generate insights from metrics."""
        
        # Summarize metrics for LLM
        metrics_summary = json.dumps(metrics_data[-20:])  # Last 20 snapshots
        
        prompt = f"""Analyze this marketing campaign performance data and generate 3-5 actionable insights.

**Metrics Data** (chronological):
{metrics_summary}

**Analysis Tasks**:
1. Identify which platforms are performing best/worst
2. Spot engagement trends (improving, declining, stagnant)
3. Compare metrics to industry benchmarks (estimate if needed)
4. Suggest specific actions to improve performance
5. Highlight any concerning patterns

Output as JSON array:
[
  {{
    "type": "opportunity|warning|trend",
    "title": "Brief insight title",
    "description": "Detailed explanation with data",
    "recommendation": "Specific action to take",
    "priority": "high|medium|low"
  }}
]
"""
        
        messages = [
            {"role": "system", "content": "You are a data analyst specializing in marketing analytics. Provide clear, actionable insights."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use reasoning model for deep analysis
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="reasoning",
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            insights = json.loads(llm_response)
            if not isinstance(insights, list):
                insights = [insights]
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}", correlation_id=correlation_id)
            return [{
                "type": "error",
                "title": "Analysis Failed",
                "description": str(e),
                "recommendation": "Retry analysis",
                "priority": "low"
            }]
    
    async def _detect_anomalies(
        self,
        move_id: UUID,
        metrics_data: List[Dict],
        correlation_id: str
    ) -> List[MoveAnomaly]:
        """Detects anomalies in performance metrics."""
        
        anomalies = []
        
        # Simple rule-based detection (can be enhanced with ML)
        for i, metric in enumerate(metrics_data[-5:]):  # Check last 5 snapshots
            platform = metric.get("platform")
            metrics = metric.get("metrics", {})
            
            # Detect sudden drops
            if i > 0:
                prev_metrics = metrics_data[-(6-i)].get("metrics", {})
                
                # Check engagement drop
                current_engagement = metrics.get("engagement", 0)
                prev_engagement = prev_metrics.get("engagement", 0)
                
                if prev_engagement > 0 and current_engagement < prev_engagement * 0.5:
                    anomalies.append(MoveAnomaly(
                        move_id=move_id,
                        type="underperformance",
                        description=f"{platform} engagement dropped by {int((1 - current_engagement/prev_engagement) * 100)}%",
                        severity="high",
                        resolution_suggestion=f"Review recent {platform} content quality and posting times"
                    ))
        
        return anomalies
    
    async def suggest_pivot(
        self,
        workspace_id: UUID,
        move_id: UUID,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Suggests strategic pivots based on performance analysis.
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Suggesting pivot", move_id=move_id, correlation_id=correlation_id)
        
        # Get performance analysis
        performance = await self.analyze_performance(workspace_id, move_id, 14, correlation_id)
        
        # Get move details
        move_data = await supabase_client.fetch_one("moves", {"id": str(move_id)})
        
        prompt = f"""Based on this campaign's performance, suggest a strategic pivot.

**Campaign**: {move_data.get('name')}
**Current Performance**: {json.dumps(performance)}

**Pivot Options**:
1. Channel Shift (move budget from underperforming to high-performing channels)
2. Content Format Change (try different formats)
3. Audience Refinement (adjust targeting)
4. Timing Optimization (change posting schedule)
5. Messaging Adjustment (update value proposition)

Suggest the best pivot with rationale. Output as JSON:
{{
  "pivot_type": "channel_shift|format_change|audience|timing|messaging",
  "recommendation": "Specific action",
  "rationale": "Why this pivot",
  "expected_impact": "Predicted outcome",
  "effort": "low|medium|high"
}}
"""
        
        messages = [
            {"role": "system", "content": "You are a marketing strategist specializing in campaign optimization."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="reasoning",
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            
            return json.loads(llm_response)
            
        except Exception as e:
            logger.error(f"Failed to suggest pivot: {e}", correlation_id=correlation_id)
            return {"error": str(e)}


insight_agent = InsightAgent()



