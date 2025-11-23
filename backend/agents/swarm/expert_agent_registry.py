"""
Expert agent registry for hyper-specialized AI agents.

This module maintains a registry of domain-expert agents that can be
dynamically assembled into teams based on task requirements.

Expert Agents:
- SEO Expert: Search engine optimization and keyword strategy
- Copywriting Ninja: Persuasive writing and conversion optimization
- Data Storyteller: Data-driven narratives and insights
- Psychological Persuasion Specialist: Behavioral psychology and influence
- Viral Engineer: Viral content and shareability optimization
- Brand Guardian: Brand consistency and voice alignment
- Technical Writer: Complex technical content simplification

Key Features:
- Agent capability metadata and expertise levels
- Dynamic team assembly based on task type
- Multi-agent collaboration protocols
- Performance tracking per agent
- Agent skill evolution over time

Usage:
    registry = ExpertAgentRegistry()
    team = await registry.assemble_team(
        task_type="viral_social_campaign",
        required_skills=["viral_mechanics", "psychology", "copywriting"]
    )
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from backend.agents.base_agent import BaseAgent


class ExpertiseLevel(str, Enum):
    """Level of expertise for a skill."""

    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class AgentRole(str, Enum):
    """Specialized agent roles."""

    SEO_EXPERT = "seo_expert"
    COPYWRITING_NINJA = "copywriting_ninja"
    DATA_STORYTELLER = "data_storyteller"
    PSYCHOLOGY_SPECIALIST = "psychology_specialist"
    VIRAL_ENGINEER = "viral_engineer"
    BRAND_GUARDIAN = "brand_guardian"
    TECHNICAL_WRITER = "technical_writer"
    CONTENT_STRATEGIST = "content_strategist"
    ENGAGEMENT_OPTIMIZER = "engagement_optimizer"


class SkillTag(str, Enum):
    """Skill tags for agent capabilities."""

    # SEO Skills
    KEYWORD_RESEARCH = "keyword_research"
    SEMANTIC_SEO = "semantic_seo"
    TECHNICAL_SEO = "technical_seo"

    # Copywriting Skills
    PERSUASIVE_WRITING = "persuasive_writing"
    STORYTELLING = "storytelling"
    CTA_OPTIMIZATION = "cta_optimization"
    HEADLINE_WRITING = "headline_writing"

    # Psychology Skills
    BEHAVIORAL_PSYCHOLOGY = "behavioral_psychology"
    COGNITIVE_BIASES = "cognitive_biases"
    EMOTIONAL_TRIGGERS = "emotional_triggers"
    PERSUASION_TACTICS = "persuasion_tactics"

    # Viral Engineering
    VIRAL_MECHANICS = "viral_mechanics"
    SHAREABILITY = "shareability"
    TREND_ANALYSIS = "trend_analysis"
    MEME_CULTURE = "meme_culture"

    # Brand Skills
    BRAND_VOICE = "brand_voice"
    TONE_CONSISTENCY = "tone_consistency"
    STYLE_GUIDELINES = "style_guidelines"

    # Technical Skills
    TECHNICAL_WRITING = "technical_writing"
    DOCUMENTATION = "documentation"
    SIMPLIFICATION = "simplification"

    # Data Skills
    DATA_ANALYSIS = "data_analysis"
    DATA_VISUALIZATION = "data_visualization"
    INSIGHT_GENERATION = "insight_generation"

    # Engagement Skills
    ENGAGEMENT_OPTIMIZATION = "engagement_optimization"
    COMMUNITY_BUILDING = "community_building"
    INTERACTION_DESIGN = "interaction_design"


class AgentSkill(BaseModel):
    """
    Represents a skill and expertise level.

    Attributes:
        skill: Skill tag
        level: Expertise level
        confidence: Confidence in this skill (0.0-1.0)
        examples: Example outputs demonstrating this skill
    """

    skill: SkillTag
    level: ExpertiseLevel
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    examples: List[str] = Field(default_factory=list)


class ExpertAgentProfile(BaseModel):
    """
    Profile of a specialized expert agent.

    Attributes:
        agent_id: Unique identifier
        role: Primary agent role
        name: Human-readable name
        description: What this agent does
        skills: List of agent skills with expertise levels
        system_prompt: System prompt for this agent
        model_preference: Preferred LLM model
        temperature: Generation temperature
        performance_history: Historical performance metrics
        collaboration_affinity: Which agents this agent works well with
        metadata: Additional agent metadata
    """

    agent_id: str = Field(default_factory=lambda: str(uuid4()))
    role: AgentRole
    name: str
    description: str
    skills: List[AgentSkill]
    system_prompt: str
    model_preference: str = "gpt-4"
    temperature: float = 0.7
    performance_history: Dict[str, float] = Field(default_factory=dict)
    collaboration_affinity: Dict[str, float] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def has_skill(self, skill: SkillTag, min_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE) -> bool:
        """
        Check if agent has a skill at minimum level.

        Args:
            skill: Skill to check
            min_level: Minimum expertise level required

        Returns:
            True if agent has skill at sufficient level
        """
        level_order = [
            ExpertiseLevel.NOVICE,
            ExpertiseLevel.INTERMEDIATE,
            ExpertiseLevel.ADVANCED,
            ExpertiseLevel.EXPERT,
            ExpertiseLevel.MASTER,
        ]

        for agent_skill in self.skills:
            if agent_skill.skill == skill:
                agent_level_idx = level_order.index(agent_skill.level)
                min_level_idx = level_order.index(min_level)
                return agent_level_idx >= min_level_idx

        return False

    def get_skill_level(self, skill: SkillTag) -> Optional[ExpertiseLevel]:
        """Get expertise level for a specific skill."""
        for agent_skill in self.skills:
            if agent_skill.skill == skill:
                return agent_skill.level
        return None


class TaskRequirements(BaseModel):
    """
    Requirements for assembling an agent team.

    Attributes:
        task_type: Type of task (e.g., "viral_campaign", "technical_blog")
        required_skills: Must-have skills
        preferred_skills: Nice-to-have skills
        min_team_size: Minimum team size
        max_team_size: Maximum team size
        min_expertise: Minimum expertise level for required skills
        domain: Domain context (e.g., "saas", "ecommerce")
    """

    task_type: str
    required_skills: List[SkillTag]
    preferred_skills: List[SkillTag] = Field(default_factory=list)
    min_team_size: int = 2
    max_team_size: int = 5
    min_expertise: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE
    domain: Optional[str] = None


class ExpertAgentRegistry:
    """
    Registry of hyper-specialized expert agents.

    This registry maintains a pool of expert agents with different
    specializations and provides methods to:
    1. Register new expert agents
    2. Query agents by skills and expertise
    3. Assemble optimal teams for specific tasks
    4. Track agent performance over time

    Methods:
        register_agent: Add an agent to the registry
        get_agent: Retrieve an agent by ID or role
        find_agents_by_skill: Find agents with specific skills
        assemble_team: Create an optimal team for a task
        update_performance: Update agent performance metrics
    """

    def __init__(self):
        """Initialize the expert agent registry."""
        self.logger = logging.getLogger(__name__)
        self.agents: Dict[str, ExpertAgentProfile] = {}
        self.role_index: Dict[AgentRole, List[str]] = {}
        self.skill_index: Dict[SkillTag, List[str]] = {}

        # Initialize default expert agents
        self._initialize_default_agents()

    def _initialize_default_agents(self) -> None:
        """Initialize the registry with default expert agents."""

        # SEO Expert
        seo_expert = ExpertAgentProfile(
            role=AgentRole.SEO_EXPERT,
            name="SEO Specialist",
            description="Expert in search engine optimization, keyword strategy, and organic visibility",
            skills=[
                AgentSkill(skill=SkillTag.KEYWORD_RESEARCH, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.SEMANTIC_SEO, level=ExpertiseLevel.ADVANCED),
                AgentSkill(skill=SkillTag.TECHNICAL_SEO, level=ExpertiseLevel.ADVANCED),
                AgentSkill(skill=SkillTag.DATA_ANALYSIS, level=ExpertiseLevel.INTERMEDIATE),
            ],
            system_prompt="""You are an SEO expert specializing in search engine optimization and organic visibility.
