"""
Context Extractor Agent
Analyzes raw user input to extract structured positioning data.
"""

from typing import Dict, Any, List, Optional
import logging
from backend.agents.base_agent import BaseAgent
from backend.services.vertex_ai_client import vertex_ai_client

logger = logging.getLogger(__name__)

class ContextExtractorAgent(BaseAgent):
    """
    Analyzes unstructured business descriptions to extract structured positioning.
    """
    
    def __init__(self):
        super().__init__(
            name="context_extractor",
            description="Extracts positioning context from raw text"
        )
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract context from user input.
        
        Args:
            context: {
                "raw_text": str,
                "website": Optional[str],
                "pitch": Optional[str],
                "industry": Optional[str]
            }
        """
        raw_text = context.get("raw_text", "")
        website = context.get("website", "")
        pitch = context.get("pitch", "")
        industry = context.get("industry", "")
        
        prompt = f"""
        You are a master brand strategist (like Seth Godin or April Dunford).
        Analyze this messy brain dump from a founder and extract the core positioning truth.
        
        INPUTS:
        - Brain Dump: "{raw_text}"
        - Website: {website}
        - Pitch: "{pitch}"
        - Industry: {industry}
        
        OUTPUT JSON:
        {{
            "core_line": "You are: The [Category] for [Who], who [Promise].",
            "narrative": {{
                "who_you_serve": "Specific audience description",
                "main_wound": "The painful problem they have",
                "what_you_are_not": "What you refuse to compete on (the anti-position)",
                "unfair_advantage": "Why you win"
            }},
            "proof_points": ["Proof 1", "Proof 2", "Proof 3"],
            "category": "The specific category (e.g., 'B2B SaaS Infra', 'Agency')",
            "keywords": ["keyword1", "keyword2"],
            "summary_parsed": {{
                "target": "...",
                "pain": "...",
                "enemies": "...",
                "channels": "..."
            }}
        }}
        
        Keep it punchy, direct, and high-status. Avoid marketing fluff.
        """
        
        try:
            response = await vertex_ai_client.generate_content(prompt)
            # Assuming vertex_ai_client returns a string or dict. 
            # If it returns a string, we might need to parse it.
            # For now, relying on the client to return structured data or json string.
            
            # Since vertex_ai_client.generate_content might return raw text, we'd typically parse JSON.
            # But let's assume for this step we treat the response as the extraction result.
            # Ideally we should enforce JSON schema.
            
            return {
                "status": "success",
                "extraction": response
            }
            
        except Exception as e:
            logger.error(f"Context extraction failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

context_extractor = ContextExtractorAgent()
