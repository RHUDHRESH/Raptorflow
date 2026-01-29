"""
Skills system for Raptorflow agents.
Defines available skills and skill management.
"""

from ..base import Skill, SkillCategory, SkillLevel
from .registry import get_skill, get_skills_registry, list_skills

# Core skills available to agents
CORE_SKILLS = {
    # Content skills
    "content_generation": SkillCategory.CONTENT,
    "seo_optimization": SkillCategory.CONTENT,
    "brand_voice_adaptation": SkillCategory.CONTENT,
    "multi_format_writing": SkillCategory.CONTENT,
    "copywriting": SkillCategory.CONTENT,
    "storytelling": SkillCategory.CONTENT,
    # Research skills
    "competitor_analysis": SkillCategory.RESEARCH,
    "market_sizing": SkillCategory.RESEARCH,
    "trend_identification": SkillCategory.RESEARCH,
    "data_synthesis": SkillCategory.RESEARCH,
    "industry_research": SkillCategory.RESEARCH,
    "due_diligence": SkillCategory.RESEARCH,
    # Strategy skills
    "strategic_planning": SkillCategory.STRATEGY,
    "growth_hacking": SkillCategory.STRATEGY,
    "positioning": SkillCategory.STRATEGY,
    "go_to_market": SkillCategory.STRATEGY,
    "competitive_strategy": SkillCategory.STRATEGY,
    # Analytics skills
    "data_analysis": SkillCategory.ANALYTICS,
    "performance_tracking": SkillCategory.ANALYTICS,
    "conversion_optimization": SkillCategory.ANALYTICS,
    "metrics_interpretation": SkillCategory.ANALYTICS,
    "reporting": SkillCategory.ANALYTICS,
    # Technical skills
    "web_scraping": SkillCategory.TECHNICAL,
    "api_integration": SkillCategory.TECHNICAL,
    "database_querying": SkillCategory.TECHNICAL,
    "automation": SkillCategory.TECHNICAL,
    # Communication skills
    "stakeholder_communication": SkillCategory.COMMUNICATION,
    "presentation": SkillCategory.COMMUNICATION,
    "negotiation": SkillCategory.COMMUNICATION,
    "client_management": SkillCategory.COMMUNICATION,
}

__all__ = [
    "get_skills_registry",
    "get_skill",
    "list_skills",
    "Skill",
    "SkillLevel",
    "SkillCategory",
    "CORE_SKILLS",
]
