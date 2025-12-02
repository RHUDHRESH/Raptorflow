# Memory-Aware Orchestration System

## Overview

The RaptorFlow supervisor has been overhauled to implement intelligent, memory-aware orchestration. The system now learns from past executions, adapts agent selection based on performance, implements self-correction loops, and supports human-in-the-loop checkpoints.

## Key Features

### 1. Memory-Aware Routing

The supervisor uses historical task data to route requests intelligently:

- **Searches memory** for similar successful tasks
- **Reuses proven agent sequences** when confidence > 0.8
- **Falls back to LLM planning** for novel tasks
- **Stores routing decisions** for future learning

```python
# Route with memory-aware intelligence
agent_sequence, context = await master_orchestrator.route_with_context(
    goal="Create a blog post about AI",
    workspace_id=workspace_id,
    user_id=user_id,
)
```

### 2. Adaptive Agent Selection

Agents are selected based on workspace-specific performance metrics:

- **Tracks success rates** for each agent type
- **Measures result quality** for completed tasks
- **Swaps agents** based on performance data
- **Falls back to defaults** when no history exists

```python
# Select best performing agent for task type
best_agent = await master_orchestrator.select_best_agent(
    task_type="content_generation",
    workspace_id=workspace_id,
    fallback_agent="content",
)
```

### 3. Self-Correction Loops

Content and strategy generation includes iterative improvement:

- **Generates initial output**
- **Critiques against quality thresholds**
- **Revises based on critique**
- **Repeats until quality threshold met** or max iterations
- **Stores failed attempts** in memory for learning

```python
# Execute with self-correction
config = SelfCorrectionConfig(
    max_iterations=3,
    min_quality_score=0.85,
    critique_aspects=["clarity", "persuasiveness", "brand_alignment"],
)

result = await master_orchestrator.execute_with_self_correction(
    agent_name="content",
    payload={"goal": "Generate blog post"},
    context=agent_context,
    config=config,
)
```

### 4. Human-in-the-Loop Checkpoints

Workflow checkpoints with configurable approval rules:

- **Pauses at critical stages** for human review
- **Auto-approves when conditions met** (quality, success rate, etc.)
- **Timeout handling** for approval requests
- **User notifications** (mock implementation)

```python
# Define checkpoints
checkpoints = WorkflowCheckpoints(
    workspace_id=workspace_id,
    checkpoints=[
        WorkflowCheckpoint(
            name="strategy_review",
            description="Review strategy before content generation",
            condition=CheckpointCondition.AFTER_STAGE,
            action=CheckpointAction.REQUEST_APPROVAL,
            auto_approve_if={"quality_above": 0.85},
            timeout_seconds=3600,
        )
    ],
)

# Evaluate checkpoint
result = await master_orchestrator.evaluate_checkpoint(
    checkpoint_name="strategy_review",
    checkpoints_config=checkpoints,
    context=agent_context,
    execution_data={"quality_score": 0.9},
)
```

### 5. Context Propagation

Comprehensive AgentContext passed through entire execution chain:

- **Workspace ID** and **User ID**
- **Brand voice** profile
- **Target ICPs** (customer profiles)
- **Past successes** from memory
- **User preferences** and settings
- **Task history** for the workspace
- **Performance data** for agents
- **Quality thresholds** and **budget constraints**

```python
# Build comprehensive context
context = AgentContext(
    workspace_id=workspace_id,
    correlation_id=correlation_id,
    user_id=user_id,
    brand_voice={"tone": "professional", "style": "conversational"},
    target_icps=[icp_id_1, icp_id_2],
    quality_thresholds={"content_quality": 0.8},
    budget_constraints={"max_api_calls": 100},
)
```

## Architecture

### Components

1. **MemoryManager** (`backend/services/memory_manager.py`)
   - Stores task history, agent performance, and critiques
   - Provides semantic search for similar tasks
   - Uses Redis for fast retrieval

2. **AgentContext** (`backend/models/orchestration.py`)
   - Carries comprehensive context through agent hierarchy
   - Includes workspace data, preferences, and performance metrics

