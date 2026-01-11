"""
Integration between agents and cognitive engine.
Wraps agent execution with full cognitive pipeline.
"""

import logging
from typing import Any, Dict, Optional

from agents.base import BaseAgent
from agents.state import AgentState
from cognitive import CognitiveEngine
from cognitive.models import ExecutionPlan, PerceivedInput, ReflectionResult

logger = logging.getLogger(__name__)


async def execute_with_cognition(
    agent: BaseAgent, state: AgentState, cognitive_engine: CognitiveEngine
) -> AgentState:
    """
    Execute agent with full cognitive pipeline.

    Args:
        agent: Agent to execute
        state: Initial agent state
        cognitive_engine: Cognitive engine instance

    Returns:
        Updated agent state with cognitive processing
    """
    try:
        logger.info(f"Starting cognitive execution for agent: {agent.name}")

        # Step 1: Perception
        perceived_input = await cognitive_engine.perception.perceive(
            text=state.get("input", ""), history=state.get("messages", [])
        )

        logger.info(
            f"Perceived intent: {perceived_input.intent}, entities: {len(perceived_input.entities)}"
        )

        # Step 2: Planning
        execution_plan = await cognitive_engine.planning.plan(
            goal=state.get("goal", f"Execute {agent.name}"),
            perceived=perceived_input,
            context=state.get("context", {}),
        )

        logger.info(
            f"Created plan with {len(execution_plan.steps)} steps, estimated cost: ${execution_plan.total_cost:.4f}"
        )

        # Step 3: Budget check
        if execution_plan.requires_approval:
            logger.info("Plan requires approval, creating approval gate")
            # Create approval gate
            from cognitive.hitl.gate import ApprovalGate

            approval_gate = ApprovalGate()

            gate_id = await approval_gate.request_approval(
                workspace_id=state.get("workspace_id"),
                user_id=state.get("user_id"),
                output={"plan": execution_plan, "perceived_input": perceived_input},
                risk_level=execution_plan.risk_level,
                reason=f"Agent {agent.name} execution requires approval",
            )

            state["pending_approval"] = True
            state["approval_gate_id"] = gate_id
            state["execution_plan"] = execution_plan

            return state

        # Step 4: Execute agent
        logger.info(f"Executing agent {agent.name}")
        agent_state = await agent.execute(state)

        # Step 5: Reflection
        reflection_result = await cognitive_engine.reflection.reflect(
            output=agent_state.get("output", ""),
            goal=execution_plan.goal,
            context=state.get("context", {}),
            max_iterations=3,
        )

        logger.info(
            f"Reflection completed with quality score: {reflection_result.quality_score}"
        )

        # Step 6: Update state with cognitive results
        agent_state.update(
            {
                "perceived_input": perceived_input,
                "execution_plan": execution_plan,
                "reflection_result": reflection_result,
                "cognitive_processing": True,
                "quality_score": reflection_result.quality_score,
                "approved": reflection_result.approved,
            }
        )

        # Step 7: Store in memory
        await _store_cognitive_results(agent_state, cognitive_engine.memory_controller)

        logger.info(f"Cognitive execution completed for agent: {agent.name}")

        return agent_state

    except Exception as e:
        logger.error(f"Error in cognitive execution: {e}")
        state["error"] = str(e)
        state["cognitive_processing"] = False
        return state


async def _store_cognitive_results(state: AgentState, memory_controller):
    """
    Store cognitive results in memory.

    Args:
        state: Agent state with cognitive results
        memory_controller: Memory controller
    """
    try:
        workspace_id = state.get("workspace_id")

        if not workspace_id:
            return

        # Store perceived input
        perceived = state.get("perceived_input")
        if perceived:
            await memory_controller.store(
                workspace_id=workspace_id,
                memory_type="conversation",
                content=f"Intent: {perceived.intent}, Entities: {perceived.entities}",
                metadata={
                    "type": "perception",
                    "agent": state.get("current_agent"),
                    "timestamp": perceived.timestamp,
                },
            )

        # Store execution plan
        plan = state.get("execution_plan")
        if plan:
            await memory_controller.store(
                workspace_id=workspace_id,
                memory_type="conversation",
                content=f"Plan: {plan.goal}, Steps: {len(plan.steps)}, Cost: ${plan.total_cost:.4f}",
                metadata={
                    "type": "planning",
                    "agent": state.get("current_agent"),
                    "risk_level": plan.risk_level,
                },
            )

        # Store reflection result
        reflection = state.get("reflection_result")
        if reflection:
            await memory_controller.store(
                workspace_id=workspace_id,
                memory_type="conversation",
                content=f"Quality Score: {reflection.quality_score}, Approved: {reflection.approved}",
                metadata={
                    "type": "reflection",
                    "agent": state.get("current_agent"),
                    "quality_score": reflection.quality_score,
                },
            )

    except Exception as e:
        logger.error(f"Error storing cognitive results: {e}")


class CognitiveAgentWrapper:
    """
    Wrapper that adds cognitive processing to any agent.
    """

    def __init__(self, agent: BaseAgent, cognitive_engine: CognitiveEngine):
        self.agent = agent
        self.cognitive_engine = cognitive_engine

    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute agent with cognitive processing.

        Args:
            state: Initial agent state

        Returns:
        Processed agent state
        """
        return await execute_with_cognition(
            agent=self.agent, state=state, cognitive_engine=self.cognitive_engine
        )

    @property
    def name(self) -> str:
        return self.agent.name

    @property
    def description(self) -> str:
        return self.agent.description


async def create_cognitive_wrapper(
    agent: BaseAgent, cognitive_engine: CognitiveEngine
) -> CognitiveAgentWrapper:
    """
    Create cognitive wrapper for an agent.

    Args:
        agent: Base agent to wrap
        cognitive_engine: Cognitive engine

    Returns:
        Cognitive agent wrapper
    """
    return CognitiveAgentWrapper(agent, cognitive_engine)


async def batch_execute_with_cognition(
    agents: list[BaseAgent], states: list[AgentState], cognitive_engine: CognitiveEngine
) -> list[AgentState]:
    """
    Execute multiple agents with cognitive processing in parallel.

    Args:
        agents: List of agents to execute
        states: List of agent states
        cognitive_engine: Cognitive engine

    Returns:
        List of processed agent states
    """
    import asyncio

    tasks = []
    for agent, state in zip(agents, states):
        wrapper = await create_cognitive_wrapper(agent, cognitive_engine)
        tasks.append(wrapper.execute(state))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    processed_states = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(
                f"Error in batch cognitive execution for agent {agents[i].name}: {result}"
            )
            states[i]["error"] = str(result)
            states[i]["cognitive_processing"] = False
            processed_states.append(states[i])
        else:
            processed_states.append(result)

    return processed_states
