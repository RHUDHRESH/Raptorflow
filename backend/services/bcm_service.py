from typing import Any, Dict, List
from ..schemas.business_context import BusinessContext

class BCMService:
    """Service to convert BusinessContext to Business Context Map (BCM)."""
    
    @staticmethod
    def calculate_bcm(context: BusinessContext) -> Dict[str, Any]:
        """
        Transforms the flat business context into a semantic map (BCM).
        In a real scenario, this might involve generating vector embeddings 
        or complex relational graphs.
        """
        bcm = {
            "ucid": context.ucid,
            "nodes": [],
            "edges": [],
            "semantic_vectors": {} # Mocked for now
        }
        
        # Identity Node
        if context.identity.name:
            bcm["nodes"].append({
                "id": "identity",
                "type": "anchor",
                "label": context.identity.name,
                "data": context.identity.model_dump()
            })
            
        # Audience Node
        if context.audience.primary_segment:
            bcm["nodes"].append({
                "id": "audience",
                "type": "target",
                "label": context.audience.primary_segment,
                "data": context.audience.model_dump()
            })
            bcm["edges"].append({"source": "identity", "target": "audience", "relation": "serves"})
            
        # Positioning Node
        if context.positioning.category:
            bcm["nodes"].append({
                "id": "positioning",
                "type": "strategy",
                "label": context.positioning.category,
                "data": context.positioning.model_dump()
            })
            bcm["edges"].append({"source": "identity", "target": "positioning", "relation": "claims"})
            
        return bcm

    @staticmethod
    def sync_context_to_bcm(context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to sync raw dict context to BCM."""
        # Use partial validation if needed
        context = BusinessContext.model_validate(context_data, strict=False)
        return BCMService.calculate_bcm(context)
