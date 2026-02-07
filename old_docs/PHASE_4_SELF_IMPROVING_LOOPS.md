# Phase 4: Self-Improving Loops and Meta-Learning

## Overview

Phase 4 implements the self-improving loop system that enables the RaptorFlow Agent Swarm to learn from its own recommendations and continuously improve decision-making quality.

**Status**: ✅ COMPLETE

## Architecture

### Core Components

1. **Recommendation Tracking System**
   - Tracks every recommendation made by agents
   - Records confidence scores and reasoning
   - Stores outcomes and quality evaluations

2. **Trust Scoring System**
   - Dynamically calculates trust scores for each agent
   - Multi-dimensional scoring: accuracy, consistency, timeliness, reliability
   - Bayesian learning for continuous improvement

3. **Meta-Learning Agent**
   - Analyzes recommendation patterns
   - Profiles agent strengths and weaknesses
   - Generates decision rules
   - Continuous learning cycles

4. **Learning Integration Layer**
   - Seamlessly integrates with SwarmOrchestrator
   - Automatic recommendation tracking
   - Outcome evaluation and trust updates

## Database Schema

### New Tables (Migration 008)

**agent_recommendations**
- Stores every recommendation with confidence, reasoning, and evidence
- Tracks outcomes (approved, rejected, partial, pending)
- Quality scores and evaluation feedback

**recommendation_patterns**
- Discovered patterns from successful recommendations
- Pattern types: high_confidence, consensus, expert_opinion, failure_avoidance
- Success rates and confidence levels

**agent_trust_scores**
- Dynamic trust metrics for each agent
- Dimensions: accuracy, consistency, timeliness, reliability
- Overall trust score with trend analysis

**recommendation_outcomes**
- Detailed evaluation of recommendation results
- Quality dimension scoring
- Comparative ranking against alternatives

**meta_learner_state**
- Stores learned patterns, agent profiles, decision rules
- Model performance metrics
- Learning iteration history

## Key Classes

### RecommendationTracker
```python
# Track a recommendation
recommendation_id = await tracker.record_recommendation(
    workspace_id="ws_123",
    agent_id="STRAT-01",
    agent_name="MoveArchitect",
    correlation_id="workflow_456",
    workflow_id="move_123",
    recommendation_type=RecommendationType.STRATEGY,
    recommendation_content={"channels": ["linkedin"]},
    confidence_score=0.85,
    reasoning="Based on cohort analysis",
    evidence={"source": "psychographics_analysis"}
)

# Evaluate outcome
outcome_id = await tracker.evaluate_outcome(
    recommendation_id=recommendation_id,
    quality_scores={"accuracy": 90, "relevance": 85},
    overall_quality_score=87.5,
    evaluator_feedback="Excellent recommendation"
)

# Get stats
stats = await tracker.get_agent_stats(workspace_id, agent_id)
```

### TrustScorer
```python
# Initialize trust score
trust = await trust_scorer.initialize_trust_score(
    workspace_id="ws_123",
    agent_id="STRAT-01",
    agent_name="MoveArchitect"
)

# Update trust based on outcome
from backend.models.learning import TrustScoreUpdate

update = TrustScoreUpdate(
    agent_id="STRAT-01",
    recommendation_id="rec_123",
    outcome_quality_score=87.5,
    accuracy_impact=0.1,
    consistency_impact=0.05
)

updated_trust = await trust_scorer.update_trust_score(update, workspace_id)

# Get all trust scores
scores = await trust_scorer.get_all_trust_scores(workspace_id)

# Get trusted agents above threshold
trusted = await trust_scorer.get_trusted_agents(workspace_id, min_trust=0.7)
```

### MetaLearnerAgent
```python
from backend.agents.executive.meta_learner import MetaLearnerAgent

meta_learner = MetaLearnerAgent(
    redis_client,
    db_client,
    llm_client,
    recommendation_tracker,
    trust_scorer
)

# Trigger learning cycle
result = await meta_learner.trigger_learning_cycle(
    workspace_id="ws_123",
    {
        "lookback_days": 7,
        "min_pattern_confidence": 0.7
    }
)

# Get discovered patterns
patterns = await meta_learner.get_patterns(
    workspace_id="ws_123",
    pattern_category="consensus"
)

# Get agent profile
profile = await meta_learner.get_agent_profile(
    workspace_id="ws_123",
    agent_id="STRAT-01"
)

# Get decision rules
rules = await meta_learner.suggest_decision_rules(
    workspace_id="ws_123",
    {"context": {"task_type": "strategy"}}
)
```

