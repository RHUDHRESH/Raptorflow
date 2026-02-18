# RaptorFlow Backend Modernization Plan
## Production-Grade AI System Architecture Transformation

**Version:** 1.0  
**Date:** February 2026  
**Estimated Effort:** 3-4 months  
**Team Size:** 3-4 engineers  

---

## Executive Summary

This plan provides a comprehensive roadmap to transform RaptorFlow's backend from its current state into a world-class, production-grade AI system. The current architecture shows signs of organic growth with multiple overlapping AI orchestration layers (LangGraph, custom strategies, legacy patterns) that need consolidation.

### Current State Assessment
- **Lines of Code:** ~22,000 Python LOC across 206 files
- **Test Coverage:** ~49% (66 tests passing)
- **Architecture:** Mixed patterns with some clean separation but overlapping concerns
- **AI System:** LangGraph-based with multiple orchestrators, some legacy patterns
- **Infrastructure:** Docker-ready with multi-stage builds

### Target State Vision
A clean, hexagonal architecture with:
- Clear domain boundaries and dependency inversion
- Unified AI orchestration layer with pluggable backends
- Comprehensive observability and monitoring
- Production-ready scalability patterns
- Type-safe, well-tested codebase

---

## Table of Contents

1. [Current Architecture Analysis](#1-current-architecture-analysis)
2. [Target Architecture Overview](#2-target-architecture-overview)
3. [Phase 1: Foundation & Clean Architecture](#3-phase-1-foundation--clean-architecture)
4. [Phase 2: AI System Unification](#4-phase-2-ai-system-unification)
5. [Phase 3: Production Infrastructure](#5-phase-3-production-infrastructure)
6. [Phase 4: Observability & Optimization](#6-phase-4-observability--optimization)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Risk Assessment & Mitigation](#8-risk-assessment--mitigation)

---

## 1. Current Architecture Analysis

### 1.1 Directory Structure Assessment

```
backend/
├── agents/                    # LangGraph orchestrators (GOOD)
│   ├── campaign_moves/        # Campaign orchestration
│   ├── context/               # Context management
│   ├── muse/                  # Content generation
│   ├── optional/              # Module execution
│   └── runtime/               # Profile management
├── ai/                        # AI abstraction layer (GOOD)
│   ├── backends/              # Vertex AI, GenAI, Deterministic
│   ├── orchestration/         # Single/Council/Swarm strategies
│   ├── profiles/              # Intensity profiles
│   └── prompts/               # Prompt compilation
├── api/                       # API layer (NEEDS CLEANUP)
│   ├── v1/                    # Versioned endpoints
│   └── dependencies/          # Auth, injection
├── bcm/                       # Business Context Model
├── features/                  # Domain features (INCOMPLETE)
├── infrastructure/            # Infra layer (GOOD)
│   ├── cache/                 # Redis, Sentinel
│   ├── database/              # Supabase, pooling
│   └── storage/               # Asset storage
└── services/                  # Service layer (MIXED QUALITY)
```

### 1.2 Key Strengths

1. **AI Backend Abstraction:** Well-designed `BaseAIBackend` with protocol
2. **Service Layer:** `BaseService` with circuit breaker pattern
3. **Type Safety:** Comprehensive type definitions in `backend/ai/types.py`
4. **Configuration:** Pydantic-based settings with validation
5. **Docker:** Multi-stage builds for production
6. **Testing:** Pytest with good coverage on critical paths

### 1.3 Critical Issues

#### 1.3.1 AI System Complexity
- **Problem:** Multiple overlapping orchestration patterns
  - `LangGraphMuseOrchestrator` (739 lines)
  - `LangGraphContextOrchestrator` (148 lines)
  - `LangGraphCampaignMovesOrchestrator` (277 lines)
  - `LangGraphOptionalOrchestrator` (115 lines)
  - Plus `AIClient` with strategy pattern
  - Plus legacy service shims

- **Impact:** Difficult to maintain, inconsistent behavior, hard to test
- **Root Cause:** Organic growth without architectural consolidation

#### 1.3.2 Inconsistent Error Handling
- Mixed exception types across layers
- No unified error response format
- Partial circuit breaker implementation

#### 1.3.3 Missing Production Patterns
- No distributed tracing
- Limited metrics beyond basic logging
- No rate limiting at API layer
- No request ID propagation

#### 1.3.4 Database Access Patterns
- Direct Supabase client usage scattered
- No repository pattern abstraction
- Connection pooling not unified

#### 1.3.5 Configuration Management
- Some env var access outside settings
- Feature flags not centralized
- No environment-specific overrides

---

## 2. Target Architecture Overview

### 2.1 Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FastAPI    │  │   Redis      │  │  Supabase    │      │
│  │   Adapters   │  │   Adapter    │  │  Adapter     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼────────────────┼────────────────┼────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Use Cases / Services                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │   │
│  │  │  Muse    │ │ Campaign │ │ Context  │             │   │
│  │  │ Service  │ │ Service  │ │ Service  │             │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘             │   │
│  └───────┼────────────┼────────────┼────────────────────┘   │
└──────────┼────────────┼────────────┼────────────────────────┘
           │            │            │
           ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              AI Orchestration Domain                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │   │
│  │  │  Agent   │ │  Token   │ │  Model   │             │   │
│  │  │Registry  │ │ Manager  │ │ Router   │             │   │
│  │  └──────────┘ └──────────┘ └──────────┘             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Core Principles

1. **Dependency Inversion:** Domain depends on abstractions, not concrete implementations
2. **Single Responsibility:** Each module has one reason to change
3. **Interface Segregation:** Small, focused ports and adapters
4. **Don't Repeat Yourself:** Unified patterns for common concerns
5. **Fail Fast:** Comprehensive validation at boundaries

### 2.3 Technology Stack (Evolved)

| Layer | Current | Target | Rationale |
|-------|---------|--------|-----------|
| Web Framework | FastAPI 0.104 | FastAPI 0.115+ | Latest features, security |
| AI Orchestration | LangGraph 0.2.60 | LangGraph 0.3+ | Better state management |
| HTTP Client | httpx 0.25 | httpx 0.27+ | Performance improvements |
| Validation | Pydantic 2.5 | Pydantic 2.9+ | Better performance |
| Testing | pytest | pytest + fixtures | Better test organization |
| Observability | structlog | OpenTelemetry + structlog | Distributed tracing |

---

## 3. Phase 1: Foundation & Clean Architecture

### 3.1 Project Structure Refactoring

#### 3.1.1 New Directory Structure

```
backend/
├── src/                           # Source code (src-layout)
│   ├── raptorflow/               # Main package
│   │   ├── __init__.py
│   │   ├── domain/               # Domain layer (inner hexagon)
│   │   │   ├── __init__.py
│   │   │   ├── ai/               # AI domain
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py     # Domain entities
│   │   │   │   ├── repositories.py # Repository interfaces (ports)
│   │   │   │   ├── services.py   # Domain services
│   │   │   │   └── value_objects.py
│   │   │   ├── workspace/
│   │   │   ├── campaign/
│   │   │   └── bcm/
│   │   │
│   │   ├── application/          # Application layer
│   │   │   ├── __init__.py
│   │   │   ├── ports/            # Input/output ports
│   │   │   │   ├── inbound/      # Use case interfaces
│   │   │   │   └── outbound/     # Repository interfaces
│   │   │   ├── services/         # Application services
│   │   │   └── use_cases/        # Specific use cases
│   │   │
│   │   ├── infrastructure/       # Infrastructure layer
│   │   │   ├── __init__.py
│   │   │   ├── adapters/         # Adapters for external systems
│   │   │   │   ├── persistence/  # Database adapters
│   │   │   │   ├── ai/           # AI provider adapters
│   │   │   │   ├── cache/        # Redis adapter
│   │   │   │   └── messaging/    # Event adapters
│   │   │   ├── config/           # Configuration
│   │   │   └── web/              # Web framework adapters
│   │   │
│   │   └── interfaces/           # Interface layer
│   │       ├── __init__.py
│   │       ├── api/              # REST API
│   │       ├── cli/              # Command line
│   │       └── events/           # Event handlers
│   │
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── e2e/                      # End-to-end tests
│   └── fixtures/                 # Test fixtures
│
├── pyproject.toml               # Modern Python packaging
├── requirements.txt             # Dependencies
└── docker-compose.yml           # Local development
```

#### 3.1.2 Migration Strategy

**Step 1: Create Parallel Structure (Week 1-2)**
- Create new `src/raptorflow/` directory
- Move code incrementally maintaining git history
- Keep old structure for reference during migration

**Step 2: Port-by-Port Migration (Week 3-6)**
For each domain:
1. Define domain models
2. Create repository interfaces (ports)
3. Implement adapters
4. Migrate services
5. Update API layer
6. Add tests

**Step 3: Deprecation (Week 7-8)**
- Add deprecation warnings to old code
- Update imports in consuming code
- Monitor for issues
- Remove old structure

### 3.2 Domain Layer Implementation

#### 3.2.1 AI Domain Models

```python
# src/raptorflow/domain/ai/models.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4


class ModelTier(Enum):
    """AI model capability tiers."""
    FAST = auto()      # Low latency, lower quality
    BALANCED = auto()  # Good balance
    PREMIUM = auto()   # Highest quality


class ExecutionStrategy(Enum):
    """AI execution strategies."""
    SINGLE = "single"      # One model, one pass
    ENSEMBLE = "ensemble"  # Multiple models, vote
    PIPELINE = "pipeline"  # Sequential processing


@dataclass(frozen=True)
class TokenBudget:
    """Immutable token budget for generation."""
    max_input: int
    max_output: int
    max_total: int
    
    def __post_init__(self):
        if self.max_total < self.max_input + self.max_output:
            raise ValueError("max_total must accommodate input + output")


@dataclass(frozen=True)
class GenerationConfig:
    """Immutable generation configuration."""
    temperature: float = 0.7
    top_p: float = 1.0
    top_k: int = 50
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")


@dataclass
class GenerationRequest:
    """Domain entity for generation requests."""
    id: UUID = field(default_factory=uuid4)
    workspace_id: str = ""
    user_id: str = "system"
    prompt: str = ""
    system_prompt: Optional[str] = None
    config: GenerationConfig = field(default_factory=GenerationConfig)
    budget: TokenBudget = field(default_factory=lambda: TokenBudget(4000, 1000, 8000))
    strategy: ExecutionStrategy = ExecutionStrategy.SINGLE
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.workspace_id:
            raise ValueError("workspace_id is required")
        if not self.prompt:
            raise ValueError("prompt is required")


@dataclass
class GenerationResult:
    """Domain entity for generation results."""
    request_id: UUID
    text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    provider: str = ""
    cost_usd: float = 0.0
    latency_ms: int = 0
    finish_reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
    
    @property
    def success(self) -> bool:
        return bool(self.text) and self.finish_reason != "error"


@dataclass
class ModelCapability:
    """Model capability specification."""
    name: str
    tier: ModelTier
    max_tokens: int
    supports_system_prompt: bool = True
    supports_functions: bool = False
    supports_vision: bool = False
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
```

#### 3.2.2 Repository Interfaces (Ports)

```python
# src/raptorflow/domain/ai/repositories.py

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .models import (
    GenerationRequest,
    GenerationResult,
    ModelCapability,
)


class GenerationRepository(ABC):
    """Repository for generation history and analytics."""
    
    @abstractmethod
    async def save_request(self, request: GenerationRequest) -> None:
        """Persist a generation request."""
        pass
    
    @abstractmethod
    async def save_result(self, result: GenerationResult) -> None:
        """Persist a generation result."""
        pass
    
    @abstractmethod
    async def get_by_workspace(
        self,
        workspace_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[GenerationResult]:
        """Get generation history for workspace."""
        pass
    
    @abstractmethod
    async def get_cost_by_period(
        self,
        workspace_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Get total cost for period."""
        pass


class ModelRepository(ABC):
    """Repository for model registry."""
    
    @abstractmethod
    async def get_available_models(self) -> List[ModelCapability]:
        """Get all available models."""
        pass
    
    @abstractmethod
    async def get_model(self, name: str) -> Optional[ModelCapability]:
        """Get specific model by name."""
        pass
    
    @abstractmethod
    async def get_by_tier(self, tier: ModelTier) -> List[ModelCapability]:
        """Get models by capability tier."""
        pass
```

### 3.3 Application Layer

#### 3.3.1 Use Case Pattern

```python
# src/raptorflow/application/use_cases/generate_content.py

from dataclasses import dataclass
from typing import Optional

from raptorflow.domain.ai.models import (
    GenerationRequest,
    GenerationResult,
    ExecutionStrategy,
)
from raptorflow.domain.ai.services import AIService
from raptorflow.application.ports.outbound import EventPublisher


@dataclass
class GenerateContentCommand:
    """Command for content generation."""
    workspace_id: str
    user_id: str
    prompt: str
    content_type: str = "general"
    tone: str = "professional"
    strategy: ExecutionStrategy = ExecutionStrategy.SINGLE


@dataclass
class GenerateContentResult:
    """Result of content generation."""
    success: bool
    content: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    error_message: str = ""


class GenerateContentUseCase:
    """Use case for generating content with AI."""
    
    def __init__(
        self,
        ai_service: AIService,
        event_publisher: EventPublisher,
    ):
        self._ai_service = ai_service
        self._event_publisher = event_publisher
    
    async def execute(
        self,
        command: GenerateContentCommand
    ) -> GenerateContentResult:
        """Execute the use case."""
        try:
            # Create domain request
            request = GenerationRequest(
                workspace_id=command.workspace_id,
                user_id=command.user_id,
                prompt=command.prompt,
                strategy=command.strategy,
                context={
                    "content_type": command.content_type,
                    "tone": command.tone,
                }
            )
            
            # Execute generation
            result = await self._ai_service.generate(request)
            
            # Publish event
            await self._event_publisher.publish(
                "content.generated",
                {
                    "workspace_id": command.workspace_id,
                    "tokens_used": result.total_tokens,
                    "cost_usd": result.cost_usd,
                }
            )
            
            return GenerateContentResult(
                success=result.success,
                content=result.text,
                tokens_used=result.total_tokens,
                cost_usd=result.cost_usd,
            )
            
        except Exception as e:
            return GenerateContentResult(
                success=False,
                error_message=str(e),
            )
```

### 3.4 Infrastructure Layer

#### 3.4.1 Database Adapters

```python
# src/raptorflow/infrastructure/adapters/persistence/supabase_generation_repo.py

from datetime import datetime
from typing import List
from uuid import UUID

from supabase import AsyncClient

from raptorflow.domain.ai.models import (
    GenerationRequest,
    GenerationResult,
)
from raptorflow.domain.ai.repositories import GenerationRepository


class SupabaseGenerationRepository(GenerationRepository):
    """Supabase implementation of generation repository."""
    
    def __init__(self, client: AsyncClient):
        self._client = client
    
    async def save_request(self, request: GenerationRequest) -> None:
        """Save generation request to Supabase."""
        await self._client.table("generation_requests").insert({
            "id": str(request.id),
            "workspace_id": request.workspace_id,
            "user_id": request.user_id,
            "prompt": request.prompt,
            "system_prompt": request.system_prompt,
            "config": request.config.__dict__,
            "strategy": request.strategy.value,
            "created_at": request.created_at.isoformat(),
        }).execute()
    
    async def save_result(self, result: GenerationResult) -> None:
        """Save generation result to Supabase."""
        await self._client.table("generation_results").insert({
            "request_id": str(result.request_id),
            "text": result.text,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "model": result.model,
            "provider": result.provider,
            "cost_usd": result.cost_usd,
            "latency_ms": result.latency_ms,
            "finish_reason": result.finish_reason,
            "created_at": result.created_at.isoformat(),
        }).execute()
    
    async def get_by_workspace(
        self,
        workspace_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[GenerationResult]:
        """Get generation history."""
        response = await self._client.table("generation_results")\
            .select("*")\
            .eq("workspace_id", workspace_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .offset(offset)\
            .execute()
        
        return [self._to_domain(r) for r in response.data]
    
    def _to_domain(self, data: dict) -> GenerationResult:
        """Convert database record to domain model."""
        return GenerationResult(
            request_id=UUID(data["request_id"]),
            text=data["text"],
            input_tokens=data["input_tokens"],
            output_tokens=data["output_tokens"],
            model=data["model"],
            provider=data["provider"],
            cost_usd=data["cost_usd"],
            latency_ms=data["latency_ms"],
            finish_reason=data["finish_reason"],
        )
```

---

## 4. Phase 2: AI System Unification

### 4.1 Current State Analysis

The AI system currently has:
- 4 separate LangGraph orchestrators
- Custom strategy pattern in `ai/orchestration/`
- Legacy service shims
- Direct Vertex AI integration

### 4.2 Unified AI Architecture

#### 4.2.1 Core Abstractions

```python
# src/raptorflow/domain/ai/executor.py

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

from .models import GenerationRequest, GenerationResult


class AIExecutor(ABC):
    """Abstract base for AI execution engines."""
    
    @abstractmethod
    async def execute(
        self,
        request: GenerationRequest
    ) -> GenerationResult:
        """Execute a single generation request."""
        pass
    
    @abstractmethod
    async def stream(
        self,
        request: GenerationRequest
    ) -> AsyncIterator[str]:
        """Stream generation tokens."""
        pass


class ExecutionPlanner(ABC):
    """Plans execution strategy for requests."""
    
    @abstractmethod
    async def plan(
        self,
        request: GenerationRequest
    ) -> AIExecutor:
        """Determine and return appropriate executor."""
        pass
```

#### 4.2.2 Unified Orchestrator

```python
# src/raptorflow/application/services/ai_orchestrator.py

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional

from raptorflow.domain.ai.models import (
    GenerationRequest,
    GenerationResult,
    ExecutionStrategy,
    ModelTier,
)
from raptorflow.domain.ai.executor import AIExecutor, ExecutionPlanner
from raptorflow.domain.ai.repositories import ModelRepository
from raptorflow.application.ports.outbound import (
    CachePort,
    MetricsPort,
)


@dataclass
class OrchestrationConfig:
    """Configuration for orchestration."""
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_cost_tracking: bool = True
    max_parallel_executions: int = 3
    fallback_enabled: bool = True


class UnifiedAIOrchestrator:
    """
    Unified AI orchestration service.
    
    Replaces multiple LangGraph orchestrators with a single,
    configurable orchestration layer.
    """
    
    def __init__(
        self,
        planner: ExecutionPlanner,
        model_repo: ModelRepository,
        cache: CachePort,
        metrics: MetricsPort,
        config: OrchestrationConfig,
    ):
        self._planner = planner
        self._model_repo = model_repo
        self._cache = cache
        self._metrics = metrics
        self._config = config
    
    async def generate(
        self,
        request: GenerationRequest
    ) -> GenerationResult:
        """
        Generate content using appropriate strategy.
        
        Handles caching, retries, fallbacks, and metrics.
        """
        # Check cache
        if self._config.enable_caching:
            cached = await self._get_cached(request)
            if cached:
                await self._metrics.increment("cache.hit")
                return cached
        
        # Plan execution
        executor = await self._planner.plan(request)
        
        # Execute with metrics
        start_time = asyncio.get_event_loop().time()
        
        try:
            result = await executor.execute(request)
            
            # Record metrics
            latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            await self._record_metrics(request, result, latency_ms)
            
            # Cache result
            if self._config.enable_caching:
                await self._cache_result(request, result)
            
            return result
            
        except Exception as e:
            await self._metrics.increment("generation.error", {
                "error_type": type(e).__name__,
            })
            
            if self._config.fallback_enabled:
                return await self._execute_fallback(request, e)
            
            raise
    
    async def _get_cached(
        self,
        request: GenerationRequest
    ) -> Optional[GenerationResult]:
        """Get cached result if available."""
        cache_key = self._generate_cache_key(request)
        cached = await self._cache.get(cache_key)
        return cached
    
    async def _cache_result(
        self,
        request: GenerationRequest,
        result: GenerationResult
    ) -> None:
        """Cache generation result."""
        if not result.success:
            return
        
        cache_key = self._generate_cache_key(request)
        await self._cache.set(
            cache_key,
            result,
            ttl=self._config.cache_ttl_seconds
        )
    
    def _generate_cache_key(self, request: GenerationRequest) -> str:
        """Generate cache key for request."""
        import hashlib
        import json
        
        key_data = {
            "prompt": request.prompt,
            "system_prompt": request.system_prompt,
            "temperature": request.config.temperature,
            "workspace_id": request.workspace_id,
        }
        
        key_hash = hashlib.sha256(
            json.dumps(key_data, sort_keys=True).encode()
        ).hexdigest()
        
        return f"ai:gen:{key_hash}"
    
    async def _record_metrics(
        self,
        request: GenerationRequest,
        result: GenerationResult,
        latency_ms: int
    ) -> None:
        """Record generation metrics."""
        await asyncio.gather(
            self._metrics.increment("generation.success"),
            self._metrics.histogram("generation.tokens", result.total_tokens),
            self._metrics.histogram("generation.cost", result.cost_usd),
            self._metrics.histogram("generation.latency", latency_ms),
        )
    
    async def _execute_fallback(
        self,
        request: GenerationRequest,
        original_error: Exception
    ) -> GenerationResult:
        """Execute fallback generation on failure."""
        # Fallback to deterministic/simple model
        fallback_request = GenerationRequest(
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            config=request.config,
            budget=request.budget,
            strategy=ExecutionStrategy.SINGLE,
            context={**request.context, "fallback": True},
        )
        
        executor = await self._planner.plan(fallback_request)
        result = await executor.execute(fallback_request)
        result.metadata["fallback"] = True
        result.metadata["original_error"] = str(original_error)
        
        return result
```

#### 4.2.3 LangGraph Integration (Simplified)

```python
# src/raptorflow/infrastructure/adapters/ai/langgraph_executor.py

from typing import AsyncIterator

from langgraph.graph import StateGraph, END

from raptorflow.domain.ai.executor import AIExecutor
from raptorflow.domain.ai.models import GenerationRequest, GenerationResult


class LangGraphExecutor(AIExecutor):
    """
    LangGraph-based executor for complex workflows.
    
    Simplified from multiple orchestrators to single configurable executor.
    """
    
    def __init__(self, model_client, config: dict):
        self._client = model_client
        self._config = config
        self._graph = self._build_graph()
    
    def _build_graph(self):
        """Build the execution graph."""
        from typing import TypedDict
        
        class GraphState(TypedDict):
            request: GenerationRequest
            result: GenerationResult
            step: str
        
        def init_node(state: GraphState):
            """Initialize generation."""
            return {"step": "initialized"}
        
        def generate_node(state: GraphState):
            """Execute generation."""
            # Actual generation logic
            request = state["request"]
            result = self._client.generate(request)
            return {
                "result": result,
                "step": "completed"
            }
        
        def validate_node(state: GraphState):
            """Validate result."""
            result = state["result"]
            if not result.success:
                return {"step": "failed"}
            return {"step": "validated"}
        
        # Build graph
        workflow = StateGraph(GraphState)
        
        workflow.add_node("init", init_node)
        workflow.add_node("generate", generate_node)
        workflow.add_node("validate", validate_node)
        
        workflow.set_entry_point("init")
        workflow.add_edge("init", "generate")
        workflow.add_edge("generate", "validate")
        workflow.add_conditional_edges(
            "validate",
            lambda s: "success" if s["step"] == "validated" else "retry",
            {"success": END, "retry": "generate"}
        )
        
        return workflow.compile()
    
    async def execute(self, request: GenerationRequest) -> GenerationResult:
        """Execute via LangGraph."""
        result = await self._graph.ainvoke({
            "request": request,
            "result": None,
            "step": "pending"
        })
        
        return result["result"]
    
    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Stream tokens."""
        # Streaming implementation
        async for token in self._client.stream(request.prompt):
            yield token
```

### 4.3 Token Management System

```python
# src/raptorflow/domain/ai/token_manager.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

from .models import TokenBudget, GenerationResult


@dataclass
class TokenUsage:
    """Token usage record."""
    workspace_id: str
    period_start: datetime
    period_end: datetime
    input_tokens: int
    output_tokens: int
    cost_usd: float


class TokenManager:
    """Manages token budgets and usage tracking."""
    
    def __init__(self, repository):
        self._repo = repository
        self._budgets: Dict[str, TokenBudget] = {}
    
    async def check_budget(
        self,
        workspace_id: str,
        requested_budget: TokenBudget
    ) -> bool:
        """Check if request fits within budget."""
        # Get current period usage
        period_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        period_end = period_start + timedelta(days=1)
        
        usage = await self._repo.get_usage(
            workspace_id,
            period_start,
            period_end
        )
        
        # Check against daily limit
        daily_limit = self._budgets.get(
            workspace_id,
            TokenBudget(100000, 25000, 125000)  # Default
        )
        
        projected_input = usage.input_tokens + requested_budget.max_input
        projected_output = usage.output_tokens + requested_budget.max_output
        
        return (
            projected_input <= daily_limit.max_input and
            projected_output <= daily_limit.max_output
        )
    
    async def record_usage(
        self,
        workspace_id: str,
        result: GenerationResult
    ) -> None:
        """Record token usage from result."""
        await self._repo.add_usage(
            workspace_id=workspace_id,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_usd=result.cost_usd,
        )
    
    def set_budget(self, workspace_id: str, budget: TokenBudget) -> None:
        """Set budget for workspace."""
        self._budgets[workspace_id] = budget
```

---

## 5. Phase 3: Production Infrastructure

### 5.1 Dependency Injection Container

```python
# src/raptorflow/infrastructure/config/container.py

from dependency_injector import containers, providers

from raptorflow.domain.ai.repositories import (
    GenerationRepository,
    ModelRepository,
)
from raptorflow.infrastructure.adapters.persistence import (
    SupabaseGenerationRepository,
    InMemoryModelRepository,
)
from raptorflow.infrastructure.adapters.cache import RedisCacheAdapter
from raptorflow.infrastructure.adapters.metrics import PrometheusMetricsAdapter
from raptorflow.application.services.ai_orchestrator import (
    UnifiedAIOrchestrator,
    OrchestrationConfig,
)


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""
    
    wiring_config = containers.WiringConfiguration(
        modules=[
            "raptorflow.interfaces.api.routes",
            "raptorflow.interfaces.api.dependencies",
        ]
    )
    
    # Configuration
    config = providers.Configuration()
    
    # Database
    supabase_client = providers.Singleton(
        # Supabase client initialization
    )
    
    # Repositories
    generation_repository = providers.Factory(
        SupabaseGenerationRepository,
        client=supabase_client,
    )
    
    model_repository = providers.Factory(
        InMemoryModelRepository,
    )
    
    # Adapters
    cache = providers.Factory(
        RedisCacheAdapter,
        url=config.redis.url,
    )
    
    metrics = providers.Factory(
        PrometheusMetricsAdapter,
        prefix="raptorflow",
    )
    
    # Services
    ai_orchestrator = providers.Factory(
        UnifiedAIOrchestrator,
        planner=providers.Dependency(),
        model_repo=model_repository,
        cache=cache,
        metrics=metrics,
        config=providers.Factory(
            OrchestrationConfig,
            enable_caching=config.ai.cache_enabled,
        ),
    )
```

### 5.2 FastAPI Integration

```python
# src/raptorflow/interfaces/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from raptorflow.infrastructure.config.container import Container
from raptorflow.interfaces.api.routes import router
from raptorflow.infrastructure.middleware import (
    RequestIDMiddleware,
    TimingMiddleware,
    ErrorHandlingMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    container = Container()
    container.init_resources()
    app.container = container
    
    yield
    
    # Shutdown
    container.shutdown_resources()


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="RaptorFlow API",
        version="2.0.0",
        lifespan=lifespan,
    )
    
    # Middleware (order matters)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routes
    app.include_router(router, prefix="/api/v2")
    
    return app
```

### 5.3 Middleware Implementation

```python
# src/raptorflow/infrastructure/middleware/request_id.py

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to all requests."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """Add request timing headers."""
    
    async def dispatch(self, request: Request, call_next):
        import time
        
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response
```

---

## 6. Phase 4: Observability & Optimization

### 6.1 Structured Logging

```python
# src/raptorflow/infrastructure/logging.py

import structlog
from pythonjsonlogger import jsonlogger


def configure_logging():
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

### 6.2 Metrics Collection

```python
# src/raptorflow/infrastructure/adapters/metrics/prometheus.py

from prometheus_client import Counter, Histogram, Gauge

from raptorflow.application.ports.outbound import MetricsPort


class PrometheusMetricsAdapter(MetricsPort):
    """Prometheus metrics implementation."""
    
    def __init__(self, prefix: str = "app"):
        self._prefix = prefix
        self._counters: dict = {}
        self._histograms: dict = {}
        self._gauges: dict = {}
    
    async def increment(self, name: str, labels: dict = None) -> None:
        """Increment counter."""
        full_name = f"{self._prefix}_{name}_total"
        
        if full_name not in self._counters:
            self._counters[full_name] = Counter(
                full_name,
                f"Counter for {name}",
                list(labels.keys()) if labels else []
            )
        
        counter = self._counters[full_name]
        if labels:
            counter.labels(**labels).inc()
        else:
            counter.inc()
    
    async def histogram(self, name: str, value: float, labels: dict = None) -> None:
        """Record histogram value."""
        full_name = f"{self._prefix}_{name}"
        
        if full_name not in self._histograms:
            self._histograms[full_name] = Histogram(
                full_name,
                f"Histogram for {name}",
                list(labels.keys()) if labels else []
            )
        
        histogram = self._histograms[full_name]
        if labels:
            histogram.labels(**labels).observe(value)
        else:
            histogram.observe(value)
```

### 6.3 Distributed Tracing

```python
# src/raptorflow/infrastructure/tracing.py

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_tracing(service_name: str = "raptorflow"):
    """Configure OpenTelemetry tracing."""
    provider = TracerProvider()
    
    # OTLP exporter
    otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317")
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)
    
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(service_name)
```

---

## 7. Implementation Roadmap

### Sprint 1-2: Foundation (Weeks 1-4)
- [ ] Set up new project structure
- [ ] Implement domain layer models
- [ ] Create repository interfaces
- [ ] Set up dependency injection
- [ ] Migrate configuration

### Sprint 3-4: AI Unification (Weeks 5-8)
- [ ] Implement unified orchestrator
- [ ] Create simplified LangGraph executor
- [ ] Implement token management
- [ ] Add caching layer
- [ ] Write comprehensive tests

### Sprint 5-6: API Migration (Weeks 9-12)
- [ ] Create new API routes
- [ ] Implement middleware
- [ ] Add error handling
- [ ] Set up validation
- [ ] API versioning strategy

### Sprint 7-8: Production Readiness (Weeks 13-16)
- [ ] Add observability (logging, metrics, tracing)
- [ ] Implement rate limiting
- [ ] Add circuit breakers
- [ ] Performance optimization
- [ ] Load testing

### Sprint 9-10: Testing & Documentation (Weeks 17-20)
- [ ] Unit test coverage >80%
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] API documentation
- [ ] Architecture documentation

### Sprint 11-12: Deployment (Weeks 21-24)
- [ ] Docker optimization
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline
- [ ] Monitoring setup
- [ ] Production rollout

---

## 8. Risk Assessment & Mitigation

### High Risks

1. **AI Behavior Changes**
   - Risk: Unified orchestrator behaves differently than current system
   - Mitigation: Comprehensive test suite, A/B testing, gradual rollout

2. **Performance Degradation**
   - Risk: New architecture slower than current
   - Mitigation: Benchmarks, profiling, optimization sprints

3. **Data Migration Issues**
   - Risk: Existing data incompatible with new models
   - Mitigation: Migration scripts, backward compatibility layer

### Medium Risks

4. **Team Learning Curve**
   - Risk: Team unfamiliar with hexagonal architecture
   - Mitigation: Training sessions, pair programming, documentation

5. **Integration Failures**
   - Risk: External service integrations break
   - Mitigation: Contract tests, integration test suite

### Low Risks

6. **Dependency Conflicts**
   - Risk: Package version conflicts
   - Mitigation: Virtual environments, lock files

---

## Appendix A: Database Schema Additions

```sql
-- Generation tracking
CREATE TABLE generation_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id TEXT NOT NULL,
    user_id TEXT NOT NULL DEFAULT 'system',
    prompt TEXT NOT NULL,
    system_prompt TEXT,
    config JSONB NOT NULL DEFAULT '{}',
    strategy TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE generation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES generation_requests(id),
    text TEXT,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    model TEXT NOT NULL,
    provider TEXT NOT NULL,
    cost_usd DECIMAL(10, 6) NOT NULL DEFAULT 0,
    latency_ms INTEGER NOT NULL,
    finish_reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_generation_workspace ON generation_results(request_id);
CREATE INDEX idx_generation_created ON generation_results(created_at);

-- Token budgets
CREATE TABLE workspace_budgets (
    workspace_id TEXT PRIMARY KEY,
    daily_input_limit INTEGER NOT NULL DEFAULT 100000,
    daily_output_limit INTEGER NOT NULL DEFAULT 25000,
    max_cost_per_day DECIMAL(10, 2) NOT NULL DEFAULT 10.00,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Appendix B: API Specification (OpenAPI)

```yaml
openapi: 3.0.0
info:
  title: RaptorFlow API v2
  version: 2.0.0

paths:
  /api/v2/muse/generate:
    post:
      summary: Generate content with AI
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - prompt
                - workspace_id
              properties:
                prompt:
                  type: string
                  minLength: 1
                content_type:
                  type: string
                  default: general
                strategy:
                  type: string
                  enum: [single, ensemble, pipeline]
                  default: single
      responses:
        200:
          description: Generated content
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  content:
                    type: string
                  tokens_used:
                    type: integer
                  cost_usd:
                    type: number
                    format: float
```

---

**Document End**

This modernization plan provides a comprehensive roadmap for transforming RaptorFlow into a production-grade AI system. The phased approach allows for incremental delivery while maintaining system stability.
