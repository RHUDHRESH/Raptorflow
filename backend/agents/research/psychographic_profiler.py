"""
Psychographic Profiler Agent - Enriches ICPs with B=MAP framework and psychological attributes.
"""

from typing import Dict, List, Optional
import logging

from backend.models.persona import ICPProfile, Psychographics
from backend.config.settings import get_settings
from backend.services.vertex_ai_client import vertex_ai_client

logger = logging.getLogger(__name__)
settings = get_settings()


class PsychographicProfilerAgent:
    """
    Enriches ICPs with psychological and behavioral attributes.
    
    Responsibilities:
    - Apply B=MAP framework (Behavior = Motivation × Ability × Prompt)
    - Assess risk tolerance
    - Determine status drive and community orientation
    - Identify decision-making patterns
    - Map to psychological frameworks
    """
    
    def __init__(self):
        self.bmap_framework = {
            "motivation": [
                "ROI-driven",
                "Innovation-seeking",
                "Problem-solving",
                "Status-seeking",
                "Risk-mitigation",
                "Efficiency-driven",
                "Growth-oriented",
                "Quality-focused"
            ],
            "ability": [
                "Novice - Limited technical knowledge",
                "Intermediate - Moderate expertise",
                "Expert - Deep domain knowledge",
                "Power User - Advanced technical skills"
            ],
            "prompt_receptiveness": [
                "Highly receptive - Actively seeking solutions",
                "Moderately receptive - Open but cautious",
                "Low receptiveness - Satisfied with status quo",
                "Very low - Resistant to change"
            ]
        }
    
    async def enrich_psychographics(self, icp: ICPProfile) -> Psychographics:
        """
        Enriches an ICP with psychographic attributes.
        
        Args:
            icp: ICP to enrich
            
        Returns:
            Complete Psychographics profile
        """
        logger.info(f"Enriching psychographics for: {icp.name}")
        
        # Extract psychographic attributes using LLM
        psychographic_data = await self._analyze_psychographics(icp)
        
        # Create Psychographics object
        psychographics = Psychographics(
            motivation=psychographic_data.get("motivation"),
            ability=psychographic_data.get("ability"),
            prompt_receptiveness=psychographic_data.get("prompt_receptiveness"),
            risk_tolerance=psychographic_data.get("risk_tolerance"),
            status_drive=psychographic_data.get("status_drive"),
            community_orientation=psychographic_data.get("community_orientation")
        )
        
        logger.info("Psychographics enriched successfully")
        return psychographics
    
    async def _analyze_psychographics(self, icp: ICPProfile) -> Dict[str, str]:
        """
        Analyzes ICP and determines psychographic attributes.
        
        Args:
            icp: ICP to analyze
            
        Returns:
            Dictionary of psychographic attributes
        """
        # Build context from ICP
        context = self._build_context(icp)
        
        analysis_prompt = f"""
You are a customer psychology expert applying the B=MAP framework and behavioral science.

ICP Profile:
{context}

B=MAP Framework:
- Behavior = Motivation × Ability × Prompt
- Motivation: What drives them to seek solutions
- Ability: Their capability level and resources
- Prompt: Receptiveness to new solutions/change

Analyze this ICP and determine:

1. **Motivation**: Primary buying motivation
   Options: {', '.join(self.bmap_framework['motivation'])}

2. **Ability**: Capability and expertise level
   Options: {', '.join(self.bmap_framework['ability'])}

3. **Prompt Receptiveness**: How receptive they are to new solutions
   Options: {', '.join(self.bmap_framework['prompt_receptiveness'])}

4. **Risk Tolerance**: Conservative, Moderate, or Aggressive

5. **Status Drive**: How important is status/reputation? (High, Medium, Low)

6. **Community Orientation**: Independent, Community-driven, or Network-focused

Return JSON:
{{
    "motivation": "chosen motivation",
    "ability": "chosen ability level",
    "prompt_receptiveness": "chosen receptiveness",
    "risk_tolerance": "Conservative|Moderate|Aggressive",
    "status_drive": "High|Medium|Low",
    "community_orientation": "Independent|Community-driven|Network-focused",
    "reasoning": "Brief explanation of your choices"
}}
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a behavioral psychologist and customer intelligence expert."
                },
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.4,  # Lower for more consistent psychological profiling
                response_format={"type": "json_object"}
            )
            
            import json
            psychographic_data = json.loads(response)
            
            logger.info(f"Psychographic analysis: {psychographic_data.get('reasoning', 'N/A')}")
            return psychographic_data
            
        except Exception as e:
            logger.error(f"Psychographic analysis failed: {e}")
            return self._fallback_psychographics()
    
    async def determine_buying_triggers(self, icp: ICPProfile) -> List[str]:
        """
        Determines specific triggers that would prompt this persona to buy.
        
        Args:
            icp: ICP to analyze
            
        Returns:
            List of buying triggers
        """
        context = self._build_context(icp)
        
        trigger_prompt = f"""
