import logging
from typing import Dict, Any, List
from backend.agents.specialists.campaign_planner import CampaignArcOutput

logger = logging.getLogger("raptorflow.core.briefing")

class BriefGenerator:
    """
    Industrial Campaign Brief Generator.
    Synthesizes strategic arcs into surgical markdown documents.
    """
    
    @staticmethod
    def generate_markdown(arc: CampaignArcOutput) -> str:
        """Converts a campaign arc into a SOTA executive brief."""
        md = f"# 📋 CAMPAIGN BRIEF: {arc.campaign_title}\n\n"
        md += f"## OVERALL OBJECTIVE\n{arc.overall_objective}\n\n"
        
        md += "## 🗓️ 90-DAY STRATEGIC ARC\n"
        for month in arc.monthly_arcs:
            md += f"### Month {month.month_number}: {month.theme}\n"
            for ms in month.milestones:
                md += f"- **{ms.title}:** {ms.description} (KPI: {ms.target_kpi})\n"
            md += "\n"
            
        md += "## 📈 SUCCESS METRICS\n"
        for metric in arc.success_metrics:
            md += f"- {metric}\n"
            
        logger.info(f"Brief generated for: {arc.campaign_title}")
        return md