Your expertise includes keyword research, semantic SEO, technical optimization, and ranking strategies.
When analyzing content or providing recommendations:
- Identify high-value keywords with search intent alignment
- Optimize for semantic relevance and topic clusters
- Consider technical SEO factors (meta tags, structure, speed)
- Provide data-driven recommendations with estimated impact
- Balance SEO optimization with user experience and readability
Always provide specific, actionable SEO improvements.""",
            temperature=0.3,  # Lower temperature for precision
        )
        self.register_agent(seo_expert)

        # Copywriting Ninja
        copywriter = ExpertAgentProfile(
            role=AgentRole.COPYWRITING_NINJA,
            name="Conversion Copywriter",
            description="Master of persuasive writing, conversion optimization, and compelling narratives",
            skills=[
                AgentSkill(skill=SkillTag.PERSUASIVE_WRITING, level=ExpertiseLevel.MASTER),
                AgentSkill(skill=SkillTag.STORYTELLING, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.CTA_OPTIMIZATION, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.HEADLINE_WRITING, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.EMOTIONAL_TRIGGERS, level=ExpertiseLevel.ADVANCED),
            ],
            system_prompt="""You are a master copywriter specializing in persuasive writing and conversion optimization.
Your expertise includes crafting compelling narratives, optimizing CTAs, and writing headlines that convert.
When creating or reviewing copy:
- Use powerful storytelling to create emotional connections
- Apply proven copywriting frameworks (AIDA, PAS, BAB)
- Optimize headlines for curiosity and value proposition
- Craft CTAs that are specific, urgent, and benefit-focused
- Use power words and sensory language effectively
- Balance persuasion with authenticity and trust-building
Focus on conversion outcomes while maintaining brand voice.""",
            temperature=0.8,  # Higher temperature for creativity
        )
        self.register_agent(copywriter)

        # Data Storyteller
        data_storyteller = ExpertAgentProfile(
            role=AgentRole.DATA_STORYTELLER,
            name="Data Storytelling Expert",
            description="Transforms complex data into compelling narratives and actionable insights",
            skills=[
                AgentSkill(skill=SkillTag.DATA_ANALYSIS, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.DATA_VISUALIZATION, level=ExpertiseLevel.ADVANCED),
                AgentSkill(skill=SkillTag.INSIGHT_GENERATION, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.STORYTELLING, level=ExpertiseLevel.ADVANCED),
                AgentSkill(skill=SkillTag.SIMPLIFICATION, level=ExpertiseLevel.ADVANCED),
            ],
            system_prompt="""You are a data storytelling expert who transforms complex data into compelling narratives.
