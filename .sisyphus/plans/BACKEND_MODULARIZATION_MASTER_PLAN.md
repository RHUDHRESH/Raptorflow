# Backend Modularization Master Plan
## Raptorflow Backend Architecture Transformation

**Status:** Planning Complete  
**Estimated Effort:** Large (5-7 days for full migration)  
**Architecture Pattern:** Hexagonal (Ports & Adapters) + Clean Architecture Principles  
**Approach:** Incremental, Slice-by-Slice Migration

---

## Executive Summary

This plan transforms Raptorflow's monolithic backend into a modular, domain-driven architecture using Hexagonal Architecture (Ports & Adapters) with Clean Architecture layering principles. The goal is clear domain boundaries, testability, and maintainability while avoiding "architecture tax" (excessive ceremony).

### Key Principles
- **Business logic lives in domain/application, never in routers**
- **External systems are behind ports; adapters are swappable**
- **Composition root is the only place where concrete meets abstract**
- **Prefer clarity over cleverness**
- **Feature-level coarse modules, not micro-modules per endpoint**

---

## Phase 1: Current State Analysis

### Current Backend Structure

```
backend/
├── main.py                    # Entry point (canonical)
├── app_factory.py            # FastAPI app creation
├── config/
│   ├── __init__.py
│   └── settings.py           # Pydantic settings (365 lines)
├── config.py                 # Additional config
├── core/
│   └── __init__.py           # Core utilities (currently empty?)
├── app/
│   ├── __init__.py
│   ├── middleware.py         # Session, CSRF, Timing middleware
│   ├── lifespan.py           # App lifecycle management
│   ├── compression.py        # Compression middleware
│   └── metrics.py            # Prometheus metrics
├── api/
│   ├── __init__.py
│   ├── system.py             # Health check, root endpoints
│   ├── registry.py           # Router registration (dynamic import)
│   ├── dependencies.py       # Shared dependencies
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py           # Auth dependencies (219 lines)
│   └── v1/
│       ├── auth/             # Auth routes
│       ├── workspaces/       # Workspace routes
│       ├── campaigns/        # Campaign routes
│       ├── moves/            # Move routes
│       ├── assets/           # Asset routes
│       ├── muse/             # Muse AI routes
│       ├── context/          # Context routes
│       ├── scraper/          # Scraper routes
│       ├── search/           # Search routes
│       ├── communications/   # Communications routes
│       ├── foundation/       # Foundation routes
│       ├── bcm_feedback/     # BCM feedback routes
│       ├── health/           # Health routes
│       └── workspace_guard/  # Workspace guard routes
├── services/
│   ├── __init__.py
│   ├── registry.py           # Service registry (84 lines, singleton pattern)
│   ├── base_service.py       # BaseService with circuit breaker (152 lines)
│   ├── exceptions.py         # Service exceptions
│   ├── muse_service.py       # Direct service (not following pattern)
│   ├── auth/                 # Auth services
│   │   ├── __init__.py
│   │   ├── factory.py        # Auth service factory
│   │   ├── supabase.py       # Supabase auth implementation
│   │   ├── demo.py           # Demo auth implementation
│   │   ├── disabled.py       # Disabled auth
│   │   ├── redis_rate_limiter.py
│   │   └── token_blacklist.py
│   ├── asset/                # Asset service
│   ├── campaign/             # Campaign service
│   ├── move/                 # Move service
│   ├── bcm/                  # BCM services
│   ├── cached_queries/       # Cached queries service
│   └── email/                # Email service
├── infrastructure/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── supabase.py       # Supabase client
│   │   ├── pool.py           # Connection pool
│   │   └── monitor.py        # DB monitoring
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── redis.py          # Redis client
│   │   ├── redis_sentinel.py # Redis Sentinel (HA)
│   │   └── decorator.py      # Cache decorators
│   ├── storage/
│   │   └── manager.py        # Storage manager
│   └── tasks/
│       └── async_tasks.py    # Background tasks
├── schemas/
│   ├── __init__.py
│   ├── asset.py
│   └── business_context.py
├── agents/
│   ├── __init__.py
│   ├── runtime/
│   ├── context/
│   ├── campaign_moves/
│   ├── muse/
│   └── optional/
├── ai/
│   ├── __init__.py
│   ├── client.py
│   ├── types.py
│   ├── prompts/
│   └── profiles/
├── bcm/
│   ├── __init__.py
│   ├── core/
│   ├── memory/
│   ├── reflection/
│   └── prompts/
├── templates/
├── tests/
├── fixtures/
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── Dockerfile
└── Dockerfile.production
```

### Current Issues Identified

