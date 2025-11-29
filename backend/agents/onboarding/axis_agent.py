"""
Axis Selector Agent
Generates dynamic 2D positioning frames based on business context.
"""

from typing import Dict, Any, List, Optional
import logging
from backend.agents.base_agent import BaseAgent
from backend.services.vertex_ai_client import vertex_ai_client

logger = logging.getLogger(__name__)

class AxisSelectorAgent(BaseAgent):
    """
    Selects the best 2D graphs to visualize a company's positioning.
    """
    
    def __init__(self):
        super().__init__(
            name="axis_selector",
            description="Generates positioning axes based on category"
        )
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate axis options.
        
        Args:
            context: {
                "category": str,
                "narrative": Dict,
                "keywords": List[str]
            }
        """
        category = context.get("category", "General Business")
        narrative = context.get("narrative", {})
        keywords = context.get("keywords", [])
        
        prompt = f"""
        You are a positioning expert. 
        Create 3 distinct "2D Positioning Frames" for a company in this category: "{category}".
        
        Context:
        - Audience: {narrative.get('who_you_serve')}
        - Problem: {narrative.get('main_wound')}
        - Keywords: {', '.join(keywords)}
        
        The goal is to find a graph where this company can claim a "Blue Ocean" or a unique corner.
        Avoid generic "Low Quality vs High Quality" axes. Use strategic tradeoffs (e.g. "Done-for-you vs DIY", "Enterprise vs SMB", "Integrated vs Best-of-breed").
        
        OUTPUT JSON:
        {{
            "frames": [
                {{
                    "id": "frame_1",
                    "name": "Strategy vs Execution (Example Name)",
                    "x_axis": {{
                        "label": "Generic <-> Specialist",
                        "left_label": "Broad / Generic",
                        "right_label": "Ultra-Niche Specialist",
                        "question": "Are you a one-size-fits-all solution or a category-of-one specialist?"
                    }},
                    "y_axis": {{
                        "label": "DIY <-> Done-For-You",
                        "bottom_label": "Pure DIY Tool",
                        "top_label": "White-Glove Service",
                        "question": "Do customers do the work themselves, or do you do it for them?"
                    }},
                    "q3": {{
                        "question": "If you had to sacrifice one thing, what would it be?",
                        "options": ["Being cheap", "Being fast", "Being comprehensive"]
                    }},
                    "quadrants": {{
                        "top_right": "Premium Partners",
                        "top_left": "Managed Services",
                        "bottom_right": "Niche Tools",
                        "bottom_left": "Commodity Platforms"
                    }}
                }},
                ... (2 more frames)
            ],
            "recommended_frame_id": "frame_1"
        }}
        """
        
        try:
            response = await vertex_ai_client.generate_content(prompt)
            
            return {
                "status": "success",
                "frames": response
            }
            
        except Exception as e:
            logger.error(f"Axis generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

axis_selector = AxisSelectorAgent()