Based on this ICP's psychographic profile, identify 5-7 specific triggers that would prompt them to take action:

{context}

Buying triggers are specific events or thresholds that create urgency. Consider:
- B=MAP framework: What increases their motivation, ability, or prompt?
- Pain point severity: When does the pain become unbearable?
- External events: Market changes, competition, regulations
- Internal events: Leadership changes, budget cycles, team growth
- Social proof: Peer adoption, industry trends

Return JSON array:
{{"triggers": ["trigger 1", "trigger 2", ...]}}
"""
        
        try:
            messages = [
                {"role": "system", "content": "You identify behavioral triggers for purchasing decisions."},
                {"role": "user", "content": trigger_prompt}
            ]
            
            response = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response)
            return result.get("triggers", [])
            
        except Exception as e:
            logger.error(f"Trigger determination failed: {e}")
            return []
    
    async def assess_decision_structure(self, icp: ICPProfile) -> str:
        """
        Assesses how this persona makes decisions.
        
        Args:
            icp: ICP to analyze
            
        Returns:
            Decision structure description
        """
        context = self._build_context(icp)
        
        decision_prompt = f"""
Based on this ICP profile, describe their decision-making structure:

{context}

Consider:
- Individual vs. committee decisions
- Number of stakeholders typically involved
- Decision timeline (days, weeks, months)
- Key decision criteria
- Who has veto power
- Typical buying journey stages

Return a 2-3 sentence description of their decision structure:
"""
        
        try:
            messages = [
                {"role": "system", "content": "You analyze B2B decision-making structures."},
                {"role": "user", "content": decision_prompt}
            ]
            
            decision_structure = await vertex_ai_client.chat_completion(
                messages=messages,
                temperature=0.5
            )
            
            return decision_structure.strip()
            
        except Exception as e:
            logger.error(f"Decision structure assessment failed: {e}")
            return "Decision structure unknown"
    
    def _build_context(self, icp: ICPProfile) -> str:
        """Builds context string from ICP."""
        context_parts = [f"Name: {icp.name}"]
        
        if icp.executive_summary:
            context_parts.append(f"Summary: {icp.executive_summary}")
        
        if icp.demographics:
            if icp.demographics.buyer_role:
                context_parts.append(f"Role: {icp.demographics.buyer_role}")
            if icp.demographics.company_size:
                context_parts.append(f"Company Size: {icp.demographics.company_size}")
            if icp.demographics.industry:
                context_parts.append(f"Industry: {icp.demographics.industry}")
        
        if icp.pain_points:
            context_parts.append(f"Pain Points: {', '.join(icp.pain_points[:5])}")
        
        if icp.goals:
            context_parts.append(f"Goals: {', '.join(icp.goals[:5])}")
        
        if icp.tags:
            context_parts.append(f"Tags: {', '.join(icp.tags[:15])}")
        
        return "\n".join(context_parts)
    
    def _fallback_psychographics(self) -> Dict[str, str]:
        """Provides fallback psychographics if analysis fails."""
        return {
            "motivation": "Problem-solving",
            "ability": "Intermediate - Moderate expertise",
            "prompt_receptiveness": "Moderately receptive - Open but cautious",
            "risk_tolerance": "Moderate",
            "status_drive": "Medium",
            "community_orientation": "Community-driven"
        }


# Global instance
psychographic_profiler = PsychographicProfilerAgent()