3. **WorkflowCheckpoints** (`backend/models/orchestration.py`)
   - Defines checkpoint configuration
   - Implements auto-approval logic
   - Handles timeout and notifications

4. **SelfCorrectionConfig** (`backend/models/orchestration.py`)
   - Configures self-correction loops
   - Sets quality thresholds and iteration limits

5. **MasterOrchestrator** (`backend/agents/supervisor.py`)
   - Implements all orchestration features
   - Coordinates memory, routing, checkpoints, and self-correction

### Data Flow

```
User Request
    ↓
route_with_context()
    ↓
[Search Memory] → High confidence match? → Use proven sequence
    ↓ No
[LLM Planner] → Generate new sequence
    ↓
[Build AgentContext] → Include history, performance, preferences
    ↓
[Select Best Agents] → Based on workspace metrics
    ↓
[Execute with Self-Correction]
    ↓
[Evaluate Checkpoints] → Auto-approve or pause?
    ↓
[Store Results] → Update memory for future tasks
    ↓
Return Result
```

## Usage Examples

### Example 1: Memory-Aware Routing

```python
# First execution: No memory, uses LLM planner
agent_sequence, context = await master_orchestrator.route_with_context(
    goal="Create a blog post about AI trends",
    workspace_id=workspace_id,
)
# Returns: ["content", "blog_writer"]

# Store the result
await memory_manager.store_task_result(
    goal="Create a blog post about AI trends",
    agent_sequence=agent_sequence,
    success=True,
    workspace_id=workspace_id,
    result_quality=0.92,
)

# Second execution: Memory exists, reuses proven sequence
agent_sequence, context = await master_orchestrator.route_with_context(
    goal="Write a blog about machine learning",  # Similar task
    workspace_id=workspace_id,
)
# Returns: ["content", "blog_writer"] (from memory)
```

### Example 2: Self-Correction Loop

```python
# Configure self-correction
config = SelfCorrectionConfig(
    max_iterations=3,
    min_quality_score=0.85,
    improvement_threshold=0.1,
    critique_aspects=["clarity", "persuasiveness", "brand_alignment"],
    store_failures=True,
)

# Execute with self-correction
result = await master_orchestrator.execute_with_self_correction(
    agent_name="content",
    payload={
        "goal": "Generate blog post",
        "topic": "AI in healthcare",
    },
    context=agent_context,
    config=config,
)

# Result includes metadata
print(result["self_correction_metadata"])
# {
#     "iterations": 2,
#     "final_quality_score": 0.87,
#     "threshold_met": True,
#     "attempts": 2
# }
```

### Example 3: Workflow Checkpoints

```python
# Define checkpoints
checkpoints = WorkflowCheckpoints(
    workspace_id=workspace_id,
    checkpoints=[
        WorkflowCheckpoint(
            name="strategy_review",
            description="Review strategy before content generation",
            condition=CheckpointCondition.AFTER_STAGE,
            condition_params={"stage": "strategy"},
            action=CheckpointAction.REQUEST_APPROVAL,
            auto_approve_if={
                "quality_above": 0.85,
                "success_rate_above": 0.8,
            },
            timeout_seconds=3600,
        ),
        WorkflowCheckpoint(
            name="pre_publish",
            description="Review before publishing",
            condition=CheckpointCondition.BEFORE_EXECUTION,
            action=CheckpointAction.REQUEST_APPROVAL,
            auto_approve_if={"quality_above": 0.9},
        ),
    ],
)

# Evaluate checkpoint
result = await master_orchestrator.evaluate_checkpoint(
    checkpoint_name="strategy_review",
    checkpoints_config=checkpoints,
    context=agent_context,
    execution_data={
        "quality_score": 0.9,
        "agent_success_rate": 0.85,
    },
)

if result["status"] == "auto_approved":
    print("Checkpoint auto-approved, continuing workflow")
elif result["status"] == "pending_approval":
    print("Pausing for user approval")
```

## Configuration

### Self-Correction Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_iterations` | 3 | Maximum correction attempts |
| `min_quality_score` | 0.8 | Minimum acceptable quality (0.0-1.0) |
| `improvement_threshold` | 0.1 | Minimum improvement to continue |
| `critique_aspects` | 5 aspects | What to critique (clarity, etc.) |
| `store_failures` | True | Store failed attempts in memory |

