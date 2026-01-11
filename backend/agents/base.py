"""
Base agent class for all Raptorflow agents.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config import ModelTier
from .exceptions import DatabaseError, ValidationError
from .skills.registry import get_skills_registry
from .state import AgentState, add_message, update_state
from .tools.registry import get_tool_registry

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all Raptorflow agents."""

    def __init__(
        self,
        name: str,
        description: str,
        model_tier: ModelTier = ModelTier.FLASH_LITE,
        tools: Optional[List[str]] = None,
        skills: Optional[List[str]] = None,
    ):
        """Initialize the agent."""
        self.name = name
        self.description = description
        self.model_tier = model_tier
        self.tools = tools or []
        self.skills = skills or []

        # LLM instance will be created lazily when needed
        self.llm = None

        # Tool registry instance
        self.tool_registry = get_tool_registry()

        # Skills registry instance
        self.skills_registry = get_skills_registry()

        # Agent metadata
        self.metadata = {
            "name": name,
            "description": description,
            "model_tier": model_tier,
            "tools": self.tools,
            "skills": self.skills,
            "version": "1.0.0",
        }

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass

    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        """Execute the agent's primary function."""
        pass

    def get_tools(self) -> List[str]:
        """Get the list of tools this agent can use."""
        return self.tools.copy()

    def register_tool(self, tool_name: str):
        """Register a new tool for this agent."""
        if tool_name not in self.tools:
            self.tools.append(tool_name)
            logger.info(f"Registered tool '{tool_name}' for agent '{self.name}'")

    async def _call_llm(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        """Call the LLM with the agent's model tier."""
        if system_prompt is None:
            system_prompt = self.get_system_prompt()

        # Get LLM instance lazily
        if self.llm is None:
            from .llm import get_llm

            self.llm = get_llm(self.model_tier)

        try:
            response = await self.llm.generate(prompt, system_prompt, **kwargs)
            return response
        except Exception as e:
            logger.error(f"LLM call failed for agent '{self.name}': {e}")
            raise

    async def _call_llm_structured(
        self, prompt: str, output_schema, system_prompt: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Call the LLM for structured output."""
        if system_prompt is None:
            system_prompt = self.get_system_prompt()

        # Get LLM instance lazily
        if self.llm is None:
            from .llm import get_llm

            self.llm = get_llm(self.model_tier)

        try:
            response = await self.llm.generate_structured(
                prompt, output_schema, system_prompt, **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Structured LLM call failed for agent '{self.name}': {e}")
            raise

    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        try:
            tool = self.tool_registry.get(tool_name)
            if not tool:
                raise ValidationError(f"Tool '{tool_name}' not found in registry")

            logger.info(f"Agent '{self.name}' using tool '{tool_name}'")
            result = await tool.arun(**kwargs)

            if not result.success:
                raise ValidationError(f"Tool '{tool_name}' failed: {result.error}")

            return result.data

        except Exception as e:
            logger.error(f"Tool execution failed for '{tool_name}': {e}")
            raise

    async def get_tool(self, tool_name: str):
        """Get a tool instance."""
        return self.tool_registry.get(tool_name)

    def has_skill(self, skill: str) -> bool:
        """Check if agent has a specific skill."""
        return skill in self.skills

    def get_skills(self) -> List[str]:
        """Get list of agent skills."""
        return self.skills.copy()

    async def execute_with_tools(
        self, state: AgentState, tool_calls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute multiple tools in sequence."""
        results = {}

        for tool_call in tool_calls:
            tool_name = tool_call.get("tool")
            tool_params = tool_call.get("params", {})

            if tool_name in self.tools:
                result = await self.use_tool(tool_name, **tool_params)
                results[tool_name] = result
            else:
                logger.warning(
                    f"Agent '{self.name}' doesn't have access to tool '{tool_name}'"
                )

        return results

    def assess_skills(self) -> Dict[str, Any]:
        """Assess agent's skill proficiency."""
        try:
            assessments = self.skills_registry.assess_agent_skills(
                agent_name=self.name, agent_skills=self.skills, agent_tools=self.tools
            )

            # Calculate overall skill score
            total_confidence = sum(assessment.confidence for assessment in assessments)
            avg_confidence = total_confidence / len(assessments) if assessments else 0.0

            # Group assessments by category
            by_category = {}
            for assessment in assessments:
                skill = self.skills_registry.get_skill(assessment.skill_name)
                if skill:
                    category = skill.category.value
                    if category not in by_category:
                        by_category[category] = []
                    by_category[category].append(assessment.to_dict())

            return {
                "agent_name": self.name,
                "total_skills": len(self.skills),
                "assessed_skills": len(assessments),
                "overall_confidence": avg_confidence,
                "assessments": [assessment.to_dict() for assessment in assessments],
                "by_category": by_category,
                "assessment_date": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Skill assessment failed for agent '{self.name}': {e}")
            return {
                "agent_name": self.name,
                "error": str(e),
                "assessment_date": datetime.now().isoformat(),
            }

    def get_skill_requirements(self, task: str) -> Dict[str, Any]:
        """Get skill requirements for a specific task."""
        try:
            # Simple task-to-skill mapping
            task_keywords = task.lower().split()
            required_skills = []

            # Map task keywords to skills
            skill_mapping = {
                "content": [
                    "content_generation",
                    "seo_optimization",
                    "brand_voice_adaptation",
                ],
                "research": [
                    "competitor_analysis",
                    "market_sizing",
                    "trend_identification",
                ],
                "strategy": ["strategic_planning", "growth_hacking", "positioning"],
                "analyze": [
                    "data_analysis",
                    "performance_tracking",
                    "metrics_interpretation",
                ],
                "write": ["content_generation", "copywriting", "storytelling"],
                "market": ["market_sizing", "competitor_analysis", "industry_research"],
                "plan": ["strategic_planning", "go_to_market"],
                "report": ["data_analysis", "reporting", "metrics_interpretation"],
            }

            for keyword, skills in skill_mapping.items():
                if keyword in task_keywords:
                    required_skills.extend(skills)

            # Remove duplicates and check availability
            available_skills = list(set(required_skills) & set(self.skills))
            missing_skills = list(set(required_skills) - set(self.skills))

            return {
                "task": task,
                "required_skills": required_skills,
                "available_skills": available_skills,
                "missing_skills": missing_skills,
                "can_execute": len(missing_skills) == 0,
                "skill_coverage": (
                    len(available_skills) / len(required_skills)
                    if required_skills
                    else 1.0
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get skill requirements for task '{task}': {e}")
            return {"task": task, "error": str(e), "can_execute": False}

    def validate_skill_requirements(self, task: str) -> bool:
        """Validate if agent has required skills for a task."""
        requirements = self.get_skill_requirements(task)
        return requirements.get("can_execute", False)

    def _update_state(self, state: AgentState, **updates) -> AgentState:
        """Update the agent state and track changes."""
        # Add current agent to routing path if not already there
        if "current_agent" in updates:
            current_agent = updates["current_agent"]
            if current_agent not in state.get("routing_path", []):
                if "routing_path" not in updates:
                    updates["routing_path"] = state.get("routing_path", []).copy()
                updates["routing_path"].append(current_agent)

        return update_state(state, **updates)

    def _add_user_message(self, state: AgentState, content: str) -> AgentState:
        """Add a user message to the state."""
        return add_message(state, "user", content, agent=self.name)

    def _add_assistant_message(self, state: AgentState, content: str) -> AgentState:
        """Add an assistant message to the state."""
        return add_message(state, "assistant", content, agent=self.name)

    def _add_system_message(self, state: AgentState, content: str) -> AgentState:
        """Add a system message to the state."""
        return add_message(state, "system", content, agent=self.name)

    def _set_error(self, state: AgentState, error: str) -> AgentState:
        """Set an error in the state."""
        return self._update_state(
            state, error=error, output=None, pending_approval=False
        )

    def _set_output(self, state: AgentState, output: Any) -> AgentState:
        """Set the output in the state."""
        return self._update_state(state, output=output, error=None)

    def _get_context_summary(self, state: AgentState) -> str:
        """Get a summary of the current context."""
        context_parts = []

        # Foundation summary
        if state.get("foundation_summary"):
            context_parts.append(f"Foundation: {state['foundation_summary']}")

        # Brand voice
        if state.get("brand_voice"):
            context_parts.append(f"Brand Voice: {state['brand_voice']}")

        # Active ICPs
        if state.get("active_icps"):
            icp_names = [icp.get("name", "Unknown") for icp in state["active_icps"]]
            context_parts.append(f"Target ICPs: {', '.join(icp_names)}")

        return (
            "\n".join(context_parts)
            if context_parts
            else "No additional context available."
        )

    def _get_recent_messages(
        self, state: AgentState, max_messages: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent messages from the state."""
        messages = state.get("messages", [])
        return messages[-max_messages:] if messages else []

    def _extract_user_input(self, state: AgentState) -> Optional[str]:
        """Extract the most recent user input."""
        messages = state.get("messages", [])
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg.get("content")
        return None

    def _requires_approval(self, state: AgentState) -> bool:
        """Check if the current output requires approval."""
        return state.get("pending_approval", False)

    def _get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            **self.metadata,
            "system_prompt": self.get_system_prompt(),
            "llm_model": self.model_tier.value,
            "tool_count": len(self.tools),
        }

    async def validate_input(self, state: AgentState) -> bool:
        """Validate the input state before execution."""
        # Check required fields
        required_fields = ["workspace_id", "user_id", "session_id"]
        for field in required_fields:
            if not state.get(field):
                logger.error(
                    f"Missing required field '{field}' for agent '{self.name}'"
                )
                return False

        return True

    async def prepare_execution(self, state: AgentState) -> AgentState:
        """Prepare the state for execution."""
        # Set current agent
        state = self._update_state(state, current_agent=self.name)

        # Add system message about agent execution
        state = self._add_system_message(
            state, f"Starting execution with agent '{self.name}'"
        )

        return state

    async def finalize_execution(self, state: AgentState) -> AgentState:
        """Finalize the execution."""
        # Add completion message
        if state.get("error"):
            state = self._add_system_message(
                state, f"Agent '{self.name}' execution failed: {state['error']}"
            )
        else:
            state = self._add_system_message(
                state, f"Agent '{self.name}' execution completed successfully"
            )

        return state
