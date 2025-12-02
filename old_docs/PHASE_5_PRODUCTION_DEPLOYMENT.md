# Phase 5: Production Deployment and Integration

## Overview

Phase 5 focuses on integrating the self-improving loops system with the existing orchestrator, deploying to production, and building frontend dashboards for monitoring and management.

**Status**: 🟡 IN PROGRESS

## Goals

1. **Integrate with SwarmOrchestrator**
   - Automatic recommendation tracking
   - Trust-based agent routing
   - Dynamic confidence boosting

2. **Update move_creation_workflow**
   - Track all agent recommendations
   - Evaluate workflow outcomes
   - Trigger learning cycles

3. **Build Frontend Dashboards**
   - Trust score visualization
   - Agent performance analytics
   - Pattern discovery insights
   - Real-time learning updates

4. **Production Deployment**
   - Database migration execution
   - Celery Beat configuration
   - Performance optimization
   - Monitoring and alerting

## Phase 5 Tasks

### Task 1: SwarmOrchestrator Integration

**File**: `backend/orchestration/swarm_orchestrator.py`

**Changes Required**:

```python
# At initialization
from backend.services.learning_integration import LearningIntegration

self.learning = LearningIntegration(db_client, redis_client)

# In execute_workflow() - Before executing workflow
workflow_context = {
    "recommendations": [],
    "quality_scores": {}
}

# In fan_out_agents() - After agent returns result
async def fan_out_agents(...):
    # ... existing code ...

    # NEW: Track recommendation
    for agent_id, result in results.items():
        recommendation_id = await self.learning.track_agent_recommendation(
            workspace_id=workflow.workspace_id,
            agent_id=agent_id,
            agent_name=agent_config.agent_name,
            correlation_id=correlation_id,
            workflow_id=workflow.id,
            recommendation_type=self._get_recommendation_type(agent_id),
            recommendation_content=result,
            confidence_score=result.get("confidence", 0.5),
            reasoning=result.get("reasoning")
        )
        workflow_context["recommendations"].append(recommendation_id)

# In execute_workflow() - After workflow completes
try:
    result = await handler(...)

    # NEW: Evaluate workflow outcome
    await self.learning.evaluate_workflow_outcome(
        workspace_id=workflow.workspace_id,
        workflow_id=workflow.id,
        recommendations=workflow_context["recommendations"],
        overall_quality_score=self._calculate_quality_score(result),
        feedback=result.get("evaluation")
    )

    # NEW: Check if learning cycle should trigger
    if await self.learning.should_trigger_learning_cycle(workflow.workspace_id):
        # Trigger in background
        from backend.tasks.learning_jobs import run_meta_learning_cycle
        run_meta_learning_cycle.delay(workflow.workspace_id)

    return result
```

**Difficulty**: Medium
**Estimated Time**: 2-3 hours
**Testing**: Unit tests + integration tests with sample workflows

### Task 2: move_creation_workflow Integration

**File**: `backend/workflows/move_creation_workflow.py`

**Changes Required**:

```python
# At function start
async def create_move_with_swarm(
    orchestrator: SwarmOrchestrator,
    workflow_id: str,
    correlation_id: str,
    goal: Dict[str, Any]
) -> Dict[str, Any]:

    # NEW: Initialize workflow context for learning
    workflow_context = {
        "recommendations": [],
        "stage_results": {},
        "quality_indicators": {}
    }

    # ... existing stages ...

    # In research_analysis stage - after parallel execution
    research_results = await orchestrator.execute_parallel_stage(...)

    # NEW: Track stage recommendations
    for agent_id, result in research_results.items():
        rec_id = await orchestrator.learning.track_agent_recommendation(
            workspace_id=orchestrator.db.workspace_id,
            agent_id=agent_id,
            agent_name=agent_id,
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            recommendation_type="strategy",
            recommendation_content=result
        )
        workflow_context["recommendations"].append(rec_id)

    # ... rest of workflow ...

    # In finalization - Before returning package

    # NEW: Calculate quality metrics
    quality_score = orchestrator._calculate_workflow_quality(
        final_move_package,
        research_results,
        review_results
    )

    # NEW: Evaluate all recommendations
    await orchestrator.learning.evaluate_workflow_outcome(
        workspace_id=orchestrator.db.workspace_id,
        workflow_id=workflow_id,
        recommendations=workflow_context["recommendations"],
        overall_quality_score=quality_score
    )

    return final_move_package
```