### LearningIntegration
```python
from backend.services.learning_integration import LearningIntegration

learning = LearningIntegration(db_client, redis_client)

# Track recommendation
rec_id = await learning.track_agent_recommendation(
    workspace_id="ws_123",
    agent_id="STRAT-01",
    agent_name="MoveArchitect",
    correlation_id="workflow_456",
    workflow_id="move_123",
    recommendation_type="strategy",
    recommendation_content={"channels": ["linkedin"]},
    confidence_score=0.85
)

# Evaluate workflow outcome
summary = await learning.evaluate_workflow_outcome(
    workspace_id="ws_123",
    workflow_id="move_123",
    recommendations=[rec_id],
    overall_quality_score=87.5,
    feedback="Great recommendations"
)

# Get confidence boost for agent
boost = await learning.get_agent_decision_boost(
    workspace_id="ws_123",
    agent_id="STRAT-01",
    recommendation_type="strategy"
)

# Check if learning cycle should run
should_learn = await learning.should_trigger_learning_cycle(workspace_id="ws_123")
```

## API Endpoints

### Recommendation Tracking
- `POST /api/v1/learning/recommendations/track` - Track a recommendation
- `GET /api/v1/learning/recommendations/{recommendation_id}` - Get specific recommendation
- `GET /api/v1/learning/recommendations/agent/{agent_id}` - Get agent's recommendations

### Outcome Evaluation
- `POST /api/v1/learning/outcomes/evaluate` - Evaluate recommendation outcome

### Trust Scoring
- `GET /api/v1/learning/trust-scores/{agent_id}` - Get agent trust score
- `GET /api/v1/learning/trust-scores` - Get all trust scores

### Meta-Learning
- `POST /api/v1/learning/learning-cycles/trigger` - Trigger learning cycle
- `GET /api/v1/learning/patterns` - Get discovered patterns
- `GET /api/v1/learning/patterns?category=consensus` - Get patterns by category
- `GET /api/v1/learning/agent-profiles/{agent_id}` - Get agent profile

### Statistics
- `GET /api/v1/learning/stats` - Get learning system statistics

## Scheduled Jobs

### Learning Tasks (learning_jobs.py)

**run_meta_learning_cycle** (Daily at 2 AM)
- Discovers patterns from last 7 days of recommendations
- Profiles all agents
- Generates decision rules
- Updates meta-learner state

**update_trust_scores** (Every 6 hours)
- Recalculates all trust scores
- Updates trends
- Prepares for decision making

**refresh_patterns** (Daily at 1 AM)
- Removes low-confidence patterns
- Re-validates existing patterns
- Runs before learning cycle

**cleanup_old_recommendations** (Weekly on Sunday)
- Deletes recommendations older than 90 days
- Maintains database performance

## Trust Scoring Algorithm

### Trust Dimensions (0-1 scale)

1. **Accuracy Score**: How often recommendations are approved
2. **Consistency Score**: How well recommendations align with patterns
3. **Timeliness Score**: How quickly recommendations are delivered
4. **Reliability Score**: Agent availability and execution

### Overall Trust Calculation

```
overall_trust = (
    accuracy_score * 0.40 +
    consistency_score * 0.25 +
    timeliness_score * 0.15 +
    reliability_score * 0.20
) * confidence_factor
```

Confidence factor increases with sample size (more recommendations = higher confidence).

### Bayesian Learning

Each dimension updates using:
```
updated = current + learning_rate * (quality_factor + dimension_impact)
```

Default learning_rate = 0.1 (10% move toward signal).

## Pattern Discovery

### Pattern Types

1. **High Confidence** - Recommendations with confidence >= 0.8
2. **Consensus** - Multiple agents recommending same action
3. **Expert Opinion** - Agents with >75% approval rate
4. **Failure Avoidance** - Patterns that prevent bad outcomes
5. **Success Indicator** - Patterns strongly predicting approval

### Pattern Metrics

- `success_rate`: % of time pattern leads to approved recommendations
- `frequency_count`: How many times pattern observed
- `confidence_level`: Meta-learner confidence in pattern
- `recommendation_strength`: weak/moderate/strong/very_strong

## Workflow Integration Example