1. **Mixed Responsibilities**: API routes mix HTTP handling with business logic
2. **Deep Coupling**: Services directly import infrastructure (database, cache)
3. **Inconsistent Patterns**: Some services follow BaseService pattern, others don't
4. **Scattered Configuration**: Config split between config/ and root config.py
5. **No Clear Domain Boundaries**: Business logic not clearly separated from adapters
6. **Import Web**: Complex import dependencies (api → services → infrastructure → config)
7. **God Files**: settings.py (365 lines), auth.py dependencies (219 lines)
8. **Missing Ports**: No interfaces/Protocols defining service contracts
9. **Testing Difficulties**: Hard to mock infrastructure dependencies

### Dependency Flow Issues

```
Current (messy):
  api/v1/campaigns/routes.py 
    → services/campaign/service.py
      → infrastructure/database/supabase.py
        → config/settings.py

  api/v1/auth/routes.py
    → services/auth/factory.py
      → services/auth/supabase.py OR demo.py
        → infrastructure/cache/redis_sentinel.py
          → config/settings.py

  (Testing nightmare: Can't mock Supabase without monkey-patching)
```

---

## Phase 2: Target Architecture

### Architectural Pattern: Hexagonal + Clean Hybrid

**Why this pattern?**
- Clear boundaries between business logic and infrastructure
- Framework-agnostic domain layer (can swap FastAPI/SQLAlchemy/Redis easily)
- Testability: mock ports instead of monkey-patching
- Scales with complexity without "enterprise architecture tax"

**Layer Definitions:**

| Layer | Responsibility | Dependencies | Example |
|-------|---------------|--------------|---------|
| **Domain** | Pure business logic, entities, policies | None (stdlib only) | User entity, validation rules |
| **Application** | Use cases, orchestration, ports | Domain only | CreateCampaignUseCase, UserRepo (Protocol) |
| **Adapters** | Implement ports, external integrations | Application + vendor libs | SupabaseUserRepo, RedisCache |
| **API** | HTTP handling, serialization | Application only | FastAPI routers, Pydantic schemas |
| **Bootstrap** | Wiring, composition root | Everything | App factory, dependency providers |

### Target Directory Structure

```
backend/
├── main.py                          # Entry point (minimal)
├── bootstrap/                       # Composition root
│   ├── __init__.py
│   ├── container.py                 # DI container/providers
│   ├── dependencies.py              # FastAPI Depends providers
│   └── wiring.py                    # Adapter instantiation
│
├── core/                            # Cross-cutting (NOT a dumping ground)
│   ├── __init__.py
│   ├── config.py                    # Unified configuration (moved from config/)
│   ├── logging.py                   # Logging configuration
│   ├── exceptions.py                # Shared exceptions
│   ├── security.py                  # Security utilities (hasher, JWT utils)
│   └── types.py                     # Shared type aliases
│
├── api/                             # HTTP layer (FastAPI specific)
│   ├── __init__.py
│   ├── router.py                    # Unified router registration
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── system.py                # Health, readiness
│   │   ├── dependencies.py          # API-level dependencies
│   │   └── campaigns/               # Campaign feature API
│   │       ├── router.py
│   │       ├── schemas.py           # Pydantic request/response
│   │       └── dependencies.py      # Feature-specific deps
│   │   └── [other features]/
│   └── deps.py                      # Re-export from bootstrap
│
├── features/                        # Domain modules (vertical slices)
│   └── campaign/                    # Campaign domain
│       ├── __init__.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities.py          # Campaign, Move entities (pure Python)
│       │   ├── value_objects.py     # CampaignStatus, MoveType
│       │   └── policies.py          # Business rules (pure functions)
│       ├── application/
│       │   ├── __init__.py
│       │   ├── ports.py             # Protocols: CampaignRepo, MoveRepo
│       │   ├── services.py          # Application services (use cases)
│       │   └── dto.py               # Data transfer objects
│       └── adapters/
│           ├── __init__.py
│           ├── supabase_repo.py     # Implements CampaignRepo
│           └── cache_repo.py        # CachedCampaignRepo (decorator)
│   └── auth/
│       ├── domain/
│       │   ├── entities.py          # User, Session
│       │   └── policies.py          # Auth policies
│       ├── application/
│       │   ├── ports.py             # AuthService, TokenService
│       │   └── services.py          # LoginUseCase, RegisterUseCase
│       └── adapters/
│           ├── supabase_auth.py
│           ├── demo_auth.py
│           └── jwt_service.py
│   └── [other features]/            # Same pattern for each
│       ├── domain/
│       ├── application/
│       └── adapters/
│
├── infrastructure/                  # Shared infrastructure (optional adapters)
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py            # Connection management
│   │   └── transaction.py           # Transaction context
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── redis_client.py          # Redis client factory
│   │   └── sentinel.py              # Redis Sentinel
│   └── storage/
│       └── client.py
│
├── middleware/                      # HTTP middleware (FastAPI specific)
│   ├── __init__.py
│   ├── auth.py                      # Auth middleware
│   ├── session.py                   # Session middleware
│   ├── csrf.py                      # CSRF protection
│   ├── timing.py                    # Request timing
│   └── cors.py                      # CORS config
│
├── app/                             # App lifecycle (minimal)
│   ├── __init__.py
│   ├── lifespan.py                  # Startup/shutdown events
│   └── compression.py               # Compression middleware
│
├── schemas/                         # Shared schemas (optional)
│   └── __init__.py
│
├── agents/                          # AI agents (keep as-is initially)
├── ai/                              # AI client/profiles
├── bcm/                             # BCM system (keep as-is)
├── tests/                           # Test structure mirrors src
│   ├── unit/
│   │   ├── features/
│   │   │   └── campaign/            # Tests for campaign domain
│   │   └── core/
│   ├── integration/
│   │   ├── adapters/                # Test real adapters
│   │   └── api/                     # API integration tests
│   └── e2e/
│
└── [config files, Docker, etc.]
```

