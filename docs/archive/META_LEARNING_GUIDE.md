# Meta-Learning and Agent Swarm Framework Guide

## Overview

This guide documents the meta-learning capabilities and agent swarm framework added to RaptorFlow. These systems enable continuous improvement, knowledge transfer, and multi-agent collaboration.

## Table of Contents

1. [Meta-Learning Components](#meta-learning-components)
2. [Agent Swarm Framework](#agent-swarm-framework)
3. [Integration Workflows](#integration-workflows)
4. [API Reference](#api-reference)
5. [Best Practices](#best-practices)

---

## Meta-Learning Components

### 1. PerformanceAnalyzer

**Purpose:** Analyze historical content and campaign performance to identify winning and losing patterns.

**Location:** `backend/meta_learning/performance_analyzer.py`

#### Features

- Pattern extraction from historical data using ML
- Statistical significance testing
- Confidence scoring and sample size tracking
- Task-specific pattern recommendations

#### Usage

```python
from backend.meta_learning.performance_analyzer import PerformanceAnalyzer

# Initialize
analyzer = PerformanceAnalyzer(
    min_confidence=0.7,
    min_sample_size=30,
    min_effect_size=0.3
)

# Analyze patterns
patterns = await analyzer.analyze_patterns(
    workspace_id=workspace_id,
    content_type="social",  # or "blog", "email", etc.
    lookback_days=90,
    min_samples=50
)

# Get recommendations for specific tasks
recommendations = await analyzer.get_pattern_recommendations(
    workspace_id=workspace_id,
    task_type="blog_writing",
    top_k=3
)
```

#### Output Format

```python
{
    "winning_patterns": [
        {
            "pattern_id": "winning_cluster_0",
            "pattern_type": "winning",
            "description": "Content performs 45.2% better when: includes emojis, has clear CTA",
            "features": {
                "avg_word_count": 487.3,
                "emoji_usage": 0.85,
                "cta_inclusion": 0.92,
                "avg_sentiment": 0.73
            },
            "confidence": 0.89,
            "sample_size": 67,
            "effect_size": 0.45,
            "applicable_tasks": ["social_media_post", "email_campaign"]
        }
    ],
    "losing_patterns": [...],
    "insights": [
        "Identified 3 high-performing patterns with average 0.38 effect size",
        "Top strategy: Content performs 45.2% better when: includes emojis, has clear CTA (confidence: 89.0%)"
    ],
    "statistics": {
        "sample_count": 150,
        "winning_pattern_count": 3,
        "losing_pattern_count": 2,
        "lookback_days": 90
    }
}
```

#### Integration with Agents

```python
class ContentAgent(BaseAgent):
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Get learned patterns before generating content
        analyzer = PerformanceAnalyzer()
        patterns = await analyzer.analyze_patterns(
            workspace_id=payload["workspace_id"],
            content_type=payload["content_type"]
        )

        # Apply winning patterns to generation
        for pattern in patterns["winning_patterns"]:
            if pattern["confidence"] > 0.8:
                # Incorporate pattern features into prompt/generation
                self._apply_pattern(pattern)

        # Generate content...
```

---

### 2. TransferLearner

**Purpose:** Transfer knowledge across workspaces by identifying similar contexts and extracting anonymized patterns.

**Location:** `backend/meta_learning/transfer_learner.py`

#### Features

- Privacy-preserving workspace similarity detection
- Cross-workspace pattern aggregation
- Confidence-scored recommendations
- Cold-start problem mitigation

#### Usage

```python
from backend.meta_learning.transfer_learner import TransferLearner

# Initialize
transfer_learner = TransferLearner(
    min_source_workspaces=3,
    min_confidence=0.6,
    similarity_threshold=0.7
)

# Get insights for a workspace
insights = await transfer_learner.get_transfer_insights(
    target_workspace_id=workspace_id,
    top_k=5,
    insight_types=["strategy", "content", "timing", "channel"]
)

# Calculate similarity between workspaces
similarity = await transfer_learner.compute_workspace_similarity(
    workspace_a=workspace_id_1,
    workspace_b=workspace_id_2
)
```

#### Output Format

```python
{
    "insights": [
        {
            "insight_id": "timing_optimal_hours",
            "insight_type": "timing",
            "description": "Post during 9, 10, 14, 17 hours for 1.3x better engagement based on similar workspaces",
            "source_workspaces": 12,
            "confidence": 0.87,
            "effect_size": 0.3,
            "applicable_scenarios": ["content_scheduling", "campaign_planning"],
            "metadata": {"optimal_hours": [9, 10, 14, 17]}
        }
    ],
    "similar_workspaces": 12,
    "coverage": "high",
    "metadata": {
        "target_industry": "saas",
        "target_size": "smb",
        "total_insights_found": 8
    }
}
```

#### When to Use

- **New workspaces:** Bootstrap strategy with proven tactics
- **Underperforming workspaces:** Learn from successful similar businesses
- **Strategy planning:** Validate approaches against broader data
- **Cold start:** Provide recommendations when local data is insufficient

---

### 3. ModelUpdater

**Purpose:** Manage predictive model lifecycle with drift detection and automated retraining.

**Location:** `backend/meta_learning/model_updater.py`

#### Features

- Automated drift detection using statistical tests
- Model retraining with recent data
- Version control and rollback
- Performance monitoring
- Scheduled update orchestration

#### Supported Models

- `ENGAGEMENT_PREDICTOR` - Predicts content engagement rates
- `TONE_CLASSIFIER` - Classifies content tone/sentiment
- `CONVERSION_PREDICTOR` - Predicts conversion likelihood
- `SENTIMENT_ANALYZER` - Analyzes sentiment
- `TOPIC_CLASSIFIER` - Classifies content topics

#### Usage

```python
from backend.meta_learning.model_updater import ModelUpdater, ModelType

# Initialize
updater = ModelUpdater(
    drift_warning_threshold=0.1,
    drift_critical_threshold=0.2,
    min_samples_for_drift=50
)

# Check and update models
results = await updater.check_and_update_models(
    workspace_id=workspace_id,
    model_types=[
        ModelType.ENGAGEMENT_PREDICTOR,
        ModelType.TONE_CLASSIFIER
    ],
    force_retrain=False  # Only retrain if drift detected
)

# Schedule automatic updates
schedule = await updater.schedule_updates(
    model_type=ModelType.ENGAGEMENT_PREDICTOR,
    frequency_days=7,  # Weekly checks
    min_new_samples=100,
    drift_threshold=0.15
)

# Rollback if needed
await updater.rollback_model(
    workspace_id=workspace_id,
    model_type=ModelType.ENGAGEMENT_PREDICTOR,
    target_version="v_20240115_143022"
)
```

#### Drift Detection

The system uses multiple drift detection methods:

1. **Performance Degradation:** Compares current vs. baseline metrics
2. **Statistical Testing:** T-tests for significance
3. **Drift Score:** Normalized performance change

```python
# Detect drift for a specific model
drift_report = await updater.detect_drift(
    workspace_id=workspace_id,
    model_type=ModelType.ENGAGEMENT_PREDICTOR
)

# drift_report contains:
# - drift_status: "no_drift", "warning", or "critical"
# - drift_score: 0.0 to 1.0 (higher = more drift)
# - p_value: Statistical significance
# - recommendation: "continue_monitoring", "schedule_retrain_soon", "immediate_retrain_required"
```

---

### 4. ExperimentEngine

**Purpose:** Run A/B tests and continuous experiments to optimize strategies.

**Location:** `backend/meta_learning/experiment_engine.py`

#### Features

- A/B and multivariate testing
- Multi-armed bandit algorithms (Thompson Sampling, UCB)
- Bayesian inference for significance
- Early stopping
- Automatic winner selection

#### Experiment Types

- `AB_TEST` - Classic A/B test with fixed allocation
- `MULTIVARIATE` - Test multiple variables simultaneously
- `MULTI_ARMED_BANDIT` - Dynamic allocation to better variants
- `SEQUENTIAL` - Sequential testing with early stopping

#### Usage

```python
from backend.meta_learning.experiment_engine import (
    ExperimentEngine,
    ExperimentType,
    VariantAllocation
)

# Initialize
engine = ExperimentEngine(
    default_confidence=0.95,
    min_effect_size=0.05
)

# Create experiment
experiment = await engine.create_experiment(
    name="Hook Style Test",
    workspace_id=workspace_id,
    variants=[
        {"name": "control", "description": "Current hook style"},
        {"name": "curiosity_gap", "description": "Curiosity gap hook"},
        {"name": "emotional", "description": "Emotional trigger hook"}
    ],
    metric_name="engagement_rate",
    experiment_type=ExperimentType.AB_TEST,
    allocation_strategy=VariantAllocation.THOMPSON,  # Dynamic allocation
    min_sample_size=100,
    confidence_level=0.95
)

# Start experiment
await engine.start_experiment(experiment.experiment_id)

# Assign variant to user
variant_id = await engine.assign_variant(experiment.experiment_id)

# Record outcome
await engine.record_outcome(
    experiment_id=experiment.experiment_id,
    variant_id=variant_id,
    outcome=0.15  # 15% engagement rate
)

# Analyze results
results = await engine.analyze_experiment(experiment.experiment_id)

# Auto-complete when significant
if results.confidence >= 0.95:
    await engine.complete_experiment(experiment.experiment_id)
```

#### Allocation Strategies

**EQUAL:** Equal traffic split (classic A/B)
```python
allocation_strategy=VariantAllocation.EQUAL
```

**THOMPSON:** Thompson Sampling (explores less, exploits more)
```python
allocation_strategy=VariantAllocation.THOMPSON
```

**UCB:** Upper Confidence Bound (balances exploration/exploitation)
```python
allocation_strategy=VariantAllocation.UCB
```

---

## Agent Swarm Framework

### 1. ExpertAgentRegistry

**Purpose:** Maintain a registry of hyper-specialized expert agents with different capabilities.

**Location:** `backend/agents/swarm/expert_agent_registry.py`

#### Expert Agents

| Agent | Expertise | Key Skills |
|-------|-----------|------------|
| **SEO Expert** | Search optimization, keyword strategy | keyword_research, semantic_seo, technical_seo |
| **Copywriting Ninja** | Persuasive writing, conversion | persuasive_writing, storytelling, cta_optimization, headline_writing |
| **Data Storyteller** | Data narratives, insights | data_analysis, data_visualization, insight_generation |
| **Psychology Specialist** | Behavioral psychology, persuasion | behavioral_psychology, cognitive_biases, emotional_triggers |
| **Viral Engineer** | Viral content, shareability | viral_mechanics, shareability, trend_analysis, meme_culture |
| **Brand Guardian** | Brand consistency, voice | brand_voice, tone_consistency, style_guidelines |
| **Technical Writer** | Technical simplification | technical_writing, documentation, simplification |

#### Usage

```python
from backend.agents.swarm.expert_agent_registry import (
    ExpertAgentRegistry,
    AgentRole,
    SkillTag,
    TaskRequirements
)

# Initialize registry (comes with default expert agents)
registry = ExpertAgentRegistry()

# Get a specific agent
seo_expert = registry.get_agent(role=AgentRole.SEO_EXPERT)

# Find agents by skill
writers = registry.find_agents_by_skill(
    skills=[SkillTag.PERSUASIVE_WRITING, SkillTag.STORYTELLING],
    min_level=ExpertiseLevel.ADVANCED,
    require_all=False  # Match any skill
)

# Assemble optimal team for a task
team = await registry.assemble_team(
    TaskRequirements(
        task_type="viral_social_campaign",
        required_skills=[
            SkillTag.VIRAL_MECHANICS,
            SkillTag.PERSUASIVE_WRITING,
            SkillTag.EMOTIONAL_TRIGGERS
        ],
        preferred_skills=[
            SkillTag.TREND_ANALYSIS,
            SkillTag.BRAND_VOICE
        ],
        min_team_size=3,
        max_team_size=5
    )
)

# Update agent performance (for learning)
await registry.update_performance(
    agent_id=seo_expert.agent_id,
    task_type="blog_optimization",
    performance_score=0.89
)
```

#### Registering Custom Agents

```python
from backend.agents.swarm.expert_agent_registry import (
    ExpertAgentProfile,
    AgentRole,
    AgentSkill,
    SkillTag,
    ExpertiseLevel
)

# Create custom expert agent
custom_agent = ExpertAgentProfile(
    role=AgentRole.CONTENT_STRATEGIST,
    name="Content Strategy Expert",
    description="Expert in content strategy and planning",
    skills=[
        AgentSkill(
            skill=SkillTag.STORYTELLING,
            level=ExpertiseLevel.EXPERT,
            confidence=0.9
        ),
        AgentSkill(
            skill=SkillTag.DATA_ANALYSIS,
            level=ExpertiseLevel.ADVANCED,
            confidence=0.85
        )
    ],
    system_prompt="You are a content strategy expert...",
    temperature=0.7
)

# Register agent
agent_id = registry.register_agent(custom_agent)
```

---

### 2. AgentDebateOrchestrator

**Purpose:** Orchestrate multi-agent debates where agents propose, critique, refine, and reach consensus.

**Location:** `backend/agents/swarm/agent_debate_orchestrator.py`

#### Debate Process

1. **Proposal Phase:** Each agent proposes a solution from their perspective
2. **Critique Phase:** Agents critique each other's proposals
3. **Refinement Phase:** Agents refine based on feedback (implicit in next round)
4. **Consensus Phase:** Reach final decision through voting or synthesis

#### Consensus Strategies

- `MAJORITY_VOTE` - Simple majority wins
- `WEIGHTED_VOTE` - Weight by agent expertise
- `SYNTHESIS` - Synthesize all perspectives (recommended)
- `MODERATOR` - Moderator agent decides

#### Usage

```python
from backend.agents.swarm.agent_debate_orchestrator import (
    AgentDebateOrchestrator,
    ConsensusStrategy
)
from backend.agents.swarm.expert_agent_registry import AgentRole

# Initialize
registry = ExpertAgentRegistry()
orchestrator = AgentDebateOrchestrator(
    agent_registry=registry,
    max_rounds=3,
    default_consensus=ConsensusStrategy.SYNTHESIS
)

# Run debate
result = await orchestrator.orchestrate_debate(
    problem="How to create a viral social media campaign for a SaaS product?",
    agent_roles=[
        AgentRole.VIRAL_ENGINEER,
        AgentRole.COPYWRITING_NINJA,
        AgentRole.PSYCHOLOGY_SPECIALIST,
        AgentRole.SEO_EXPERT
    ],
    rounds=2,  # 2 rounds of proposal -> critique -> refine
    consensus_strategy=ConsensusStrategy.SYNTHESIS,
    context={"budget": 10000, "timeline": "3 months"}
)

# Access results
decision = result["decision"]  # Final consensus decision
reasoning = result["reasoning"]  # Combined reasoning
confidence = result["confidence"]  # Confidence in decision
proposals = result["proposals"]  # All proposals made
critiques = result["critiques"]  # All critiques
transcript = result["transcript"]  # Complete debate history
```

#### Output Format

```python
{
    "decision": "Integrated solution combining multiple expert perspectives...",
    "reasoning": "This solution synthesizes insights from:\n- Viral Engineer: viral mechanics expertise\n- Copywriting Ninja: persuasive writing expertise...",
    "confidence": 0.87,
    "proposals": [
        {
            "agent_name": "Viral Content Specialist",
            "agent_role": "viral_engineer",
            "proposal": "Create a challenge-based campaign...",
            "reasoning": "Challenges drive participation...",
            "confidence": 0.92,
            "round_number": 1
        }
    ],
    "critiques": [
        {
            "critic_name": "Conversion Copywriter",
            "target_proposal_id": "...",
            "strengths": ["Strong use of viral_engineer principles"],
            "weaknesses": ["Could integrate more copywriting elements"],
            "suggestions": ["Add storytelling hooks"],
            "agreement_level": 0.75
        }
    ],
    "transcript": { /* Complete debate history */ },
    "debate_id": "..."
}
```

---

## Integration Workflows

### Workflow 1: Content Agent with Performance Learning

```python
class SmartContentAgent(BaseAgent):
    """Content agent that learns from performance patterns."""

    def __init__(self):
        super().__init__("smart_content_agent")
        self.analyzer = PerformanceAnalyzer()
        self.transfer_learner = TransferLearner()

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        workspace_id = payload["workspace_id"]
        content_type = payload["content_type"]

        # Step 1: Learn from local performance
        patterns = await self.analyzer.analyze_patterns(
            workspace_id=workspace_id,
            content_type=content_type,
            lookback_days=90
        )

        # Step 2: Get insights from similar workspaces
        insights = await self.transfer_learner.get_transfer_insights(
            target_workspace_id=workspace_id,
            insight_types=["content", "timing"]
        )

        # Step 3: Apply learned patterns to generation
        generation_context = {
            "patterns": patterns["winning_patterns"],
            "insights": insights["insights"],
            "requirements": payload.get("requirements", {})
        }

        # Step 4: Generate content with learned optimizations
        content = await self._generate_with_patterns(generation_context)

        return {
            "status": "success",
            "content": content,
            "applied_patterns": len(patterns["winning_patterns"]),
            "applied_insights": len(insights["insights"])
        }
```

### Workflow 2: Strategy Supervisor with Agent Debate

```python
class SmartStrategySupervisor(BaseSupervisor):
    """Strategy supervisor using multi-agent debate."""

    def __init__(self):
        super().__init__("smart_strategy_supervisor")
        self.registry = ExpertAgentRegistry()
        self.orchestrator = AgentDebateOrchestrator(self.registry)

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Assemble expert team
        team = await self.registry.assemble_team(
            TaskRequirements(
                task_type="campaign_strategy",
                required_skills=[
                    SkillTag.PERSUASIVE_WRITING,
                    SkillTag.DATA_ANALYSIS,
                    SkillTag.VIRAL_MECHANICS
                ],
                min_team_size=3
            )
        )

        # Run multi-agent debate
        debate_result = await self.orchestrator.orchestrate_debate(
            problem=goal,
            agent_roles=[m["role"] for m in team["team"]],
            rounds=2,
            consensus_strategy=ConsensusStrategy.SYNTHESIS,
            context=context
        )

        return {
            "status": "success",
            "strategy": debate_result["decision"],
            "reasoning": debate_result["reasoning"],
            "confidence": debate_result["confidence"],
            "team": team["team"]
        }
```

### Workflow 3: Continuous Experimentation

```python
class ExperimentingContentAgent(BaseAgent):
    """Content agent that runs continuous A/B tests."""

    def __init__(self):
        super().__init__("experimenting_content_agent")
        self.engine = ExperimentEngine()
        self.active_experiments = {}

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        workspace_id = payload["workspace_id"]

        # Check for active experiments
        experiment_id = self.active_experiments.get("hook_style")

        if not experiment_id:
            # Create new experiment
            experiment = await self.engine.create_experiment(
                name="Hook Style Test",
                workspace_id=workspace_id,
                variants=[
                    {"name": "control", "description": "Standard hook"},
                    {"name": "curiosity", "description": "Curiosity gap"},
                    {"name": "emotional", "description": "Emotional trigger"}
                ],
                metric_name="engagement_rate"
            )
            await self.engine.start_experiment(experiment.experiment_id)
            self.active_experiments["hook_style"] = experiment.experiment_id
            experiment_id = experiment.experiment_id

        # Assign variant
        variant_id = await self.engine.assign_variant(experiment_id)

        # Generate content with assigned variant
        content = await self._generate_with_variant(variant_id)

        return {
            "status": "success",
            "content": content,
            "experiment_id": experiment_id,
            "variant_id": variant_id
        }

    async def record_performance(
        self,
        experiment_id: str,
        variant_id: str,
        engagement_rate: float
    ):
        """Called when engagement metrics are available."""
        await self.engine.record_outcome(
            experiment_id=experiment_id,
            variant_id=variant_id,
            outcome=engagement_rate
        )

        # Check if experiment is complete
        is_significant, winner = await self.engine.check_significance(experiment_id)
        if is_significant:
            await self.engine.complete_experiment(experiment_id, winner=winner)
            # Update strategy based on winner
            self._update_default_strategy(winner)
```

---

## Best Practices

### Performance Analysis

1. **Minimum Sample Size:** Ensure at least 50-100 samples for reliable patterns
2. **Regular Updates:** Re-analyze patterns monthly or when significant changes occur
3. **Confidence Thresholds:** Use high confidence (>0.8) for critical decisions
4. **Context Matters:** Filter by content type, channel, and time period

### Transfer Learning

1. **Privacy First:** System anonymizes workspace IDs and sensitive data
2. **Similarity Threshold:** Use 0.7+ similarity for reliable insights
3. **Multiple Sources:** Require insights from 3+ similar workspaces
4. **Validate Locally:** Test transferred insights with local A/B tests

### Model Management

1. **Regular Monitoring:** Check drift weekly for critical models
2. **Gradual Rollout:** A/B test new model versions before full deployment
3. **Keep History:** Maintain version history for 90 days minimum
4. **Rollback Plan:** Always have ability to rollback to previous version

### Experimentation

1. **Clear Hypotheses:** Define what you're testing and why
2. **Sufficient Sample Size:** Calculate required sample size before starting
3. **Single Variable:** Test one variable at a time for A/B tests
4. **Statistical Rigor:** Use 95%+ confidence for important decisions
5. **Document Results:** Record all experiment results for learning

### Agent Debates

1. **Diverse Teams:** Include 3-5 agents with complementary expertise
2. **Clear Problems:** Provide specific, well-defined problems to solve
3. **Multiple Rounds:** Use 2-3 rounds for complex problems
4. **Synthesis Over Voting:** Prefer synthesis to leverage all perspectives
5. **Track Reasoning:** Preserve debate transcripts for transparency

---

## API Reference

See individual module docstrings for complete API documentation:

- `backend/meta_learning/performance_analyzer.py`
- `backend/meta_learning/transfer_learner.py`
- `backend/meta_learning/model_updater.py`
- `backend/meta_learning/experiment_engine.py`
- `backend/agents/swarm/expert_agent_registry.py`
- `backend/agents/swarm/agent_debate_orchestrator.py`

## Examples

Complete integration examples are available in:

```
backend/examples/meta_learning_examples.py
```

Run examples:
```bash
cd backend
python -m examples.meta_learning_examples
```

---

## Future Enhancements

Planned improvements:

1. **Meta-Learning:**
   - Deep learning models for pattern recognition
   - Automated feature engineering
   - Reinforcement learning for strategy optimization
   - Causal inference for understanding why patterns work

2. **Agent Swarm:**
   - Agent skill evolution and learning
   - Hierarchical agent teams
   - Cross-debate knowledge sharing
   - Agent specialization through experience

3. **Integration:**
   - Real-time drift detection dashboards
   - Automated experiment orchestration
   - Pattern recommendation API endpoints
   - Transfer learning marketplace

---

## Support

For questions or issues:
- Check examples in `backend/examples/meta_learning_examples.py`
- Review docstrings in individual modules
- Consult existing agent implementations for integration patterns

---

**Version:** 1.0
**Last Updated:** 2024-01-22
**Status:** Production Ready ✅
