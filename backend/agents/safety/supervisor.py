"""
Safety Supervisor (Tier 1) - Orchestrates content safety and compliance checks.

Responsibilities:
- Coordinate guardian agents (Brand, Privacy, Quality)
- Validate content against safety guidelines
- Enforce brand consistency
"""

from typing import Dict, List, Any, Optional
import logging

from backend.agents.base_agent import BaseSupervisor
from backend.agents.safety.brand_guardian import brand_guardian
from backend.agents.safety.privacy_guardian import privacy_guardian
from backend.agents.safety.critic_agent import critic_agent
from backend.utils.correlation import generate_correlation_id

logger = logging.getLogger(__name__)

class SafetySupervisor(BaseSupervisor):
    """
    Tier 1 Supervisor: Safety Domain.
    
    Orchestrates the Guardian Guild agents to ensure content quality, 
    safety, and brand compliance.
    """
    
    def __init__(self):
        super().__init__(name="safety_supervisor")
        
        # Register sub-agents
        self.register_agent("brand_guardian", brand_guardian)
        self.register_agent("privacy_guardian", privacy_guardian)
        self.register_agent("critic_agent", critic_agent)
        
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute safety checks.
        
        Args:
            payload: Dict containing:
                - content: The content to check
                - checks: List of checks to perform ["brand", "privacy", "quality"]
                - context: Additional context
        """
        correlation_id = payload.get("correlation_id") or generate_correlation_id()
        content = payload.get("content")
        checks = payload.get("checks", ["brand", "privacy", "quality"])
        context = payload.get("context", {})
        
        self.log(f"Safety supervisor execution: {checks}", correlation_id=correlation_id)
        
        results = {
            "status": "success",
            "safe": True,
            "issues": [],
            "scores": {}
        }
        
        try:
            # Run requested checks (could be parallelized)
            
            # 1. Privacy Check
            if "privacy" in checks:
                privacy_result = await privacy_guardian.execute({
                    "content": content,
                    "context": context
                })
                if privacy_result.get("status") == "success":
                    results["scores"]["privacy"] = privacy_result.get("score", 1.0)
                    if privacy_result.get("issues"):
                        results["issues"].extend(privacy_result["issues"])
                        results["safe"] = False

            # 2. Brand Check
            if "brand" in checks:
                brand_result = await brand_guardian.execute({
                    "content": content,
                    "context": context
                })
                if brand_result.get("status") == "success":
                    results["scores"]["brand"] = brand_result.get("score", 1.0)
                    if brand_result.get("issues"):
                        results["issues"].extend(brand_result["issues"])
                        # Brand issues might not be "unsafe" but require revision

            # 3. Quality/Critic Check
            if "quality" in checks:
                quality_result = await critic_agent.execute({
                    "content": content,
                    "context": context
                })
                if quality_result.get("status") == "success":
                    results["scores"]["quality"] = quality_result.get("score", 0.0)
                    results["critique"] = quality_result.get("critique")

            return results
                
        except Exception as e:
            logger.error(f"Safety execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "correlation_id": correlation_id
            }

# Global instance
safety_supervisor = SafetySupervisor()