### Dependency Rules (ENFORCED)

```
Allowed Dependencies:
  domain           ← nothing (pure Python)
  application      ← domain only
  adapters         ← application + infrastructure
  api              ← application + core
  bootstrap        ← everything (composition root)
  core             ← nothing (stdlib only)

Forbidden (CI will block):
  domain           → application, adapters, api, infrastructure
  application      → adapters, api, infrastructure
  adapters         → api
  api              → adapters, infrastructure (except through ports)
```

### Feature Module Template

Each feature follows this exact structure:

```python
# features/campaign/domain/entities.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Campaign:
    id: str
    workspace_id: str
    name: str
    status: str
    created_at: datetime
    
    def activate(self) -> None:
        """Pure business logic - no infrastructure."""
        if self.status == "archived":
            raise ValueError("Cannot activate archived campaign")
        self.status = "active"

# features/campaign/application/ports.py
from typing import Protocol, Optional
from features.campaign.domain.entities import Campaign

class CampaignRepository(Protocol):
    """Port - implemented by adapters."""
    async def get_by_id(self, campaign_id: str) -> Optional[Campaign]: ...
    async def save(self, campaign: Campaign) -> None: ...
    async def list_by_workspace(self, workspace_id: str) -> list[Campaign]: ...

# features/campaign/application/services.py
from features.campaign.domain.entities import Campaign
from features.campaign.application.ports import CampaignRepository

class CreateCampaignUseCase:
    def __init__(self, repo: CampaignRepository):
        self._repo = repo
    
    async def execute(self, workspace_id: str, name: str) -> Campaign:
        campaign = Campaign(
            id=generate_id(),
            workspace_id=workspace_id,
            name=name,
            status="draft",
            created_at=utc_now()
        )
        await self._repo.save(campaign)
        return campaign

# features/campaign/adapters/supabase_repo.py
from features.campaign.application.ports import CampaignRepository
from features.campaign.domain.entities import Campaign
from infrastructure.database.connection import get_supabase_client

class SupabaseCampaignRepository(CampaignRepository):
    """Adapter - implements the port."""
    
    def __init__(self, client):
        self._client = client
    
    async def get_by_id(self, campaign_id: str) -> Optional[Campaign]:
        response = self._client.table("campaigns").select("*").eq("id", campaign_id).execute()
        if not response.data:
            return None
        return Campaign(**response.data[0])
    
    async def save(self, campaign: Campaign) -> None:
        data = {
            "id": campaign.id,
            "workspace_id": campaign.workspace_id,
            "name": campaign.name,
            "status": campaign.status,
            "created_at": campaign.created_at.isoformat()
        }
        self._client.table("campaigns").upsert(data).execute()

# features/campaign/adapters/cache_repo.py
from features.campaign.application.ports import CampaignRepository
from infrastructure.cache.redis_client import get_redis

class CachedCampaignRepository(CampaignRepository):
    """Decorator pattern - adds caching."""
    
    def __init__(self, inner: CampaignRepository, cache, ttl: int = 300):
        self._inner = inner
        self._cache = cache
        self._ttl = ttl
    
    async def get_by_id(self, campaign_id: str) -> Optional[Campaign]:
        # Try cache first
        cached = await self._cache.get(f"campaign:{campaign_id}")
        if cached:
            return Campaign(**cached)
        
        # Fall through to inner repo
        campaign = await self._inner.get_by_id(campaign_id)
        if campaign:
            await self._cache.setex(f"campaign:{campaign_id}", self._ttl, campaign.__dict__)
        return campaign
    
    async def save(self, campaign: Campaign) -> None:
        await self._inner.save(campaign)
        await self._cache.delete(f"campaign:{campaign.id}")

# api/v1/campaigns/router.py
from fastapi import APIRouter, Depends
from bootstrap.dependencies import get_create_campaign_usecase
from features.campaign.application.services import CreateCampaignUseCase

router = APIRouter()

@router.post("/campaigns")
async def create_campaign(
    request: CreateCampaignRequest,
    usecase: CreateCampaignUseCase = Depends(get_create_campaign_usecase)
):
    """API layer - just HTTP handling, no business logic."""
    campaign = await usecase.execute(
        workspace_id=request.workspace_id,
        name=request.name
    )
    return CampaignResponse.from_domain(campaign)
```

