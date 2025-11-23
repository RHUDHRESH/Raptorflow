"""
Example demonstrating memory-aware orchestration capabilities.

This example shows how to use the overhauled supervisor with:
- Memory-aware routing
- Adaptive agent selection
- Self-correction loops
- Human-in-the-loop checkpoints
- Context propagation
"""

import asyncio
from uuid import uuid4, UUID

from backend.agents.supervisor import master_orchestrator
from backend.services.memory_manager import memory_manager
from backend.models.orchestration import (
    AgentContext,
    WorkflowCheckpoints,
    WorkflowCheckpoint,
    CheckpointCondition,
    CheckpointAction,
    SelfCorrectionConfig,
)


async def example_1_memory_aware_routing():
    """
    Example 1: Memory-Aware Routing

    Demonstrates how the supervisor uses historical task data to route requests.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Memory-Aware Routing")
    print("=" * 80)

    workspace_id = uuid4()
    user_id = uuid4()

    # First, store some successful task history
    print("\n1. Storing successful task history in memory...")

    await memory_manager.store_task_result(
        goal="Create a blog post about AI trends",
        agent_sequence=["content", "blog_writer"],
        success=True,
        workspace_id=workspace_id,
        execution_time=5.2,
        result_quality=0.92,
    )

    await memory_manager.store_task_result(
        goal="Write a blog about machine learning",
        agent_sequence=["content", "blog_writer"],
        success=True,
        workspace_id=workspace_id,
        execution_time=4.8,
        result_quality=0.88,
    )

    print("✓ Stored 2 successful blog writing tasks with high confidence")

    # Now route a similar task
    print("\n2. Routing a similar task...")

    agent_sequence, context = await master_orchestrator.route_with_context(
        goal="Create a blog post about neural networks",
        workspace_id=workspace_id,
        user_id=user_id,
    )

    print(f"\n✓ Routed to agent sequence: {agent_sequence}")
    print(f"✓ Context includes {len(context.past_successes)} past successes")
    print(f"✓ Context includes {len(context.task_history)} historical tasks")


async def example_2_adaptive_agent_selection():
    """
    Example 2: Adaptive Agent Selection

    Demonstrates how the supervisor selects agents based on performance metrics.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Adaptive Agent Selection")
    print("=" * 80)

    workspace_id = uuid4()

    # Store performance data for different agents
    print("\n1. Storing agent performance data...")

    # Content agent performs well
    for i in range(5):
        await memory_manager.store_task_result(
            goal=f"Generate content {i}",
            agent_sequence=["content_supervisor", "blog_writer"],
            success=True,
            workspace_id=workspace_id,
            result_quality=0.9,
        )

    print("✓ Stored 5 successful content generation tasks")

    # Now select best agent
    print("\n2. Selecting best agent for content generation...")

    best_agent = await master_orchestrator.select_best_agent(
        task_type="content_generation",
        workspace_id=workspace_id,
        fallback_agent="content",
    )

    print(f"\n✓ Selected best agent: {best_agent}")


