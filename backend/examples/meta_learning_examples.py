"""
Integration examples for meta-learning and agent swarm framework.

This module demonstrates how to use:
- PerformanceAnalyzer for pattern discovery
- TransferLearner for cross-workspace insights
- ModelUpdater for continuous model improvement
- ExperimentEngine for A/B testing
- ExpertAgentRegistry for assembling specialized teams
- AgentDebateOrchestrator for multi-agent consensus

These examples show real-world integration patterns with RaptorFlow agents.
"""

import asyncio
from uuid import uuid4

from backend.agents.swarm.agent_debate_orchestrator import (
    AgentDebateOrchestrator,
    ConsensusStrategy,
)
from backend.agents.swarm.expert_agent_registry import (
    AgentRole,
    ExpertAgentRegistry,
    SkillTag,
    TaskRequirements,
)
from backend.meta_learning.experiment_engine import (
    ExperimentEngine,
    ExperimentType,
    VariantAllocation,
)
from backend.meta_learning.model_updater import ModelType, ModelUpdater
from backend.meta_learning.performance_analyzer import PerformanceAnalyzer
from backend.meta_learning.transfer_learner import TransferLearner


# ============================================================================
# Example 1: Performance Pattern Analysis
# ============================================================================


async def example_performance_analysis():
    """
    Example: Analyze historical content performance to identify winning patterns.

    Use case: A content agent wants to learn what works best for a workspace
    before generating new content.
    """
    print("=" * 80)
    print("Example 1: Performance Pattern Analysis")
    print("=" * 80)

    # Initialize analyzer
    analyzer = PerformanceAnalyzer(
        min_confidence=0.7,
        min_sample_size=30,
        min_effect_size=0.3,
    )

    # Analyze patterns for a workspace
    workspace_id = uuid4()
    patterns = await analyzer.analyze_patterns(
        workspace_id=workspace_id,
        content_type="social",  # Focus on social media content
        lookback_days=90,  # Last 3 months
        min_samples=50,
    )

    # Display results
    print(f"\n✓ Analyzed {patterns['statistics']['sample_count']} content pieces")
    print(f"✓ Found {len(patterns['winning_patterns'])} winning patterns")
    print(f"✓ Found {len(patterns['losing_patterns'])} patterns to avoid\n")

    # Show winning patterns
    print("🏆 Winning Patterns:")
    for pattern in patterns["winning_patterns"][:3]:  # Top 3
        print(f"\n  Pattern: {pattern['description']}")
        print(f"  Confidence: {pattern['confidence']:.1%}")
        print(f"  Effect Size: {pattern['effect_size']:.2f}")
        print(f"  Sample Size: {pattern['sample_size']}")

    # Show insights
    print("\n💡 Key Insights:")
    for insight in patterns["insights"]:
        print(f"  • {insight}")

    # How content agents would use this
    print("\n📝 Integration with Content Agent:")
    print("  1. Content agent calls analyzer before generating content")
    print("  2. Applies learned patterns to new content")
    print("  3. Adapts strategy based on what's working")

    return patterns


# ============================================================================
# Example 2: Cross-Workspace Transfer Learning
# ============================================================================


async def example_transfer_learning():
    """
    Example: Get insights from similar successful workspaces.

    Use case: A new workspace wants to bootstrap their strategy using
    proven tactics from similar businesses.
    """
    print("\n" + "=" * 80)
    print("Example 2: Cross-Workspace Transfer Learning")
    print("=" * 80)

    # Initialize transfer learner
    transfer_learner = TransferLearner(
        min_source_workspaces=3,
        min_confidence=0.6,
        similarity_threshold=0.7,
    )

    # Get insights for a new workspace
    target_workspace = uuid4()
    insights = await transfer_learner.get_transfer_insights(
        target_workspace_id=target_workspace,
        top_k=5,
        insight_types=["strategy", "content", "timing"],
    )

    # Display results
    print(f"\n✓ Found {insights['similar_workspaces']} similar workspaces")
    print(f"✓ Coverage: {insights['coverage']}")
    print(f"✓ Generated {len(insights['insights'])} insights\n")

    # Show insights
    print("🎯 Transfer Insights:")
    for insight in insights["insights"]:
        print(f"\n  {insight['description']}")
        print(f"  Type: {insight['insight_type']}")
        print(f"  Confidence: {insight['confidence']:.1%}")
        print(f"  Based on {insight['source_workspaces']} workspaces")

    # How strategy agents would use this
    print("\n📊 Integration with Strategy Agent:")
    print("  1. Strategy agent requests insights for new workspace")
    print("  2. Incorporates proven tactics into campaign plan")
    print("  3. Adapts recommendations based on similar business success")

    return insights


