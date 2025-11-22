"""
Enhanced base classes for memory-enabled agents.

This module extends the base agent classes with integrated memory capabilities,
enabling agents to learn from past executions, recall relevant experiences,
and improve performance over time.

Key Features:
- Automatic memory storage after executions
- Semantic search for relevant past experiences
- Feedback incorporation and learning
- Workspace-specific memory isolation

Classes:
- BaseAgentEnhanced: Memory-enabled base agent
- BaseSupervisorEnhanced: Memory-enabled supervisor agent

Usage:
    class HookGeneratorAgent(BaseAgentEnhanced):
        async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
            # Recall relevant past successes
            similar = await self.memory.search(
                query=f"successful hooks for {payload['topic']}",
                memory_types=["success"],
                top_k=3
            )

            # Use insights from past successes
            # ... agent logic ...

            # Store this execution
            await self.remember(
                context=payload,
                result=result,
                success_score=0.85
            )

            return result
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from backend.agents.base_agent import BaseAgent, BaseSupervisor
from backend.services.memory_manager import MemoryManager
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class BaseAgentEnhanced(BaseAgent):
    """
    Enhanced base agent with integrated memory capabilities.

    Extends BaseAgent to provide automatic memory integration for all agents.
    Agents can recall relevant past executions, store new experiences, and
    learn from feedback.

    Attributes:
        name: Agent identifier
        logger: Structured logger
        memory: MemoryManager instance for this agent
        workspace_id: Current workspace ID (set per execution)
        auto_remember: If True, automatically store memories after execute()

    Memory Integration Pattern:
        1. Before execute(): Call memory.search() to recall relevant experiences
        2. During execute(): Use insights from past memories
        3. After execute(): Call remember() to store results (automatic if auto_remember=True)
        4. On feedback: Call learn_from_feedback() to update memories

    Example:
        class ICPBuilderAgent(BaseAgentEnhanced):
            async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
                # Extract workspace_id from payload
                workspace_id = payload.get("workspace_id")
                self.set_workspace(workspace_id)

                # Recall similar ICPs
                similar_icps = await self.memory.search(
                    query=f"ICP for {payload['industry']} in {payload['company_stage']}",
                    memory_types=["success"],
                    min_success_score=0.7,
                    top_k=3
                )

                # Use insights from past ICPs
                past_patterns = self._extract_patterns(similar_icps)

                # Build new ICP with learned patterns
                icp = await self._build_icp(payload, past_patterns)

                # Automatically stored by auto_remember
                return {
                    "status": "success",
                    "icp": icp,
                    "success_score": 0.8
                }
    """

    def __init__(
        self,
        name: str,
        workspace_id: Optional[str] = None,
        auto_remember: bool = False
    ):
        """
        Initialize enhanced agent with memory.

        Args:
            name: Unique agent identifier
            workspace_id: Optional workspace ID (can be set later via set_workspace())
            auto_remember: If True, automatically store memories after each execution
        """
        super().__init__(name)
        self.workspace_id = workspace_id
        self.auto_remember = auto_remember
        self._memory: Optional[MemoryManager] = None

        if workspace_id:
            self._initialize_memory()

    def set_workspace(self, workspace_id: str) -> None:
        """
        Set the current workspace and initialize memory manager.

        Must be called before using memory features. Typically called at the
        start of execute() method.

        Args:
            workspace_id: UUID of the workspace
        """
        if workspace_id != self.workspace_id:
            self.workspace_id = workspace_id
            self._initialize_memory()
            self.log(
                "Workspace context updated",
                workspace_id=workspace_id,
                level="debug"
            )

    def _initialize_memory(self) -> None:
        """Initialize memory manager for current workspace."""
        if self.workspace_id:
            self._memory = MemoryManager(
                workspace_id=self.workspace_id,
                agent_name=self.name
            )

    @property
    def memory(self) -> MemoryManager:
        """
        Get memory manager instance.

        Raises:
            RuntimeError: If workspace_id not set

        Returns:
            MemoryManager instance for this agent and workspace
        """
        if not self._memory:
            raise RuntimeError(
                f"{self.name}: Memory not initialized. Call set_workspace(workspace_id) first."
            )
        return self._memory

    async def remember(
        self,
        context: Dict[str, Any],
        result: Dict[str, Any],
        success_score: Optional[float] = None,
        memory_type: str = "success",
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Store a memory from this execution.

        Convenience method that wraps memory.remember() with automatic
        success score extraction and logging.

        Args:
            context: Input context/payload
            result: Output result
            success_score: Optional success score (0.0-1.0).
                If None, extracts from result["success_score"] or defaults to 0.5
            memory_type: Memory type ("success", "failure", "preference", "insight")
            tags: Optional tags for categorization

        Returns:
            Memory ID

        Example:
            await self.remember(
                context={"topic": "AI automation", "icp_id": "icp-123"},
                result={"hooks": [...], "score": 0.9},
                success_score=0.9,
                tags=["b2b", "high-performing"]
            )
        """
        correlation_id = get_correlation_id()

        # Extract success score from result if not provided
        if success_score is None:
            success_score = result.get("success_score", 0.5)

        # Determine memory type from result status if "success" but result indicates failure
        if memory_type == "success" and result.get("status") == "error":
            memory_type = "failure"
            success_score = 0.0

        try:
            memory_id = await self.memory.remember(
                context=context,
                result=result,
                success_score=success_score,
                memory_type=memory_type,
                tags=tags,
            )

            self.log(
                "Memory stored",
                memory_id=memory_id,
                memory_type=memory_type,
                success_score=success_score,
                level="debug"
            )

            return memory_id

        except Exception as exc:
            # Don't fail execution if memory storage fails
            self.log(
                "Failed to store memory",
                error=str(exc),
                level="warning"
            )
            return ""

    async def recall(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        min_success_score: float = 0.6,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant memories using semantic search.

        Convenience method that wraps memory.search() with sensible defaults
        for common recall patterns.

        Args:
            query: Natural language search query
            memory_types: Filter by types (default: ["success"])
            tags: Filter by tags
            min_success_score: Minimum success score (default: 0.6 for quality)
            top_k: Max results (default: 5)

        Returns:
            List of relevant memories with similarity scores

        Example:
            # Recall successful hooks for similar topics
            past_hooks = await self.recall(
                query=f"successful hooks for {topic} in {industry}",
                min_success_score=0.7,
                top_k=3
            )

            for mem in past_hooks:
                print(f"Past context: {mem['context']}")
                print(f"Past result: {mem['result']}")
                print(f"Similarity: {mem.get('similarity', 0):.2f}")
        """
        correlation_id = get_correlation_id()
        memory_types = memory_types or ["success"]

        try:
            memories = await self.memory.search(
                query=query,
                memory_types=memory_types,
                tags=tags,
                min_success_score=min_success_score,
                top_k=top_k,
            )

            self.log(
                "Memories recalled",
                query_length=len(query),
                results_found=len(memories),
                memory_types=memory_types,
                level="debug"
            )

            return memories

        except Exception as exc:
            # Don't fail execution if recall fails
            self.log(
                "Failed to recall memories",
                error=str(exc),
                level="warning"
            )
            return []

    async def learn_from_feedback(
        self,
        memory_id: str,
        feedback: Dict[str, Any],
        adjust_score: bool = True,
    ) -> bool:
        """
        Update a memory with new feedback and optionally adjust success score.

        This method allows agents to incorporate post-execution feedback such as:
        - User ratings and comments
        - Critic reviews
        - Performance metrics (click rates, conversion rates, etc.)
        - A/B test results

        Args:
            memory_id: ID of the memory to update
            feedback: Feedback data to store
                Example: {
                    "user_rating": 5,
                    "critic_review": {...},
                    "actual_performance": {"clicks": 1200, "conversions": 45}
                }
            adjust_score: If True, recalculates success_score based on feedback

        Returns:
            True if feedback was successfully incorporated

        Example:
            # After user provides feedback
            await self.learn_from_feedback(
                memory_id="mem-123",
                feedback={
                    "user_rating": 5,
                    "user_comment": "Best hooks we've seen!",
                    "actual_clicks": 1500,
                    "conversion_rate": 0.08
                },
                adjust_score=True
            )
        """
        correlation_id = get_correlation_id()

        try:
            # Calculate new success score if requested
            new_score = None
            if adjust_score:
                new_score = self._calculate_feedback_score(feedback)

            success = await self.memory.update_feedback(
                memory_id=memory_id,
                feedback=feedback,
                new_success_score=new_score,
            )

            if success:
                self.log(
                    "Feedback incorporated",
                    memory_id=memory_id,
                    new_score=new_score,
                    level="info"
                )
            else:
                self.log(
                    "Failed to incorporate feedback",
                    memory_id=memory_id,
                    level="warning"
                )

            return success

        except Exception as exc:
            self.log(
                "Error incorporating feedback",
                memory_id=memory_id,
                error=str(exc),
                level="error"
            )
            return False

    def _calculate_feedback_score(self, feedback: Dict[str, Any]) -> float:
        """
        Calculate success score from feedback data.

        Override this method in subclasses to implement agent-specific
        scoring logic based on feedback metrics.

        Args:
            feedback: Feedback dictionary

        Returns:
            Success score (0.0-1.0)

        Default Implementation:
            - Uses feedback["user_rating"] if available (1-5 scale -> 0.0-1.0)
            - Uses feedback["critic_score"] if available (0.0-1.0)
            - Defaults to 0.5 if no scoreable feedback
        """
        # User rating (1-5 scale)
        if "user_rating" in feedback:
            return min(feedback["user_rating"] / 5.0, 1.0)

        # Critic score (0.0-1.0 scale)
        if "critic_score" in feedback:
            return min(max(feedback["critic_score"], 0.0), 1.0)

        # Performance metrics (agent-specific, override in subclasses)
        if "performance_score" in feedback:
            return min(max(feedback["performance_score"], 0.0), 1.0)

        # Default: no change
        return 0.5

    async def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics for this agent.

        Returns summary of stored memories, success rates, and top tags.

        Returns:
            Dictionary with memory statistics

        Example:
            stats = await self.get_memory_stats()
            print(f"Total memories: {stats['total_memories']}")
            print(f"Success rate: {stats['avg_success_score']:.2%}")
            print(f"Top tags: {stats['top_tags']}")
        """
        try:
            return await self.memory.get_statistics()
        except Exception as exc:
            self.log(
                "Failed to get memory statistics",
                error=str(exc),
                level="warning"
            )
            return {}

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task with automatic memory handling.

        This method wraps the standard execute() with automatic memory features:
        1. Sets workspace context from payload
        2. Calls _execute_with_memory() (subclass implementation)
        3. Automatically stores memory if auto_remember=True

        Subclasses should implement _execute_with_memory() instead of execute().

        Args:
            payload: Execution payload with workspace_id

        Returns:
            Result dictionary with status and output
        """
        correlation_id = get_correlation_id()

        # Set workspace context
        workspace_id = payload.get("workspace_id")
        if workspace_id:
            self.set_workspace(workspace_id)

        # Execute (delegate to subclass)
        result = await self._execute_with_memory(payload)

        # Auto-remember if enabled
        if self.auto_remember and workspace_id:
            try:
                await self.remember(
                    context=payload,
                    result=result,
                )
            except Exception as exc:
                self.log(
                    "Auto-remember failed",
                    error=str(exc),
                    level="warning"
                )

        return result

    async def _execute_with_memory(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task with memory available.

        Subclasses should implement this method instead of execute().
        Memory is guaranteed to be initialized when this method is called.

        Args:
            payload: Execution payload

        Returns:
            Result dictionary

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError(
            f"{self.name}._execute_with_memory() must be implemented"
        )


class BaseSupervisorEnhanced(BaseSupervisor):
    """
    Enhanced base supervisor with integrated memory capabilities.

    Extends BaseSupervisor to provide memory integration for supervisor agents.
    Supervisors can recall past routing decisions, successful agent combinations,
    and coordination patterns.

    Attributes:
        name: Supervisor identifier
        logger: Structured logger
        sub_agents: Dictionary of registered sub-agents
        memory: MemoryManager instance
        workspace_id: Current workspace ID

    Memory Usage Patterns:
        - Store successful routing decisions and agent combinations
        - Recall similar past goals and their solutions
        - Learn from feedback about supervisor decisions
        - Track which agents work well together

    Example:
        class ContentSupervisor(BaseSupervisorEnhanced):
            async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
                workspace_id = context.get("workspace_id")
                self.set_workspace(workspace_id)

                # Recall similar past goals
                similar_goals = await self.recall(
                    query=f"content generation goal: {goal}",
                    top_k=3
                )

                # Use successful patterns from past executions
                # ... supervisor logic ...

                return result
    """

    def __init__(
        self,
        name: str,
        workspace_id: Optional[str] = None,
        auto_remember: bool = False
    ):
        """
        Initialize enhanced supervisor with memory.

        Args:
            name: Unique supervisor identifier
            workspace_id: Optional workspace ID
            auto_remember: If True, automatically store memories
        """
        super().__init__(name)
        self.workspace_id = workspace_id
        self.auto_remember = auto_remember
        self._memory: Optional[MemoryManager] = None

        if workspace_id:
            self._initialize_memory()

    def set_workspace(self, workspace_id: str) -> None:
        """Set workspace context and initialize memory."""
        if workspace_id != self.workspace_id:
            self.workspace_id = workspace_id
            self._initialize_memory()
            self.log(
                "Workspace context updated",
                workspace_id=workspace_id,
                level="debug"
            )

    def _initialize_memory(self) -> None:
        """Initialize memory manager."""
        if self.workspace_id:
            self._memory = MemoryManager(
                workspace_id=self.workspace_id,
                agent_name=self.name
            )

    @property
    def memory(self) -> MemoryManager:
        """Get memory manager instance."""
        if not self._memory:
            raise RuntimeError(
                f"{self.name}: Memory not initialized. Call set_workspace(workspace_id) first."
            )
        return self._memory

    async def remember(
        self,
        context: Dict[str, Any],
        result: Dict[str, Any],
        success_score: Optional[float] = None,
        memory_type: str = "success",
        tags: Optional[List[str]] = None,
    ) -> str:
        """Store a memory from this supervision execution."""
        if success_score is None:
            success_score = result.get("success_score", 0.5)

        if memory_type == "success" and result.get("status") == "error":
            memory_type = "failure"
            success_score = 0.0

        try:
            memory_id = await self.memory.remember(
                context=context,
                result=result,
                success_score=success_score,
                memory_type=memory_type,
                tags=tags,
            )

            self.log(
                "Supervisor memory stored",
                memory_id=memory_id,
                memory_type=memory_type,
                level="debug"
            )

            return memory_id

        except Exception as exc:
            self.log(
                "Failed to store supervisor memory",
                error=str(exc),
                level="warning"
            )
            return ""

    async def recall(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        min_success_score: float = 0.6,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Recall relevant supervisor memories."""
        memory_types = memory_types or ["success"]

        try:
            memories = await self.memory.search(
                query=query,
                memory_types=memory_types,
                tags=tags,
                min_success_score=min_success_score,
                top_k=top_k,
            )

            self.log(
                "Supervisor memories recalled",
                results_found=len(memories),
                level="debug"
            )

            return memories

        except Exception as exc:
            self.log(
                "Failed to recall supervisor memories",
                error=str(exc),
                level="warning"
            )
            return []

    async def learn_from_feedback(
        self,
        memory_id: str,
        feedback: Dict[str, Any],
        adjust_score: bool = True,
    ) -> bool:
        """Update supervisor memory with feedback."""
        try:
            new_score = None
            if adjust_score and "supervisor_rating" in feedback:
                new_score = min(feedback["supervisor_rating"] / 5.0, 1.0)

            success = await self.memory.update_feedback(
                memory_id=memory_id,
                feedback=feedback,
                new_success_score=new_score,
            )

            if success:
                self.log("Supervisor feedback incorporated", memory_id=memory_id)

            return success

        except Exception as exc:
            self.log(
                "Error incorporating supervisor feedback",
                error=str(exc),
                level="error"
            )
            return False

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute supervisor task with automatic memory handling.

        Args:
            goal: High-level goal
            context: Execution context with workspace_id

        Returns:
            Result dictionary
        """
        # Set workspace context
        workspace_id = context.get("workspace_id")
        if workspace_id:
            self.set_workspace(workspace_id)

        # Execute (delegate to subclass)
        result = await self._execute_with_memory(goal, context)

        # Auto-remember if enabled
        if self.auto_remember and workspace_id:
            try:
                await self.remember(
                    context={"goal": goal, **context},
                    result=result,
                )
            except Exception as exc:
                self.log(
                    "Auto-remember failed",
                    error=str(exc),
                    level="warning"
                )

        return result

    async def _execute_with_memory(
        self,
        goal: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute supervisor task with memory available.

        Subclasses should implement this method instead of execute().

        Args:
            goal: High-level goal
            context: Execution context

        Returns:
            Result dictionary

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError(
            f"{self.name}._execute_with_memory() must be implemented"
        )