**Difficulty**: Medium
**Estimated Time**: 2-3 hours
**Testing**: End-to-end workflow testing with quality measurement

### Task 3: Trust-Based Agent Selection

**File**: `backend/orchestration/swarm_orchestrator.py` (fan_out_agents method)

**Enhancement**: Use trust scores to adjust agent selection priority

```python
async def fan_out_agents(
    self,
    correlation_id: str,
    agent_specs: List[Dict[str, Any]],
    timeout: float = 120.0
) -> Dict[str, Any]:
    """Enhanced with trust-based selection"""

    # ... existing barrier creation ...

    # NEW: For each agent spec, get trust boost
    for spec in agent_specs:
        agent_id = spec.get("agent_id")

        # Get trust-based confidence boost
        boost = await self.learning.get_agent_decision_boost(
            workspace_id=workflow.workspace_id,
            agent_id=agent_id,
            recommendation_type=spec.get("recommendation_type", "general")
        )

        # Adjust message priority if trust is high
        if boost > 0.2:
            spec["priority"] = "CRITICAL"  # Boost high-trust agents
        elif boost < -0.2:
            spec["priority"] = "LOW"  # De-prioritize low-trust agents

    # ... rest of fan_out_agents ...
```

**Difficulty**: Low
**Estimated Time**: 1-2 hours
**Testing**: Mock trust scores and verify priority changes

### Task 4: Frontend - Trust Score Dashboard

**Files to Create**:
- `frontend/components/LearningDashboard.tsx`
- `frontend/pages/learning/index.tsx`
- `frontend/pages/learning/trust-scores.tsx`
- `frontend/pages/learning/patterns.tsx`
- `frontend/pages/learning/agent-profiles.tsx`

**Components**:

**TrustScoreDashboard**
```typescript
interface AgentTrustCard {
    agentId: string
    agentName: string
    overallTrust: number
    accuracyScore: number
    consistencyScore: number
    timeliness: number
    reliability: number
    trend: 'improving' | 'stable' | 'declining'
    approvalRate: number
    avgQuality: number
}

// Features:
// - Color-coded trust bars (red/yellow/green)
// - Trend indicators (up/down/flat)
// - Approval rate percentage
// - Average quality score
// - Comparison with workspace average
```

**PatternDiscoveryBoard**
```typescript
interface DiscoveredPattern {
    patternName: string
    category: 'consensus' | 'expert' | 'high_confidence'
    successRate: number
    confidenceLevel: number
    agentIds: string[]
    participatingAgents: number
    lastConfirmed: DateTime
}

// Features:
// - Pattern cards with success rates
// - Agent participation visualization
// - Pattern strength indicators
// - Category filtering
// - Timeline of pattern discovery
```

**AgentPerformanceAnalytics**
```typescript
interface AgentMetrics {
    agentId: string
    totalRecommendations: number
    approvedCount: number
    rejectedCount: number
    partialCount: number
    approvalRate: number
    avgConfidence: number
    avgQuality: number
    recommendationStrength: 'weak' | 'moderate' | 'strong' | 'very_strong'
}

// Features:
// - Recommendation count trend
// - Approval rate over time
// - Quality score progression
// - Comparison with other agents
// - Exportable reports
```

**Difficulty**: High (requires UI/UX work)
**Estimated Time**: 8-10 hours
**Dependencies**: Needs API endpoints from Phase 4

### Task 5: Learning Insights Widget

**File**: `frontend/components/LearningInsightsWidget.tsx`

**Features**:
- Real-time learning cycle status
- Key insights display
- Pattern recommendations
- Trust trend alerts
- Recommended actions

**Example Output**:
```
🎯 Latest Learning Cycle (2 hours ago)

Patterns Discovered: 8
Confirmed Patterns: 6
Rules Updated: 12
Model Accuracy: 87%

Key Insights:
• 3 agents identified as experts (>75% approval rate)
• Consensus recommendations have 85% approval rate
• MoveArchitect shows improving trend (+12% this week)

Recommendations:
• Increase consensus requirements for risky recommendations
• Provide training to PsycheLens (recent decline detected)
• Leverage expert agents for strategic decisions
```

**Difficulty**: Medium
**Estimated Time**: 4-5 hours

### Task 6: Database Migration Execution

**Steps**:

