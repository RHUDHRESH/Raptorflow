from typing import Dict, Any, List
import json
from .pillar_base import BasePillar

class AudiencePillar(BasePillar):
    def __init__(self):
        super().__init__()
        self.pillar_id = 1
        self.name = "Audience Intelligence"
        
    async def process(self, input_data: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract audience data from inputs"""
        prompt = f"""
        Extract Audience Intelligence from this data:
        {json.dumps(input_data, default=str)}
        
        Find:
        - Target Audience Description
        - Demographics (Age, Location, Role)
        - Psychographics (Values, Fears)
        - Buying Triggers (What event causes them to search?)
        - Decision Criteria (What matters most?)
        - Objections (Why wouldn't they buy?)
        """
        
        result = await self.ai.generate_json(prompt, model_type="reasoning")
        
        # Simple merge: overwrite with new non-empty values
        # In a real system, we'd use a smarter merge (e.g. list append or conflict resolution)
        new_state = current_state.copy()
        for key, value in result.items():
            if value:
                new_state[key] = value
                
        return new_state

    async def identify_gaps(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for missing audience info"""
        gaps = []
        
        if not current_state.get("demographics"):
            gaps.append({
                "id": "demographics",
                "question": "Who exactly is this for? (Age, Role, Location)",
                "placeholder": "e.g. Restaurant Owners, 35-50, Urban",
                "type": "text"
            })
            
        if not current_state.get("buying_trigger"):
            gaps.append({
                "id": "buying_trigger",
                "question": "What happens right before they buy? What's the trigger event?",
                "placeholder": "e.g. Just fired their agency, Revenue dropped",
                "type": "text"
            })
            
        if not current_state.get("objections"):
            gaps.append({
                "id": "objections",
                "question": "What almost stops them from buying?",
                "placeholder": "e.g. Price, Complexity, Trust",
                "type": "text"
            })
            
        return gaps

    def calculate_completeness(self, current_state: Dict[str, Any]) -> int:
        required_fields = ["demographics", "psychographics", "buying_trigger", "objections", "decision_criteria"]
        present = sum(1 for field in required_fields if current_state.get(field))
        return int((present / len(required_fields)) * 100)