async def example_3_self_correction_loops():
    """
    Example 3: Self-Correction Loops

    Demonstrates iterative content improvement with critique and revision.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Self-Correction Loops")
    print("=" * 80)

    workspace_id = uuid4()
    user_id = uuid4()

    # Build agent context
    context = AgentContext(
        workspace_id=workspace_id,
        correlation_id="test-correlation-id",
        user_id=user_id,
        brand_voice={
            "tone": "professional",
            "style": "conversational",
            "vocabulary": "technical but accessible",
        },
        quality_thresholds={
            "content_quality": 0.85,
        },
    )

    # Configure self-correction
    config = SelfCorrectionConfig(
        max_iterations=3,
        min_quality_score=0.85,
        improvement_threshold=0.05,
        critique_aspects=["clarity", "persuasiveness", "brand_alignment"],
        store_failures=True,
    )

    print("\n1. Self-correction configuration:")
    print(f"   - Max iterations: {config.max_iterations}")
    print(f"   - Min quality score: {config.min_quality_score}")
    print(f"   - Improvement threshold: {config.improvement_threshold}")
    print(f"   - Critique aspects: {', '.join(config.critique_aspects)}")

    # Note: This would execute with self-correction if the agent was registered
    print("\n2. Self-correction loop would:")
    print("   a) Generate initial content")
    print("   b) Evaluate quality against thresholds")
    print("   c) Generate critique if below threshold")
    print("   d) Revise based on critique")
    print("   e) Repeat until quality threshold met or max iterations")
    print("   f) Store failed attempts in memory for learning")

    print("\n✓ Self-correction configuration ready")


async def example_4_workflow_checkpoints():
    """
    Example 4: Human-in-the-Loop Checkpoints

    Demonstrates workflow checkpoints with auto-approval rules.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Human-in-the-Loop Checkpoints")
    print("=" * 80)

    workspace_id = uuid4()
    user_id = uuid4()

    # Define workflow checkpoints
    checkpoints = WorkflowCheckpoints(
        workspace_id=workspace_id,
        checkpoints=[
            WorkflowCheckpoint(
                name="strategy_review",
                description="Review strategy before content generation",
                condition=CheckpointCondition.AFTER_STAGE,
                condition_params={"stage": "strategy"},
                action=CheckpointAction.REQUEST_APPROVAL,
                timeout_seconds=3600,
                auto_approve_if={
                    "quality_above": 0.85,
                    "success_rate_above": 0.8,
                },
            ),
            WorkflowCheckpoint(
                name="pre_publish",
                description="Review content before publishing",
                condition=CheckpointCondition.BEFORE_EXECUTION,
                action=CheckpointAction.REQUEST_APPROVAL,
                timeout_seconds=7200,
                auto_approve_if={
                    "quality_above": 0.9,
                },
            ),
        ],
        default_timeout=3600,
        auto_approve_for_users=[user_id],
        enabled=True,
    )

    print("\n1. Workflow checkpoints configured:")
    for checkpoint in checkpoints.checkpoints:
        print(f"\n   Checkpoint: {checkpoint.name}")
        print(f"   - Description: {checkpoint.description}")
        print(f"   - Condition: {checkpoint.condition.value}")
        print(f"   - Action: {checkpoint.action.value}")
        print(f"   - Timeout: {checkpoint.timeout_seconds}s")
        if checkpoint.auto_approve_if:
            print(f"   - Auto-approve if: {checkpoint.auto_approve_if}")

    # Build context
    context = AgentContext(
        workspace_id=workspace_id,
        correlation_id="test-correlation-id",
        user_id=user_id,
    )

    # Evaluate checkpoint with high quality (should auto-approve)
    print("\n2. Evaluating checkpoint with high quality score...")

    result = await master_orchestrator.evaluate_checkpoint(
        checkpoint_name="strategy_review",
        checkpoints_config=checkpoints,
        context=context,
        execution_data={
            "quality_score": 0.9,
            "agent_success_rate": 0.85,
        },
    )

    print(f"\n✓ Checkpoint result: {result['status']}")
    print(f"✓ Reason: {result['reason']}")

    # Evaluate checkpoint with low quality (should pause)
    print("\n3. Evaluating checkpoint with low quality score...")

    result = await master_orchestrator.evaluate_checkpoint(
        checkpoint_name="pre_publish",
        checkpoints_config=checkpoints,
        context=context,
        execution_data={
            "quality_score": 0.7,  # Below threshold
        },
    )

    print(f"\n✓ Checkpoint result: {result['status']}")
    print(f"✓ Reason: {result['reason']}")


