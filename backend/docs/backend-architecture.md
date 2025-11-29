# RaptorFlow Backend Architecture

## Overview

RaptorFlow is a multi-agent marketing operating system built with Python, FastAPI, and modern async patterns. This document outlines the core architecture and Genesis Engine infrastructure that enables the agent society.

## Core Infrastructure Stack

```
┌─────────────────────────────────────┐
│           FastAPI Application        │
├─────────────────────────────────────┤
│ Middleware: Auth, CORS, Correlation │
├─────────────────────────────────────┤
│ Request Context + Workspace Guards  │
├─────────────────────────────────────┤
│ Service Layer: Models, Bus, Agents  │
├─────────────────────────────────────┤
│ Core: Redis, Config, Errors, Health │
├─────────────────────────────────────┤
│ External: Supabase, Vertex AI, Upstash │
└─────────────────────────────────────┘
```

## 1. Core Infrastructure Components

### 1.1 Configuration (`backend/core/config.py`)
- **Purpose**: Centralized configuration management with Pydantic settings
- **Features**:
  - Environment validation (production vs development)
  - GCP/Vertex AI settings
  - Redis/Upstash configuration
  - Database connection settings
- **Usage**: `get_settings()` for global access
- **Validation**: Strict mode in production, flexible in development

### 1.2 Request Context (`backend/core/request_context.py`)
- **Purpose**: Thread-safe request-scoped context management
- **Features**:
  - ContextVar-based storage for user, workspace, role
  - Correlation ID tracking
  - Helper functions: `get_current_user_id()`, `get_current_workspace_id()`
- **Integration**: Automatically populated by authentication dependencies

### 1.3 Errors & Exception Handling (`backend/core/errors.py`, `backend/api/exception_handlers.py`)
- **Purpose**: Standardized error contracts and FastAPI exception handlers
- **Error Types**:
  - `PermissionDeniedError` (403)
  - `NotFoundError` (404)
  - `ValidationFailedError` (422)
  - `ConflictError` (409)
  - `BudgetExceededError` (402)
- **Response Format**: Structured JSON with correlation ID and error codes

### 1.4 Logging (`backend/utils/logging_config.py`)
- **Purpose**: Structured JSON logging with correlation tracking
- **Features**:
  - Request-scoped correlation ID
  - Automatic workspace/user binding from context
  - Component-specific loggers
- **Output**: JSON in production, human-readable in development

### 1.5 Redis & Bus (`backend/core/redis_client.py`, `backend/bus/raptor_bus.py`)
- **Purpose**: Async Redis client factory and event bus
- **Features**:
  - Connection pooling for Redis/Upstash
  - RaptorBus for agent communication with simple publish API
  - Event envelope format: `{event_type, workspace_id, correlation_id, payload, timestamp}`
- **Usage**: `await get_bus().publish("event.type", payload)`

### 1.6 Health Checks (`backend/core/health.py`)
- **Purpose**: Comprehensive service health monitoring
- **Checks**:
  - Redis connectivity
  - Database connectivity
  - Vertex AI configuration
  - Environment validation
- **Endpoint**: `GET /health` returns full system status

## 2. Authentication & Authorization

### 2.1 Dependency Chain (`backend/api/deps.py`)
```
JWT Token → get_current_user_id() → get_current_workspace_id() → get_request_context_dep()
                                                              ↓
Role Guards: require_workspace_member() ← require_workspace_role("owner", "admin")
```

### 2.2 Workspace Resolution Order
1. Explicit `X-Workspace-Id` header
2. Query parameter `workspace_id`
3. URL path parameter (e.g., `/workspaces/{workspace_id}`)
4. Default: First workspace user belongs to

### 2.3 Membership Validation
- Database lookup via `workspace_members` table
- Role hierarchy: `owner` > `admin` > `member`
- Context persistence: Set once, available throughout request

## 3. Business Services Layer

### 3.1 Agent Registry (`backend/services/agent_registry.py`)
- **Purpose**: Manage canonical Council of Lords agents
- **Lords**:
  - Architect: System design and evolution
  - Cognition: Research and knowledge acquisition
  - Strategos: Strategic planning and execution
  - Aesthete: Brand quality and creative oversight
  - Seer: Trend analysis and intelligence
  - Arbiter: Rules, compliance, conflict resolution
  - Herald: Communication and messaging
- **Features**: Idempotent seeding for workspaces

