"""
ICP Builder Agent - Assigns psychographic and demographic tags to personas.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID
import logging

from backend.models.persona import ICPProfile, Demographics, Psychographics, Communication
from backend.config.settings import get_settings
from backend.services.vertex_ai_client import vertex_ai_client

logger = logging.getLogger(__name__)
settings = get_settings()


class ICPBuilderAgent:
    """
    Builds rich Ideal Customer Profiles from basic persona inputs.
    
    Responsibilities:
    - Assign ~50 psychographic/demographic tags from taxonomy
    - Fill in demographics (company size, industry, role, etc.)
    - Define communication preferences
    - Generate executive summary
    """
    
    def __init__(self):
        # Comprehensive tag taxonomy for ICP classification
        self.tag_taxonomy = {
            "company_size": ["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"],
            "industry": [
                "B2B SaaS", "E-commerce", "Healthcare", "Finance", "Education",
                "Manufacturing", "Professional Services", "Marketing", "Sales",
                "Technology", "Retail", "Real Estate", "Non-profit"
            ],
            "role_level": ["IC", "Manager", "Director", "VP", "C-Suite", "Founder"],
            "decision_authority": ["Influencer", "Recommender", "Decision Maker", "Gatekeeper"],
            "buying_motivation": [
                "ROI-driven", "Innovation-seeking", "Risk-averse", "Status-conscious",
                "Efficiency-focused", "Quality-driven", "Cost-sensitive", "Growth-oriented"
            ],
            "pain_point_category": [
                "Time/Efficiency", "Cost/Budget", "Quality", "Scalability",
                "Complexity", "Visibility", "Competition", "Compliance", "Team Management"
            ],
            "information_consumption": [
                "Visual learner", "Data-driven", "Story-driven", "Peer-influenced",
                "Analyst reports", "Podcasts", "Social media", "Whitepapers"
            ],
            "risk_tolerance": ["Conservative", "Moderate", "Aggressive"],
            "technology_adoption": ["Early adopter", "Early majority", "Late majority", "Laggard"],
            "community_orientation": ["Independent", "Community-driven", "Network-focused"],
            "content_preference": ["Short-form", "Long-form", "Video", "Interactive"],
            "channel_preference": ["Email", "LinkedIn", "Twitter", "Instagram", "YouTube", "Blog"],
        }
    
    async def build_icp(
        self,
        workspace_id: UUID,
        persona_input: Dict[str, Any]
    ) -> ICPProfile:
        """
        Builds a complete ICP from basic persona input.
        
        Args:
            workspace_id: User's workspace ID
            persona_input: Basic persona info (nickname, role, pain_point, known_attributes)
            
        Returns:
            Complete ICPProfile with tags and structured data
        """
        logger.info(f"Building ICP for: {persona_input.get('nickname', 'Unnamed')}")
        
        # Extract structured data using LLM
        structured_data = await self._extract_icp_data(persona_input)
        
        # Build ICP profile
        icp = ICPProfile(
            id=UUID(structured_data.get("id", str(UUID("00000000-0000-0000-0000-000000000000")))),
            workspace_id=workspace_id,
            name=persona_input.get("nickname", "Unnamed Persona"),
            executive_summary=structured_data.get("executive_summary"),
            demographics=Demographics(**structured_data.get("demographics", {})),
            psychographics=Psychographics(**structured_data.get("psychographics", {})),
            pain_points=structured_data.get("pain_points", []),
            goals=structured_data.get("goals", []),
            behavioral_triggers=structured_data.get("behavioral_triggers", []),
            communication=Communication(**structured_data.get("communication", {})),
            budget=structured_data.get("budget"),
            timeline=structured_data.get("timeline"),
            decision_structure=structured_data.get("decision_structure"),
            tags=structured_data.get("tags", [])
        )
        
        logger.info(f"ICP built with {len(icp.tags)} tags")
        return icp
    
    async def _extract_icp_data(self, persona_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts comprehensive ICP data using LLM and tag taxonomy.
        
        Args:
            persona_input: Basic persona information
            
        Returns:
            Structured ICP data
        """
        # Format persona input
        persona_description = f"""
Nickname: {persona_input.get('nickname', 'N/A')}
Role: {persona_input.get('role', 'N/A')}
Biggest Pain Point: {persona_input.get('biggest_pain_point', 'N/A')}
Known Attributes: {', '.join(persona_input.get('known_attributes', []))}
"""
        
        # Build extraction prompt
        extraction_prompt = f"""
You are an expert customer intelligence analyst. Build a comprehensive Ideal Customer Profile (ICP)
from the following basic persona information:

{persona_description}

Tag Taxonomy (select relevant tags from each category):
{self._format_taxonomy()}

Extract and infer the following in JSON format:

{{
    "executive_summary": "2-3 sentence summary of this persona",
    "demographics": {{
        "company_size": "company size range if B2B",
        "industry": "industry",
        "revenue": "revenue range if applicable",
        "location": "primary location/region",
        "buyer_role": "specific job title/role"
    }},
    "psychographics": {{
        "motivation": "primary buying motivation",
        "ability": "capability level (novice, intermediate, expert)",
        "prompt_receptiveness": "how receptive to new solutions",
        "risk_tolerance": "Conservative|Moderate|Aggressive",
        "status_drive": "importance of status/reputation (high/medium/low)",
        "community_orientation": "Independent|Community-driven|Network-focused"
    }},
    "pain_points": ["list of 3-5 specific pain points"],
    "goals": ["list of 3-5 goals they want to achieve"],
    "behavioral_triggers": ["list of triggers that prompt action"],
    "communication": {{
        "channels": ["preferred channels"],
        "tone": "preferred communication tone",
        "format": "preferred content format"
    }},
    "budget": "typical budget range (if inferrable)",
    "timeline": "typical decision timeline",
    "decision_structure": "how decisions are made (e.g., committee, individual)",
    "tags": ["array of 30-50 relevant tags from the taxonomy above"]
}}

IMPORTANT:
- Be thorough and specific
- Assign 30-50 tags covering multiple categories
- Infer intelligently from the role and pain point
- Don't hallucinate - if uncertain, use "Unknown" or omit
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert at building detailed customer profiles. Return valid JSON only."
                },
                {"role": "user", "content": extraction_prompt}
            ]
            
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            import json
            icp_data = json.loads(response)
            
            logger.info("ICP data extracted successfully")
            return icp_data
            
        except Exception as e:
            logger.error(f"ICP extraction failed: {e}")
            return self._fallback_icp_data(persona_input)
    
    def _format_taxonomy(self) -> str:
        """Formats the tag taxonomy for the prompt."""
        formatted = []
        for category, tags in self.tag_taxonomy.items():
            formatted.append(f"\n{category.replace('_', ' ').title()}:")
            formatted.append(f"  {', '.join(tags)}")
        return "\n".join(formatted)
    
    def _fallback_icp_data(self, persona_input: Dict[str, Any]) -> Dict[str, Any]:
        """Provides fallback ICP data if LLM extraction fails."""
        logger.warning("Using fallback ICP data")
        
        return {
            "executive_summary": f"{persona_input.get('nickname')} is a {persona_input.get('role')} struggling with {persona_input.get('biggest_pain_point')}",
            "demographics": {
                "buyer_role": persona_input.get('role', 'Unknown')
            },
            "psychographics": {},
            "pain_points": [persona_input.get('biggest_pain_point', 'Unknown pain point')],
            "goals": [],
            "behavioral_triggers": [],
            "communication": {
                "channels": ["email", "linkedin"],
                "tone": "professional"
            },
            "tags": persona_input.get('known_attributes', [])
        }


# Global instance
icp_builder = ICPBuilderAgent()