---

## Phase 3: Migration Strategy

### Approach: Incremental, Slice-by-Slice

**Why incremental?**
- Zero downtime migration
- Maintain existing functionality
- Test each slice thoroughly
- Rollback capability per slice
- Team can learn pattern gradually

### Migration Phases

#### Phase 0: Preparation (Day 1)

**Goals:**
- Stabilize current codebase
- Add safety nets
- Set up enforcement tools

**Tasks:**

1. **Add Characterization Tests**
   ```python
   # tests/characterization/test_campaign_api.py
   # Record current behavior BEFORE changes
   
   async def test_create_campaign_returns_201():
       response = await client.post("/api/v1/campaigns", json={...})
       assert response.status_code == 201
       assert "id" in response.json()
       # Save response shape for regression testing
   ```

2. **Set Up Import Linting**
   ```bash
   # Add to requirements-dev.txt
   import-linter
   
   # .importlinter configuration
   [importlinter]
   root_package = backend
   
   [importlinter:contract:domain-isolation]
   name = Domain layer is isolated
   type = forbidden
   source_modules =
       backend.features.*.domain
   forbidden_modules =
       backend.infrastructure
       backend.api
       fastapi
       sqlalchemy
       redis
   ```

3. **Create Bootstrap Structure**
   ```
   mkdir -p backend/bootstrap
   mkdir -p backend/features
   mkdir -p backend/middleware
   ```

4. **Move Core Config**
   ```bash
   # Merge config/settings.py and config.py into core/config.py
   mv backend/config/settings.py backend/core/config.py
   rm -rf backend/config/
   ```

#### Phase 1: Scaffold First Feature (Day 1-2)

**Feature:** Campaign (medium complexity, well-understood)

**Step-by-Step:**

1. **Create Feature Structure**
   ```bash
   mkdir -p backend/features/campaign/{domain,application,adapters}
   touch backend/features/campaign/__init__.py
   touch backend/features/campaign/domain/__init__.py
   touch backend/features/campaign/application/__init__.py
   touch backend/features/campaign/adapters/__init__.py
   ```

2. **Extract Domain Entities**
   ```python
   # backend/features/campaign/domain/entities.py
   # Copy logic from services/campaign/service.py
   # Remove all infrastructure dependencies
   # Make pure Python dataclasses
   ```

3. **Define Ports**
   ```python
   # backend/features/campaign/application/ports.py
   # Extract interfaces from service methods
   # Use typing.Protocol (not ABC)
   ```

4. **Create Application Service**
   ```python
   # backend/features/campaign/application/services.py
   # Move business logic from services/campaign/service.py
   # Inject ports via constructor
   ```

5. **Implement Adapter**
   ```python
   # backend/features/campaign/adapters/supabase_repo.py
   # Wrap existing Supabase calls
   # Implement port interface
   ```

6. **Create API Router**
   ```python
   # backend/api/v1/campaigns/router.py
   # Move routes from api/v1/campaigns/routes.py
   # Use FastAPI Depends for injection
   ```

7. **Set Up Bootstrap**
   ```python
   # backend/bootstrap/dependencies.py
   # Create provider functions for DI
   
   from features.campaign.adapters.supabase_repo import SupabaseCampaignRepository
   from features.campaign.application.services import CreateCampaignUseCase
   from infrastructure.database.connection import get_db_client
   
   def get_campaign_repository():
       return SupabaseCampaignRepository(get_db_client())
   
   def get_create_campaign_usecase():
       return CreateCampaignUseCase(get_campaign_repository())
   ```

