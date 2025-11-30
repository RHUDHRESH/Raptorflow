from typing import Dict, Any, List
import json
from .pillar_base import BasePillar

class ValuePillar(BasePillar):
    def __init__(self):
        super().__init__()
        self.pillar_id = 2
        self.name = "Value Proposition"
        
    async def process(self, input_data: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Extract Value Proposition Intelligence:
        {json.dumps(input_data, default=str)}
        
        Find:
        - Functional Value (What does it do?)
        - Economic/Quantified Value (ROI, Time Saved, Money Saved)
        - Emotional Value (How do they feel?)
        - Jobs to be Done
        """
        result = await self.ai.generate_json(prompt, model_type="reasoning")
        
        new_state = current_state.copy()
        for key, value in result.items():
            if value:
                new_state[key] = value
        return new_state

    async def identify_gaps(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        gaps = []
        if not current_state.get("quantified_value"):
            gaps.append({
                "id": "quantified_value",
                "question": "Give me a NUMBER. How much revenue gained or time saved?",
                "placeholder": "e.g. Saved 10 hours/week, Increased revenue by 20%",
                "type": "text"
            })
            
        if not current_state.get("emotional_value"):
             gaps.append({
                "id": "emotional_value",
                "question": "How does the customer FEEL after using this?",
                "placeholder": "e.g. Relieved, Confident, In Control",
                "type": "text"
            })
            
        return gaps

    def calculate_completeness(self, current_state: Dict[str, Any]) -> int:
        required = ["functional_value", "quantified_value", "emotional_value"]
        present = sum(1 for field in required if current_state.get(field))
        return int((present / len(required)) * 100)
