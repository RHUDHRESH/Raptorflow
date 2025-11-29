# Cost Logging Service

## Overview

The canonical LLM cost logging service provides a single entrypoint for recording all GPU/LLM costs in RaptorFlow. Every model call must go through this service to ensure consistent cost tracking, proper workspace/agent linkage, and correlation ID tracing.

## Core Table

All costs are stored in the normalized `cost_logs` table:

```sql
CREATE TABLE cost_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id),
  agent_id uuid REFERENCES agents(id),
  agent_run_id uuid REFERENCES agent_runs(id),
  model text NOT NULL,
  prompt_tokens integer NOT NULL DEFAULT 0,
  completion_tokens integer NOT NULL DEFAULT 0,
  total_tokens integer NOT NULL DEFAULT 0,
  estimated_cost_usd numeric(12,6) NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now()
);
```

## API

### `log_llm_call()`

The main entrypoint for logging any LLM call:

```python
from backend.services.cost_logging import log_llm_call

await log_llm_call(
    workspace_id="ws-123",
    model="gemini-1.5-flash",
    prompt_tokens=150,
    completion_tokens=75,
    agent_id="agent-456",  # optional
    agent_run_id="run-789",  # optional
)
```

**Parameters:**
- `workspace_id`: Required tenant identifier
- `model`: Model identifier (e.g., "gemini-1.5-flash")
- `prompt_tokens`: Input token count
- `completion_tokens`: Output token count
- `agent_id`: Associated agent UUID (optional)
- `agent_run_id`: Associated agent run UUID (optional)

**Behavior:**
- Automatically calculates `total_tokens = prompt_tokens + completion_tokens`
- Looks up pricing for the model and estimates USD cost
- Inserts structured record into `cost_logs` table
- Logs a structured event with correlation context
- Handles errors gracefully (doesn't crash business logic)

### Pricing Configuration

Costs are estimated using centralized pricing configuration:

```python
MODEL_PRICING = {
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},  # $0.075/1K input, $0.30/1K output
    "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},     # $1.25/1K input, $5.00/1K output
    "unknown": {"input": 0.00125, "output": 0.005},           # Conservative fallback (highest tier)
}
```

**Note:** Currently assumes 50/50 input/output split for simplicity. Refinements will come with actual model response parsing.

## Integration Pattern

### Model Dispatcher Integration

All model calls must route through the future ModelDispatcher service:

```python
# In ModelDispatcher (future)
async def dispatch_call(workspace_id, model, prompt, agent_id=None, agent_run_id=None):
    # Make actual LLM call
    response = await vertex_ai_client.generate(model, prompt)

    # Extract token counts from response
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens

    # LOG COST FIRST - critical for budget enforcement
    await log_llm_call(
        workspace_id=workspace_id,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        agent_id=agent_id,
        agent_run_id=agent_run_id,
    )

    return response
```

**Critical Order:** Always log costs *before* returning response to maintain audit trail integrity.

## Cost Estimation Logic

### Known Models
For recognized models, costs use actual pricing:
```
estimated_cost = (prompt_tokens * input_rate) + (completion_tokens * output_rate)
```

### Unknown Models
Falls back to highest-tier pricing to avoid underestimating costs:
```
estimated_cost = max_tier_rate * total_tokens
```
This ensures budgets are never exceeded due to unrecognized models.

## Logging and Monitoring

### Structured Logging
All cost operations log structured events:
```
INFO cost - LLM call logged workspace_id=ws-123 model=gemini-1.5-flash prompt_tokens=150 completion_tokens=75 total_tokens=225 estimated_cost_usd=0.044625 agent_id=agent-456
```

### Error Handling
- DB failures log errors but don't crash business logic
- Cost logging never blocks core operations
- Failures are logged for monitoring/debugging

## Future Enhancements

- **Response Parsing**: `log_llm_call_from_response()` will automatically extract tokens
- **Dynamic Pricing**: API-based price fetching for real-time accuracy
- **Budget Enforcement**: Integration with workspace spending limits
- **Advanced Analytics**: Cost trends, usage patterns, optimization insights

## Cost Table Query Examples

```sql
-- Total workspace spending
SELECT SUM(estimated_cost_usd)
FROM cost_logs
WHERE workspace_id = 'ws-123';

-- Agent cost breakdown
SELECT agent_id, model, SUM(estimated_cost_usd)
FROM cost_logs
WHERE workspace_id = 'ws-123'
  AND agent_id IS NOT NULL
GROUP BY agent_id, model
ORDER BY SUM(estimated_cost_usd) DESC;

-- Hourly usage patterns
SELECT DATE_TRUNC('hour', created_at), SUM(total_tokens)
FROM cost_logs
WHERE workspace_id = 'ws-123'
  AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY DATE_TRUNC('hour', created_at);
```

## Rules for Future Code

1. **Never Call Model Without Logging**: Every GPU/LLM inference must log via this service
2. **Log Early**: Costs must be recorded before response returns
3. **Workspace Required**: All entries need workspace context for tenant isolation
4. **Correlation**: Automatic correlation ID inclusion for request tracing
5. **Graceful Degradation**: Cost logging failures ≠ business failures

This service is the financial backbone of RaptorFlow - treat it accordingly.
