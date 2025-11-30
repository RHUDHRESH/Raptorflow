from typing import Dict, Any, List, Optional
import logging
from backend.services.vertex_ai_client import vertex_ai_client

logger = logging.getLogger(__name__)

class BasePillar:
    """Base class for Intelligence Pillars"""
    
    def __init__(self):
        self.ai = vertex_ai_client
        self.pillar_id = 0
        self.name = "Base Pillar"

    async def process(self, input_data: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process new input data and update the pillar state.
        """
        raise NotImplementedError

    async def identify_gaps(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify missing information (blind spots).
        """
        raise NotImplementedError

    def calculate_completeness(self, current_state: Dict[str, Any]) -> int:
        """
        Calculate completeness score (0-100).
        """
        return 0