### 3.2 Agent Runs (`backend/services/agent_runs.py`)
- **Purpose**: Track agent execution lifecycle
- **Features**:
  - Run start/completion with metadata
  - Status tracking (running, completed, failed)
  - Payload storage for input/output data
  - Statistics and history queries

### 3.3 Cost Logging (`backend/services/cost_logging.py`)
- **Purpose**: Track LLM costs by workspace
- **Features**:
  - Token-based cost estimation
  - Budget enforcement via `BudgetExceededError`
  - Monthly workspace limits in `MONTHLY_WORKSPACE_BUDGET_USD`

### 3.4 Audit Logging (`backend/services/audit_log.py`)
- **Purpose**: Event and tool call logging for compliance
- **Features**:
  - Workspace-scoped audit trails
  - Tool call logging with input/output
  - Structured metadata and actor tracking

## 4. ModelDispatcher Orchestration (`backend/services/model_dispatcher.py`)

- **Purpose**: Unified interface for LLM calls with cost/budget enforcement
- **Aliases**:
  - `"fast"` → Gemini Flash
  - `"standard"` → Gemini Pro
  - `"heavy"` → Claude Sonnet
- **Features** (TODO: Currently skeleton)
  - Budget checking against monthly workspace limits
  - Model resolution and Vertex AI integration
  - Automatic cost logging and audit trails

## 5. LangGraph Tooling (Skeleton: `backend/agents/tooling/`)

### 5.1 Tool Context (`contracts.py`)
```python
@dataclass
class ToolContext:
    workspace_id: str
    actor_user_id: Optional[str] = None
    agent_id: Optional[str] = None
    agent_run_id: Optional[str] = None
    correlation_id: Optional[str] = None
```

### 5.2 Tool Wrappers (`langgraph_integration.py`)
- **Model Dispatch Tool**: LangGraph-compatible wrapper around ModelDispatcher
- **Bus Publish Tool**: Tool for publishing events via RaptorBus
- **Audit Integration**: Automatic tool call logging

## 6. Background Worker (`backend/worker.py`)

- **Purpose**: Event-driven processing for asynchronous tasks
- **Handlers**:
  - `workspace.created`: Auto-seed with Council of Lords agents
  - `test.event`: Smoke testing functionality
- **Execution**: `python -m backend.worker` runs event loop

## 7. Environment Configuration

### Required Environment Variables
```
# Database & Auth
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...
SUPABASE_JWT_SECRET=...

# Redis (Upstash)
REDIS_URL=rediss://...

# GCP/Vertex AI
GOOGLE_CLOUD_PROJECT=...
GOOGLE_CLOUD_LOCATION=us-central1

# App Config
ENVIRONMENT=development
SECRET_KEY=...
```

### Production Considerations
- `ENVIRONMENT=production` enables stricter validation
- Budget limits enforced via `MONTHLY_WORKSPACE_BUDGET_USD`
- SSL required for external connections

## 8. Testing Strategy

### Unit Test Modules
- `test_config_and_health.py`: Configuration and health checks
- `test_request_context_and_guards.py`: Auth and workspace guards
- `test_error_handling.py`: Exception handling contracts
- `test_agent_registry.py`: Council of Lords management

### Integration Points
- Database connections (Supabase)
- Redis/Upstash connectivity
- Vertex AI API (when implemented)
- RaptorBus event flow

## 9. Deployment Architecture

### Key Services
- **Main API**: FastAPI application (`backend/main.py`)
- **Worker**: Event processor (`backend/worker.py`)
- **Memory System**: Vector/temporal storage
- **Frontend**: Next.js/Vercel (minimal skeleton provided)

### Scaling Considerations
- Redis for session/cache/message bus
- Supabase for transactional data
- pgvector for semantic search
- Agent orchestration via LangGraph
- Event-driven architecture for loose coupling

## 10. Migration Path

This architecture provides a **skeleton foundation** for the full Genesis Engine. Key next steps:

1. **Real Vertex AI Integration**: Implement actual Gemini/Claude API calls in ModelDispatcher
2. **LangGraph Graphs**: Build agent society flows (Research, Muse, Matrix, Guardian guardrails)
3. **Frontend UX**: Complete app shell with workspace navigation and agent dashboards
4. **Performance & Observability**: Metrics, tracing, and cost monitoring
5. **Data Layer**: SQL migrations for agents, runs, cost_logs, audit_logs

The foundation is stable: request context, auth guards, error handling, event bus, and agent infrastructure are all in place and ready for detailed implementation prompts to fill in the business logic.
