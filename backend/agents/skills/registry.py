"""
Skills registry for managing agent skills.
"""

import logging
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import Skill, SkillAssessment, SkillCategory, SkillLevel, SkillPath

logger = logging.getLogger(__name__)


class SkillsRegistry:
    """Registry for managing agent skills."""

    _instance: Optional["SkillsRegistry"] = None
    _lock: threading.Lock = threading.Lock()
    _skills: Dict[str, Skill] = {}
    _skills_lock: threading.RLock = threading.RLock()

    def __new__(cls) -> "SkillsRegistry":
        """Implement thread-safe singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the skills registry with default skills."""
        self._skills = {}
        self._register_default_skills()

    def _register_default_skills(self):
        """Register default skills."""
        # Content skills
        self.register_skill(
            Skill(
                name="content_generation",
                category=SkillCategory.CONTENT,
                level=SkillLevel.INTERMEDIATE,
                description="Generate various types of content including blog posts, social media, emails",
                tools_required=["web_search", "database"],
                capabilities=[
                    "Create blog posts",
                    "Write social media content",
                    "Generate email campaigns",
                    "Produce ad copy",
                    "Write newsletters",
                ],
                examples=[
                    "Wrote a 1000-word blog post about digital marketing trends",
                    "Created 5 social media posts for product launch",
                    "Generated email sequence for onboarding",
                ],
            )
        )

        self.register_skill(
            Skill(
                name="seo_optimization",
                category=SkillCategory.CONTENT,
                level=SkillLevel.ADVANCED,
                description="Optimize content for search engines and improve visibility",
                tools_required=["web_search"],
                capabilities=[
                    "Keyword research",
                    "On-page optimization",
                    "Meta tag creation",
                    "Content structure optimization",
                    "SEO performance analysis",
                ],
                examples=[
                    "Optimized blog post for 'digital marketing trends' keyword",
                    "Created meta descriptions for 10 pages",
                    "Improved content structure for better rankings",
                ],
            )
        )

        # Research skills
        self.register_skill(
            Skill(
                name="competitor_analysis",
                category=SkillCategory.RESEARCH,
                level=SkillLevel.ADVANCED,
                description="Analyze competitors' strategies, positioning, and performance",
                tools_required=["web_search", "database"],
                capabilities=[
                    "Competitor identification",
                    "SWOT analysis",
                    "Market positioning analysis",
                    "Competitive benchmarking",
                    "Strategy gap analysis",
                ],
                examples=[
                    "Analyzed top 5 competitors in SaaS market",
                    "Created SWOT analysis for main competitor",
                    "Identified positioning opportunities",
                ],
            )
        )

        self.register_skill(
            Skill(
                name="market_sizing",
                category=SkillCategory.RESEARCH,
                level=SkillLevel.EXPERT,
                description="Calculate market size, TAM, SAM, SOM and growth projections",
                tools_required=["web_search", "database"],
                capabilities=[
                    "TAM/SAM/SOM calculation",
                    "Market growth projections",
                    "Segment sizing",
                    "Revenue forecasting",
                    "Market opportunity assessment",
                ],
                examples=[
                    "Calculated $50M TAM for B2B SaaS market",
                    "Projected 25% CAGR for next 5 years",
                    "Identified $10M serviceable market",
                ],
            )
        )

        # Strategy skills
        self.register_skill(
            Skill(
                name="strategic_planning",
                category=SkillCategory.STRATEGY,
                level=SkillLevel.EXPERT,
                description="Develop comprehensive strategic plans and roadmaps",
                tools_required=["web_search", "database"],
                capabilities=[
                    "Strategic roadmap creation",
                    "Goal setting and KPI definition",
                    "Resource allocation planning",
                    "Risk assessment",
                    "Strategic initiative prioritization",
                ],
                examples=[
                    "Created 3-year strategic plan for startup",
                    "Defined OKRs for marketing team",
                    "Prioritized strategic initiatives based on ROI",
                ],
            )
        )

        # Analytics skills
        self.register_skill(
            Skill(
                name="data_analysis",
                category=SkillCategory.ANALYTICS,
                level=SkillLevel.ADVANCED,
                description="Analyze data to extract insights and support decision making",
                tools_required=["database"],
                capabilities=[
                    "Data visualization",
                    "Statistical analysis",
                    "Trend identification",
                    "Performance reporting",
                    "Insight generation",
                ],
                examples=[
                    "Analyzed campaign performance data",
                    "Created monthly performance dashboard",
                    "Identified key trends in customer behavior",
                ],
            )
        )

        logger.info(f"Initialized skills registry with {len(self._skills)} skills")

    def register_skill(self, skill: Skill):
        """Register a skill in the registry."""
        with self._skills_lock:
            if skill.name in self._skills:
                logger.warning(f"Skill '{skill.name}' already registered, overwriting")

            self._skills[skill.name] = skill
            logger.info(f"Registered skill: {skill.name}")

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        with self._skills_lock:
            return self._skills.get(name)

    def list_skills(self, category: Optional[SkillCategory] = None) -> List[str]:
        """List all skills, optionally filtered by category."""
        with self._skills_lock:
            if category:
                return [
                    name
                    for name, skill in self._skills.items()
                    if skill.category == category
                ]
            return list(self._skills.keys())

    def get_skills_by_category(self) -> Dict[SkillCategory, List[Skill]]:
        """Get skills grouped by category."""
        with self._skills_lock:
            categorized = {}
            for skill in self._skills.values():
                if skill.category not in categorized:
                    categorized[skill.category] = []
                categorized[skill.category].append(skill)
            return categorized

    def assess_agent_skills(
        self, agent_name: str, agent_skills: List[str], agent_tools: List[str]
    ) -> List[SkillAssessment]:
        """Assess an agent's skill proficiency."""
        assessments = []

        for skill_name in agent_skills:
            skill = self.get_skill(skill_name)
            if not skill:
                logger.warning(f"Unknown skill: {skill_name}")
                continue

            # Check if agent has required tools
            can_execute = skill.can_execute(agent_tools)

            # Check if agent meets prerequisites
            meets_prereqs = skill.meets_prerequisites(agent_skills)

            # Calculate confidence based on tools and prerequisites
            confidence = 0.5  # Base confidence
            if can_execute:
                confidence += 0.3
            if meets_prereqs:
                confidence += 0.2

            # Determine assessed level (simplified)
            if confidence >= 0.9:
                assessed_level = SkillLevel.EXPERT
            elif confidence >= 0.7:
                assessed_level = SkillLevel.ADVANCED
            elif confidence >= 0.5:
                assessed_level = SkillLevel.INTERMEDIATE
            else:
                assessed_level = SkillLevel.BEGINNER

            # Generate recommendations
            recommendations = []
            if not can_execute:
                recommendations.append(f"Add required tools: {skill.tools_required}")
            if not meets_prereqs:
                recommendations.append(
                    f"Develop prerequisite skills: {skill.prerequisites}"
                )
            if confidence < 0.7:
                recommendations.append("Practice with real-world projects")

            # Generate next steps
            next_steps = []
            if not can_execute:
                next_steps.append("Get access to required tools")
            if not meets_prereqs:
                next_steps.append("Complete prerequisite skill training")
            next_steps.append("Complete skill-specific training modules")

            assessment = SkillAssessment(
                skill_name=skill_name,
                current_level=SkillLevel.INTERMEDIATE,  # Default assumption
                assessed_level=assessed_level,
                confidence=confidence,
                evidence=[f"Agent has access to {len(agent_tools)} tools"],
                recommendations=recommendations,
                next_steps=next_steps,
                assessment_date=datetime.now().isoformat(),
            )

            assessments.append(assessment)

        return assessments

    def create_skill_path(
        self, skill_name: str, current_level: SkillLevel, target_level: SkillLevel
    ) -> SkillPath:
        """Create a learning path for skill development."""
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Unknown skill: {skill_name}")

        # Define learning steps based on level progression
        level_order = [
            SkillLevel.BEGINNER,
            SkillLevel.INTERMEDIATE,
            SkillLevel.ADVANCED,
            SkillLevel.EXPERT,
            SkillLevel.MASTER,
        ]

        current_idx = level_order.index(current_level)
        target_idx = level_order.index(target_level)

        if current_idx >= target_idx:
            raise ValueError("Target level must be higher than current level")

        steps = []
        for level in level_order[current_idx + 1 : target_idx + 1]:
            step = {
                "level": level.value,
                "description": f"Achieve {level.value} proficiency in {skill_name}",
                "duration_hours": 40,  # Default hours per level
                "activities": [
                    f"Practice {skill_name} at {level.value} level",
                    f"Complete {skill_name} training modules",
                    f"Work on {skill_name} projects",
                ],
                "assessment": f"Pass {skill_name} {level.value} assessment",
            }
            steps.append(step)

        # Calculate total duration
        total_duration = sum(step["duration_hours"] for step in steps)

        # Define resources
        resources = [
            f"{skill_name} training materials",
            f"{skill_name} practice projects",
            f"{skill_name} mentorship program",
            "Online courses and tutorials",
        ]

        # Define milestones
        milestones = []
        for i, step in enumerate(steps, 1):
            milestones.append(f"Complete {step['level']} level training (Step {i})")

        return SkillPath(
            skill_name=skill_name,
            target_level=target_level,
            current_level=current_level,
            steps=steps,
            estimated_duration_hours=total_duration,
            resources=resources,
            milestones=milestones,
        )

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._skills_lock:
            categories = {}
            for skill in self._skills.values():
                if skill.category not in categories:
                    categories[skill.category] = {"count": 0, "levels": {}}
                categories[skill.category]["count"] += 1

                if skill.level not in categories[skill.category]["levels"]:
                    categories[skill.category]["levels"][skill.level] = 0
                categories[skill.category]["levels"][skill.level] += 1

            return {
                "total_skills": len(self._skills),
                "categories": categories,
                "last_updated": datetime.now().isoformat(),
            }


# Global registry instance
def get_skills_registry() -> SkillsRegistry:
    """Get the global skills registry instance."""
    return SkillsRegistry()


# Convenience functions
def get_skill(name: str) -> Optional[Skill]:
    """Get a skill from the global registry."""
    registry = get_skills_registry()
    return registry.get_skill(name)


def list_skills(category: Optional[SkillCategory] = None) -> List[str]:
    """List skills from the global registry."""
    registry = get_skills_registry()
    return registry.list_skills(category)
