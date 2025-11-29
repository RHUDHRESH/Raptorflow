# RaptorBus - Message Bus Infrastructure

## Overview

RaptorBus is the canonical message bus for RaptorFlow's backend, enabling event-driven communication between services and agents. It provides a standardized pub/sub interface with built-in traceability via correlation IDs and workspace isolation.

## Key Characteristics

- **Event-Driven**: Decoupled communication between components
- **Traceable**: Every message includes correlation and workspace context
- **Redis-Based**: Uses Redis pub/sub for high-performance messaging
- **Typed**: Structured message envelopes with validation
- **Observable**: Integrated logging and metrics

## Core API

### Publish Events

```python
from backend.bus.raptor_bus import get_bus

bus = await get_bus()

# Simple publish (context vars used automatically)
await bus.publish("agent.task_started", {
    "agent_id": "RES-001",
    "task_type": "research"
})

# Explicit context (overrides context vars)
await bus.publish("model.inference_complete", {
    "tokens_used": 1500,
    "response": "..."
}, workspace_id="ws-123", correlation_id="corr-456")
```

### Subscribe to Events

```python
# Register handlers for event types
def handle_agent_started(payload):
    print(f"Agent started: {payload}")

bus.subscribe("agent.task_started", handle_agent_started)
```

## Message Format

All messages follow the BusEvent schema:
- `id`: Unique event identifier
- `type`: Event type string
- `payload`: Event-specific data (dict)
- `priority`: Message priority (low/normal/high/critical)
- `request_id`: Correlation ID for tracing
- `source_agent_id`: Origin agent ID
- `timestamp`: ISO 8601 timestamp

## Channel Naming

- **Prefix**: All channels use `raptorflow.events.{event_type}`
- **Examples**:
  - `raptorflow.events.agent.task_started`
  - `raptorflow.events.model.inference_complete`
  - `raptorflow.events.workflow.completed`

## Context & Tracing

RaptorBus automatically injects request context:
- **Correlation ID**: Links messages within a request flow
- **Workspace ID**: Ensures tenant isolation

```python
# Context is automatically included in logs and messages
# Example log: workspace_id=ws-123 correlation_id=corr-456 event_type=model.inference_complete
```

## Integration Patterns

### Service Communication
```python
# In one service
await bus.publish("campaign.created", campaign_data)

# In another service (with registered handler)
def handle_campaign_created(campaign_payload):
    # Process campaign
    process_campaign(campaign_payload)
```

### Agent Lifecycle
```python
# When agent starts a task
await bus.publish("agent.task_started", task_info)

# When agent completes
await bus.publish("agent.task_completed", result_data)
```

### Error Propagation
```python
# Errors include correlation context
try:
    risky_operation()
except Exception as e:
    await bus.publish("agent.error", {
        "error": str(e),
        "component": "research_agent"
    })
```

## Best Practices

1. **Use Semantic Event Names**: `agent.inference_started` vs `inference`
2. **Include Essential Context**: Always provide business-relevant data
3. **Leverage Correlation**: Don't pass explicit correlation_id unless overriding
4. **Workspace Awareness**: Let automatic context handle workspace scoping
5. **Handler Simplicity**: Keep handlers focused on processing, not coordination

## Architecture Notes

- **Singleton Pattern**: Use `get_bus()` for global access
- **Async Context**: Publish/subscribe operations are async
- **Error Resilience**: Bus failures don't crash applications (configurable)
- **No Direct Redis Access**: Always use RaptorBus wrapper
- **Future-Extensible**: Ready for background consumers, DLQ, etc.

## Integration with FastAPI

Startup includes optional bus initialization:
```python
# In main lifespan
try:
    from backend.bus.raptor_bus import get_bus
    await get_bus()  # Initialize connection
    logger.info("[OK] RaptorBus initialized")
except Exception as e:
    logger.warning(f"[SKIP] RaptorBus not available: {e}")
```

## Configuration

Redis connection uses `settings.REDIS_URL` or environment:
- `REDIS_URL`: Standard Redis URL
- `UPSTASH_REDIS_URL`: Upstash-compatible URL
- `UPSTASH_REDIS_TOKEN`: Authentication token

## Monitoring & Debugging

All bus operations are logged with component `bus`:
```
INFO bus - Publishing event agent.task_started to raptorflow.events.agent.task_started workspace_id=ws-123 correlation_id=corr-456
```

Metrics track publish/subscribe activity and can be accessed via `bus.get_metrics()`.