async def example_5_context_propagation():
    """
    Example 5: Context Propagation

    Demonstrates comprehensive context passing through agent hierarchy.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Context Propagation")
    print("=" * 80)

    workspace_id = uuid4()
    user_id = uuid4()

    # Build comprehensive context
    context = AgentContext(
        workspace_id=workspace_id,
        correlation_id="test-correlation-id",
        user_id=user_id,
        brand_voice={
            "tone": "professional yet friendly",
            "style": "storytelling",
            "vocabulary": "accessible with occasional jargon",
            "avoid": ["hype", "exaggeration"],
        },
        target_icps=[uuid4(), uuid4()],
        user_preferences={
            "content_length": "medium",
            "include_examples": True,
            "include_data": True,
        },
        quality_thresholds={
            "content_quality": 0.8,
            "strategy_viability": 0.85,
            "research_depth": 0.75,
        },
        budget_constraints={
            "max_api_calls": 100,
            "max_cost_usd": 5.0,
        },
        custom_metadata={
            "industry": "B2B SaaS",
            "target_market": "SMB",
            "campaign_type": "product_launch",
        },
    )

    print("\n1. Agent Context contains:")
    print(f"   - Workspace ID: {context.workspace_id}")
    print(f"   - User ID: {context.user_id}")
    print(f"   - Correlation ID: {context.correlation_id}")
    print(f"   - Brand voice: {len(context.brand_voice)} attributes")
    print(f"   - Target ICPs: {len(context.target_icps)}")
    print(f"   - User preferences: {len(context.user_preferences)} settings")
    print(f"   - Quality thresholds: {len(context.quality_thresholds)} metrics")
    print(f"   - Budget constraints: {context.budget_constraints}")
    print(f"   - Custom metadata: {context.custom_metadata}")

    print("\n2. This context would be propagated to all agents:")
    print("   - Ensures consistent brand voice")
    print("   - Maintains quality standards")
    print("   - Respects budget limits")
    print("   - Uses workspace-specific history")
    print("   - Applies user preferences")

    print("\n✓ Context ready for propagation through agent hierarchy")


async def example_6_complete_workflow():
    """
    Example 6: Complete Workflow

    Demonstrates a full workflow combining all features.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Complete Memory-Aware Workflow")
    print("=" * 80)

    workspace_id = uuid4()
    user_id = uuid4()

    print("\n1. MEMORY-AWARE ROUTING")
    print("-" * 40)

    # Store successful history
    await memory_manager.store_task_result(
        goal="Generate product launch content",
        agent_sequence=["strategy", "content", "execution"],
        success=True,
        workspace_id=workspace_id,
        result_quality=0.91,
    )

    # Route new task
    agent_sequence, context = await master_orchestrator.route_with_context(
        goal="Create product launch campaign",
        workspace_id=workspace_id,
        user_id=user_id,
        context_override={
            "brand_voice": {"tone": "innovative", "style": "bold"},
            "target_icps": [uuid4()],
        },
    )

    print(f"✓ Determined agent sequence: {agent_sequence}")

    print("\n2. ADAPTIVE AGENT SELECTION")
    print("-" * 40)

    best_agent = await master_orchestrator.select_best_agent(
        task_type="content_generation",
        workspace_id=workspace_id,
        fallback_agent="content",
    )

    print(f"✓ Selected best performing agent: {best_agent}")

    print("\n3. CHECKPOINT EVALUATION")
    print("-" * 40)

    checkpoints = WorkflowCheckpoints(
        workspace_id=workspace_id,
        checkpoints=[
            WorkflowCheckpoint(
                name="strategy_approval",
                description="Review strategy",
                condition=CheckpointCondition.AFTER_STAGE,
                action=CheckpointAction.REQUEST_APPROVAL,
                auto_approve_if={"quality_above": 0.85},
            )
        ],
    )

    checkpoint_result = await master_orchestrator.evaluate_checkpoint(
        checkpoint_name="strategy_approval",
        checkpoints_config=checkpoints,
        context=context,
        execution_data={"quality_score": 0.9},
    )

    print(f"✓ Checkpoint status: {checkpoint_result['status']}")

    print("\n4. SELF-CORRECTION (Configuration)")
    print("-" * 40)

    config = SelfCorrectionConfig(
        max_iterations=3,
        min_quality_score=0.85,
        critique_aspects=["clarity", "persuasiveness", "brand_alignment"],
    )

    print(f"✓ Self-correction configured with {config.max_iterations} max iterations")
    print(f"✓ Quality threshold: {config.min_quality_score}")

    print("\n5. CONTEXT PROPAGATION")
    print("-" * 40)

    print(f"✓ Context includes:")
    print(f"  - {len(context.task_history)} historical tasks")
    print(f"  - {len(context.performance_data)} performance metrics")
    print(f"  - Brand voice: {context.brand_voice}")
    print(f"  - {len(context.target_icps)} target ICPs")

    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE")
    print("=" * 80)
    print("\nThis workflow demonstrated:")
    print("✓ Memory-aware routing based on past successes")
    print("✓ Adaptive agent selection using performance metrics")
    print("✓ Human-in-the-loop checkpoints with auto-approval")
    print("✓ Self-correction configuration for quality improvement")
    print("✓ Comprehensive context propagation")
    print("\nAll features working together for intelligent orchestration!")


async def main():
    """Run all examples."""
    print("\n")
    print("=" * 80)
    print("MEMORY-AWARE ORCHESTRATION EXAMPLES")
    print("=" * 80)
    print("\nDemonstrating the overhauled supervisor with:")
    print("- Memory-aware routing")
    print("- Adaptive agent selection")
    print("- Self-correction loops")
    print("- Human-in-the-loop checkpoints")
    print("- Context propagation")

    try:
        await example_1_memory_aware_routing()
        await example_2_adaptive_agent_selection()
        await example_3_self_correction_loops()
        await example_4_workflow_checkpoints()
        await example_5_context_propagation()
        await example_6_complete_workflow()

        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