### Checkpoint Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `default_timeout` | 3600 | Default timeout in seconds (1 hour) |
| `enabled` | True | Whether checkpoints are active |
| `auto_approve_for_users` | [] | Users with auto-approval |

### Quality Thresholds

| Threshold | Default | Description |
|-----------|---------|-------------|
| `content_quality` | 0.7 | Minimum content quality score |
| `strategy_viability` | 0.8 | Minimum strategy viability |
| `research_depth` | 0.75 | Minimum research thoroughness |

## Memory Storage

### Task History

Stored in Redis with key: `memory:task_history:{workspace_id}:{goal_hash}`

Fields:
- `goal`: Task description
- `agent_sequence`: Agents used
- `success`: Whether task succeeded
- `execution_time`: Time taken
- `error`: Error message if failed
- `result_quality`: Quality score (0.0-1.0)

TTL: 30 days

### Agent Performance

Derived from task history. Tracks:
- Success rate per agent type
- Average quality score
- Best performing agent for each task type

### Critiques

Stored in Redis with key: `memory:critique:{workspace_id}:{content_id}`

Fields:
- `content_id`: ID of critiqued content
- `critique`: Critique text
- `issues`: List of specific issues
- `issue_count`: Number of issues

TTL: 7 days

## API Integration

### Route Endpoint

```python
from backend.agents.supervisor import master_orchestrator

@router.post("/orchestrate")
async def orchestrate_task(
    goal: str,
    workspace_id: UUID,
    user_id: Optional[UUID] = None,
):
    agent_sequence, context = await master_orchestrator.route_with_context(
        goal=goal,
        workspace_id=workspace_id,
        user_id=user_id,
    )

    return {
        "agent_sequence": agent_sequence,
        "context_summary": {
            "past_successes": len(context.past_successes),
            "task_history": len(context.task_history),
            "performance_data": context.performance_data,
        },
    }
```

### Execution Endpoint with Self-Correction

```python
@router.post("/execute/self-correct")
async def execute_with_self_correction(
    agent_name: str,
    payload: dict,
    workspace_id: UUID,
    user_id: Optional[UUID] = None,
):
    # Build context
    context = AgentContext(
        workspace_id=workspace_id,
        correlation_id=generate_correlation_id(),
        user_id=user_id,
    )

    # Execute with self-correction
    result = await master_orchestrator.execute_with_self_correction(
        agent_name=agent_name,
        payload=payload,
        context=context,
    )

    return result
```

## Testing

Run the examples:

```bash
python backend/examples/memory_aware_orchestration_example.py
```

This demonstrates:
1. Memory-aware routing
2. Adaptive agent selection
3. Self-correction loops
4. Workflow checkpoints
5. Context propagation
6. Complete workflow integration

## Future Enhancements

1. **Vector Embeddings**: Replace keyword matching with semantic search using embeddings
2. **Real-time Notifications**: Implement actual user notifications for checkpoints
3. **Performance Dashboard**: Visualize agent performance metrics
4. **A/B Testing**: Compare different agent sequences
5. **Cost Optimization**: Factor API costs into routing decisions
6. **Multi-workspace Learning**: Learn from successful patterns across workspaces
7. **Feedback Loop**: Allow users to rate results to improve future routing

## Troubleshooting

### Memory Not Working

- Ensure Redis is running and accessible
- Check `REDIS_URL` in settings
- Verify memory manager is initialized

### Self-Correction Not Improving

- Increase `max_iterations`
- Lower `min_quality_score`
- Adjust `critique_aspects`
- Check LLM is providing constructive critique

### Checkpoints Not Triggering

- Verify `enabled=True` in WorkflowCheckpoints
- Check condition parameters match execution data
- Ensure checkpoint names are correct

## References

- `backend/services/memory_manager.py` - Memory storage and retrieval
- `backend/models/orchestration.py` - Data models
- `backend/agents/supervisor.py` - Orchestrator implementation
- `backend/examples/memory_aware_orchestration_example.py` - Usage examples
