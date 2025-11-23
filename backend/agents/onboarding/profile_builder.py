"""
Profile Builder Agent - Constructs structured OnboardingProfile from Q&A.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID
import logging

from backend.models.onboarding import (
    OnboardingProfile,
    BusinessProfile,
    PersonalBrandProfile,
    ExecutiveBrandProfile,
    AgencyProfile,
    Goal,
    Constraints,
    ChannelFootprint,
    PersonaInput,
    StylePreferences,
)
from backend.config.settings import get_settings
from backend.services.vertex_ai_client import vertex_ai_client

logger = logging.getLogger(__name__)
settings = get_settings()


class ProfileBuilderAgent:
    """
    Constructs a structured OnboardingProfile from conversational Q&A.
    
    Responsibilities:
    - Parse natural language answers into structured data
    - Fill in entity-specific profile fields
    - Extract goals, constraints, and preferences
    - Generate initial persona inputs from user descriptions
    """
    
    async def build_profile(
        self,
        workspace_id: UUID,
        entity_type: str,
        answers: List[Dict[str, str]]
    ) -> OnboardingProfile:
        """
        Builds a complete OnboardingProfile from answers.
        
        Args:
            workspace_id: User's workspace ID
            entity_type: Type of entity (business, personal_brand, executive, agency)
            answers: List of Q&A pairs
            
        Returns:
            Structured OnboardingProfile
        """
        logger.info(f"Building profile for entity_type: {entity_type}")
        
        # Extract structured data using LLM
        structured_data = await self._extract_structured_data(entity_type, answers)
        
        # Build entity-specific profile
        entity_profile = None
        if entity_type == "business":
            entity_profile_data = structured_data.get("business", {})
            entity_profile = BusinessProfile(**entity_profile_data) if entity_profile_data else None
        elif entity_type == "personal_brand":
            entity_profile_data = structured_data.get("personal_brand", {})
            entity_profile = PersonalBrandProfile(**entity_profile_data) if entity_profile_data else None
        elif entity_type == "executive":
            entity_profile_data = structured_data.get("executive", {})
            entity_profile = ExecutiveBrandProfile(**entity_profile_data) if entity_profile_data else None
        elif entity_type == "agency":
            entity_profile_data = structured_data.get("agency", {})
            entity_profile = AgencyProfile(**entity_profile_data) if entity_profile_data else None
        
        # Extract universal fields
        goals = [Goal(**g) for g in structured_data.get("goals", [])]
        constraints = Constraints(**structured_data.get("constraints", {}))
        channels = ChannelFootprint(**structured_data.get("channels", {}))
        personas = [PersonaInput(**p) for p in structured_data.get("personas", [])]
        style_preferences = StylePreferences(**structured_data.get("style_preferences", {}))
        
        # Construct profile
        profile = OnboardingProfile(
            workspace_id=workspace_id,
            entity_type=entity_type,
            business=entity_profile if entity_type == "business" else None,
            personal_brand=entity_profile if entity_type == "personal_brand" else None,
            executive=entity_profile if entity_type == "executive" else None,
            agency=entity_profile if entity_type == "agency" else None,
            clarity_statement=structured_data.get("clarity_statement"),
            goals=goals,
            constraints=constraints,
            channels=channels,
            personas=personas,
            style_preferences=style_preferences
        )
        
        logger.info(f"Profile built successfully with {len(goals)} goals and {len(personas)} personas")
        return profile
    
    async def _extract_structured_data(
        self,
        entity_type: str,
        answers: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Extracts structured data from natural language answers using LLM.
        
        Args:
            entity_type: Type of entity
            answers: List of Q&A pairs
            
        Returns:
            Structured dictionary matching OnboardingProfile schema
        """
        # Format conversation for LLM
        conversation = "\n\n".join([
            f"Q: {qa['question_text']}\nA: {qa['answer']}"
            for qa in answers
        ])
        
        # Define expected schema based on entity type
        schema_example = self._get_schema_example(entity_type)
        
        extraction_prompt = f"""
Extract structured data from the following onboarding conversation.
The user is a: {entity_type}

Conversation:
{conversation}

Extract the following fields in JSON format:
{schema_example}

IMPORTANT:
- Extract ALL information mentioned in the answers
- Infer reasonable defaults for missing fields
- For personas, extract nickname, role, and pain points
- For goals, extract description and any mentioned timeframes
- For channels, mark as true if the user mentions using them
- Be thorough but accurate - don't hallucinate information

Return ONLY valid JSON matching the schema.
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert at extracting structured data from natural language. Return only valid JSON."
                },
                {"role": "user", "content": extraction_prompt}
            ]
            
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more accurate extraction
                response_format={"type": "json_object"}
            )
            
            import json
            structured_data = json.loads(response)
            
            logger.info("Successfully extracted structured data")
            return structured_data
            
        except Exception as e:
            logger.error(f"Structured data extraction failed: {e}")
            # Return minimal structure as fallback
            return self._fallback_extraction(entity_type, answers)
    
    def _get_schema_example(self, entity_type: str) -> str:
        """Returns JSON schema example based on entity type."""
        base_schema = """
{
    "clarity_statement": "one-line description",
    "goals": [
        {
            "description": "goal description",
            "timeframe_days": 90,
            "priority": "high|medium|low",
            "metrics": ["metric1", "metric2"]
        }
    ],
    "constraints": {
        "budget_monthly": "$10,000",
        "team_size": 3,
        "time_commitment_hours_per_week": 20,
        "content_restrictions": []
    },
    "channels": {
        "linkedin": true,
        "twitter": false,
        "instagram": false,
        "email": true,
        "blog": true
    },
    "personas": [
        {
            "nickname": "Scaling Sarah",
            "role": "VP of Sales",
            "biggest_pain_point": "Missing sales targets",
            "known_attributes": ["mid-market", "B2B"]
        }
    ],
    "style_preferences": {
        "tone": "professional|casual|inspirational",
        "formality_level": 7,
        "emoji_usage": "minimal|moderate",
        "average_post_length": "medium"
    }
"""
        
        entity_schemas = {
            "business": """
    "business": {
        "company_name": "Company Name",
        "industry": "Industry",
        "company_size": "11-50",
        "revenue_range": "$1M-$5M",
        "target_market": "B2B mid-market",
        "value_proposition": "What makes you different",
        "competitive_advantages": ["advantage1", "advantage2"],
        "proof_points": ["500+ customers", "30% avg increase"]
    }
""",
            "personal_brand": """
    "personal_brand": {
        "name": "Full Name",
        "niche": "Area of expertise",
        "expertise_areas": ["area1", "area2"],
        "current_audience_size": 5000,
        "unique_perspective": "What makes you unique",
        "content_pillars": ["pillar1", "pillar2"],
        "monetization_model": "courses|consulting|sponsorships"
    }
""",
            "executive": """
    "executive": {
        "executive_name": "Full Name",
        "company": "Company Name",
        "title": "Job Title",
        "industry_focus": "Industry",
        "thought_leadership_topics": ["topic1", "topic2"],
        "speaking_experience": "conferences, keynotes",
        "publications": ["article1", "book1"],
        "board_positions": []
    }
""",
            "agency": """
    "agency": {
        "agency_name": "Agency Name",
        "client_name": "Client Name",
        "client_industry": "Industry",
        "campaign_objectives": ["objective1", "objective2"],
        "reporting_requirements": "Weekly reports to CMO",
        "approval_workflow": "Draft > Review > Approve"
    }
"""
        }
        
        return base_schema + entity_schemas.get(entity_type, "") + "\n}"
    
    def _fallback_extraction(
        self,
        entity_type: str,
        answers: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Provides fallback extraction using simple keyword matching."""
        logger.warning("Using fallback extraction due to LLM failure")
        
        # Simple keyword-based extraction
        all_text = " ".join([qa["answer"] for qa in answers]).lower()
        
        return {
            "clarity_statement": next(
                (qa["answer"] for qa in answers if "clarity" in qa["question_text"].lower() or "one-line" in qa["question_text"].lower()),
                None
            ),
            "goals": [],
            "constraints": {},
            "channels": {
                "linkedin": "linkedin" in all_text,
                "twitter": "twitter" in all_text or "x.com" in all_text,
                "instagram": "instagram" in all_text,
                "email": "email" in all_text,
                "blog": "blog" in all_text,
            },
            "personas": [],
            "style_preferences": {}
        }


# Global instance
profile_builder = ProfileBuilderAgent()