# ============================================================================
# Example 3: Automated Model Updates
# ============================================================================


async def example_model_updates():
    """
    Example: Detect model drift and automatically retrain models.

    Use case: Engagement predictor performance degrades over time as
    user behavior changes. System detects drift and retrains.
    """
    print("\n" + "=" * 80)
    print("Example 3: Automated Model Updates and Drift Detection")
    print("=" * 80)

    # Initialize model updater
    updater = ModelUpdater(
        drift_warning_threshold=0.1,
        drift_critical_threshold=0.2,
        min_samples_for_drift=50,
    )

    # Check and update models for a workspace
    workspace_id = uuid4()
    update_results = await updater.check_and_update_models(
        workspace_id=workspace_id,
        model_types=[
            ModelType.ENGAGEMENT_PREDICTOR,
            ModelType.TONE_CLASSIFIER,
            ModelType.CONVERSION_PREDICTOR,
        ],
        force_retrain=False,  # Only retrain if drift detected
    )

    # Display results
    print(f"\n✓ Checked {len(update_results['models_checked'])} models")
    print(f"✓ Updated {len(update_results['models_updated'])} models\n")

    # Show drift reports
    print("📈 Drift Analysis:")
    for report in update_results["drift_reports"]:
        print(f"\n  Model: {report['model_type']}")
        print(f"  Drift Status: {report['drift_status']}")
        print(f"  Drift Score: {report['drift_score']:.3f}")
        print(f"  Current Performance: {report['current_performance']:.3f}")
        print(f"  Baseline Performance: {report['baseline_performance']:.3f}")
        print(f"  Recommendation: {report['recommendation']}")

    # Show updated models
    if update_results["new_metrics"]:
        print("\n🔄 Retrained Models:")
        for metrics in update_results["new_metrics"]:
            print(f"\n  Model: {metrics['model_type']}")
            print(f"  Version: {metrics['version']}")
            print(f"  Sample Count: {metrics['sample_count']}")

    # Schedule automatic updates
    print("\n⏰ Scheduling Automatic Updates:")
    schedule = await updater.schedule_updates(
        model_type=ModelType.ENGAGEMENT_PREDICTOR,
        frequency_days=7,  # Weekly checks
        min_new_samples=100,
        drift_threshold=0.15,
    )
    print(
        f"  ✓ Scheduled weekly checks for {schedule.model_type.value}"
    )
    print(f"  Next check: {schedule.next_scheduled}")

    return update_results


# ============================================================================
# Example 4: A/B Testing with Experiment Engine
# ============================================================================


