"""
Enhanced Base Agent with Memory Integration.

This module provides memory-enhanced base classes for RaptorFlow agents:
- BaseAgentEnhanced: Extends BaseAgent with memory capabilities
- Memory-aware execution flow with context enrichment
- Automatic performance tracking and feedback learning
- User preference integration

All new agents should inherit from BaseAgentEnhanced to leverage:
1. Automatic recall of relevant past experiences
2. Context enrichment with user preferences
3. Performance metric tracking
4. User feedback learning

Example:
    class MyEnhancedAgent(BaseAgentEnhanced):
        async def _execute_core(self, enriched_context: Dict[str, Any]) -> Dict[str, Any]:
            # Agent logic here with enriched context
            return {"status": "success", "result": result}
"""

from __future__ import annotations

import time
from abc import abstractmethod
from typing import Any, Dict, List, Optional

from backend.agents.base_agent import BaseAgent
from backend.memory.manager import MemoryManager


class BaseAgentEnhanced(BaseAgent):
    """
    Memory-enhanced base agent class.

    This class extends BaseAgent with memory capabilities, enabling agents to:
    - Recall relevant memories from past executions
    - Enrich task context with historical data and user preferences
    - Store execution results with performance metrics
    - Learn from user feedback over time

    The enhanced execution flow:
    1. Search memory for relevant past experiences
    2. Enrich input context with recalled memories and preferences
    3. Execute core task logic (implemented by subclass)
    4. Store result and performance metrics in memory
    5. Return result to caller

    Subclasses must implement:
    - _execute_core(): Core agent logic with enriched context
    - _get_task_type(): Return a string identifying the task type
    - _create_input_summary(): Create a summary of the input for memory search
    - _create_output_summary(): Create a summary of the output for memory storage

    Attributes:
        name: Unique agent identifier
        memory: MemoryManager instance for this agent
        logger: Configured logger instance

    Usage:
        class ICPBuilderEnhanced(BaseAgentEnhanced):
            def __init__(self, memory: MemoryManager):
                super().__init__(name="ICPBuilderEnhanced", memory=memory)

            async def _execute_core(self, enriched_context: Dict[str, Any]) -> Dict[str, Any]:
                # Access recalled memories
                past_icps = enriched_context.get("recalled_memories", [])
                user_prefs = enriched_context.get("user_preferences", {})

                # Use preferences to guide generation
                preferred_tone = user_prefs.get("preferred_tone", "professional")

                # Agent logic here
                result = await self._build_icp(enriched_context, tone=preferred_tone)
                return result

            def _get_task_type(self) -> str:
                return "icp_building"

            def _create_input_summary(self, payload: Dict[str, Any]) -> str:
                return f"Build ICP for {payload.get('company_name', 'unknown company')}"

            def _create_output_summary(self, result: Dict[str, Any]) -> str:
                return f"Created ICP: {result.get('icp_name', 'Unknown')}"
    """

    def __init__(self, name: str, memory: MemoryManager):
        """
        Initialize enhanced agent with memory.

        Args:
            name: Unique agent identifier
            memory: MemoryManager instance for storing/retrieving memories
        """
        super().__init__(name=name)
        self.memory = memory
        self.log("Enhanced agent initialized with memory", level="debug")

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task with memory-enhanced context.

        This method orchestrates the full memory-aware execution flow:
        1. Recall relevant memories
        2. Enrich context with memories and preferences
        3. Execute core task logic
        4. Store results and metrics
        5. Return final result

        Args:
            payload: Input data containing task parameters and context

        Returns:
            Dictionary containing:
                - status: "success" | "error" | "partial"
                - result: Agent-specific output data
                - metadata: Execution metadata (timing, memory_id, etc.)
                - correlation_id: Propagated correlation ID

        Raises:
            Exception: If core execution fails
        """
        start_time = time.time()

        try:
            # Step 1: Recall relevant memories
            self.log("Recalling relevant memories", level="debug")
            recalled_memories = await self._recall_memories(payload)

            # Step 2: Get user preferences
            self.log("Retrieving user preferences", level="debug")
            user_preferences = await self.memory.get_user_preferences()

            # Step 3: Enrich context
            enriched_context = self._enrich_context(
                payload=payload,
                recalled_memories=recalled_memories,
                user_preferences=user_preferences
            )

            self.log(
                f"Context enriched with {len(recalled_memories)} memories",
                memory_count=len(recalled_memories),
                has_preferences=bool(user_preferences)
            )

            # Step 4: Execute core task logic (implemented by subclass)
            self.log("Executing core task logic", level="debug")
            result = await self._execute_core(enriched_context)

            # Step 5: Calculate performance metrics
            execution_time_ms = (time.time() - start_time) * 1000
            performance_metrics = {
                "execution_time_ms": execution_time_ms,
                "recalled_memory_count": len(recalled_memories),
                **self._extract_performance_metrics(result)
            }

            # Step 6: Store result in memory
            memory_id = await self._store_result(
                payload=payload,
                result=result,
                performance_metrics=performance_metrics
            )

            self.log(
                f"Task completed successfully in {execution_time_ms:.2f}ms",
                execution_time_ms=execution_time_ms,
                memory_id=memory_id
            )

            # Step 7: Return result with metadata
            return {
                "status": "success",
                "result": result,
                "metadata": {
                    "memory_id": memory_id,
                    "execution_time_ms": execution_time_ms,
                    "recalled_memory_count": len(recalled_memories),
                },
                "correlation_id": self.memory.workspace_id  # Use workspace as correlation
            }

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self.log(
                f"Task execution failed: {str(e)}",
                level="error",
                execution_time_ms=execution_time_ms,
                exc_info=True
            )

            # Store error in memory for learning
            await self._store_error(payload, str(e), execution_time_ms)

            raise

    @abstractmethod
    async def _execute_core(self, enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the core agent task logic.

        This is the main method that subclasses must implement. It receives
        enriched context with recalled memories and user preferences.

        Args:
            enriched_context: Dictionary containing:
                - original_payload: Original input payload
                - recalled_memories: List of relevant MemoryEntry objects
                - user_preferences: User preference dictionary
                - memory_summaries: Simplified summaries of recalled memories
                - ... (all fields from original payload)

        Returns:
            Task result dictionary (agent-specific structure)

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError(f"{self.name}._execute_core() must be implemented")

    @abstractmethod
    def _get_task_type(self) -> str:
        """
        Get the task type identifier for this agent.

        This is used for memory categorization and retrieval.

        Returns:
            Task type string (e.g., "icp_building", "content_generation")

        Example:
            def _get_task_type(self) -> str:
                return "icp_building"
        """
        raise NotImplementedError(f"{self.name}._get_task_type() must be implemented")

    @abstractmethod
    def _create_input_summary(self, payload: Dict[str, Any]) -> str:
        """
        Create a brief summary of the input for memory storage/search.

        This summary is used for semantic search and display.

        Args:
            payload: Input payload

        Returns:
            Brief input summary (1-2 sentences)

        Example:
            def _create_input_summary(self, payload: Dict[str, Any]) -> str:
                company = payload.get("company_name", "unknown")
                return f"Build ICP for {company} in {payload.get('industry', 'unknown')} industry"
        """
        raise NotImplementedError(f"{self.name}._create_input_summary() must be implemented")

    @abstractmethod
    def _create_output_summary(self, result: Dict[str, Any]) -> str:
        """
        Create a brief summary of the output for memory storage/search.

        This summary is used for semantic search and display.

        Args:
            result: Task result

        Returns:
            Brief output summary (1-2 sentences)

        Example:
            def _create_output_summary(self, result: Dict[str, Any]) -> str:
                icp_name = result.get("icp_name", "Unknown")
                confidence = result.get("confidence", 0)
                return f"Created ICP '{icp_name}' with {confidence:.0%} confidence"
        """
        raise NotImplementedError(f"{self.name}._create_output_summary() must be implemented")

    async def _recall_memories(self, payload: Dict[str, Any]) -> List[Any]:
        """
        Search memory for relevant past experiences.

        Constructs a search query from the input payload and retrieves
        relevant memories from the same agent and task type.

        Args:
            payload: Input payload

        Returns:
            List of MemoryEntry objects
        """
        # Create search query from input
        search_query = self._create_input_summary(payload)

        # Search for relevant memories
        memories = await self.memory.search(
            query=search_query,
            agent_name=self.name,
            task_type=self._get_task_type(),
            limit=5  # Retrieve top 5 most relevant memories
        )

        return memories

    def _enrich_context(
        self,
        payload: Dict[str, Any],
        recalled_memories: List[Any],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich input context with memories and preferences.

        Combines original payload with recalled memories and user preferences
        to provide comprehensive context for core task execution.

        Args:
            payload: Original input payload
            recalled_memories: List of MemoryEntry objects
            user_preferences: User preference dictionary

        Returns:
            Enriched context dictionary
        """
        # Start with original payload
        enriched = payload.copy()

        # Add memory data
        enriched["recalled_memories"] = recalled_memories
        enriched["user_preferences"] = user_preferences

        # Add simplified memory summaries for easy access
        enriched["memory_summaries"] = [
            {
                "input": mem.input_summary,
                "output": mem.output_summary,
                "timestamp": mem.timestamp.isoformat(),
                "user_feedback": mem.user_feedback,
                "performance": mem.performance_metrics,
            }
            for mem in recalled_memories
        ]

        # Add helpful preference shortcuts
        enriched["average_user_rating"] = user_preferences.get("average_rating", 0)
        enriched["total_feedback_count"] = user_preferences.get("total_feedback_count", 0)

        # Store original payload for reference
        enriched["original_payload"] = payload

        return enriched

    async def _store_result(
        self,
        payload: Dict[str, Any],
        result: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> str:
        """
        Store task result and metrics in memory.

        Args:
            payload: Original input payload
            result: Task result
            performance_metrics: Performance metrics

        Returns:
            memory_id: ID of stored memory
        """
        input_summary = self._create_input_summary(payload)
        output_summary = self._create_output_summary(result)

        memory_id = await self.memory.remember(
            agent_name=self.name,
            task_type=self._get_task_type(),
            input_summary=input_summary,
            output_summary=output_summary,
            result=result,
            performance_metrics=performance_metrics,
            metadata=self._extract_metadata(payload)
        )

        return memory_id

    async def _store_error(
        self,
        payload: Dict[str, Any],
        error_message: str,
        execution_time_ms: float
    ) -> Optional[str]:
        """
        Store error information in memory for learning.

        Args:
            payload: Original input payload
            error_message: Error message
            execution_time_ms: Execution time before failure

        Returns:
            memory_id if stored, None if storage failed
        """
        try:
            input_summary = self._create_input_summary(payload)

            memory_id = await self.memory.remember(
                agent_name=self.name,
                task_type=f"{self._get_task_type()}_error",
                input_summary=input_summary,
                output_summary=f"Error: {error_message}",
                result={"error": error_message, "status": "failed"},
                performance_metrics={
                    "execution_time_ms": execution_time_ms,
                    "success": False
                },
                metadata=self._extract_metadata(payload)
            )

            return memory_id

        except Exception as e:
            self.log(f"Failed to store error in memory: {e}", level="error")
            return None

    def _extract_performance_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract additional performance metrics from result.

        Subclasses can override this to add custom metrics.

        Args:
            result: Task result

        Returns:
            Dictionary of performance metrics
        """
        metrics = {}

        # Extract common metrics if present
        if "confidence" in result:
            metrics["confidence_score"] = result["confidence"]

        if "tokens_used" in result:
            metrics["tokens_used"] = result["tokens_used"]

        if "model" in result:
            metrics["model"] = result["model"]

        return metrics

    def _extract_metadata(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from payload for memory storage.

        Subclasses can override this to add custom metadata.

        Args:
            payload: Input payload

        Returns:
            Dictionary of metadata
        """
        metadata = {}

        # Extract common metadata fields
        if "workspace_id" in payload:
            metadata["workspace_id"] = payload["workspace_id"]

        if "user_id" in payload:
            metadata["user_id"] = payload["user_id"]

        if "cohort_id" in payload:
            metadata["cohort_id"] = payload["cohort_id"]

        if "campaign_id" in payload:
            metadata["campaign_id"] = payload["campaign_id"]

        return metadata

    async def learn_from_feedback(
        self,
        memory_id: str,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user feedback and update memory.

        This method stores user feedback and can be extended by subclasses
        to implement custom learning behaviors.

        Args:
            memory_id: ID of memory to update
            feedback: Feedback dictionary containing:
                - rating: Optional[int] (1-5 stars)
                - comments: Optional[str]
                - corrections: Optional[Dict] (corrected fields)
                - helpful: Optional[bool]

        Returns:
            Dictionary with feedback processing results

        Example:
            result = await agent.learn_from_feedback(
                memory_id="mem_123",
                feedback={
                    "rating": 4,
                    "comments": "Good but needs more detail",
                    "helpful": True
                }
            )
        """
        self.log(
            f"Processing feedback for memory: {memory_id}",
            feedback_rating=feedback.get("rating"),
            has_corrections=bool(feedback.get("corrections"))
        )

        # Store feedback in memory
        success = await self.memory.add_feedback(memory_id, feedback)

        if not success:
            self.log(f"Failed to store feedback: memory {memory_id} not found", level="warning")
            return {
                "status": "error",
                "message": f"Memory {memory_id} not found"
            }

        # Extract insights from feedback
        insights = {
            "status": "success",
            "feedback_stored": True,
            "memory_id": memory_id,
        }

        # Check for corrections
        if feedback.get("corrections"):
            insights["has_corrections"] = True
            insights["corrected_fields"] = list(feedback["corrections"].keys())

        # Check for low ratings
        if feedback.get("rating") and feedback["rating"] < 3:
            insights["needs_improvement"] = True
            self.log("Low rating detected - flagged for improvement", level="warning")

        return insights

    async def get_improvement_suggestions(
        self,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze performance patterns and suggest improvements.

        This method examines historical performance and user feedback to
        identify areas for improvement.

        Args:
            limit: Number of recent executions to analyze

        Returns:
            Dictionary with improvement suggestions:
                - average_rating: Average user rating
                - common_issues: List of recurring problems
                - performance_trends: Performance metric trends
                - suggestions: List of actionable suggestions

        Example:
            suggestions = await agent.get_improvement_suggestions(limit=20)
            if suggestions["average_rating"] < 3.5:
                # Take action to improve performance
        """
        self.log(f"Analyzing performance history (last {limit} executions)")

        # Get performance history
        history = await self.memory.get_performance_history(
            agent_name=self.name,
            task_type=self._get_task_type(),
            limit=limit
        )

        if not history:
            return {
                "status": "insufficient_data",
                "message": "Not enough historical data for analysis"
            }

        # Analyze ratings
        ratings = [
            h["user_feedback"].get("rating", 0)
            for h in history
            if h.get("user_feedback") and h["user_feedback"].get("rating")
        ]

        average_rating = sum(ratings) / len(ratings) if ratings else 0

        # Analyze execution times
        execution_times = [
            h["metrics"].get("execution_time_ms", 0)
            for h in history
            if h.get("metrics")
        ]

        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        # Collect common issues from feedback
        common_issues = []
        for h in history:
            if h.get("user_feedback") and h["user_feedback"].get("comments"):
                common_issues.append(h["user_feedback"]["comments"])

        # Generate suggestions
        suggestions = []

        if average_rating < 3.5:
            suggestions.append("User satisfaction is below target - review feedback comments")

        if avg_execution_time > 5000:  # 5 seconds
            suggestions.append("Average execution time is high - consider optimization")

        if len(ratings) < 5:
            suggestions.append("Limited feedback data - encourage more user ratings")

        return {
            "status": "success",
            "total_executions": len(history),
            "feedback_count": len(ratings),
            "average_rating": average_rating,
            "average_execution_time_ms": avg_execution_time,
            "common_issues": common_issues[:5],  # Top 5 issues
            "suggestions": suggestions,
            "performance_trend": "improving" if len(ratings) >= 2 and ratings[0] > ratings[-1] else "stable"
        }