8. **Add Compatibility Layer**
   ```python
   # backend/services/campaign/service.py
   # Keep file, re-export from new structure
   # Mark as deprecated
   
   from backend.features.campaign.application.services import CreateCampaignUseCase
   from backend.bootstrap.dependencies import get_create_campaign_usecase
   
   class CampaignService:
       """DEPRECATED: Use features.campaign directly."""
       async def create(self, ...):
           usecase = get_create_campaign_usecase()
           return await usecase.execute(...)
   ```

9. **Test Migration**
   ```bash
   # Run characterization tests
   pytest tests/characterization/ -v
   
   # Run unit tests for new structure
   pytest tests/unit/features/campaign/ -v
   
   # Run integration tests
   pytest tests/integration/adapters/ -v
   ```

#### Phase 2: Migrate Remaining Features (Days 2-4)

**Order (by complexity/risk):**

1. **Auth** (high complexity, critical)
   - Move auth logic from services/auth/ to features/auth/
   - Keep factory pattern for demo/supabase switching
   - Move token_blacklist to adapter

2. **Workspace** (medium complexity)
   - Extract workspace domain
   - Move workspace guards to application policies

3. **Asset** (low complexity)
   - Good candidate for learning
   - Storage adapter pattern

4. **Move** (medium complexity)
   - Related to campaigns

5. **Foundation** (low complexity)
   - Simple CRUD operations

6. **Communications** (medium complexity)
   - Email adapter

7. **Muse/AI** (high complexity, defer if needed)
   - May keep as-is initially
   - Create adapter facade

8. **Scraper/Search** (optional modules)
   - Already have ENABLE_* flags
   - Easy to isolate

**Per-Feature Checklist:**
- [ ] Domain entities extracted (pure Python)
- [ ] Ports defined (Protocols)
- [ ] Application services created (business logic)
- [ ] Adapter implemented (infrastructure)
- [ ] API router moved (HTTP handling)
- [ ] Bootstrap dependencies wired
- [ ] Characterization tests pass
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Old code marked deprecated
- [ ] Documentation updated

#### Phase 3: Migrate Cross-Cutting (Day 4-5)

**Middleware Migration:**
```python
# middleware/auth.py → keep as-is but use bootstrap deps
# middleware/session.py → move to features/auth/adapters/
# middleware/csrf.py → keep in middleware/
# middleware/timing.py → keep in middleware/
```

**Infrastructure Cleanup:**
```python
# infrastructure/database/supabase.py
# Keep as low-level client
# Adapters wrap these, don't replace

# infrastructure/cache/redis_sentinel.py
# Keep for Redis HA
# Create CachePort in features
```

**Config Consolidation:**
```python
# core/config.py - single source of truth
# Remove all other config files
# Use Pydantic Settings
```

#### Phase 4: Cleanup & Enforcement (Day 5-6)

1. **Remove Deprecated Code**
   ```bash
   # Remove services/ directory once all features migrated
   # Remove api/v1/*/__init__.py that just re-export
   # Clean up old imports
   ```

2. **Enforce Import Rules**
   ```bash
   # Add to CI
   lint-imports
   
   # Add to pre-commit
   - repo: local
     hooks:
     - id: import-linter
       name: import-linter
       entry: lint-imports
       language: system
       pass_filenames: false
   ```

3. **Add Architecture Tests**
   ```python
   # tests/architecture/test_layer_dependencies.py
   import importlinter
   
   def test_domain_does_not_import_infrastructure():
       """Domain layer must be pure."""
       # Use import-linter API or custom check
       pass
   ```

4. **Update Documentation**
   - README with new structure
   - ADR for architecture decision
   - Developer onboarding guide

---

## Phase 4: Testing Strategy

### Test Pyramid

```
    /\
   /  \  E2E (few) - Critical user flows
  /----\ 
 /      \ Integration (some) - Adapter tests with real DB/cache
/--------\
---------- Unit (many) - Domain, application, pure functions
```

### Test Types

#### 1. Characterization Tests (Preserve Behavior)
```python
# tests/characterization/test_campaign_api.py
# Record API behavior BEFORE refactoring
# Run continuously to catch regressions

class TestCampaignAPIBehavior:
    """Preserve existing API contract during refactoring."""
    
    async def test_create_campaign_structure(self, client):
        """Response structure must not change."""
        response = await client.post("/api/v1/campaigns", json={
            "workspace_id": "ws-123",
            "name": "Test Campaign"
        })
        
        data = response.json()
        assert "id" in data
        assert "workspace_id" in data
        assert "name" in data
        assert "status" in data
        assert "created_at" in data
        # Store as golden file for regression
```