async def example_ab_testing():
    """
    Example: Run A/B test to optimize hook styles.

    Use case: Content agent wants to test different hook styles to see
    which drives better engagement.
    """
    print("\n" + "=" * 80)
    print("Example 4: A/B Testing with Experiment Engine")
    print("=" * 80)

    # Initialize experiment engine
    engine = ExperimentEngine(
        default_confidence=0.95,
        min_effect_size=0.05,
    )

    # Create an experiment
    workspace_id = uuid4()
    experiment = await engine.create_experiment(
        name="Hook Style Optimization",
        workspace_id=workspace_id,
        variants=[
            {
                "name": "control",
                "description": "Current approach - straightforward hook",
            },
            {
                "name": "curiosity_gap",
                "description": "Curiosity gap hook with open loop",
            },
            {
                "name": "emotional_trigger",
                "description": "Emotion-first hook with strong feeling",
            },
        ],
        metric_name="engagement_rate",
        description="Testing different hook styles for social posts",
        experiment_type=ExperimentType.AB_TEST,
        min_sample_size=100,
    )

    print(f"\n✓ Created experiment: {experiment.name}")
    print(f"  Variants: {len(experiment.variants)}")
    print(f"  Metric: {experiment.metric_name}\n")

    # Start experiment
    await engine.start_experiment(experiment.experiment_id)
    print("✓ Experiment started\n")

    # Simulate assigning variants and recording outcomes
    print("📊 Simulating experiment data...")
    for _ in range(150):  # Simulate 150 trials
        # Assign variant
        variant_id = await engine.assign_variant(experiment.experiment_id)

        # Simulate outcome (curiosity_gap performs better)
        variant = next(
            v for v in experiment.variants if v.variant_id == variant_id
        )
        if variant.name == "curiosity_gap":
            outcome = 0.15  # 15% engagement
        elif variant.name == "emotional_trigger":
            outcome = 0.12  # 12% engagement
        else:  # control
            outcome = 0.10  # 10% engagement

        # Add some noise
        import numpy as np

        outcome += np.random.normal(0, 0.02)

        # Record outcome
        await engine.record_outcome(
            experiment.experiment_id, variant_id, outcome
        )

    # Analyze results
    results = await engine.analyze_experiment(experiment.experiment_id)

    print("✓ Experiment data collected\n")
    print("📈 Results:")
    print(f"\n  Winner: {results.winner}")
    print(f"  Confidence: {results.confidence:.1%}")
    print(f"  Lift: {results.lift:+.1%}")
    print(f"  P-value: {results.p_value:.4f}")
    print(f"  Statistical Power: {results.statistical_power:.1%}\n")

    print("  Performance by Variant:")
    for variant_name, mean in results.means.items():
        samples = results.sample_counts[variant_name]
        print(f"    {variant_name}: {mean:.1%} ({samples} samples)")

    print(f"\n  💡 Recommendation: {results.recommendation}")

    # Integration with content agents
    print("\n🤖 Integration with Content Agent:")
    print("  1. Content agent creates variants using different hooks")
    print("  2. Experiment engine assigns variants to users")
    print("  3. Engagement tracked and analyzed automatically")
    print("  4. Winning variant becomes new default")

    return results


# ============================================================================
# Example 5: Expert Agent Team Assembly
# ============================================================================


async def example_agent_team_assembly():
    """
    Example: Assemble a team of specialized agents for a specific task.

    Use case: Need to create a viral social media campaign. System assembles
    the optimal team of expert agents.
    """
    print("\n" + "=" * 80)
    print("Example 5: Expert Agent Team Assembly")
    print("=" * 80)

    # Initialize registry
    registry = ExpertAgentRegistry()

    # Define task requirements
    requirements = TaskRequirements(
        task_type="viral_social_campaign",
        required_skills=[
            SkillTag.VIRAL_MECHANICS,
            SkillTag.PERSUASIVE_WRITING,
            SkillTag.EMOTIONAL_TRIGGERS,
        ],
        preferred_skills=[
            SkillTag.TREND_ANALYSIS,
            SkillTag.BRAND_VOICE,
        ],
        min_team_size=3,
        max_team_size=5,
    )

    print(f"\n📋 Task: {requirements.task_type}")
    print(f"   Required Skills: {[s.value for s in requirements.required_skills]}")
    print(f"   Team Size: {requirements.min_team_size}-{requirements.max_team_size}\n")

    # Assemble team
    team_result = await registry.assemble_team(requirements)

    print("✓ Team Assembled\n")
    print(f"👥 Team Members ({len(team_result['team'])}):")
    for member in team_result["team"]:
        print(f"\n  • {member['name']} ({member['role']})")
        print(f"    Skills: {', '.join(member['skills'][:3])}...")

    print(f"\n📊 Coverage Analysis:")
    coverage = team_result["coverage"]
    print(f"  Required Skills Coverage: {coverage['required_skills_coverage']:.1%}")
    print(f"  Covered Skills: {', '.join(coverage['covered_skills'])}")

    if coverage["missing_skills"]:
        print(f"  ⚠️ Missing Skills: {', '.join(coverage['missing_skills'])}")

    print(f"\n⭐ Team Score: {team_result['team_score']:.2f}/1.00")

    print("\n💡 Recommendations:")
    for rec in team_result["recommendations"]:
        print(f"  {rec}")

    return team_result


