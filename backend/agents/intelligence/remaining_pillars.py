from typing import Dict, Any, List
import json
from .pillar_base import BasePillar

class DifferentiationPillar(BasePillar):
    def __init__(self):
        super().__init__()
        self.pillar_id = 3
        self.name = "Differentiation"
        
    async def process(self, input_data: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Extract Differentiation Intelligence:
        {json.dumps(input_data, default=str)}
        
        Find:
        - Unique Value Proposition
        - Defensible Moat (Data, Tech, Network, IP)
        - Time to Replicate (How long for copycats?)
        - Exclusive Partnerships
        """
        result = await self.ai.generate_json(prompt, model_type="reasoning")
        return {**current_state, **result}

    async def identify_gaps(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        gaps = []
        if not current_state.get("defensible_moat"):
            gaps.append({
                "id": "defensible_moat",
                "question": "What takes 2+ years to copy? (Data, Tech, Network)",
                "placeholder": "e.g. 500k unique datasets, Patent #123",
                "type": "text"
            })
        return gaps

class CompetitorPillar(BasePillar):
    def __init__(self):
        super().__init__()
        self.pillar_id = 4
        self.name = "Competitive Reality"
        
    async def process(self, input_data: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Extract Competitor Intelligence:
        {json.dumps(input_data, default=str)}
        
        Find:
        - Direct Competitors
        - Indirect Alternatives (e.g. Excel, Manual)
        - Status Quo (Doing nothing)
        - Why they lose to us?
        - Why we lose to them?
        """
        result = await self.ai.generate_json(prompt, model_type="reasoning")
        return {**current_state, **result}

    async def identify_gaps(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        gaps = []
        if not current_state.get("indirect_alternatives"):
            gaps.append({
                "id": "indirect_alternatives",
                "question": "What do they use if they don't buy software? (Excel? Manual?)",
                "type": "text"
            })
        return gaps

class DiscoveryPillar(BasePillar):
    def __init__(self):
        super().__init__()
        self.pillar_id = 5
        self.name = "Discovery Channels"
        
    async def process(self, input_data: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Extract Discovery Channel Intelligence:
        {json.dumps(input_data, default=str)}
        
        Find:
        - Search Terms / Keywords
        - Communities / Groups
        - Influencers
        - Events
        - Referral Sources
        """
        result = await self.ai.generate_json(prompt, model_type="reasoning")
        return {**current_state, **result}

    async def identify_gaps(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        gaps = []
        if not current_state.get("search_terms"):
            gaps.append({
                "id": "search_terms",
                "question": "What do they type into Google to find you?",
                "type": "text"
            })
        return gaps

class RemarkabilityPillar(BasePillar):
    def __init__(self):
        super().__init__()
        self.pillar_id = 6
        self.name = "Remarkability"
        
    async def process(self, input_data: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Extract Remarkability Intelligence:
        {json.dumps(input_data, default=str)}
        
        Find:
        - "Wait, WHAT?" moments
        - Viral loops
        - Word of mouth triggers
        - Unexpected guarantees
        """
        result = await self.ai.generate_json(prompt, model_type="reasoning")
        return {**current_state, **result}

    async def identify_gaps(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        gaps = []
        if not current_state.get("wow_moment"):
            gaps.append({
                "id": "wow_moment",
                "question": "What makes them say 'Wait, really?' or tell a friend?",
                "type": "text"
            })
        return gaps

class ProofPillar(BasePillar):
    def __init__(self):
        super().__init__()
        self.pillar_id = 7
        self.name = "Proof & Evidence"
        
    async def process(self, input_data: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Extract Proof Intelligence:
        {json.dumps(input_data, default=str)}
        
        Find:
        - Testimonials
        - Case Studies
        - Stats / Metrics
        - Logos / Badges
        - Ratings
        """
        result = await self.ai.generate_json(prompt, model_type="reasoning")
        return {**current_state, **result}

    async def identify_gaps(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        gaps = []
        if not current_state.get("testimonials"):
             gaps.append({
                "id": "testimonials",
                "question": "Can you provide 3 specific customer quotes?",
                "type": "text"
            })
        return gaps
