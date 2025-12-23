from typing import Dict, Any
from backend.core.vault import Vault


def fetch_historical_performance_tool(campaign_id: str) -> Dict[str, Any]:
    """
    Synchronous tool to fetch aggregated performance outcomes for a campaign.
    """
    session = Vault().get_session()
    
    result = (
        session.table("blackbox_outcomes_industrial")
        .select("metric_value")
        .eq("campaign_id", campaign_id)
        .execute()
    )
    
    total_value = sum(float(row.get("metric_value", 0)) for row in result.data)
    
    return {
        "campaign_id": campaign_id,
        "total_value": total_value,
        "count": len(result.data),
        "status": "success"
    }