# ============================================================================
# Example 6: Multi-Agent Debate for Consensus
# ============================================================================


async def example_agent_debate():
    """
    Example: Run a multi-agent debate to solve a complex problem.

    Use case: Multiple expert perspectives needed to create optimal
    campaign strategy. Agents propose, critique, refine, and reach consensus.
    """
    print("\n" + "=" * 80)
    print("Example 6: Multi-Agent Debate for Consensus")
    print("=" * 80)

    # Initialize registry and orchestrator
    registry = ExpertAgentRegistry()
    orchestrator = AgentDebateOrchestrator(
        agent_registry=registry,
        max_rounds=3,
        default_consensus=ConsensusStrategy.SYNTHESIS,
    )

    # Define problem
    problem = (
        "Design a content strategy to launch a new SaaS product for developers. "
        "Goal: Build awareness, drive signups, and establish thought leadership. "
        "Budget: $10k, Timeline: 3 months"
    )

    print(f"\n❓ Problem:\n   {problem}\n")

    # Run debate
    print("🎭 Starting multi-agent debate...\n")

    debate_result = await orchestrator.orchestrate_debate(
        problem=problem,
        agent_roles=[
            AgentRole.COPYWRITING_NINJA,
            AgentRole.SEO_EXPERT,
            AgentRole.VIRAL_ENGINEER,
            AgentRole.PSYCHOLOGY_SPECIALIST,
        ],
        rounds=2,
        consensus_strategy=ConsensusStrategy.SYNTHESIS,
    )

    print("✓ Debate completed\n")

    # Show results
    print("=" * 80)
    print("🏆 CONSENSUS DECISION")
    print("=" * 80)
    print(f"\n{debate_result['decision']}\n")

    print("=" * 80)
    print("💭 REASONING")
    print("=" * 80)
    print(f"\n{debate_result['reasoning']}\n")

    print(f"⭐ Confidence: {debate_result['confidence']:.1%}\n")

    # Show debate statistics
    print("📊 Debate Statistics:")
    print(f"  Participants: {len(debate_result['transcript']['participants'])}")
    print(f"  Proposals: {len(debate_result['proposals'])}")
    print(f"  Critiques: {len(debate_result['critiques'])}")
    print(f"  Rounds: {len([p for p in debate_result['transcript']['phases'] if p['phase'] == 'proposal'])}")

    # Show sample proposals
    print("\n💡 Sample Proposals:")
    for i, proposal in enumerate(debate_result["proposals"][:3], 1):
        print(f"\n  {i}. {proposal['agent_name']} ({proposal['agent_role']}):")
        print(f"     {proposal['proposal'][:150]}...")
        print(f"     Confidence: {proposal['confidence']:.1%}")

    # Integration guidance
    print("\n🔗 Integration with Existing Agents:")
    print("  1. Strategy supervisor calls debate orchestrator for complex decisions")
    print("  2. Multiple expert perspectives improve solution quality")
    print("  3. Critiques surface potential issues early")
    print("  4. Synthesis creates balanced, comprehensive strategies")

    return debate_result


# ============================================================================
# Example 7: Complete Integration Workflow
# ============================================================================