Your expertise includes data analysis, visualization, insight generation, and making data accessible.
When working with data:
- Extract meaningful patterns and trends from complex datasets
- Create clear, compelling data visualizations
- Build narratives that make data relatable and actionable
- Use analogies and examples to simplify complex concepts
- Focus on the "so what" - why the data matters
- Provide context and implications for business decisions
Make data engaging, understandable, and actionable for all audiences.""",
            temperature=0.6,
        )
        self.register_agent(data_storyteller)

        # Psychology Specialist
        psychologist = ExpertAgentProfile(
            role=AgentRole.PSYCHOLOGY_SPECIALIST,
            name="Behavioral Psychology Expert",
            description="Applies psychological principles, cognitive biases, and persuasion tactics",
            skills=[
                AgentSkill(skill=SkillTag.BEHAVIORAL_PSYCHOLOGY, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.COGNITIVE_BIASES, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.EMOTIONAL_TRIGGERS, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.PERSUASION_TACTICS, level=ExpertiseLevel.ADVANCED),
            ],
            system_prompt="""You are a behavioral psychology expert specializing in persuasion, cognitive biases, and influence.
Your expertise includes applying psychological principles to marketing, content, and user experience.
When analyzing or creating content:
- Identify opportunities to leverage cognitive biases ethically (scarcity, social proof, reciprocity)
- Apply emotional trigger frameworks (fear, joy, belonging, achievement)
- Use persuasion techniques (foot-in-the-door, anchoring, framing)
- Consider psychological safety and ethical boundaries
- Explain the psychological mechanisms behind recommendations
- Balance persuasion with authenticity and user welfare
Apply psychology ethically to create genuinely valuable experiences.""",
            temperature=0.5,
        )
        self.register_agent(psychologist)

        # Viral Engineer
        viral_engineer = ExpertAgentProfile(
            role=AgentRole.VIRAL_ENGINEER,
            name="Viral Content Specialist",
            description="Masters viral mechanics, shareability, and trend-driven content",
            skills=[
                AgentSkill(skill=SkillTag.VIRAL_MECHANICS, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.SHAREABILITY, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.TREND_ANALYSIS, level=ExpertiseLevel.ADVANCED),
                AgentSkill(skill=SkillTag.MEME_CULTURE, level=ExpertiseLevel.ADVANCED),
                AgentSkill(skill=SkillTag.EMOTIONAL_TRIGGERS, level=ExpertiseLevel.ADVANCED),
            ],
            system_prompt="""You are a viral content engineer specializing in creating shareable, trend-driven content.
