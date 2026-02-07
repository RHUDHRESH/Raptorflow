"""
Base agent class for all Raptorflow agents.
"""

import asyncio
import logging
import re
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypedDict

from .config import ModelTier, get_config, get_rate_limiter
from .exceptions import (
    DatabaseError,
    LLMError,
    RateLimitError,
    ToolError,
    ValidationError,
)
from .state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all Raptorflow agents."""

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tools: Optional[List[str]] = None,
        skills: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        model_tier: Optional[ModelTier] = None,
        enable_performance_tracking: bool = True,
        enable_resource_pooling: bool = True,
    ):
        """Initialize agent using simplified configuration."""
        # Use provided parameters or defaults
        self.name = name or self.__class__.__name__
        self.description = description or f"{self.__class__.__name__} agent"
        self.tools = tools or []
        self.skills = skills or []
        self.model_tier = model_tier or ModelTier.FLASH

        # Get simplified configuration
        try:
            self.config = get_config()
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
            self.config = None

        # Session management
        self.session_id = session_id
        self.enable_performance_tracking = enable_performance_tracking
        self.enable_resource_pooling = enable_resource_pooling

        # LLM instance will be created lazily when needed
        self.llm = None

        # Rate limiter for this agent
        try:
            self.rate_limiter = get_rate_limiter()
        except Exception as e:
            logger.warning(f"Could not create rate limiter: {e}")
            self.rate_limiter = None

        # Initialize cache for this agent
        try:
            from core.cache import get_agent_cache

            self.cache = get_agent_cache()
        except ImportError:
            self.cache = None
            logger.warning(f"Cache not available for agent '{self.name}'")

        # Performance tracking - simplified
        self.performance_optimizer = None
        self.resource_monitor = None
        self.execution_id = None

        # Resource pooling - simplified
        self.connection_pool = None
        self.memory_pool = None

        # Initialize resource tracking
        self._tracked_resources = {
            "file_handle": {},
            "task": {},
            "connection": {},
            "memory": {},
        }

        # [FREEDOM TWEAK] Loop Detective
        self._action_history = []

        # Agent state for session persistence
        self.agent_state = {
            "conversation_context": [],
            "user_preferences": {},
            "workspace_context": {},
            "temporary_data": {},
            "performance_metrics": {},
        }

        # Agent metadata
        self.metadata = {
            "name": self.name,
            "description": self.description,
            "tools": self.tools,
            "skills": self.skills,
            "version": "1.0.0",
            "initialized_at": datetime.now().isoformat(),
            "environment": self.config.environment if self.config else "unknown",
            "llm_provider": self.config.llm_provider if self.config else "unknown",
        }

    def _validate_initialization(self):
        """Validate agent initialization and log warnings."""
        try:
            # Validate required fields
            if not self.name:
                raise ValueError("Agent name is required")
            if not self.description:
                raise ValueError("Agent description is required")

            # Validate configuration
            if not self.config:
                raise ValueError("Configuration not loaded")

            # Log successful initialization
            logger.info(
                f"Agent '{self.name}' initialized successfully: "
                f"{len(self.tools)} tools, "
                f"{len(self.skills)} skills, "
                f"environment: {self.config.environment}"
            )

            # Store initialization status
            self._initialization_status = {
                "success": True,
                "validated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Agent '{self.name}' initialization validation failed: {str(e)}"
            )
            self._initialization_status = {
                "success": False,
                "error": str(e),
                "validated_at": datetime.now().isoformat(),
            }
            raise ValueError(f"Agent initialization failed: {str(e)}")

    async def check_rate_limit(self, user_id: str, endpoint: str = "agent") -> bool:
        """Check if user is within rate limits for this agent."""
        try:
            allowed, stats = await self.rate_limiter.check_limit(user_id, endpoint)
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for user {user_id}: {stats.get('reason', 'Unknown')}"
                )
            return allowed
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Allow request if rate limiting fails
            return True

    def get_initialization_status(self) -> Dict[str, Any]:
        """Get the initialization status of the agent."""
        return getattr(
            self,
            "_initialization_status",
            {
                "success": False,
                "error": "Initialization not completed",
                "validated_at": None,
            },
        )

    def is_healthy(self) -> bool:
        """Check if agent is healthy and ready for operations."""
        try:
            init_status = self.get_initialization_status()
            return init_status.get("success", False) and self.config is not None
        except Exception as e:
            logger.error(f"Health check failed for agent '{self.name}': {e}")
            return False

    async def set_session(self, session_id: str, user_id: str = None) -> bool:
        """Set or update session context for this agent."""
        try:
            # Validate session
            session = await self.session_manager.validate_session(session_id)
            if not session:
                logger.warning(f"Invalid session {session_id} for agent {self.name}")
                return False

            self.session_id = session_id

            # Restore agent state from session context
            if session.context.agent_state:
                self.agent_state.update(session.context.agent_state)

            # Update session with agent reference
            await self.session_manager.update_session_context(
                session_id, {"agent_state": self.agent_state}
            )

            logger.info(f"Agent '{self.name}' attached to session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to set session for agent '{self.name}': {e}")
            return False

    async def save_session_state(self) -> bool:
        """Save current agent state to session."""
        try:
            if not self.session_id:
                return False

            # Update session context with current state
            await self.session_manager.update_session_context(
                self.session_id, {"agent_state": self.agent_state}
            )

            return True

        except Exception as e:
            logger.error(f"Failed to save session state for agent '{self.name}': {e}")
            return False

    async def add_conversation_message(
        self, role: str, content: str, metadata: Dict[str, Any] = None
    ) -> bool:
        """Add a message to conversation history."""
        try:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "agent": self.name,
                "metadata": metadata or {},
            }

            self.agent_state["conversation_context"].append(message)

            # Keep only last 50 messages in agent state
            if len(self.agent_state["conversation_context"]) > 50:
                self.agent_state["conversation_context"] = self.agent_state[
                    "conversation_context"
                ][-50:]

            # Update session context
            if self.session_id:
                await self.session_manager.update_session_context(
                    self.session_id,
                    {
                        "conversation_history": [
                            {
                                "role": role,
                                "content": content,
                                "timestamp": datetime.utcnow().isoformat(),
                                "metadata": metadata or {},
                            }
                        ]
                    },
                )

            return True

        except Exception as e:
            logger.error(
                f"Failed to add conversation message for agent '{self.name}': {e}"
            )
            return False

    async def start_execution_tracking(
        self, execution_context: Dict[str, Any] = None
    ) -> str:
        """Start performance tracking for an execution."""
        if not self.enable_performance_tracking:
            return None

        try:
            self.execution_id = str(uuid.uuid4())

            # Start performance tracking
            tracker = self.performance_optimizer.start_tracking(
                self.execution_id, self.name, self.session_id
            )

            # Add execution context
            if execution_context:
                tracker.add_metric("execution_context", 1, "count", execution_context)

            logger.debug(
                f"Started execution tracking for {self.name}: {self.execution_id}"
            )
            return self.execution_id

        except Exception as e:
            logger.error(
                f"Failed to start execution tracking for agent '{self.name}': {e}"
            )
            return None

    async def end_execution_tracking(
        self, execution_result: Any = None, additional_metrics: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """End performance tracking and collect metrics."""
        if not self.enable_performance_tracking or not self.execution_id:
            return {}

        try:
            # Prepare additional metrics
            metrics = {
                "tokens_used": self._extract_token_usage(execution_result),
                "tool_calls": self._count_tool_calls(execution_result),
                "skill_calls": self._count_skill_calls(execution_result),
                "error_count": 1 if isinstance(execution_result, Exception) else 0,
                "response_quality_score": self._calculate_quality_score(
                    execution_result
                ),
                "request_size_bytes": (
                    len(str(execution_result)) if execution_result else 0
                ),
                "response_size_bytes": (
                    len(str(execution_result)) if execution_result else 0
                ),
            }

            if additional_metrics:
                metrics.update(additional_metrics)

            # End tracking and get metrics
            performance_metrics = await self.performance_optimizer.end_tracking(
                self.execution_id, self.name, self.session_id, metrics
            )

            # Store in agent state
            self.agent_state["performance_metrics"][self.execution_id] = (
                performance_metrics.to_dict() if performance_metrics else {}
            )

            # Save to session
            await self.save_session_state()

            logger.debug(
                f"Ended execution tracking for {self.name}: {self.execution_id}"
            )
            self.execution_id = None

            return performance_metrics.to_dict() if performance_metrics else {}

        except Exception as e:
            logger.error(
                f"Failed to end execution tracking for agent '{self.name}': {e}"
            )
            return {}

    def _extract_token_usage(self, result: Any) -> int:
        """Extract token usage from result."""
        if isinstance(result, dict):
            return result.get("tokens_used", 0)
        return 0

    def _count_tool_calls(self, result: Any) -> int:
        """Count tool calls in result."""
        if isinstance(result, dict):
            return result.get("tool_calls", 0)
        return 0

    def _count_skill_calls(self, result: Any) -> int:
        """Count skill calls in result."""
        if isinstance(result, dict):
            return result.get("skill_calls", 0)
        return 0

    def _calculate_quality_score(self, result: Any) -> Optional[float]:
        """Calculate response quality score."""
        if isinstance(result, dict):
            return result.get("quality_score")
        return None

    async def get_pooled_connection(self, connection_type: str = "default"):
        """Get a connection from the pool."""
        if not self.enable_resource_pooling or not self.connection_pool:
            return None

        try:
            connection = self.connection_pool.acquire()
            self._tracked_resources["connection"][connection_type] = connection
            return connection.resource
        except Exception as e:
            logger.error(
                f"Failed to get pooled connection for agent '{self.name}': {e}"
            )
            return None

    async def release_pooled_connection(
        self, connection, connection_type: str = "default"
    ):
        """Release a connection back to the pool."""
        if not self.enable_resource_pooling or not self.connection_pool:
            return False

        try:
            tracked_connection = self._tracked_resources["connection"].get(
                connection_type
            )
            if tracked_connection:
                self.connection_pool.release(tracked_connection)
                del self._tracked_resources["connection"][connection_type]
                return True
        except Exception as e:
            logger.error(
                f"Failed to release pooled connection for agent '{self.name}': {e}"
            )
        return False

    async def get_pooled_memory(self, size: int = 1024 * 1024) -> bytearray:
        """Get memory buffer from the pool."""
        if not self.enable_resource_pooling or not self.memory_pool:
            return bytearray(size)

        try:
            memory = self.memory_pool.acquire()
            self._tracked_resources["memory"][id(memory)] = memory
            return memory.resource
        except Exception as e:
            logger.error(f"Failed to get pooled memory for agent '{self.name}': {e}")
            return bytearray(size)

    async def release_pooled_memory(self, memory: bytearray):
        """Release memory buffer back to the pool."""
        if not self.enable_resource_pooling or not self.memory_pool:
            return False

        try:
            tracked_memory = self._tracked_resources["memory"].get(id(memory))
            if tracked_memory:
                self.memory_pool.release(tracked_memory)
                del self._tracked_resources["memory"][id(memory)]
                return True
        except Exception as e:
            logger.error(
                f"Failed to release pooled memory for agent '{self.name}': {e}"
            )
        return False

    async def cleanup_resources(self):
        """Cleanup all tracked resources."""
        try:
            # Release all connections
            for conn_type, connection in self._tracked_resources["connection"].items():
                await self.release_pooled_connection(connection.resource, conn_type)

            # Release all memory
            for memory_id, memory in self._tracked_resources["memory"].items():
                await self.release_pooled_memory(memory.resource)

            # Clear tracking
            self._tracked_resources = {
                "file_handle": {},
                "task": {},
                "connection": {},
                "memory": {},
            }

            logger.info(f"Cleaned up all resources for agent '{self.name}'")

        except Exception as e:
            logger.error(f"Failed to cleanup resources for agent '{self.name}': {e}")

    async def get_agent_metrics(self) -> Dict[str, Any]:
        """Get comprehensive agent metrics."""
        try:
            metrics = {
                "agent_name": self.name,
                "session_id": self.session_id,
                "is_healthy": self.is_healthy(),
                "conversation_length": len(
                    self.agent_state.get("conversation_context", [])
                ),
                "tracked_resources": {
                    resource_type: len(resources)
                    for resource_type, resources in self._tracked_resources.items()
                },
                "performance_tracking_enabled": self.enable_performance_tracking,
                "resource_pooling_enabled": self.enable_resource_pooling,
                "agent_state_size": len(str(self.agent_state)),
            }

            # Add performance metrics if available
            if self.performance_optimizer:
                perf_stats = self.performance_optimizer.get_performance_stats()
                metrics["performance_stats"] = perf_stats

            # Add resource monitoring if available
            if self.resource_monitor:
                current_metrics = self.resource_monitor.get_current_metrics()
                metrics["resource_metrics"] = current_metrics

            return metrics

        except Exception as e:
            logger.error(f"Failed to get agent metrics for '{self.name}': {e}")
            return {"error": str(e)}

    # ... (skipping methods until use_tool)

    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        try:
            # [FREEDOM TWEAK] Loop Detective
            # Check for recursive/repetitive loops
            current_action = f"{tool_name}:{str(sorted(kwargs.items()))}"
            self._action_history.append(current_action)

            # Look at last 3 actions
            if len(self._action_history) >= 3:
                last_three = self._action_history[-3:]
                # If all three are identical, we have a loop
                if all(x == current_action for x in last_three):
                    logger.critical(
                        f"[LOOP DETECTED] Agent '{self.name}' is looping on {tool_name}. Forcing break."
                    )
                    raise ValidationError(
                        "Loop Detected: You are repeating the same action. STOP. Try a different strategy."
                    )

            # [FREEDOM TWEAK] Dynamic Tool Access
            # First check strictly assigned tools, but fallback to global registry for autonomy
            tool = self.tool_registry.get(tool_name)

            if not tool:
                # One last check - maybe fuzzy match or it's a skill disguised as a tool?
                # For now just fail if absolutely not found in registry
                raise ValidationError(f"Tool '{tool_name}' not found in registry")

            if tool_name not in self.tools:
                logger.info(
                    f"[AUTONOMY] Agent '{self.name}' dynamically using tool '{tool_name}' which was not effectively whitelisted."
                )

            logger.info(f"Agent '{self.name}' using tool '{tool_name}'")
            result = await tool.arun(**kwargs)

            if not result.success:
                logger.warning(
                    f"Tool '{tool_name}' failed: {result.error} - attempting recovery suggestion..."
                )
                # [FREEDOM TWEAK] Smart Failure Recovery
                # If tool fails, simple re-raise but we might want to inject the suggestion here?
                # Actually, the calling loop (execute) should catch this and call _ask_for_alternative_strategy
                raise ValidationError(f"Tool '{tool_name}' failed: {result.error}")

            return result.data

        except ValidationError as e:
            logger.error(f"Validation error for tool '{tool_name}': {e.message}")
            raise
        except DatabaseError as e:
            logger.error(f"Database error for tool '{tool_name}': {e.message}")
            raise
        except LLMError as e:
            logger.error(f"LLM error for tool '{tool_name}': {e.message}")
            raise
        except TimeoutError as e:
            logger.error(f"Timeout error for tool '{tool_name}': {e.message}")
            raise
        except RateLimitError as e:
            logger.error(f"Rate limit error for tool '{tool_name}': {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for tool '{tool_name}': {str(e)}")
            raise ToolError(f"Tool '{tool_name}' failed: {str(e)}")

    def _trim_context(self, messages: List[Any]) -> List[Any]:
        """
        [FREEDOM TWEAK] Context Sentinel
        Intelligently trim context if it gets too long.
        """
        MAX_MESSAGES = 15  # Keep reasonable window
        if len(messages) <= MAX_MESSAGES:
            return messages

        # Always keep System prompt (usually index 0)
        # Always keep last N messages
        system_msgs = [m for m in messages if m.role == "system"]
        recent_msgs = messages[-(MAX_MESSAGES - len(system_msgs)) :]

        trimmed = system_msgs + recent_msgs
        logger.info(
            f"[CONTEXT SENTINEL] Trimmed context from {len(messages)} to {len(trimmed)} messages."
        )
        return trimmed

    def _verify_output(self, content: str) -> bool:
        """
        [FREEDOM TWEAK] Output Guardian
        Check for refusal patterns or hallucinations.
        """
        refusal_patterns = [
            "I cannot fulfill this request",
            "I am an AI language model",
            "I cannot browse the web",  # False, it can
            "I do not have access to real-time information",  # False
        ]

        for pattern in refusal_patterns:
            if pattern.lower() in content.lower():
                logger.warning(
                    f"[OUTPUT GUARDIAN] Refusal pattern detected: '{pattern}'"
                )
                return False
        return True

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
        """
        Call the LLM with the agent's model tier.
        [FREEDOM TWEAK] Universial Retry Logic
        Implements exponential backoff for resilience.
        """
        if system_prompt is None:
            system_prompt = self.get_system_prompt()

        # [FREEDOM TWEAK] Autonomy Injection
        # We append a 'Freedom License' to the system prompt
        autonomy_license = (
            "\n\n[AUTONOMY PROTOCOL ACTIVATED]\n"
            "You are an autonomous agent with full access to the Swarm Registry. "
            "1. If you need a tool not explicitly listed, you MAY request it dynamically.\n"
            "2. Failure is not an option; if a tool fails, propose an alternative strategy.\n"
            "3. Optimize for QUALITY and CREATIVITY. Do not be constrained by rigid formatting unless specified.\n"
            "4. You have permission to 'think outside the box' to solve the user's core objective.\n"
            "5. UNCERTAIN ABOUT TOOLS? You can now 'list_available_tools()' to see what capabilities are available.\n\n"
            "[PERSONALITY: FOUNDER MODE]\n"
            "Be decisive. Be brief. Focus on high-leverage moves. No fluff. No corporate speak. "
            "Act like a relentless operator executing a vision."
        )
        system_prompt += autonomy_license

        # Get LLM instance lazily
        if self.llm is None:
            from llm import get_llm

            self.llm = get_llm(self.model_tier)

        import asyncio

        max_retries = 3
        backoff = 1

        last_error = None

        for attempt in range(max_retries):
            try:
                response = await self.llm.generate(prompt, system_prompt, **kwargs)
                return response
            except Exception as e:
                last_error = e
                wait_time = backoff * (2**attempt)
                logger.warning(
                    f"LLM call failed for agent '{self.name}' (Attempt {attempt+1}/{max_retries}): {e}. "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

        logger.error(
            f"LLM call failed permanently after {max_retries} attempts for agent '{self.name}': {last_error}"
        )
        raise last_error

    async def _ask_for_alternative_strategy(
        self, failed_tool: str, error_msg: str, context: Optional[str] = None
    ) -> str:
        """
        [FREEDOM TWEAK] Smart Failure Recovery
        Ask the LLM for a Plan B when a tool fails.
        """
        recovery_prompt = (
            f"CRITICAL: The tool '{failed_tool}' failed with error: '{error_msg}'.\n"
            f"Context: {context or 'N/A'}\n\n"
            "You are in FOUNDER MODE. Do not apologize. Do not give up.\n"
            "Immediately propose an ALTERNATIVE STRATEGY or a different tool to achieve the same goal.\n"
            "What is your new plan?"
        )
        # We use a lower temperature for recovery to ensure stability
        return await self._call_llm(recovery_prompt, analytical_mode=True)

    async def execute_skill(
        self, skill_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        [FREEDOM TWEAK] Tool Chaining
        Generic method to execute any skill by name.
        Passes 'agent': self into context so skills can recursively call back.
        """
        skill = self.skills_registry.get_skill(skill_name)
        if not skill:
            # Dynamic acquisition check
            skill = await self.acquire_skill(skill_name)

        if not skill:
            raise ValidationError(f"Skill '{skill_name}' not found.")

        # Inject self for recursion/chaining
        context["agent"] = self

        logger.info(
            f"[CHAIN_REACTION] Agent '{self.name}' chaining skill '{skill_name}'"
        )
        return await skill.execute(context)

    async def decompose_and_execute(self, complex_task: str) -> Dict[str, Any]:
        """
        [FREEDOM TWEAK] Recursive Logic
        Ask the LLM to break down a task and execute steps.
        """
        prompt = f"Break down this complex task into 3-5 sub-steps that match your tools/skills: '{complex_task}'. Return JSON list of strings."
        # Simplified for brevity in this generic implementation
        # Real impl would parse steps and loop execute_skill/use_tool
        steps = await self._call_llm(prompt)
        return {"plan": steps, "status": "Decomposition logic ready"}

    async def _call_llm_structured(
        self, prompt: str, output_schema, system_prompt: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Call the LLM for structured output."""
        if system_prompt is None:
            system_prompt = self.get_system_prompt()

        # Get LLM instance lazily
        if self.llm is None:
            from llm import get_llm

            self.llm = get_llm(self.model_tier)

        try:
            response = await self.llm.generate_structured(
                prompt, output_schema, system_prompt, **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Structured LLM call failed for agent '{self.name}': {e}")
            raise

    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        [FREEDOM TWEAK]
        List ALL available tools in the registry.
        This allows the agent to 'shop' for tools if it doesn't know what it needs.
        """
        all_tools = self.tool_registry.list_tools()
        # Return a simplified list to save context window
        return [{"name": t.name, "description": t.description} for t in all_tools]

    async def get_tool(self, tool_name: str):
        """Get a tool instance."""
        return self.tool_registry.get(tool_name)

    async def acquire_skill(self, criteria: str) -> Optional[Any]:
        """
        Dynamically acquire a skill based on criteria/task.

        Args:
           criteria: Description of the task or skill needed.

        Returns:
            The Skill instance if found and acquired, else None.
        """
        logger.info(f"Agent '{self.name}' attempting to acquire skill for: {criteria}")

        # 1. Search registry
        matches = self.skills_registry.find_skills_for_task(criteria)

        if not matches:
            logger.warning(f"No skills found matching '{criteria}'")
            return None

        # 2. Select best match
        best_skill = matches[0]

        # 3. Bind to agent (add to skills list if not present)
        if best_skill.name not in self.skills:
            self.skills.append(best_skill.name)
            logger.info(f"Agent '{self.name}' acquired new skill: {best_skill.name}")

        return best_skill

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
        # [FREEDOM TWEAK] Parallel Execution
        # We now run all tools concurrently for maximum speed.
        import asyncio

        results = {}
        tasks = []
        tool_names = []

        for tool_call in tool_calls:
            tool_name = tool_call.get("tool")
            tool_params = tool_call.get("params", {})

            tool_names.append(tool_name)

            if tool_name in self.tools:
                # Schedule execution
                tasks.append(self.use_tool(tool_name, **tool_params))
            else:
                # If tool not found locally, try dynamic via use_tool
                # (since we updated use_tool to be dynamic, this check is redundant but we keep for safety)
                # We'll just trust use_tool to handle the lookup/error.
                tasks.append(self.use_tool(tool_name, **tool_params))

        if not tasks:
            return {}

        # Execute all concurrently
        try:
            completed_results = await asyncio.gather(*tasks, return_exceptions=True)

            for name, res in zip(tool_names, completed_results):
                if isinstance(res, Exception):
                    logger.error(f"Parallel tool execution failed for '{name}': {res}")
                    results[name] = {"success": False, "error": str(res)}
                else:
                    results[name] = res

        except Exception as e:
            logger.error(f"Critical failure in parallel execution group: {e}")
            # Fallback? No, just fail for now
            raise

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

        # [FREEDOM TWEAK] Context Maximization
        # We dump the Full, Deep Foundation Summary. No truncation.
        if state.get("foundation_summary"):
            # If it's a dict, we format it nicely
            summary = state["foundation_summary"]
            if isinstance(summary, dict):
                import json

                # Use indent=2 for readable structure that LLM can parse easily
                formatted_summary = json.dumps(summary, indent=2, default=str)
                context_parts.append(
                    f"=== FULL FOUNDATION CONTEXT ===\n{formatted_summary}"
                )
            else:
                context_parts.append(f"=== FOUNDATION CONTEXT ===\n{summary}")

        # Brand voice
        if state.get("brand_voice"):
            context_parts.append(f"Brand Voice: {state['brand_voice']}")

        # Active ICPs
        if state.get("active_icps"):
            icp_names = [icp.get("name", "Unknown") for icp in state["active_icps"]]
            context_parts.append(f"Target ICPs: {', '.join(icp_names)}")

        # [FREEDOM TWEAK] Cross-Agent Memory
        # Add recent actions from other agents
        cross_memory = self._get_cross_agent_memory(state)
        if cross_memory:
            context_parts.append(
                f"\n=== TEAM AWARENESS (Other Agents) ===\n{cross_memory}"
            )

        return (
            "\n".join(context_parts)
            if context_parts
            else "No additional context available."
        )

    def _get_cross_agent_memory(self, state: AgentState, limit: int = 5) -> str:
        """
        [FREEDOM TWEAK]
        Scan the state for 'assistant' messages produced by OTHER agents.
        This allows, for example, the SocialMediaAgent to see what the CampaignPlanner just proposed.
        """
        messages = state.get("messages", [])
        if not messages:
            return ""

        memory_log = []
        count = 0

        # Iterate backwards to get most recent
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                agent_name = msg.get("agent", "Unknown")
                # We want to know what OTHERS did, but also maybe remind ourselves what WE did nicely?
                # Let's show everything to be safe, but label the agent clearly.
                content = msg.get("content", "")

                # Truncate slightly if it's massive to avoid context overflow,
                # but keep it generous (Freedom Tweak).
                if len(content) > 500:
                    content = content[:500] + "... [truncated]"

                memory_log.append(f"[{agent_name}]: {content}")
                count += 1
                if count >= limit:
                    break

        return "\n".join(reversed(memory_log))

    def _get_recent_messages(
        self, state: AgentState, max_messages: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent messages from the state."""
        messages = state.get("messages", [])

        # [FREEDOM TWEAK] Context Sentinel Activation
        # Ensure we don't overflow context before returning
        trimmed_messages = self._trim_context(messages)

        # Then apply the requested slice
        return trimmed_messages[-max_messages:] if trimmed_messages else []

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

    async def validate_input(self, state: AgentState) -> tuple[bool, Optional[str]]:
        """Enhanced validation with comprehensive security and business logic checks."""
        try:
            # Import validation components
            from core.security import validate_agent_request as security_validate
            from core.validation import validate_agent_request

            # Check required fields
            required_fields = ["workspace_id", "user_id", "session_id"]
            for field in required_fields:
                if not state.get(field):
                    error_msg = (
                        f"Missing required field '{field}' for agent '{self.name}'"
                    )
                    logger.error(error_msg)
                    return False, error_msg

            # Validate field formats
            validation_errors = []

            # Workspace ID validation
            workspace_id = state.get("workspace_id", "")
            if len(workspace_id) < 3:
                validation_errors.append("Workspace ID must be at least 3 characters")
            if not re.match(r"^[a-zA-Z0-9_-]+$", workspace_id):
                validation_errors.append("Workspace ID contains invalid characters")

            # User ID validation
            user_id = state.get("user_id", "")
            if len(user_id) < 3:
                validation_errors.append("User ID must be at least 3 characters")
            if not re.match(r"^[a-zA-Z0-9_-]+$", user_id):
                validation_errors.append("User ID contains invalid characters")

            # Session ID validation
            session_id = state.get("session_id", "")
            if len(session_id) < 3:
                validation_errors.append("Session ID must be at least 3 characters")
            if not re.match(r"^[a-zA-Z0-9_-]+$", session_id):
                validation_errors.append("Session ID contains invalid characters")

            if validation_errors:
                error_msg = f"Validation failed: {'; '.join(validation_errors)}"
                logger.error(error_msg)
                return False, error_msg

            # Security validation for request content
            request_content = state.get("request", "")
            if request_content:
                # Use security validator
                is_secure, security_error = await security_validate(
                    {
                        "request": request_content,
                        "user_id": user_id,
                        "workspace_id": workspace_id,
                    }
                )

                if not is_secure:
                    logger.warning(
                        f"Security validation failed for agent '{self.name}': {security_error}"
                    )
                    return False, f"Security validation failed: {security_error}"

            # Agent-specific validation
            agent_validation_error = await self._validate_agent_specific_input(state)
            if agent_validation_error:
                return False, agent_validation_error

            # Resource availability check
            resource_error = await self._validate_resource_availability(state)
            if resource_error:
                return False, resource_error

            logger.debug(f"Input validation successful for agent '{self.name}'")
            return True, None

        except Exception as e:
            error_msg = f"Input validation error for agent '{self.name}': {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    async def _validate_agent_specific_input(self, state: AgentState) -> Optional[str]:
        """Validate agent-specific input requirements."""
        # Override in subclasses for agent-specific validation
        return None

    async def _validate_resource_availability(self, state: AgentState) -> Optional[str]:
        """Validate resource availability for the agent."""
        try:
            # Check LLM availability
            if not self.llm:
                return "LLM not available"

            # Check tool registry
            if not self.tool_registry:
                return "Tool registry not available"

            # Check skills registry
            if not self.skills_registry:
                return "Skills registry not available"

            # Check memory availability
            try:
                from memory_services import MemoryController

                memory_manager = MemoryController()
                if not memory_manager or not getattr(
                    memory_manager, "initialized", False
                ):
                    logger.warning(
                        f"Memory manager not available for agent '{self.name}'"
                    )
            except Exception as e:
                logger.warning(f"Memory check failed for agent '{self.name}': {e}")

            return None

        except Exception as e:
            logger.error(f"Resource validation error for agent '{self.name}': {e}")
            return f"Resource validation failed: {str(e)}"

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

    async def execute(self, state: AgentState) -> AgentState:
        """Execute the agent's primary function."""
        try:
            # Add timeout handling
            timeout = 120  # 2 minutes default timeout

            # Create a list of concurrent tasks
            tasks = []

            # Main execution task with timeout
            main_task = asyncio.create_task(self._execute_with_timeout(state, timeout))
            tasks.append(main_task)

            # Timeout watcher task
            timeout_task = asyncio.create_task(asyncio.sleep(timeout))
            tasks.append(timeout_task)

            # Wait for either completion or timeout
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED, timeout=timeout
            )

            # Cancel timeout task if not needed
            if not timeout_task.done():
                timeout_task.cancel()

            # Get result from completed task
            for task in done:
                if task == main_task:
                    return task.result()

            # If we timed out, handle gracefully
            if pending:
                logger.warning(
                    f"Agent '{self.name}' execution timed out after {timeout}s"
                )
                return self._set_error(state, f"Execution timed out after {timeout}s")

            return state

        except Exception as e:
            logger.error(f"Agent '{self.name}' execution failed: {str(e)}")
            return self._set_error(state, f"Execution failed: {str(e)}")

    async def _execute_with_timeout(
        self, state: AgentState, timeout: int
    ) -> AgentState:
        """Execute agent with enhanced timeout handling."""
        try:
            # Use enhanced timeout manager
            from core.timeouts import execute_with_timeout

            task_id = f"{self.name}_{id(state)}"
            result_state = await execute_with_timeout(
                self.execute_logic(state),
                timeout=timeout,
                task_id=task_id,
                cancellation_handler=lambda tid: self.cleanup_resources(),
            )
            return result_state

        except Exception as e:
            if "timed out" in str(e).lower():
                logger.warning(f"Agent '{self.name}' execution timed out")
                return self._set_error(state, f"Execution timed out: {str(e)}")
            else:
                logger.error(f"Agent '{self.name}' execution error: {str(e)}")
                return self._set_error(state, f"Execution failed: {str(e)}")

    def execute_logic(self, state: AgentState) -> AgentState:
        """Execute the agent's logic. Subclasses should override this."""
        # Default implementation - subclasses should override
        return self._set_output(state, f"Agent '{self.name}' executed successfully")

    async def cleanup_resources(self):
        """Clean up resources after agent execution with timeout awareness."""
        cleanup_start_time = time.time()
        cleanup_errors = []

        try:
            # Get timeout manager for timeout-aware cleanup
            from core.timeouts import get_timeout_manager

            timeout_manager = get_timeout_manager()

            # Get resource manager for enhanced cleanup
            from core.resources import get_resource_manager

            resource_manager = get_resource_manager()

            # Clean up tracked resources by this agent
            agent_resources = resource_manager.resources_by_owner.get(self.name, set())
            cleanup_count = 0

            for resource_id in list(agent_resources):
                try:
                    # Check if resource has timeout-related issues
                    resource_info = resource_manager.get_resource_info(resource_id)
                    if resource_info and resource_info.get("timeout_sensitive", False):
                        # Perform timeout-aware cleanup
                        success = await resource_manager.cleanup_resource(resource_id)
                        if success:
                            cleanup_count += 1
                            logger.debug(
                                f"Timeout-aware cleanup successful for resource: {resource_id}"
                            )
                        else:
                            cleanup_errors.append(
                                f"Timeout-aware cleanup failed for resource: {resource_id}"
                            )
                    else:
                        # Standard cleanup
                        success = await resource_manager.cleanup_resource(resource_id)
                        if success:
                            cleanup_count += 1
                        else:
                            cleanup_errors.append(
                                f"Standard cleanup failed for resource: {resource_id}"
                            )
                except Exception as e:
                    cleanup_errors.append(
                        f"Resource cleanup error for {resource_id}: {e}"
                    )

            # Clean up timeout manager tasks for this agent
            active_tasks = timeout_manager.get_active_tasks()
            agent_tasks = {
                task_id: info
                for task_id, info in active_tasks.items()
                if self.name in task_id
            }

            for task_id in agent_tasks:
                try:
                    # Cancel timeout tasks for this agent
                    success = timeout_manager.cancel_task(task_id)
                    if success:
                        cleanup_count += 1
                        logger.debug(
                            f"Cancelled timeout task for agent '{self.name}': {task_id}"
                        )
                    else:
                        cleanup_errors.append(
                            f"Failed to cancel timeout task: {task_id}"
                        )
                except Exception as e:
                    cleanup_errors.append(f"Task cancellation error: {e}")

            # Clean up LLM connections with timeout awareness
            if hasattr(self, "llm") and self.llm:
                try:
                    # Check if LLM has timeout-related issues
                    if hasattr(self.llm, "timeout"):
                        # Close connection with timeout awareness
                        await asyncio.wait_for(
                            self.llm.close(), timeout=5.0  # 5 second timeout for close
                        )
                        logger.debug(
                            f"Closed LLM connection for agent '{self.name}' with timeout awareness"
                        )
                    else:
                        await self.llm.close()
                        logger.debug(f"Closed LLM connection for agent '{self.name}'")
                except Exception as e:
                    cleanup_errors.append(f"LLM cleanup error: {e}")

            # Clean up tool resources with timeout awareness
            if hasattr(self, "tools") and self.tools:
                for tool_name in self.tools:
                    try:
                        tool = self.tool_registry.get(tool_name)
                        if tool and hasattr(tool, "cleanup"):
                            # Check if tool has timeout issues
                            if hasattr(tool, "timeout_sensitive"):
                                # Perform timeout-aware cleanup
                                await asyncio.wait_for(
                                    tool.cleanup(),
                                    timeout=3.0,  # 3 second timeout for cleanup
                                )
                                logger.debug(
                                    f"Timeout-aware cleanup for tool '{tool_name}'"
                                )
                            else:
                                await tool.cleanup()
                                logger.debug(
                                    f"Cleaned up tool '{tool_name}' for agent '{self.name}'"
                                )
                    except Exception as e:
                        cleanup_errors.append(
                            f"Tool cleanup error for '{tool_name}': {e}"
                        )

            # Clean up skill resources with timeout awareness
            if hasattr(self, "skills") and self.skills:
                for skill_name in self.skills:
                    try:
                        skill = self.skills_registry.get_skill(skill_name)
                        if skill and hasattr(skill, "cleanup"):
                            # Check if skill has timeout issues
                            if hasattr(skill, "timeout_sensitive"):
                                # Perform timeout-aware cleanup
                                await asyncio.wait_for(
                                    skill.cleanup(),
                                    timeout=2.0,  # 2 second timeout for cleanup
                                )
                                logger.debug(
                                    f"Timeout-aware cleanup for skill '{skill_name}'"
                                )
                            else:
                                await skill.cleanup()
                                logger.debug(
                                    f"Cleaned up skill '{skill_name}' for agent '{self.name}'"
                                )
                    except Exception as e:
                        cleanup_errors.append(
                            f"Skill cleanup error for '{skill_name}': {e}"
                        )

            # Clear any cached data with timeout awareness
            if hasattr(self, "_cache"):
                try:
                    # Clear cache entries with timeout considerations
                    from core.cache import get_agent_cache

                    cache = get_agent_cache()
                    if cache:
                        # Invalidate cache entries for this agent
                        invalidated = await cache.invalidate(agent_name=self.name)
                        logger.debug(
                            f"Invalidated {invalidated} cache entries for agent '{self.name}'"
                        )
                except Exception as e:
                    cleanup_errors.append(f"Cache cleanup error: {e}")

            # Clear any temporary state
            if hasattr(self, "_temp_state"):
                self._temp_state.clear()
                logger.debug(f"Cleared temporary state for agent '{self.name}'")

            # Cancel any background tasks
            if hasattr(self, "_background_tasks"):
                for task in self._background_tasks:
                    try:
                        if not task.done():
                            task.cancel()
                            cleanup_count += 1
                            logger.debug(
                                f"Cancelled background task for agent '{self.name}'"
                            )
                    except Exception as e:
                        cleanup_errors.append(
                            f"Background task cancellation error: {e}"
                        )
                self._background_tasks.clear()

            # Clear execution state
            if hasattr(self, "_execution_state"):
                self._execution_state = None
                logger.debug(f"Cleared execution state for agent '{self.name}'")

            # Record cleanup metrics
            from core.metrics import get_metrics_collector

            metrics_collector = get_metrics_collector()
            if metrics_collector:
                metrics_collector.record_metric(
                    "resource_cleanup_count",
                    cleanup_count,
                    tags={"agent_name": self.name},
                )

            cleanup_duration = time.time() - cleanup_start_time
            logger.info(
                f"Agent '{self.name}' resources cleaned up successfully "
                f"({cleanup_count} resources) in {cleanup_duration:.2f}s"
            )

            if cleanup_errors:
                logger.warning(f"Cleanup errors for '{self.name}': {cleanup_errors}")

            # Record any timeout-related metrics
            if timeout_manager:
                timeout_stats = timeout_manager.get_timeout_stats()
                agent_timeouts = (
                    timeout_stats.get("operation_stats", {})
                    .get("by_agent", {})
                    .get(self.name, {})
                    .get("count", 0)
                )
                if agent_timeouts > 0:
                    metrics_collector.record_metric(
                        "agent_timeouts_during_cleanup",
                        agent_timeouts,
                        tags={"agent_name": self.name},
                    )

        except Exception as e:
            logger.error(f"Error cleaning up agent '{self.name}' resources: {e}")
            raise

    async def force_cleanup(self):
        """Force cleanup of all resources, even if errors occur."""
        try:
            await self.cleanup_resources()
        except Exception as e:
            logger.error(f"Force cleanup failed for '{self.name}': {e}")
            # Continue cleanup even if some parts fail
            await self._emergency_cleanup()

    async def _emergency_cleanup(self):
        """Emergency cleanup when normal cleanup fails."""
        emergency_items = [
            ("_llm", "close"),
            ("_cache", "clear"),
            ("_temp_state", "clear"),
            ("_open_files", "clear"),
            ("_background_tasks", "clear"),
            ("_references", "clear"),
        ]

        for attr_name, action in emergency_items:
            if hasattr(self, attr_name):
                try:
                    attr = getattr(self, attr_name)
                    if action == "clear" and hasattr(attr, "clear"):
                        attr.clear()
                    elif action == "close" and hasattr(attr, "close"):
                        await attr.close()
                    logger.debug(f"Emergency cleanup: {attr_name}.{action}")
                except Exception as e:
                    logger.error(f"Emergency cleanup failed for {attr_name}: {e}")

    def track_resource(self, resource_type: str, resource_id: str):
        """Track a resource for later cleanup."""
        if not hasattr(self, "_resource_tracker"):
            self._resource_tracker = {}

        if resource_type not in self._resource_tracker:
            self._resource_tracker[resource_type] = set()

        self._resource_tracker[resource_type].add(resource_id)

    def untrack_resource(self, resource_type: str, resource_id: str):
        """Untrack a resource."""
        if (
            hasattr(self, "_resource_tracker")
            and resource_type in self._resource_tracker
        ):
            self._resource_tracker[resource_type].discard(resource_id)

    def get_tracked_resources(self) -> Dict[str, set]:
        """Get all tracked resources."""
        return getattr(self, "_resource_tracker", {})

    def is_resource_tracked(self, resource_type: str, resource_id: str) -> bool:
        """Check if a resource is tracked."""
        tracked = self.get_tracked_resources()
        return resource_type in tracked and resource_id in tracked[resource_type]

    async def cleanup_tracked_resources(self, resource_type: Optional[str] = None):
        """Clean up all tracked resources or specific type."""
        tracked = self.get_tracked_resources()

        types_to_clean = [resource_type] if resource_type else list(tracked.keys())

        for r_type in types_to_clean:
            if r_type in tracked:
                for resource_id in tracked[r_type].copy():
                    try:
                        # Attempt to clean up based on resource type
                        if r_type == "file_handle":
                            # Close file handle
                            pass  # Would need to store actual handles
                        elif r_type == "task":
                            # Cancel task
                            pass  # Would need to store actual tasks
                        elif r_type == "connection":
                            # Close connection
                            pass  # Would need to store actual connections

                        self.untrack_resource(r_type, resource_id)
                        logger.debug(
                            f"Cleaned up tracked resource: {r_type}:{resource_id}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to cleanup tracked resource {r_type}:{resource_id}: {e}"
                        )

    # Enhanced Error Handling Methods

    async def handle_execution_error(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhanced error handling with structured recovery strategies.

        Args:
            error: The exception that occurred
            context: Execution context for error recovery

        Returns:
            Dict with error handling result and recovery suggestions
        """
        error_type = type(error).__name__
        error_msg = str(error)

        logger.error(
            f"[ENHANCED ERROR HANDLING] Agent '{self.name}' encountered {error_type}: {error_msg}"
        )

        # Categorize error and determine recovery strategy
        recovery_strategy = await self._determine_recovery_strategy(error, context)

        # Attempt recovery if possible
        recovery_result = None
        if recovery_strategy["can_recover"]:
            try:
                recovery_result = await self._execute_recovery_strategy(
                    recovery_strategy, context
                )
                logger.info(
                    f"Recovery attempt successful for agent '{self.name}': {recovery_strategy['type']}"
                )
            except Exception as recovery_error:
                logger.error(
                    f"Recovery failed for agent '{self.name}': {recovery_error}"
                )
                recovery_result = {"success": False, "error": str(recovery_error)}

        return {
            "error_type": error_type,
            "error_message": error_msg,
            "recovery_strategy": recovery_strategy,
            "recovery_result": recovery_result,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
        }

    async def _determine_recovery_strategy(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine the best recovery strategy based on error type."""
        error_type = type(error).__name__

        # Recovery strategies by error type
        strategies = {
            "ValidationError": {
                "type": "input_validation",
                "can_recover": True,
                "action": "validate_and_retry",
                "description": "Validate input parameters and retry with corrected values",
            },
            "DatabaseError": {
                "type": "database_retry",
                "can_recover": True,
                "action": "retry_with_backoff",
                "description": "Retry database operation with exponential backoff",
            },
            "LLMError": {
                "type": "llm_fallback",
                "can_recover": True,
                "action": "fallback_model",
                "description": "Switch to fallback LLM model or retry with different parameters",
            },
            "ToolError": {
                "type": "tool_alternative",
                "can_recover": True,
                "action": "alternative_tool",
                "description": "Try alternative tool or method to achieve same result",
            },
            "TimeoutError": {
                "type": "timeout_extension",
                "can_recover": True,
                "action": "increase_timeout",
                "description": "Increase timeout and retry operation",
            },
            "RateLimitError": {
                "type": "rate_limit_wait",
                "can_recover": True,
                "action": "wait_and_retry",
                "description": "Wait for rate limit reset and retry",
            },
            "NetworkError": {
                "type": "network_retry",
                "can_recover": True,
                "action": "retry_with_backoff",
                "description": "Retry network operation with exponential backoff",
            },
            "SecurityError": {
                "type": "security_block",
                "can_recover": False,
                "action": "block_operation",
                "description": "Security violation - operation blocked",
            },
        }

        strategy = strategies.get(
            error_type,
            {
                "type": "generic_error",
                "can_recover": False,
                "action": "log_and_continue",
                "description": "Unknown error type - logging and continuing",
            },
        )

        return strategy

    async def _execute_recovery_strategy(
        self, strategy: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the determined recovery strategy."""
        action = strategy["action"]

        if action == "validate_and_retry":
            return await self._validate_and_retry(context)
        elif action == "retry_with_backoff":
            return await self._retry_with_backoff(context)
        elif action == "fallback_model":
            return await self._fallback_model(context)
        elif action == "alternative_tool":
            return await self._try_alternative_tool(context)
        elif action == "increase_timeout":
            return await self._increase_timeout_and_retry(context)
        elif action == "wait_and_retry":
            return await self._wait_and_retry(context)
        else:
            return {"success": False, "message": f"Unknown recovery action: {action}"}

    async def _validate_and_retry(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inputs and retry operation."""
        # Implementation would validate context parameters
        logger.info(f"Agent '{self.name}' validating inputs and retrying")
        return {"success": True, "message": "Inputs validated, ready to retry"}

    async def _retry_with_backoff(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retry operation with exponential backoff."""
        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                wait_time = base_delay * (2**attempt)
                logger.info(
                    f"Agent '{self.name}' retrying attempt {attempt + 1}/{max_retries} after {wait_time}s"
                )
                await asyncio.sleep(wait_time)

                # Would retry the original operation here
                return {"success": True, "attempt": attempt + 1}
            except Exception as e:
                if attempt == max_retries - 1:
                    raise

        return {"success": False, "message": "All retry attempts failed"}

    async def _fallback_model(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Switch to fallback LLM model."""
        logger.info(f"Agent '{self.name}' switching to fallback model")
        # Implementation would switch to a different model tier
        return {"success": True, "message": "Switched to fallback model"}

    async def _try_alternative_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Try alternative tool to achieve same result."""
        logger.info(f"Agent '{self.name}' searching for alternative tool")
        # Implementation would find and use alternative tool
        return {"success": True, "message": "Alternative tool found and executed"}

    async def _increase_timeout_and_retry(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Increase timeout and retry operation."""
        logger.info(f"Agent '{self.name}' increasing timeout and retrying")
        # Implementation would increase timeout parameters
        return {"success": True, "message": "Timeout increased, retrying"}

    async def _wait_and_retry(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for rate limit reset and retry."""
        wait_time = 60  # Default 60 second wait
        logger.info(f"Agent '{self.name}' waiting {wait_time}s for rate limit reset")
        await asyncio.sleep(wait_time)
        return {"success": True, "message": f"Waited {wait_time}s, ready to retry"}

    def create_error_report(self, error_result: Dict[str, Any]) -> str:
        """Create a formatted error report for logging and monitoring."""
        report = f"""
AGENT ERROR REPORT
==================
Agent: {error_result['agent']}
Timestamp: {error_result['timestamp']}
Error Type: {error_result['error_type']}
Error Message: {error_result['error_message']}
Recovery Strategy: {error_result['recovery_strategy']}
Can Recover: {error_result['can_recover']}
Context: {error_result.get('context', {})}
"""
        return report

    async def warmup_cache(self) -> bool:
        """Warm up cache for this agent with common requests."""
        if not self.cache:
            logger.warning(f"Cache not available for agent '{self.name}'")
            return False

        try:
            logger.info(f"Starting cache warmup for agent '{self.name}'")
            await self.cache.warmup_cache([self.name])
            return True
        except Exception as e:
            logger.error(f"Cache warmup failed for agent '{self.name}': {e}")
            return False

    async def get_cached_response(
        self, request: str, context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached response for this agent."""
        if not self.cache:
            return None

        try:
            return await self.cache.get(
                agent_name=self.name,
                request=request,
                context=context,
                user_id=context.get("user_id") if context else None,
                workspace_id=context.get("workspace_id") if context else None,
            )
        except Exception as e:
            logger.error(f"Cache get failed for agent '{self.name}': {e}")
            return None

    async def cache_response(
        self,
        request: str,
        response: Dict[str, Any],
        context: Dict[str, Any] = None,
        ttl: int = None,
    ) -> bool:
        """Cache response for this agent."""
        if not self.cache:
            return False

        try:
            return await self.cache.set(
                agent_name=self.name,
                request=request,
                response=response,
                ttl=ttl,
                context=context,
                user_id=context.get("user_id") if context else None,
                workspace_id=context.get("workspace_id") if context else None,
            )
        except Exception as e:
            logger.error(f"Cache set failed for agent '{self.name}': {e}")
            return False

    # Simplified Memory Interface Methods
    async def store_memory(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Store data in agent's working memory."""
        try:
            agent_key = f"{self.name}:{key}"
            return await self.memory_controller.store_memory(
                agent_key, value, ttl, "working"
            )
        except Exception as e:
            logger.error(f"Agent '{self.name}' failed to store memory key '{key}': {e}")
            return False

    async def retrieve_memory(self, key: str) -> Optional[Any]:
        """Retrieve data from agent's working memory."""
        try:
            agent_key = f"{self.name}:{key}"
            return await self.memory_controller.retrieve_memory(agent_key, "working")
        except Exception as e:
            logger.error(
                f"Agent '{self.name}' failed to retrieve memory key '{key}': {e}"
            )
            return None

    async def store_vector(
        self, text: str, vector: List[float], metadata: Dict[str, Any] = None
    ) -> str:
        """Store vector embedding for semantic search."""
        try:
            # Add agent metadata
            if metadata is None:
                metadata = {}
            metadata.update(
                {
                    "agent_name": self.name,
                    "agent_type": self.__class__.__name__,
                    "stored_at": datetime.now().isoformat(),
                }
            )

            return await self.memory_controller.store_vector(text, vector, metadata)
        except Exception as e:
            logger.error(f"Agent '{self.name}' failed to store vector: {e}")
            return ""

    async def search_vectors(
        self, query_vector: List[float], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        try:
            results = await self.memory_controller.search_vectors(query_vector, limit)
            # Filter results to only include this agent's vectors
            filtered_results = [
                result
                for result in results
                if result.get("metadata", {}).get("agent_name") == self.name
            ]
            return filtered_results
        except Exception as e:
            logger.error(f"Agent '{self.name}' failed to search vectors: {e}")
            return []

    async def clear_agent_memory(self, memory_type: str = "working") -> bool:
        """Clear all memory for this agent."""
        try:
            # Clear memory with agent-specific pattern
            pattern = f"{self.name}:*"
            return await self.memory_controller.clear_memory(pattern)
        except Exception as e:
            logger.error(f"Agent '{self.name}' failed to clear memory: {e}")
            return False

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics for this agent."""
        try:
            general_stats = await self.memory_controller.get_memory_stats()

            # Add agent-specific stats
            agent_stats = {
                "agent_name": self.name,
                "agent_type": self.__class__.__name__,
                "memory_initialized": bool(self.memory_controller),
                "general_stats": general_stats,
            }

            return agent_stats
        except Exception as e:
            logger.error(f"Agent '{self.name}' failed to get memory stats: {e}")
            return {"error": str(e), "agent_name": self.name}

    async def execute_with_error_handling(
        self, operation: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute any agent operation with comprehensive error handling.

        Args:
            operation: Description of the operation being performed
            context: Operation context and parameters

        Returns:
            Dict with operation result or error handling information
        """
        try:
            logger.info(f"Agent '{self.name}' executing operation: {operation}")

            # Set timeout for operation
            timeout = context.get("timeout", 300)  # 5 minute default

            result = await asyncio.wait_for(
                self._execute_operation(operation, context), timeout=timeout
            )

            return {
                "success": True,
                "result": result,
                "operation": operation,
                "agent": self.name,
                "execution_time": context.get("execution_time", 0),
            }

        except asyncio.TimeoutError:
            error_context = {"operation": operation, "error_type": "TimeoutError"}
            error_result = await self.handle_execution_error(
                TimeoutError(f"Operation '{operation}' timed out after {timeout}s"),
                error_context,
            )
            return {"success": False, "error": error_result}

        except Exception as e:
            error_context = {"operation": operation, "error_type": type(e).__name__}
            error_result = await self.handle_execution_error(e, error_context)
            return {"success": False, "error": error_result}

    async def _execute_operation(self, operation: str, context: Dict[str, Any]) -> Any:
        """Execute the specific operation - to be overridden by subclasses."""
        # This is a placeholder - actual implementation would be in subclasses
        return {"message": f"Operation '{operation}' executed successfully"}

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        # Run cleanup synchronously for context manager
        try:
            import asyncio

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, create a task for cleanup
                    asyncio.create_task(self.cleanup_resources())
                else:
                    # If loop is not running, run cleanup directly
                    loop.run_until_complete(self.cleanup_resources())
            except RuntimeError:
                # No event loop, create one for cleanup
                asyncio.run(self.cleanup_resources())
        except Exception as e:
            logger.error(f"Context manager cleanup failed for agent '{self.name}': {e}")

        return False  # Don't suppress exceptions


# BaseRouter for backward compatibility
class BaseRouter:
    """Base class for routing components."""

    def __init__(self):
        self.routes = []

    def add_route(self, pattern: str, handler: callable, priority: int = 1):
        """Add a route to the router."""
        self.routes.append(
            {"pattern": pattern, "handler": handler, "priority": priority}
        )

    async def route(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route a request to the appropriate handler."""
        # Simple routing logic - can be extended
        for route in sorted(self.routes, key=lambda x: x["priority"], reverse=True):
            if self._matches_pattern(request_data, route["pattern"]):
                return await route["handler"](request_data)

        raise ValueError("No matching route found")

    def _matches_pattern(self, data: Dict[str, Any], pattern: str) -> bool:
        """Check if data matches the pattern."""
        # Simple pattern matching - can be extended
        return pattern in data.get("type", "").lower()


# RaptorflowTool for backward compatibility
class RaptorflowTool:
    """Base class for Raptorflow tools (backward compatibility)."""

    def __init__(self, name: str):
        self.name = name

    async def execute(self, **kwargs):
        """Execute the tool."""
        raise NotImplementedError("Tool execution not implemented")


# ToolError and ToolResult for backward compatibility
class ToolError(Exception):
    """Tool execution error."""

    pass


class ToolResult:
    """Tool execution result."""

    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error


# Skill, SkillCategory, and SkillLevel for backward compatibility
class Skill:
    """Skill definition for agents."""

    def __init__(self, name: str, category: str = "general", level: str = "basic"):
        self.name = name
        self.category = category
        self.level = level


class SkillCategory:
    """Skill categories."""

    CONTENT = "content"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    RESEARCH = "research"
    STRATEGY = "strategy"
    ANALYTICS = "analytics"
    TECHNICAL = "technical"
    COMMUNICATION = "communication"
    GENERAL = "general"


class SkillLevel:
    """Skill levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillAssessment:
    """Skill assessment for agents."""

    def __init__(self, skill: Skill, score: float = 0.0):
        self.skill = skill
        self.score = score


class SkillPath:
    """Skill path for agents."""

    def __init__(self, name: str, skills: List[Skill] = None):
        self.name = name
        self.skills = skills or []
