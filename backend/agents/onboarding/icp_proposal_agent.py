"""
ICP Proposal Agent
Proposes a set of Ideal Customer Profiles based on positioning.
"""

from typing import Dict, Any, List
import logging
from backend.agents.base_agent import BaseAgent
from backend.services.vertex_ai_client import vertex_ai_client

logger = logging.getLogger(__name__)

class ICPProposalAgent(BaseAgent):
    """
    Proposes candidate ICPs for the user to review.
    """
    
    def __init__(self):
        super().__init__(
            name="icp_proposal_agent",
            description="Proposes ICP candidates"
        )
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propose ICPs.
        
        Args:
            context: {
                "industry": str,
                "context_summary": Dict,
                "positioning": Dict
            }
        """
        industry = context.get("industry", "")
        summary = context.get("context_summary", {})
        positioning = context.get("positioning", {})
        
        prompt = f"""
        You are a growth strategist.
        Based on this company's positioning, propose 3 distinct "Ideal Customer Profiles" (ICPs) they should target.
        
        CONTEXT:
        - Industry: {industry}
        - Core Value: {summary.get('core_line')}
        - Positioning Frame: {positioning.get('frame_data', {}).get('name')}
        
        OUTPUT JSON:
        {{
            "icps": [
                {{
                    "title": "The Frustrated Enterprise Director",
                    "summary": "Mid-level execs at F500 companies who are tired of slow legacy tools.",
                    "why_target": "High budget, high pain, willing to switch for speed."
                }},
                {{
                    "title": "The Scaling Agency Owner",
                    "summary": "Founders of 10-50 person agencies needing to automate operations.",
                    "why_target": "Matches your 'Done-for-you' positioning perfectly."
                }},
                {{
                    "title": "The Technical Marketer",
                    "summary": "Marketing ops pros who want API access and power features.",
                    "why_target": "They value your 'Specialist' feature set."
                }}
            ]
        }}
        """
        
        try:
            response = await vertex_ai_client.generate_content(prompt)
            
            return {
                "status": "success",
                "proposal": response
            }
            
        except Exception as e:
            logger.error(f"ICP proposal failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

icp_proposal_agent = ICPProposalAgent()
