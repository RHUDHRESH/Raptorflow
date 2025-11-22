"""
Email Writer Agent - Crafts email sequences with proven copywriting formulas.
"""

import json
import structlog
from typing import List, Dict, Any, Literal, Optional
from uuid import UUID

from backend.config.prompts import EMAIL_WRITER_SYSTEM_PROMPT
from backend.services.vertex_ai_client import vertex_ai_client
from backend.models.content import ContentVariant
from backend.models.persona import ICPProfile
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class EmailWriterAgent:
    """
    Generates email copy using proven frameworks (AIDA, PAS, etc.).
    Uses creative_fast model for rapid email generation.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
        self.copywriting_formulas = {
            "AIDA": "Attention → Interest → Desire → Action",
            "PAS": "Problem → Agitate → Solution",
            "PPPP": "Picture → Promise → Prove → Push",
            "4P": "Problem → Promise → Proof → Proposal",
            "FAB": "Features → Advantages → Benefits"
        }
    
    async def write_email(
        self,
        purpose: str,
        icp_profile: ICPProfile,
        email_type: Literal["welcome", "nurture", "promotional", "abandoned_cart", "re_engagement"] = "nurture",
        formula: Literal["AIDA", "PAS", "PPPP", "4P", "FAB"] = "PAS",
        subject_line: Optional[str] = None,
        cta: Optional[str] = None,
        brand_voice: Optional[str] = None,
        correlation_id: str = None
    ) -> ContentVariant:
        """
        Generates a single email using a specified copywriting formula.
        
        Args:
            purpose: What the email aims to achieve
            icp_profile: Target audience
            email_type: Category of email
            formula: Copywriting framework to use
            subject_line: Pre-defined subject line (optional, will generate if not provided)
            cta: Call-to-action text (optional)
            brand_voice: Brand voice guidelines
            
        Returns:
            ContentVariant with email HTML/text
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Writing email", purpose=purpose, email_type=email_type, formula=formula, correlation_id=correlation_id)
        
        cache_key = f"email:{icp_profile.id}:{purpose}:{email_type}:{formula}"
        cached_email = await redis_cache.get(cache_key)
        if cached_email:
            logger.info("Returning cached email", correlation_id=correlation_id)
            return ContentVariant(**cached_email)
        
        # Build context
        pain_points_str = ", ".join(icp_profile.pain_points[:2]) if icp_profile.pain_points else "N/A"
        goals_str = ", ".join(icp_profile.goals[:2]) if icp_profile.goals else "N/A"
        formula_structure = self.copywriting_formulas[formula]
        
        prompt = f"""Write a compelling email for:

**Purpose**: {purpose}
**Email Type**: {email_type}
**Target Audience**: {icp_profile.name}
- Role: {icp_profile.demographics.buyer_role or 'Professional'}
- Pain Points: {pain_points_str}
- Goals: {goals_str}
- Motivation: {icp_profile.psychographics.motivation or 'N/A'}

**Copywriting Formula**: {formula} ({formula_structure})
{f"**Subject Line**: {subject_line}" if subject_line else "**Task**: Generate a compelling subject line"}
{f"**CTA**: {cta}" if cta else "**Task**: Create a strong CTA"}
{f"**Brand Voice**: {brand_voice}" if brand_voice else ""}

**Requirements**:
1. Follow the {formula} structure strictly
2. Keep it concise (200-300 words)
3. Personalize to the audience's pain points
4. Use conversational, human tone (not salesy)
5. Strong subject line that gets opens
6. Clear, action-oriented CTA
7. Output in plain text format (can include basic HTML if needed)

Generate the complete email now, including subject line and body.
"""
        
        messages = [
            {"role": "system", "content": EMAIL_WRITER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Use creative_fast for rapid email generation
            email_content = await self.llm.chat_completion(
                messages,
                model_type="creative_fast",
                temperature=0.75
            )
            
            word_count = len(email_content.split())
            
            variant = ContentVariant(
                format="email_body",
                content=email_content,
                word_count=word_count,
                readability_score=0.85,
                seo_keywords=[],
                platform_specific_attributes={
                    "email_type": email_type,
                    "formula": formula
                }
            )
            
            # Cache for 7 days
            await redis_cache.set(cache_key, variant.model_dump(), ttl=604800)
            
            logger.info("Email generated", word_count=word_count, correlation_id=correlation_id)
            return variant
            
        except Exception as e:
            logger.error("Error writing email", error=str(e), correlation_id=correlation_id)
            raise
    
    async def write_email_sequence(
        self,
        purpose: str,
        icp_profile: ICPProfile,
        sequence_length: int = 3,
        brand_voice: Optional[str] = None,
        correlation_id: str = None
    ) -> List[ContentVariant]:
        """
        Generates a multi-email nurture sequence.
        
        Args:
            purpose: Overall goal of the sequence
            icp_profile: Target audience
            sequence_length: Number of emails (3-7 recommended)
            brand_voice: Brand voice guidelines
            
        Returns:
            List of ContentVariant emails
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Writing email sequence", length=sequence_length, correlation_id=correlation_id)
        
        emails = []
        sequence_stages = ["introduce", "educate", "nurture", "convert", "reinforce", "upsell", "advocate"]
        
        for i in range(sequence_length):
            stage = sequence_stages[min(i, len(sequence_stages) - 1)]
            email_purpose = f"{purpose} - Email {i+1}/{sequence_length}: {stage}"
            
            email = await self.write_email(
                purpose=email_purpose,
                icp_profile=icp_profile,
                email_type="nurture",
                formula="PAS" if i < 2 else "AIDA",
                brand_voice=brand_voice,
                correlation_id=correlation_id
            )
            emails.append(email)
        
        return emails


email_writer_agent = EmailWriterAgent()