#### 2. Unit Tests (Fast, Isolated)
```python
# tests/unit/features/campaign/domain/test_entities.py
class TestCampaign:
    def test_activate_changes_status(self):
        campaign = Campaign(
            id="1", workspace_id="ws", name="Test",
            status="draft", created_at=utc_now()
        )
        campaign.activate()
        assert campaign.status == "active"
    
    def test_activate_archived_raises(self):
        campaign = Campaign(
            id="1", workspace_id="ws", name="Test",
            status="archived", created_at=utc_now()
        )
        with pytest.raises(ValueError):
            campaign.activate()

# tests/unit/features/campaign/application/test_services.py
class TestCreateCampaignUseCase:
    async def test_creates_campaign_with_draft_status(self):
        mock_repo = Mock(spec=CampaignRepository)
        usecase = CreateCampaignUseCase(mock_repo)
        
        result = await usecase.execute("ws-123", "New Campaign")
        
        assert result.workspace_id == "ws-123"
        assert result.name == "New Campaign"
        assert result.status == "draft"
        mock_repo.save.assert_called_once_with(result)
```

#### 3. Integration Tests (Real Adapters)
```python
# tests/integration/adapters/test_supabase_campaign_repo.py
@pytest.mark.integration
class TestSupabaseCampaignRepository:
    async def test_round_trip(self, supabase_client):
        repo = SupabaseCampaignRepository(supabase_client)
        
        campaign = Campaign(
            id="test-123", workspace_id="ws-123",
            name="Integration Test", status="draft",
            created_at=utc_now()
        )
        
        await repo.save(campaign)
        retrieved = await repo.get_by_id("test-123")
        
        assert retrieved.name == "Integration Test"
        
        # Cleanup
        await repo.delete("test-123")
```

#### 4. Contract Tests (API Stability)
```python
# tests/contract/test_campaign_api_contract.py
class TestCampaignAPIContract:
    """Ensure API contract stability."""
    
    def test_openapi_schema_unchanged(self, client):
        """Detect breaking API changes."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Compare with stored golden schema
        golden = load_golden("campaign_api_schema.json")
        assert schema == golden, "API schema changed! Breaking change?"
```

### Test Infrastructure

```python
# tests/conftest.py

@pytest.fixture
def mock_campaign_repo():
    """Mock repository for unit tests."""
    return Mock(spec=CampaignRepository)

@pytest.fixture
async def real_supabase_repo():
    """Real repository for integration tests."""
    client = get_test_supabase_client()
    repo = SupabaseCampaignRepository(client)
    yield repo
    # Cleanup test data

@pytest.fixture
def characterisation_client():
    """Client for characterization tests."""
    # Use real app, not test app
    from backend.main import app
    return TestClient(app)
```

---

## Phase 5: Enforcement & Tooling

### Import Linting Configuration

```ini
# .importlinter
[importlinter]
root_package = backend
include_external_packages = true

[importlinter:contract:domain-isolation]
name = Domain layer must not depend on infrastructure
 type = forbidden
source_modules =
    backend.features.*.domain
forbidden_modules =
    backend.infrastructure
    backend.api
    fastapi
    sqlalchemy
    redis
    httpx
    pydantic

[importlinter:contract:application-isolation]
name = Application layer must not depend on adapters
 type = forbidden
source_modules =
    backend.features.*.application
forbidden_modules =
    backend.features.*.adapters
    backend.infrastructure
    sqlalchemy
    redis

[importlinter:contract:api-isolation]
name = API layer must not depend on adapters directly
 type = forbidden
source_modules =
    backend.api
forbidden_modules =
    backend.features.*.adapters
    backend.infrastructure.database
    backend.infrastructure.cache

[importlinter:contract:dependency-direction]
name = Dependencies must flow inward
 type = layers
layers =
    bootstrap
    api
    adapters
    application
    domain
containers =
    backend.features.*
```

### CI/CD Integration

```yaml
# .github/workflows/architecture.yml
name: Architecture Compliance

on: [push, pull_request]

jobs:
  architecture:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install import-linter
      
      - name: Check architecture compliance
        run: lint-imports
      
      - name: Run architecture tests
        run: pytest tests/architecture/ -v
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: import-linter
        name: Check architecture compliance
        entry: lint-imports
        language: system
        pass_filenames: false
        files: ^backend/
      
      - id: architecture-tests
        name: Run architecture tests
        entry: pytest tests/architecture/ -v
        language: system
        pass_filenames: false
        files: ^backend/
```

---

## Phase 6: Feature-Specific Migration Details

### Feature: Auth (Priority: HIGH, Complexity: HIGH)