```python
# In SwarmOrchestrator.execute_workflow()

from backend.services.learning_integration import LearningIntegration

learning = LearningIntegration(db, redis_client)

# When agent makes recommendation:
recommendation_id = await learning.track_agent_recommendation(
    workspace_id=workflow.workspace_id,
    agent_id=result.agent_id,
    agent_name=agent_name,
    correlation_id=workflow.correlation_id,
    workflow_id=workflow.id,
    recommendation_type="strategy",
    recommendation_content=agent_result,
    confidence_score=agent_confidence
)

# Store recommendation ID in workflow context
workflow_context["recommendations"].append(recommendation_id)

# When workflow completes:
await learning.evaluate_workflow_outcome(
    workspace_id=workflow.workspace_id,
    workflow_id=workflow.id,
    recommendations=workflow_context["recommendations"],
    overall_quality_score=workflow_quality_score,
    feedback=evaluation_feedback
)

# Check if learning cycle should trigger:
if await learning.should_trigger_learning_cycle(workflow.workspace_id):
    # Trigger learning cycle in background
    trigger_learning_cycle(workflow.workspace_id)
```

## Model Performance

The meta-learner tracks two key metrics:

**Model Accuracy**
- Accuracy of learned patterns in predicting outcomes
- Ranges 0-1 (1.0 = perfect)
- Target: >= 0.80

**Model Coverage**
- Percentage of recommendations explained by patterns
- Ranges 0-1 (1.0 = all recommendations covered)
- Target: >= 0.70

## Sample Output

### Learning Cycle Result
```json
{
    "iteration_id": "iter_ws_123_1700000000",
    "workspace_id": "ws_123",
    "samples_analyzed": 245,
    "patterns_discovered": 8,
    "patterns_confirmed": 6,
    "rules_updated": 12,
    "iteration_accuracy": 0.87,
    "pattern_confidence_improvement": 0.05,
    "rule_effectiveness_improvement": 0.03,
    "key_insights": [
        "Identified 3 expert agents with high approval rates",
        "Multi-agent consensus strongly predicts successful recommendations",
        "4 agents are strong consensus builders"
    ],
    "recommendations_for_swarm": [
        "Increase use of multi-agent consensus for critical decisions",
        "Route recommendations through expert agents",
        "Provide additional training to weak-area agents"
    ],
    "started_at": "2024-01-15T02:00:00Z",
    "completed_at": "2024-01-15T02:05:32Z",
    "processing_time_seconds": 332
}
```

### Trust Score Response
```json
{
    "agent_id": "STRAT-01",
    "agent_name": "MoveArchitect",
    "overall_trust_score": 0.78,
    "accuracy_score": 0.82,
    "consistency_score": 0.75,
    "approval_rate": 0.8,
    "avg_quality_score": 83.5,
    "trend": "improving",
    "recommendation_strength": "strong"
}
```

## Integration Checklist

- [x] Database migration (008_self_improving_loops.sql)
- [x] Pydantic models (backend/models/learning.py)
- [x] RecommendationTracker service
- [x] TrustScorer service
- [x] MetaLearnerAgent
- [x] LearningIntegration service
- [x] API endpoints (backend/routers/learning.py)
- [x] Scheduled tasks (backend/tasks/learning_jobs.py)
- [ ] Integration with SwarmOrchestrator (Phase 5)
- [ ] Integration with move_creation_workflow (Phase 5)
- [ ] Frontend dashboards (Phase 5)

## Next Steps (Phase 5)

1. **Integrate with SwarmOrchestrator**
   - Automatic recommendation tracking during workflow execution
   - Apply trust scores to agent selection
   - Use decision rules for routing

2. **Integrate with move_creation_workflow**
   - Track all agent recommendations in workflow
   - Evaluate workflow outcome
   - Trigger learning cycles

3. **Frontend Dashboards**
   - Trust score visualization
   - Pattern discovery dashboard
   - Agent performance analytics
   - Learning insights display

4. **Production Deployment**
   - Database migration execution
   - Celery task scheduling
   - Performance optimization
   - Monitoring and alerting

## Performance Considerations

- Learning cycles run nightly, not blocking workflows
- Recommendation tracking is async and fire-and-forget
- Trust scores cached in Redis for fast access
- Old recommendations purged weekly
- Pattern discovery uses efficient batch operations

## Key Insights

The meta-learning system provides:

1. **Continuous Improvement**: Each workflow teaches the system
2. **Agent Accountability**: Clear metrics on agent performance
3. **Dynamic Routing**: Decision rules automatically adapt
4. **Pattern Recognition**: Discovers what works best
5. **Risk Mitigation**: Avoids agents with low trust
6. **Consensus Building**: Strengthens multi-agent decisions

This creates a virtuous cycle where successful patterns are reinforced and failures are analyzed to prevent recurrence.