Your expertise includes viral mechanics, meme culture, trend analysis, and maximizing shareability.
When creating or analyzing content for virality:
- Identify viral triggers (humor, controversy, inspiration, surprise, utility)
- Optimize for platform-specific sharing mechanics
- Leverage current trends and cultural moments
- Create "shareable units" - memorable, quotable elements
- Balance virality with brand safety and authenticity
- Consider timing and cultural context
- Use formats proven to drive shares (lists, challenges, hot takes)
Focus on creating genuine value that people want to share.""",
            temperature=0.9,  # High temperature for creative viral ideas
        )
        self.register_agent(viral_engineer)

        # Brand Guardian
        brand_guardian = ExpertAgentProfile(
            role=AgentRole.BRAND_GUARDIAN,
            name="Brand Consistency Expert",
            description="Ensures brand voice, tone, and style consistency across all content",
            skills=[
                AgentSkill(skill=SkillTag.BRAND_VOICE, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.TONE_CONSISTENCY, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.STYLE_GUIDELINES, level=ExpertiseLevel.ADVANCED),
            ],
            system_prompt="""You are a brand guardian ensuring consistency in voice, tone, and style across all content.
Your expertise includes brand voice development, tone calibration, and style guide enforcement.
When reviewing or creating content:
- Verify alignment with established brand voice and values
- Ensure tone matches context and audience expectations
- Check adherence to style guidelines (language, formatting, terminology)
- Identify off-brand elements and suggest corrections
- Balance consistency with flexibility for different contexts
- Protect brand integrity while allowing creative expression
Maintain brand authenticity and recognition across all touchpoints.""",
            temperature=0.3,  # Low temperature for consistency
        )
        self.register_agent(brand_guardian)

        # Technical Writer
        tech_writer = ExpertAgentProfile(
            role=AgentRole.TECHNICAL_WRITER,
            name="Technical Communication Expert",
            description="Simplifies complex technical concepts for diverse audiences",
            skills=[
                AgentSkill(skill=SkillTag.TECHNICAL_WRITING, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.DOCUMENTATION, level=ExpertiseLevel.ADVANCED),
                AgentSkill(skill=SkillTag.SIMPLIFICATION, level=ExpertiseLevel.EXPERT),
                AgentSkill(skill=SkillTag.STORYTELLING, level=ExpertiseLevel.INTERMEDIATE),
            ],
            system_prompt="""You are a technical writing expert specializing in making complex concepts accessible.