**Current State:**
- services/auth/factory.py - Creates auth service
- services/auth/supabase.py - Supabase implementation
- services/auth/demo.py - Demo implementation
- services/auth/token_blacklist.py - Token management
- api/dependencies/auth.py - Auth dependencies

**Target Structure:**
```
features/auth/
├── domain/
│   ├── entities.py          # User, Session, Token
│   └── policies.py          # Auth policies, password rules
├── application/
│   ├── ports.py             # AuthService, TokenService, UserRepo
│   ├── services.py          # LoginUseCase, RegisterUseCase, LogoutUseCase
│   └── dto.py               # LoginRequest, TokenResponse
└── adapters/
    ├── supabase_auth.py     # SupabaseAuthService
    ├── demo_auth.py         # DemoAuthService
    ├── jwt_service.py       # JWTTokenService
    └── redis_token_blacklist.py
```

**Key Decisions:**
- Keep factory pattern for auth mode switching
- TokenBlacklist becomes TokenService adapter
- Move session management to domain (not infrastructure)
- HTTP-only cookie logic stays in API layer

### Feature: Campaign (Priority: MEDIUM, Complexity: MEDIUM)

**Current State:**
- services/campaign/service.py - Campaign operations
- api/v1/campaigns/routes.py - CRUD endpoints

**Target Structure:**
```
features/campaign/
├── domain/
│   ├── entities.py          # Campaign
│   └── policies.py          # Campaign lifecycle rules
├── application/
│   ├── ports.py             # CampaignRepository
│   ├── services.py          # CreateCampaign, UpdateCampaign, etc.
│   └── dto.py               # CampaignCreate, CampaignUpdate
└── adapters/
    └── supabase_repo.py
```

**Key Decisions:**
- Simple CRUD, good learning example
- No complex business logic
- Straightforward port-adapter pattern

### Feature: Asset (Priority: MEDIUM, Complexity: LOW)

**Current State:**
- services/asset/service.py
- Uses GCS/Supabase storage

**Target Structure:**
```
features/asset/
├── domain/
│   └── entities.py          # Asset, AssetType
├── application/
│   ├── ports.py             # AssetRepository, StorageService
│   └── services.py          # UploadAsset, DeleteAsset
└── adapters/
    ├── supabase_repo.py
    └── gcs_storage.py       # Implements StorageService
```

### Feature: Muse/AI (Priority: LOW, Complexity: HIGH)

**Recommendation:** DEFER

**Rationale:**
- Complex orchestration with LangGraph
- Agents are already somewhat modular
- High risk of breaking AI flows
- Can create adapter facade later

**Interim Solution:**
```python
# features/muse/adapters/muse_facade.py
# Wrap existing muse_service.py without changing it

class MuseServiceAdapter:
    """Adapter that wraps existing Muse service."""
    def __init__(self, inner_service):
        self._inner = inner_service
    
    async def generate(self, request: MuseRequest) -> MuseResponse:
        # Delegate to existing service
        return await self._inner.generate(request)
```

---

## Phase 7: Risk Mitigation

### Risk: Breaking Changes

**Mitigation:**
- Characterization tests for each endpoint
- Gradual migration (compatibility layers)
- Feature flags for new implementation
- Staged rollout (dev → staging → prod)

### Risk: Performance Regression

**Mitigation:**
- Benchmark before/after
- Keep caching at adapter level
- Profile database queries
- Load test critical paths

### Risk: Team Learning Curve

**Mitigation:**
- Start with simple features (Asset, Foundation)
- Pair programming for complex features
- Document patterns with examples
- Code review checklist

### Risk: Over-Engineering

**Mitigation:**
- Keep it simple: Protocols over ABCs
- Don't create interfaces "just in case"
- Review: "Does this add value or just complexity?"
- YAGNI principle: add abstraction only when needed

---

## Phase 8: Success Criteria

### Completion Checklist

- [ ] All features migrated to new structure
- [ ] Old services/ directory removed
- [ ] Import linting passes in CI
- [ ] Characterization tests all pass
- [ ] Unit test coverage > 80% for domain/application
- [ ] Integration tests for all adapters
- [ ] Documentation updated
- [ ] Team trained on new patterns
- [ ] Performance benchmarks meet targets
- [ ] Zero critical bugs in production

### Quality Metrics

| Metric | Before | Target After |
|--------|--------|--------------|
| Test Coverage | ?% | >80% |
| Import cycle count | ? | 0 |
| Domain file dependencies | Mixed | 0 (stdlib only) |
| Average file length | 200+ lines | <100 lines |
| Time to add new feature | ? | 50% reduction |
| Test execution time | ? | <30 seconds unit |

---