```bash
# 1. Backup production database
pg_dump raptorflow_db > raptorflow_backup_$(date +%Y%m%d).sql

# 2. Run migration
psql raptorflow_db < database/migrations/008_self_improving_loops.sql

# 3. Verify tables created
psql raptorflow_db -c "
  SELECT tablename FROM pg_tables
  WHERE schemaname='public' AND tablename LIKE 'agent_%'
  OR tablename LIKE 'recommendation_%'
  OR tablename LIKE 'meta_learner%'
"

# 4. Create initial RLS policies
psql raptorflow_db < scripts/setup_rls.sql

# 5. Initialize trust scores for existing agents
curl -X POST http://localhost:8000/api/v1/learning/debug/initialize-trust-scores \
  -H "Authorization: Bearer $TOKEN"
```

**Difficulty**: Low
**Estimated Time**: 1 hour
**Risk**: High (production database change) - Requires backup and rollback plan

### Task 7: Celery Beat Configuration

**File**: `backend/config/celery_config.py`

**Changes**:

```python
from backend.tasks.learning_jobs import register_learning_tasks
from backend.tasks.agent_jobs import register_scheduled_tasks

def configure_celery(app):
    # Register swarm tasks (Phase 3)
    register_scheduled_tasks(app)

    # Register learning tasks (Phase 4)
    register_learning_tasks(app)

    # Verify configuration
    print(f"Configured {len(app.conf.beat_schedule)} scheduled tasks")
    for task_name, task_config in app.conf.beat_schedule.items():
        print(f"  ✓ {task_name}")
```

**Verification**:

```bash
# 1. Start Celery Beat
celery -A backend.celery_app beat -l info

# 2. Verify tasks are scheduled
# Look for output like:
# [beat] Scheduled 'learning.run_meta_learning_cycle' at 02:00

# 3. Monitor Celery
celery -A backend.celery_app events

# 4. Check task execution
# In separate terminal: celery -A backend.celery_app worker -l info
```

**Difficulty**: Low
**Estimated Time**: 1-2 hours

### Task 8: Monitoring and Alerting

**Metrics to Monitor**:

```yaml
Learning System Health:
  - Learning cycle success rate (should be >95%)
  - Average learning cycle duration (target <5 min)
  - Pattern count trend (should grow initially, stabilize)
  - Model accuracy trend (should increase to >0.8)
  - Model coverage trend (should increase to >0.7)

Trust Score Health:
  - Average trust score by agent
  - Trust score variance
  - Agents with declining trust (alert if >2 agents declining)
  - Agents with improving trust

Recommendation Quality:
  - Approval rate by agent (alert if <40%)
  - Average outcome quality score (target >70)
  - Recommendation coverage (% evaluated)
  - Quality improvement over time

Database Health:
  - agent_recommendations table size (alert if >1M rows)
  - recommendation_patterns table size
  - Database query performance
  - RLS policy enforcement
```

**Alerts to Configure**:

```yaml
Critical:
  - Learning cycle fails (email admin)
  - Agent trust drops below 0.3 (disable agent)
  - Database connection errors (page on-call)

Warning:
  - Agent approval rate drops below 50%
  - Learning cycle takes >10 minutes
  - Pattern confidence drops below threshold

Info:
  - Daily learning cycle completion
  - New patterns discovered
  - Trust score updates
```

**Tools**: Prometheus + Grafana or CloudWatch

**Difficulty**: Medium
**Estimated Time**: 4-5 hours

### Task 9: Performance Optimization

**Areas to Optimize**:

1. **Database Indexing**
```sql
-- Existing indexes from migration:
CREATE INDEX idx_recommendations_agent ON agent_recommendations(agent_id);
CREATE INDEX idx_recommendations_status ON agent_recommendations(outcome_status);

-- Potential additional indexes:
CREATE INDEX idx_recommendations_workspace_created ON agent_recommendations(workspace_id, created_at DESC);
CREATE INDEX idx_trust_workspace_score ON agent_trust_scores(workspace_id, overall_trust_score DESC);
```

2. **Query Optimization**
```python
# Use query batching for get_recent_recommendations
# Add pagination for large result sets
# Cache patterns in Redis with TTL
```

3. **Learning Cycle Optimization**
```python
# Process recommendations in batches
# Parallel pattern discovery
# Incremental updates instead of full recalculation
```

**Difficulty**: Medium
**Estimated Time**: 3-4 hours

### Task 10: Documentation and Training

**Materials to Create**:

1. **Operator Guide**
   - How to monitor learning health
   - How to interpret dashboards
   - Troubleshooting guide
   - Rollback procedures

