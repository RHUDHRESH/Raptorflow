"""
Persona Narrative Agent - Converts ICP tags into human-readable stories.
"""

from typing import Dict, List, Optional
from uuid import UUID
import logging

from backend.models.persona import ICPProfile
from backend.config.settings import get_settings
from backend.services.vertex_ai_client import vertex_ai_client

logger = logging.getLogger(__name__)
settings = get_settings()


class PersonaNarrativeAgent:
    """
    Generates compelling, human-readable narratives from ICP data.
    
    Responsibilities:
    - Convert tags and data into 2-3 paragraph stories
    - Create memorable persona names (e.g., "Scaling Sarah")
    - Build empathy and understanding for marketing teams
    - Make ICPs feel like real people
    """
    
    async def generate_narrative(self, icp: ICPProfile) -> str:
        """
        Generates a narrative story for an ICP.
        
        Args:
            icp: Complete ICP profile
            
        Returns:
            2-3 paragraph narrative describing the persona
        """
        logger.info(f"Generating narrative for: {icp.name}")
        
        # Build context from ICP data
        context = self._build_context(icp)
        
        # Generate narrative using LLM
        narrative_prompt = f"""
You are an expert at creating compelling persona narratives. Write a human, empathetic
2-3 paragraph story about this customer persona.

Persona: {icp.name}
{context}

The narrative should:
1. Start with a day-in-the-life scenario
2. Highlight their main pain points and frustrations
3. Show their goals and aspirations
4. Make them feel like a real person with emotions and motivations
5. Be written in third person
6. Be engaging and memorable

Write the narrative now (2-3 paragraphs only):
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert copywriter specializing in persona narratives. Write compelling, human stories."
                },
                {"role": "user", "content": narrative_prompt}
            ]
            
            narrative = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.8  # Higher temperature for more creative narratives
            )
            
            logger.info("Narrative generated successfully")
            return narrative.strip()
            
        except Exception as e:
            logger.error(f"Narrative generation failed: {e}")
            return self._fallback_narrative(icp)
    
    async def generate_persona_name(self, basic_info: Dict[str, str]) -> str:
        """
        Generates an alliterative, memorable persona name.
        
        Args:
            basic_info: Basic persona info (role, pain_point)
            
        Returns:
            Memorable name (e.g., "Scaling Sarah", "Technical Tom")
        """
        role = basic_info.get("role", "Professional")
        pain_point = basic_info.get("biggest_pain_point", "challenges")
        
        prompt = f"""
Generate a memorable, alliterative persona name for a customer with this profile:

Role: {role}
Main Challenge: {pain_point}

The name should:
1. Be alliterative (first name and descriptor start with same letter)
2. Reflect their role or challenge
3. Be memorable and catchy
4. Examples: "Scaling Sarah", "Technical Tom", "Marketing Mary", "Analytical Alex"

Return ONLY the name, nothing else:
"""
        
        try:
            messages = [
                {"role": "system", "content": "You generate memorable, alliterative persona names."},
                {"role": "user", "content": prompt}
            ]
            
            name = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.9
            )
            
            return name.strip()
            
        except Exception as e:
            logger.error(f"Name generation failed: {e}")
            # Fallback to simple name based on role
            first_letter = role[0].upper() if role else "P"
            return f"{first_letter}rofessional {first_letter}atricia"
    
    def _build_context(self, icp: ICPProfile) -> str:
        """Builds context string from ICP data."""
        context_parts = []
        
        if icp.executive_summary:
            context_parts.append(f"Summary: {icp.executive_summary}")
        
        if icp.demographics and icp.demographics.buyer_role:
            context_parts.append(f"Role: {icp.demographics.buyer_role}")
        
        if icp.demographics and icp.demographics.company_size:
            context_parts.append(f"Company Size: {icp.demographics.company_size}")
        
        if icp.pain_points:
            context_parts.append(f"Pain Points: {', '.join(icp.pain_points[:3])}")
        
        if icp.goals:
            context_parts.append(f"Goals: {', '.join(icp.goals[:3])}")
        
        if icp.psychographics:
            psych_items = []
            if icp.psychographics.motivation:
                psych_items.append(f"motivated by {icp.psychographics.motivation}")
            if icp.psychographics.risk_tolerance:
                psych_items.append(f"risk tolerance: {icp.psychographics.risk_tolerance}")
            if psych_items:
                context_parts.append(f"Psychology: {', '.join(psych_items)}")
        
        if icp.tags:
            context_parts.append(f"Tags: {', '.join(icp.tags[:10])}")
        
        return "\n".join(context_parts)
    
    def _fallback_narrative(self, icp: ICPProfile) -> str:
        """Provides fallback narrative if LLM generation fails."""
        return f"""
{icp.name} is a {icp.demographics.buyer_role if icp.demographics else 'professional'} who faces significant challenges in their role. 
{f'Their biggest pain point is {icp.pain_points[0]}' if icp.pain_points else 'They struggle with various operational challenges'}.

They are looking for solutions that can help them {icp.goals[0] if icp.goals else 'achieve their goals more effectively'}. 
{icp.name} values {icp.psychographics.motivation if icp.psychographics and icp.psychographics.motivation else 'efficiency and results'}, 
and prefers to communicate via {', '.join(icp.communication.channels) if icp.communication else 'email and professional networks'}.

Understanding {icp.name}'s needs and preferences is key to crafting messaging that resonates and drives engagement.
"""


# Global instance
persona_narrative = PersonaNarrativeAgent()