## Appendix A: Code Examples

### Before (Monolithic)

```python
# api/v1/campaigns/routes.py
@router.post("/campaigns")
async def create_campaign(
    request: CreateCampaignRequest,
    user: dict = Depends(get_current_user)
):
    # Business logic in router!
    if not user.get("workspace_id"):
        raise HTTPException(400, "No workspace")
    
    # Direct database access!
    supabase = get_supabase_client()
    response = supabase.table("campaigns").insert({
        "id": generate_uuid(),
        "workspace_id": user["workspace_id"],
        "name": request.name,
        "status": "draft"
    }).execute()
    
    # Direct cache access!
    redis = get_redis()
    await redis.delete(f"workspace:{user['workspace_id']}:campaigns")
    
    return response.data[0]
```

### After (Modular)

```python
# api/v1/campaigns/router.py
@router.post("/campaigns")
async def create_campaign(
    request: CreateCampaignRequest,
    usecase: CreateCampaignUseCase = Depends(get_create_campaign_usecase)
):
    """HTTP handling only - no business logic."""
    campaign = await usecase.execute(
        workspace_id=request.workspace_id,
        name=request.name
    )
    return CampaignResponse.from_domain(campaign)

# features/campaign/application/services.py
class CreateCampaignUseCase:
    def __init__(
        self,
        repo: CampaignRepository,
        cache: CacheService
    ):
        self._repo = repo
        self._cache = cache
    
    async def execute(self, workspace_id: str, name: str) -> Campaign:
        """Business logic here - no FastAPI/HTTP."""
        campaign = Campaign.create(
            workspace_id=workspace_id,
            name=name
        )
        await self._repo.save(campaign)
        await self._cache.invalidate_workspace_campaigns(workspace_id)
        return campaign

# features/campaign/adapters/supabase_repo.py
class SupabaseCampaignRepository:
    def __init__(self, client):
        self._client = client
    
    async def save(self, campaign: Campaign) -> None:
        """Infrastructure concerns isolated."""
        self._client.table("campaigns").insert(campaign.to_dict()).execute()
```

---

## Appendix B: Migration Order

### Week 1

| Day | Feature | Complexity | Risk |
|-----|---------|------------|------|
| Mon | Setup, Characterization tests | Low | Low |
| Tue | Asset | Low | Low |
| Wed | Foundation | Low | Low |
| Thu | Campaign | Medium | Medium |
| Fri | Review, fix issues | - | - |

### Week 2

| Day | Feature | Complexity | Risk |
|-----|---------|------------|------|
| Mon | Workspace | Medium | Medium |
| Tue | Move | Medium | Medium |
| Wed | Auth | High | High |
| Thu | Communications | Medium | Medium |
| Fri | Cleanup, testing | - | - |

### Week 3 (Buffer)

- Muse/AI (if needed)
- Documentation
- Performance tuning
- Team training

---

## Appendix C: FAQ

**Q: Why not use a DI framework like dependency-injector?**
A: FastAPI's Depends is sufficient for most cases. Add a container only if you have many services with complex lifecycles.

**Q: Should we use ABC or Protocol for ports?**
A: Protocol is preferred (better ergonomics, no inheritance). Use ABC only for runtime enforcement needs.

**Q: What about the existing tests?**
A: Keep them as characterization tests. Add new tests in the new structure. Remove old tests once migration complete.

**Q: Can we migrate multiple features in parallel?**
A: Yes, but recommend sequential for first 2-3 to establish patterns. Then parallelize.

**Q: What if we find circular dependencies?**
A: Refactor to use events/dependency inversion. Move shared types to core/types.py.

**Q: How do we handle database migrations?**
A: Keep existing migration system. Domain entities should match DB schema (or use mapper).

---

## Conclusion

This plan provides a pragmatic path from monolithic to modular architecture using Hexagonal/Clean Architecture principles. The incremental approach minimizes risk while the enforcement tools (import-linter, architecture tests) ensure long-term maintainability.

**Key Takeaways:**
1. **Start small**: Asset or Foundation first
2. **Test first**: Characterization tests prevent regressions
3. **Enforce boundaries**: Import rules prevent backsliding
4. **Pragmatic over perfect**: Don't over-engineer
5. **Team alignment**: Ensure everyone understands the patterns

**Next Steps:**
1. Review this plan with the team
2. Set up tooling (import-linter, characterization tests)
3. Begin Phase 0: Preparation
4. Start with Asset feature as proof of concept

---

**Plan Version:** 1.0  
**Last Updated:** 2026-02-15  
**Author:** Prometheus (Planning Agent)  
**Reviewers:** Team leads, architects

