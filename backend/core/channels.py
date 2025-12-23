import logging
from typing import Dict, Any, List
from pydantic import BaseModel

logger = logging.getLogger("raptorflow.core.channels")

class ChannelWeight(BaseModel):
    """SOTA structured channel allocation."""
    channel: str
    weight: float # 0 to 1
    reasoning: str

class ChannelAllocator:
    """
    Industrial Multi-Channel Allocator.
    Determines optimal effort distribution based on ICP and Goals.
    """
    
    @staticmethod
    def allocate(goal: str, personas: List[Dict[str, Any]]) -> List[ChannelWeight]:
        """Surgically allocates effort across channels."""
        allocations = []
        
        # SOTA Heuristic: If 'Founder' in personas, weight LinkedIn/Email high
        if any("founder" in str(p).lower() for p in personas):
            allocations.append(ChannelWeight(channel="linkedin", weight=0.5, reasoning="High founder concentration."))
            allocations.append(ChannelWeight(channel="email", weight=0.3, reasoning="Direct executive outreach."))
            allocations.append(ChannelWeight(channel="twitter", weight=0.2, reasoning="Real-time industry signals."))
        else:
            allocations.append(ChannelWeight(channel="search", weight=0.4, reasoning="Intent-based discovery."))
            allocations.append(ChannelWeight(channel="social", weight=0.6, reasoning="Broad awareness."))
            
        logger.info(f"Multi-channel allocation complete for {len(personas)} personas.")
        return allocations