async def example_complete_integration():
    """
    Example: Complete workflow showing all components working together.

    Scenario: Content agent generating social posts for a campaign
    """
    print("\n" + "=" * 80)
    print("Example 7: Complete Integration Workflow")
    print("=" * 80)

    workspace_id = uuid4()

    print("\n📝 Scenario: Content agent generating optimized social posts\n")

    # Step 1: Analyze performance patterns
    print("Step 1: Analyze historical performance patterns")
    analyzer = PerformanceAnalyzer()
    patterns = await analyzer.analyze_patterns(
        workspace_id=workspace_id,
        content_type="social",
        lookback_days=90,
    )
    print(f"  ✓ Found {len(patterns['winning_patterns'])} winning patterns")

    # Step 2: Get transfer learning insights
    print("\nStep 2: Get insights from similar workspaces")
    transfer_learner = TransferLearner()
    insights = await transfer_learner.get_transfer_insights(
        target_workspace_id=workspace_id,
        top_k=3,
    )
    print(f"  ✓ Got {len(insights['insights'])} insights from {insights['similar_workspaces']} similar workspaces")

    # Step 3: Assemble expert team
    print("\nStep 3: Assemble expert agent team")
    registry = ExpertAgentRegistry()
    team = await registry.assemble_team(
        TaskRequirements(
            task_type="social_content_creation",
            required_skills=[SkillTag.COPYWRITING, SkillTag.ENGAGEMENT_OPTIMIZATION],
            min_team_size=2,
            max_team_size=3,
        )
    )
    print(f"  ✓ Assembled team of {len(team['team'])} expert agents")

    # Step 4: Run debate for strategy
    print("\nStep 4: Multi-agent debate for content strategy")
    orchestrator = AgentDebateOrchestrator(registry)
    debate = await orchestrator.orchestrate_debate(
        problem="Create engaging social post strategy based on learned patterns",
        agent_roles=[AgentRole.COPYWRITING_NINJA, AgentRole.VIRAL_ENGINEER],
        rounds=1,
    )
    print(f"  ✓ Reached consensus with {debate['confidence']:.1%} confidence")

    # Step 5: Run A/B test
    print("\nStep 5: Create A/B test for content variants")
    engine = ExperimentEngine()
    experiment = await engine.create_experiment(
        name="Content Variant Test",
        workspace_id=workspace_id,
        variants=[
            {"name": "variant_a", "description": "Using pattern insights"},
            {"name": "variant_b", "description": "Using transfer learning insights"},
        ],
        metric_name="engagement_rate",
    )
    print(f"  ✓ Created experiment: {experiment.name}")

    # Step 6: Check model health
    print("\nStep 6: Verify predictive models are up-to-date")
    updater = ModelUpdater()
    updates = await updater.check_and_update_models(
        workspace_id=workspace_id,
        model_types=[ModelType.ENGAGEMENT_PREDICTOR],
    )
    print(f"  ✓ Checked models - {len(updates['models_updated'])} updated")

    print("\n" + "=" * 80)
    print("🎉 Complete Workflow Executed Successfully!")
    print("=" * 80)
    print("\nContent agent now has:")
    print("  ✓ Learned patterns from historical data")
    print("  ✓ Insights from similar successful workspaces")
    print("  ✓ Expert team consensus on strategy")
    print("  ✓ A/B test framework for continuous improvement")
    print("  ✓ Up-to-date predictive models")
    print("\nReady to generate high-performing content! 🚀")


# ============================================================================
# Main: Run All Examples
# ============================================================================


async def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("META-LEARNING & AGENT SWARM FRAMEWORK - INTEGRATION EXAMPLES")
    print("=" * 80)

    # Run examples
    await example_performance_analysis()
    await example_transfer_learning()
    await example_model_updates()
    await example_ab_testing()
    await example_agent_team_assembly()
    await example_agent_debate()
    await example_complete_integration()

    print("\n" + "=" * 80)
    print("All examples completed successfully! ✨")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
