"""
Enhanced Supervisor with Memory Integration.

This module provides memory-enhanced supervisor classes that:
- Pass memory context to sub-agents
- Track supervisor-level performance metrics
- Enable cross-agent memory sharing
- Aggregate feedback from multiple sub-agent executions

Supervisors using this enhanced base can:
1. Initialize sub-agents with shared or isolated memory
2. Track which sub-agents were invoked and their performance
3. Learn from multi-agent workflow patterns
4. Pass memory context throughout the agent hierarchy
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from backend.agents.base_agent import BaseSupervisor
from backend.agents.base_enhanced import BaseAgentEnhanced
from backend.memory.manager import MemoryManager


class BaseSupervisorEnhanced(BaseSupervisor):
    """
    Memory-enhanced supervisor base class.

    This class extends BaseSupervisor with memory capabilities, enabling supervisors to:
    - Share memory context with sub-agents
    - Track multi-agent workflow performance
    - Learn from orchestration patterns
    - Pass user preferences down the agent hierarchy

    Key differences from regular supervisors:
    1. Accepts a MemoryManager and passes it to sub-agents
    2. Tracks which sub-agents were invoked and their results
    3. Stores supervisor-level execution patterns
    4. Enables cross-agent learning (sub-agents can learn from each other)

    Attributes:
        name: Supervisor identifier
        memory: MemoryManager instance
        sub_agents: Dictionary of registered sub-agents
        logger: Configured logger instance

    Usage:
        class ContentSupervisorEnhanced(BaseSupervisorEnhanced):
            def __init__(self, memory: MemoryManager):
                super().__init__(name="content_supervisor_enhanced", memory=memory)

                # Register enhanced sub-agents with shared memory
                self.register_agent("blog_writer", BlogWriterEnhanced(memory))
                self.register_agent("email_writer", EmailWriterEnhanced(memory))

            async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
                # Supervisor orchestration logic
                if "blog" in goal:
                    result = await self.invoke_agent("blog_writer", context)
                elif "email" in goal:
                    result = await self.invoke_agent("email_writer", context)

                return result
    """

    def __init__(self, name: str, memory: MemoryManager):
        """
        Initialize enhanced supervisor with memory.

        Args:
            name: Unique supervisor identifier
            memory: MemoryManager instance to share with sub-agents
        """
        super().__init__(name=name)
        self.memory = memory
        self.log("Enhanced supervisor initialized with memory", level="debug")

    async def invoke_agent(
        self,
        agent_name: str,
        payload: Dict[str, Any],
        pass_memory: bool = True
    ) -> Dict[str, Any]:
        """
        Invoke a sub-agent with optional memory context passing.

        This method provides a convenient way to invoke sub-agents while
        tracking invocations and optionally enriching the payload with
        memory context.

        Args:
            agent_name: Name of the sub-agent to invoke
            payload: Input payload for the sub-agent
            pass_memory: Whether to pass memory context to sub-agent

        Returns:
            Sub-agent execution result

        Raises:
            ValueError: If agent is not registered

        Example:
            result = await self.invoke_agent(
                agent_name="blog_writer",
                payload={"topic": "AI trends", "tone": "professional"}
            )
        """
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not registered with supervisor '{self.name}'")

        self.log(f"Invoking sub-agent: {agent_name}", level="debug")

        start_time = time.time()

        try:
            # Execute sub-agent
            result = await agent.execute(payload)

            execution_time_ms = (time.time() - start_time) * 1000

            self.log(
                f"Sub-agent '{agent_name}' completed in {execution_time_ms:.2f}ms",
                agent_name=agent_name,
                execution_time_ms=execution_time_ms,
                status=result.get("status", "unknown")
            )

            # Add invocation metadata
            result["invoked_by"] = self.name
            result["invocation_time_ms"] = execution_time_ms

            return result

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self.log(
                f"Sub-agent '{agent_name}' failed: {str(e)}",
                level="error",
                agent_name=agent_name,
                execution_time_ms=execution_time_ms,
                exc_info=True
            )
            raise

    async def invoke_agents_parallel(
        self,
        invocations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Invoke multiple sub-agents in parallel.

        This method enables concurrent execution of multiple sub-agents,
        useful for workflows where sub-agents don't depend on each other.

        Args:
            invocations: List of invocation specs, each containing:
                - agent_name: str (name of agent to invoke)
                - payload: Dict (input payload)
                - pass_memory: Optional[bool] (default True)

        Returns:
            List of results from all invocations (same order as input)

        Example:
            results = await self.invoke_agents_parallel([
                {"agent_name": "blog_writer", "payload": {"topic": "AI"}},
                {"agent_name": "email_writer", "payload": {"topic": "Product Launch"}}
            ])
        """
        import asyncio

        self.log(f"Invoking {len(invocations)} sub-agents in parallel")

        # Create tasks for all invocations
        tasks = [
            self.invoke_agent(
                agent_name=inv["agent_name"],
                payload=inv["payload"],
                pass_memory=inv.get("pass_memory", True)
            )
            for inv in invocations
        ]

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.log(
                    f"Parallel invocation failed: {invocations[i]['agent_name']}",
                    level="error",
                    error=str(result)
                )

        return results

    async def invoke_agents_sequential(
        self,
        invocations: List[Dict[str, Any]],
        pass_results: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Invoke multiple sub-agents sequentially (one after another).

        This method enables sequential execution where each agent can
        optionally receive results from previous agents.

        Args:
            invocations: List of invocation specs (see invoke_agents_parallel)
            pass_results: Whether to pass previous results to next agent

        Returns:
            List of results from all invocations

        Example:
            # Pipeline: ICP Builder -> Persona Narrative -> Tag Assignment
            results = await self.invoke_agents_sequential([
                {"agent_name": "icp_builder", "payload": company_data},
                {"agent_name": "persona_narrative", "payload": {}},
                {"agent_name": "tag_assignment", "payload": {}}
            ], pass_results=True)
        """
        self.log(f"Invoking {len(invocations)} sub-agents sequentially")

        results = []
        accumulated_context = {}

        for i, inv in enumerate(invocations):
            payload = inv["payload"].copy()

            # Optionally pass results from previous agents
            if pass_results and accumulated_context:
                payload["previous_results"] = accumulated_context

            result = await self.invoke_agent(
                agent_name=inv["agent_name"],
                payload=payload,
                pass_memory=inv.get("pass_memory", True)
            )

            results.append(result)

            # Accumulate results for next agent
            if pass_results:
                accumulated_context[inv["agent_name"]] = result.get("result", {})

        return results

    async def store_workflow_pattern(
        self,
        workflow_name: str,
        agents_invoked: List[str],
        context: Dict[str, Any],
        results: List[Dict[str, Any]],
        performance_metrics: Dict[str, Any]
    ) -> str:
        """
        Store a multi-agent workflow pattern in memory.

        This enables the supervisor to learn from orchestration patterns
        and improve future routing decisions.

        Args:
            workflow_name: Name of the workflow (e.g., "full_icp_pipeline")
            agents_invoked: List of agent names that were invoked
            context: Input context that triggered this workflow
            results: Results from all agent invocations
            performance_metrics: Workflow-level metrics

        Returns:
            memory_id: ID of stored memory

        Example:
            memory_id = await self.store_workflow_pattern(
                workflow_name="content_creation_pipeline",
                agents_invoked=["hook_generator", "blog_writer", "asset_quality"],
                context={"topic": "AI trends"},
                results=[hook_result, blog_result, quality_result],
                performance_metrics={"total_time_ms": 5000, "quality_score": 0.92}
            )
        """
        input_summary = f"Workflow '{workflow_name}' with {len(agents_invoked)} agents"
        output_summary = f"Completed {workflow_name}: {', '.join(agents_invoked)}"

        memory_id = await self.memory.remember(
            agent_name=self.name,
            task_type="workflow_orchestration",
            input_summary=input_summary,
            output_summary=output_summary,
            result={
                "workflow_name": workflow_name,
                "agents_invoked": agents_invoked,
                "results": results,
            },
            performance_metrics=performance_metrics,
            metadata={
                "workflow_type": workflow_name,
                "agent_count": len(agents_invoked),
            }
        )

        self.log(
            f"Stored workflow pattern: {workflow_name}",
            memory_id=memory_id,
            agents_invoked=agents_invoked
        )

        return memory_id

    async def get_workflow_suggestions(
        self,
        goal: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get workflow suggestions based on historical patterns.

        Analyzes past workflow executions to suggest the best sub-agents
        to invoke for the current goal.

        Args:
            goal: Current goal to achieve
            context: Current execution context

        Returns:
            Dictionary with suggestions:
                - suggested_agents: List of agent names to invoke
                - suggested_workflow: Workflow name if pattern match found
                - confidence: Confidence score (0-1)
                - reasoning: Explanation of suggestion

        Example:
            suggestions = await self.get_workflow_suggestions(
                goal="Create blog content about AI",
                context={"topic": "AI", "tone": "professional"}
            )
            # Returns: {
            #   "suggested_agents": ["hook_generator", "blog_writer"],
            #   "confidence": 0.85,
            #   "reasoning": "Based on 5 similar past workflows"
            # }
        """
        self.log(f"Getting workflow suggestions for goal: {goal}")

        # Search for similar past workflows
        memories = await self.memory.search(
            query=goal,
            agent_name=self.name,
            task_type="workflow_orchestration",
            limit=5
        )

        if not memories:
            return {
                "suggested_agents": [],
                "confidence": 0.0,
                "reasoning": "No historical workflow patterns found"
            }

        # Analyze most common agent sequences
        agent_sequences = []
        for memory in memories:
            agents = memory.result.get("agents_invoked", [])
            agent_sequences.append(agents)

        # Find most common sequence (simple heuristic)
        # In production, this could use more sophisticated pattern matching
        if agent_sequences:
            suggested_agents = agent_sequences[0]  # Use most recent successful pattern
            confidence = 0.7 + (0.05 * len(memories))  # Higher confidence with more examples

            return {
                "suggested_agents": suggested_agents,
                "suggested_workflow": memories[0].result.get("workflow_name", "unknown"),
                "confidence": min(confidence, 0.95),
                "reasoning": f"Based on {len(memories)} similar past workflows",
                "example_memories": [m.memory_id for m in memories[:3]]
            }

        return {
            "suggested_agents": [],
            "confidence": 0.0,
            "reasoning": "No matching workflow patterns found"
        }

    def register_enhanced_agent(
        self,
        agent_name: str,
        agent: BaseAgentEnhanced
    ) -> None:
        """
        Register an enhanced agent with this supervisor.

        This is a convenience method that ensures only BaseAgentEnhanced
        instances are registered, enabling full memory integration.

        Args:
            agent_name: Unique identifier for the agent
            agent: Enhanced agent instance

        Raises:
            TypeError: If agent is not a BaseAgentEnhanced instance

        Example:
            supervisor.register_enhanced_agent(
                "blog_writer",
                BlogWriterEnhanced(memory=memory)
            )
        """
        if not isinstance(agent, BaseAgentEnhanced):
            raise TypeError(
                f"Agent '{agent_name}' must be a BaseAgentEnhanced instance, "
                f"got {type(agent).__name__}"
            )

        self.register_agent(agent_name, agent)
        self.log(f"Registered enhanced agent: {agent_name}", level="debug")

    async def get_supervisor_performance(self) -> Dict[str, Any]:
        """
        Get performance summary for this supervisor.

        Analyzes workflow execution history to provide insights into
        supervisor performance and commonly invoked agents.

        Returns:
            Dictionary with:
                - total_workflows: Number of workflows executed
                - most_invoked_agents: List of most frequently used agents
                - average_workflow_time: Average execution time
                - success_rate: Percentage of successful workflows

        Example:
            perf = await supervisor.get_supervisor_performance()
            # Returns: {
            #   "total_workflows": 50,
            #   "most_invoked_agents": ["blog_writer", "hook_generator"],
            #   "average_workflow_time_ms": 3500,
            #   "success_rate": 0.94
            # }
        """
        history = await self.memory.get_performance_history(
            agent_name=self.name,
            task_type="workflow_orchestration",
            limit=50
        )

        if not history:
            return {
                "total_workflows": 0,
                "most_invoked_agents": [],
                "average_workflow_time_ms": 0,
                "success_rate": 0.0
            }

        # Calculate metrics
        total_workflows = len(history)

        # Count agent invocations
        agent_counts: Dict[str, int] = {}
        total_time = 0
        success_count = 0

        for h in history:
            # Count agents
            agents = h.get("metrics", {}).get("agents_invoked", [])
            for agent in agents:
                agent_counts[agent] = agent_counts.get(agent, 0) + 1

            # Sum execution time
            exec_time = h.get("metrics", {}).get("total_time_ms", 0)
            total_time += exec_time

            # Count successes
            if h.get("user_feedback", {}).get("helpful", True):
                success_count += 1

        # Sort agents by invocation count
        most_invoked = sorted(
            agent_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "total_workflows": total_workflows,
            "most_invoked_agents": [agent for agent, count in most_invoked[:5]],
            "agent_invocation_counts": dict(most_invoked[:10]),
            "average_workflow_time_ms": total_time / total_workflows if total_workflows > 0 else 0,
            "success_rate": success_count / total_workflows if total_workflows > 0 else 0.0
        }
