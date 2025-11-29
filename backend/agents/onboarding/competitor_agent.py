"""
Competitor Agent
Identifies competitors and plots them on the user's positioning graph.
"""

from typing import Dict, Any, List
import logging
from backend.agents.base_agent import BaseAgent
from backend.services.vertex_ai_client import vertex_ai_client

logger = logging.getLogger(__name__)

class CompetitorAgent(BaseAgent):
    """
    Identifies competitors and estimates their position on the selected frame.
    """
    
    def __init__(self):
        super().__init__(
            name="competitor_agent",
            description="Finds competitors and plots them"
        )
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find competitors and plot them.
        
        Args:
            context: {
                "industry": str,
                "context_summary": Dict,
                "axis_frame": Dict (The selected 2D frame)
            }
        """
        industry = context.get("industry", "")
        summary = context.get("context_summary", {})
        frame = context.get("axis_frame", {})
        
        prompt = f"""
        You are a market research expert.
        
        CONTEXT:
        - Industry: {industry}
        - User's Core Value: {summary.get('core_line')}
        
        SELECTED BATTLEFIELD (2D Graph):
        - X-Axis: {frame.get('x_axis', {}).get('label')} ({frame.get('x_axis', {}).get('left_label')} <-> {frame.get('x_axis', {}).get('right_label')})
        - Y-Axis: {frame.get('y_axis', {}).get('label')} ({frame.get('y_axis', {}).get('bottom_label')} <-> {frame.get('y_axis', {}).get('top_label')})
        
        TASK:
        1. Identify 5-8 well-known competitors or archetypes in this space.
        2. Estimate their coordinates (0-100) on the X and Y axes based on their public perception.
        3. Identify 1-2 "Growth Vectors" (opportunities for the user to move into white space).
        
        OUTPUT JSON:
        {{
            "competitors": [
                {{ "name": "Competitor A", "x": 20, "y": 80, "label": "The Incumbent" }},
                {{ "name": "Competitor B", "x": 85, "y": 30, "label": "The Niche Player" }}
            ],
            "growth_vectors": [
                {{ 
                    "title": "Move Upstream", 
                    "description": "Shift towards Enterprise (High Touch) while maintaining specialization.",
                    "vector": {{ "from": {{ "x": 50, "y": 50 }}, "to": {{ "x": 80, "y": 90 }} }}
                }}
            ]
        }}
        """
        
        try:
            response = await vertex_ai_client.generate_content(prompt)
            
            return {
                "status": "success",
                "analysis": response
            }
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

competitor_agent = CompetitorAgent()