2. **Developer Guide**
   - API documentation
   - Integration examples
   - Testing procedures
   - Extension points

3. **Business Guide**
   - Understanding trust scores
   - Interpreting patterns
   - Decision recommendations
   - ROI measurement

**Difficulty**: Low-Medium
**Estimated Time**: 2-3 hours

## Implementation Timeline

```
Week 1:
  Mon-Tue: SwarmOrchestrator Integration (Task 1)
  Wed-Thu: move_creation_workflow Integration (Task 2)
  Fri: Trust-based Agent Selection (Task 3)

Week 2:
  Mon-Tue: Frontend Dashboard Components (Task 4)
  Wed-Thu: Learning Insights Widget (Task 5)
  Fri: Database Migration + Initial Testing (Task 6)

Week 3:
  Mon: Celery Beat Configuration (Task 7)
  Tue-Wed: Monitoring and Alerting (Task 8)
  Thu-Fri: Performance Optimization (Task 9)

Week 4:
  Mon-Tue: Documentation (Task 10)
  Wed: Comprehensive Testing
  Thu: Staging Deployment
  Fri: Production Deployment + Monitoring
```

## Risk Mitigation

### Database Migration Risk
- ✅ Backup before migration
- ✅ Test on staging first
- ✅ Rollback script ready
- ✅ Minimal downtime (5-10 minutes)

### Performance Impact
- ✅ Learning runs during off-hours (2 AM)
- ✅ Trust scoring async (every 6 hours)
- ✅ Recommendation tracking fire-and-forget
- ✅ Query optimization before production

### Agent Behavioral Changes
- ✅ Gradual trust confidence boost (max +0.5)
- ✅ Agents with low trust still usable (just deprioritized)
- ✅ All existing workflows continue working
- ✅ Can disable learning integration without impact

## Rollback Plan

If critical issues arise:

```bash
# 1. Disable learning endpoints
# Set LEARNING_ENABLED = False in config

# 2. Keep recommendation tracking disabled
# This prevents database bloat

# 3. Disable scheduled learning jobs
celery -A backend.celery_app inspect shutdown

# 4. Remove trust-based routing
# Revert SwarmOrchestrator to Phase 3 behavior

# 5. Restore from backup if needed
psql raptorflow_db < raptorflow_backup_20240101.sql

# All systems continue to work with Phase 3 capabilities
```

## Success Criteria

- [x] All Phase 4 components implemented
- [ ] SwarmOrchestrator integration complete and tested
- [ ] move_creation_workflow tracking working end-to-end
- [ ] Frontend dashboards deployed
- [ ] Database migration executed successfully
- [ ] Celery tasks scheduled and executing
- [ ] Monitoring and alerting operational
- [ ] Performance meets targets (<10ms recommendation tracking)
- [ ] Documentation complete
- [ ] Zero critical issues in production for 1 week

## Performance Targets

| Operation | Target | Actual |
|-----------|--------|--------|
| Track recommendation | <10ms | TBD |
| Get trust score | <50ms | TBD |
| Learning cycle (1000 recs) | <5min | TBD |
| Pattern query | <100ms | TBD |
| API response | <200ms | TBD |

## Go-Live Checklist

- [ ] Database backed up and migration tested
- [ ] All tests passing (unit, integration, e2e)
- [ ] Performance benchmarks met
- [ ] Monitoring and alerting operational
- [ ] Runbooks and documentation ready
- [ ] Team trained
- [ ] Rollback plan verified
- [ ] Staging environment validated
- [ ] Load testing completed
- [ ] Security audit complete

## Estimated Effort

- **Development**: 35-40 hours
- **Testing**: 15-20 hours
- **Deployment**: 5-10 hours
- **Documentation**: 5-8 hours
- **Total**: 60-78 hours (~2 weeks with 1 developer)

## Next Steps After Phase 5

1. **Phase 5+: Advanced Analytics**
   - Long-term trend analysis
   - Predictive modeling
   - Agent capability matrix
   - Workforce planning insights

2. **Phase 5+: Multi-Workspace Learning**
   - Cross-workspace pattern sharing
   - Federated learning
   - Global best practices

3. **Phase 5+: User Feedback Integration**
   - Human-in-the-loop evaluations
   - Feedback-driven learning
   - Custom quality metrics

---

**Current Status**: 🟡 Planning Complete
**Ready to Start**: YES
**First Task**: SwarmOrchestrator Integration