Your expertise includes technical documentation, concept simplification, and clear communication.
When creating or reviewing technical content:
- Break down complex concepts into digestible chunks
- Use analogies and examples to illustrate technical ideas
- Structure content with clear hierarchy and progressive disclosure
- Balance technical accuracy with readability
- Adapt complexity level to target audience
- Use visuals and diagrams to support understanding
- Avoid jargon unless necessary, and define when used
Make technical content clear, accurate, and accessible to your audience.""",
            temperature=0.4,
        )
        self.register_agent(tech_writer)

        self.logger.info(f"Initialized registry with {len(self.agents)} expert agents")

    def register_agent(self, profile: ExpertAgentProfile) -> str:
        """
        Register an expert agent in the registry.

        Args:
            profile: Agent profile to register

        Returns:
            Agent ID
        """
        agent_id = profile.agent_id
        self.agents[agent_id] = profile

        # Update role index
        if profile.role not in self.role_index:
            self.role_index[profile.role] = []
        self.role_index[profile.role].append(agent_id)

        # Update skill index
        for skill_obj in profile.skills:
            skill = skill_obj.skill
            if skill not in self.skill_index:
                self.skill_index[skill] = []
            if agent_id not in self.skill_index[skill]:
                self.skill_index[skill].append(agent_id)

        self.logger.info(f"Registered agent '{profile.name}' ({profile.role.value})")
        return agent_id

    def get_agent(
        self, agent_id: Optional[str] = None, role: Optional[AgentRole] = None
    ) -> Optional[ExpertAgentProfile]:
        """
        Retrieve an agent by ID or role.

        Args:
            agent_id: Agent ID to retrieve
            role: Agent role to retrieve (returns first match)

        Returns:
            ExpertAgentProfile or None if not found
        """
        if agent_id:
            return self.agents.get(agent_id)

        if role and role in self.role_index:
            agent_ids = self.role_index[role]
            if agent_ids:
                return self.agents[agent_ids[0]]

        return None

    def find_agents_by_skill(
        self,
        skills: List[SkillTag],
        min_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE,
        require_all: bool = False,
    ) -> List[ExpertAgentProfile]:
        """
        Find agents with specific skills.

        Args:
            skills: List of skills to search for
            min_level: Minimum expertise level
            require_all: If True, agent must have all skills; if False, any skill matches

        Returns:
            List of matching agent profiles
        """
        matching_agents = []

        for agent_id, profile in self.agents.items():
            if require_all:
                # Agent must have all skills
                has_all = all(profile.has_skill(skill, min_level) for skill in skills)
                if has_all:
                    matching_agents.append(profile)
            else:
                # Agent must have at least one skill
                has_any = any(profile.has_skill(skill, min_level) for skill in skills)
                if has_any:
                    matching_agents.append(profile)

        return matching_agents

    async def assemble_team(
        self, requirements: TaskRequirements
    ) -> Dict[str, Any]:
        """
        Assemble an optimal team of agents for a task.

        Uses a scoring algorithm to select the best combination of agents
        based on required skills, preferred skills, and collaboration affinity.

        Args:
            requirements: Task requirements including skills and constraints

        Returns:
            Dictionary containing:
                - team: List of selected agent profiles
                - coverage: Skill coverage analysis
                - team_score: Overall team quality score
                - recommendations: Suggestions for team composition
        """
        self.logger.info(
            f"Assembling team for '{requirements.task_type}' "
            f"with {len(requirements.required_skills)} required skills"
        )

        # Score all agents for this task
        agent_scores = []
        for agent_id, profile in self.agents.items():
            score = self._score_agent_for_task(profile, requirements)
            if score > 0:
                agent_scores.append((profile, score))

        # Sort by score
        agent_scores.sort(key=lambda x: x[1], reverse=True)

        # Select team
        selected_team = []
        covered_skills: Set[SkillTag] = set()

        # First, select agents for required skills
        for profile, score in agent_scores:
            if len(selected_team) >= requirements.max_team_size:
                break

            # Check if this agent adds new required skill coverage
            agent_required_skills = [
                s for s in requirements.required_skills
                if profile.has_skill(s, requirements.min_expertise)
            ]

            new_coverage = set(agent_required_skills) - covered_skills
            if new_coverage or len(selected_team) < requirements.min_team_size:
                selected_team.append(profile)
                covered_skills.update(agent_required_skills)

        # Analyze coverage
        required_coverage = len(covered_skills) / len(requirements.required_skills) if requirements.required_skills else 1.0

        # Add agents for preferred skills if room
        if len(selected_team) < requirements.max_team_size:
            for profile, score in agent_scores:
                if profile in selected_team:
                    continue
                if len(selected_team) >= requirements.max_team_size:
                    break

                # Check if adds preferred skills
                adds_preferred = any(
                    profile.has_skill(s) for s in requirements.preferred_skills
                )
                if adds_preferred:
                    selected_team.append(profile)

        # Calculate team score
        team_score = self._calculate_team_score(selected_team, requirements)

        # Generate recommendations
        recommendations = self._generate_team_recommendations(
            selected_team, requirements, covered_skills
        )

        return {
            "team": [
                {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "role": agent.role.value,
                    "skills": [s.skill.value for s in agent.skills],
                }
                for agent in selected_team
            ],
            "coverage": {
                "required_skills_coverage": required_coverage,
                "covered_skills": [s.value for s in covered_skills],
                "missing_skills": [
                    s.value
                    for s in requirements.required_skills
                    if s not in covered_skills
                ],
            },
            "team_score": team_score,
            "recommendations": recommendations,
        }

    def _score_agent_for_task(
        self, profile: ExpertAgentProfile, requirements: TaskRequirements
    ) -> float:
        """
        Score how well an agent fits a task.

        Args:
            profile: Agent profile
            requirements: Task requirements

        Returns:
            Score (0.0-1.0)
        """
        score = 0.0

        # Required skills (weighted heavily)
        required_match_count = sum(
            1
            for skill in requirements.required_skills
            if profile.has_skill(skill, requirements.min_expertise)
        )
        if requirements.required_skills:
            score += 0.6 * (required_match_count / len(requirements.required_skills))

        # Preferred skills
        preferred_match_count = sum(
            1 for skill in requirements.preferred_skills if profile.has_skill(skill)
        )
        if requirements.preferred_skills:
            score += 0.2 * (preferred_match_count / len(requirements.preferred_skills))

        # Average expertise level (higher is better)
        level_map = {
            ExpertiseLevel.NOVICE: 1,
            ExpertiseLevel.INTERMEDIATE: 2,
            ExpertiseLevel.ADVANCED: 3,
            ExpertiseLevel.EXPERT: 4,
            ExpertiseLevel.MASTER: 5,
        }
        avg_level = sum(level_map[s.level] for s in profile.skills) / len(
            profile.skills
        )
        score += 0.2 * (avg_level / 5.0)

        return min(1.0, score)

    def _calculate_team_score(
        self, team: List[ExpertAgentProfile], requirements: TaskRequirements
    ) -> float:
        """
        Calculate overall team quality score.

        Args:
            team: Selected team
            requirements: Task requirements

        Returns:
            Team score (0.0-1.0)
        """
        if not team:
            return 0.0

        # Coverage score
        all_team_skills = set()
        for agent in team:
            for skill_obj in agent.skills:
                all_team_skills.add(skill_obj.skill)

        required_covered = sum(
            1 for s in requirements.required_skills if s in all_team_skills
        )
        coverage_score = (
            required_covered / len(requirements.required_skills)
            if requirements.required_skills
            else 1.0
        )

        # Diversity score (prefer diverse skill sets)
        unique_roles = len(set(agent.role for agent in team))
        diversity_score = min(1.0, unique_roles / len(team))

        # Size score (prefer optimal team size)
        optimal_size = (requirements.min_team_size + requirements.max_team_size) / 2
        size_score = 1.0 - abs(len(team) - optimal_size) / optimal_size

        # Combined score
        team_score = 0.5 * coverage_score + 0.3 * diversity_score + 0.2 * size_score
        return team_score

    def _generate_team_recommendations(
        self,
        team: List[ExpertAgentProfile],
        requirements: TaskRequirements,
        covered_skills: Set[SkillTag],
    ) -> List[str]:
        """Generate recommendations for team composition."""
        recommendations = []

        # Check for missing required skills
        missing_skills = set(requirements.required_skills) - covered_skills
        if missing_skills:
            recommendations.append(
                f"⚠️ Missing required skills: {', '.join(s.value for s in missing_skills)}"
            )

        # Check team size
        if len(team) < requirements.min_team_size:
            recommendations.append(
                f"⚠️ Team size ({len(team)}) below minimum ({requirements.min_team_size})"
            )

        # Provide positive feedback
        if not missing_skills and len(team) >= requirements.min_team_size:
            recommendations.append(
                "✓ Team has full coverage of required skills"
            )

        # Suggest complementary skills
        if len(team) < requirements.max_team_size:
            recommendations.append(
                f"💡 Consider adding {requirements.max_team_size - len(team)} more agent(s) for better coverage"
            )

        return recommendations

    async def update_performance(
        self,
        agent_id: str,
        task_type: str,
        performance_score: float,
    ) -> None:
        """
        Update an agent's performance history.

        Args:
            agent_id: Agent to update
            task_type: Type of task performed
            performance_score: Performance score (0.0-1.0)
        """
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        # Update performance history
        if task_type not in agent.performance_history:
            agent.performance_history[task_type] = performance_score
        else:
            # Exponential moving average
            alpha = 0.3
            agent.performance_history[task_type] = (
                alpha * performance_score
                + (1 - alpha) * agent.performance_history[task_type]
            )

        self.logger.info(
            f"Updated performance for {agent.name}: "
            f"{task_type}={performance_score:.2f}"
        )
