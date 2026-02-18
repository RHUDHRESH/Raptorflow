# Backend Modularization Fix Plan

## Executive Summary

The backend modularization has **critical runtime issues** that will cause production failures. While the architecture is sound, the implementation has compatibility gaps that break existing code paths.

**Total Issues Found: 15**
- CRITICAL: 3
- HIGH: 4
- MEDIUM: 5
- LOW: 3

---

## Critical Issues (Fix Immediately)

### 1. Missing Import Module - `backend/services/campaign_service.py`
**Severity:** CRITICAL
**Impact:** Runtime crash - orchestrator cannot import required module

**Problem:**
The LangGraph orchestrator at `backend/agents/campaign_moves/orchestrator.py` imports:
```python
from backend.services.campaign_service import campaign_service
```

But `backend/services/campaign_service.py` does **not exist**.

**Error:**
```
ModuleNotFoundError: No module named 'backend.services.campaign_service'
```

**Fix:**
Create `backend/services/campaign_service.py`:
```python
"""
Campaign Service Compatibility Shim.

This module provides backward compatibility for code importing
from backend.services.campaign_service.
"""

from backend.services import campaign_service

__all__ = ["campaign_service"]
```

---

### 2. API Signature Mismatch - New vs Old CampaignService
**Severity:** CRITICAL
**Impact:** Orchestrator calls will fail with TypeError or return wrong types

**Problem:**
The new hexagonal CampaignService has a completely different interface:

| Aspect | Old Service | New Service |
|--------|-------------|-------------|
| `create_campaign` | `(workspace_id, campaign_data: Dict) -> Dict` | `(workspace_id, title, description, ...) -> Campaign` |
| Return Type | `Dict[str, Any]` | `Campaign` (domain entity) |
| Sync/Async | Synchronous | Async |

The orchestrator expects dictionaries but gets domain entities.

**Fix Options:**
1. **Create compatibility wrapper** (Recommended):
   - Create `backend/services/campaign/compat.py`
   - Wrap new service to match old interface
   - Convert domain entities to dictionaries

2. **Update orchestrator** (Breaking change):
   - Modify orchestrator to use new interface
   - Update all call sites

**Recommended Fix:**
Create compatibility layer in `backend/services/campaign/compat.py`:
```python
class CampaignServiceCompat:
    def list_campaigns(self, workspace_id: str) -> List[Dict]:
        # Call new async service and convert to dict
        result = asyncio.run(self._new_service.list_campaigns(workspace_id))
        return [c.to_dict() for c in result]
    
    def create_campaign(self, workspace_id: str, campaign_data: Dict) -> Dict:
        result = asyncio.run(self._new_service.create_campaign(
            workspace_id=workspace_id,
            title=campaign_data["name"],
            description=campaign_data.get("description"),
            objective=campaign_data.get("objective"),
            status=campaign_data.get("status"),
        ))
        return result.to_dict()
    # ... other methods
```

---

### 3. Duplicate Route Files
**Severity:** CRITICAL
**Impact:** API ambiguity - which router is actually used?

**Problem:**
Two route files exist:
- `backend/api/v1/campaigns/routes.py` - Old implementation (uses orchestrator)
- `backend/api/v1/campaigns/router.py` - New implementation (uses hexagonal)

The `__init__.py` was modified to export from `router.py` instead of `routes.py`.

**Risk:**
- Old routes may have different behavior
- URL patterns might differ
- Request/response schemas might differ

**Fix:**
1. Compare both files thoroughly
2. Ensure new router handles ALL endpoints from old routes
3. Remove old `routes.py` once verified
4. Add deprecation warnings if needed

---

## High Severity Issues

### 4. Error Handling Gaps in Adapters
**Severity:** HIGH
**Impact:** Generic errors make debugging difficult

**Problem:**
All Supabase adapters use bare `RuntimeError`:
```python
if not response.data:
    raise RuntimeError("Failed to save campaign")
```

**Issues:**
- No context about what failed
- Cannot distinguish between not-found vs database error
- Violates hexagonal architecture (should use domain exceptions)

**Affected Files:**
- `backend/features/campaign/adapters/supabase_repo.py`
- `backend/features/asset/adapters/supabase_repo.py`
- `backend/features/workspace/adapters/supabase_repo.py`

**Fix:**
Use domain exceptions from `backend/core/exceptions.py`:
```python
from backend.core.exceptions import NotFoundError, RepositoryError

async def get_by_id(self, campaign_id: str, workspace_id: str) -> Optional[Campaign]:
    try:
        response = self._client.table("campaigns").select("*").eq("id", campaign_id).execute()
        if not response.data:
            return None
        return Campaign.from_dict(response.data[0])
    except Exception as e:
        raise RepositoryError(f"Failed to get campaign {campaign_id}: {e}") from e
```

---

### 5. Missing Type Hints in Adapters
**Severity:** HIGH
**Impact:** Reduced IDE support, potential runtime errors

**Problem:**
Constructor parameters lack type hints:
```python
def __init__(self, supabase_client):  # Missing type!
    self._client = supabase_client
```

**Affected:**
- All `__init__` methods in adapter classes
- `supabase_client`, `storage_manager`, `supabase_auth_service`

**Fix:**
Add proper type hints:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from supabase import Client

def __init__(self, supabase_client: "Client") -> None:
    self._client = supabase_client
```

---

### 6. Test Coverage Gaps
**Severity:** HIGH
**Impact:** Unverified code in production

**Current State:**
| Feature | Domain Tests | Application Tests | Adapter Tests |
|---------|--------------|-------------------|---------------|
| Campaign | ✅ 1 file | ❌ 0 | ❌ 0 |
| Asset | ❌ 0 | ❌ 0 | ❌ 0 |
| Auth | ❌ 0 | ❌ 0 | ❌ 0 |
| Workspace | ❌ 0 | ❌ 0 | ❌ 0 |

**Fix:**
Create test files:
- `backend/tests/unit/features/campaign/test_services.py`
- `backend/tests/unit/features/campaign/test_repository.py`
- `backend/tests/unit/features/asset/test_entities.py`
- `backend/tests/unit/features/asset/test_services.py`
- etc.

---

### 7. Bootstrap Dependencies Architecture Violation
**Severity:** HIGH
**Impact:** bootstrap module depends on FastAPI

**Problem:**
`backend/bootstrap/dependencies.py` imports from FastAPI:
```python
from fastapi import Depends
```

**Architecture Violation:**
Bootstrap should be a pure composition root without framework dependencies.

**Fix:**
Separate FastAPI-specific code:
- `backend/bootstrap/providers.py` - Pure dependency providers
- `backend/api/dependencies.py` - FastAPI-specific wiring

---

## Medium Severity Issues

### 8. Protocol Implementation Not Explicit
**Severity:** MEDIUM
**Impact:** No compile-time verification of protocol compliance

**Problem:**
Repository classes don't explicitly inherit from protocols:
```python
class SupabaseCampaignRepository:  # Should be (CampaignRepository)
```

**Fix:**
```python
class SupabaseCampaignRepository(CampaignRepository):
```

---

### 9. Missing Module Docstrings
**Severity:** MEDIUM
**Impact:** Poor documentation

**Affected:**
- `backend/bootstrap/__init__.py`
- `backend/core/__init__.py` (existing but minimal)

**Fix:**
Add proper module docstrings.

---

### 10. Import Cycle Risk in Bootstrap
**Severity:** MEDIUM
**Impact:** Potential circular import issues

**Problem:**
`backend/bootstrap/dependencies.py` imports infrastructure at module level:
```python
from backend.infrastructure.database.supabase import get_supabase_client
```

This creates: bootstrap -> infrastructure -> (potential cycle)

**Fix:**
Use lazy imports or dependency injection container.

---

### 11. No Database Transaction Support
**Severity:** MEDIUM
**Impact:** Data consistency issues

**Problem:**
Repository methods don't support transactions:
```python
async def save(self, campaign: Campaign) -> Campaign:
    # No transaction handling
    response = self._client.table("campaigns").upsert(data).execute()
```

**Fix:**
Add transaction support via Unit of Work pattern or pass transaction context.

---

## Low Severity Issues

### 12. Empty __init__.py Files
**Severity:** LOW
**Impact:** No functional impact, but incomplete

**Affected:**
- `backend/bootstrap/__init__.py`

**Fix:**
Add appropriate exports or docstrings.

---

### 13. Hardcoded Table Names
**Severity:** LOW
**Impact:** Difficult to change schema

**Problem:**
Table names are hardcoded in adapters:
```python
self._client.table("campaigns")
```

**Fix:**
Make table names configurable or use constants.

---

### 14. Missing Logging in Adapters
**Severity:** LOW
**Impact:** Hard to debug database issues

**Problem:**
No logging in repository methods for debugging.

**Fix:**
Add structured logging for database operations.

---

## Fix Priority Order

### Phase 1: Critical (Must Fix Before Production)
1. ✅ Create `backend/services/campaign_service.py` shim
2. ✅ Create compatibility wrapper for CampaignService
3. ✅ Consolidate route files

### Phase 2: High (Fix This Week)
4. Add proper error handling to adapters
5. Add type hints to adapter constructors
6. Create comprehensive unit tests
7. Separate bootstrap from FastAPI

### Phase 3: Medium (Fix Next Sprint)
8. Explicit protocol inheritance
9. Add missing docstrings
10. Address import cycle risks
11. Add transaction support

### Phase 4: Low (Technical Debt)
12. Clean up __init__.py files
13. Make table names configurable
14. Add logging

---

## Verification Checklist

After fixes are implemented:

- [ ] All characterization tests pass
- [ ] New unit tests pass (>80% coverage)
- [ ] Import linter passes
- [ ] No circular import errors
- [ ] Orchestrator works with new code
- [ ] API routes work correctly
- [ ] No RuntimeError in production

---

## Architecture Compliance

The new structure follows hexagonal architecture principles:

```
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                            │
│              (FastAPI routes, controllers)                   │
├─────────────────────────────────────────────────────────────┤
│                      Bootstrap/DI                            │
│              (Dependency injection wiring)                   │
├─────────────────────────────────────────────────────────────┤
│                      Adapters Layer                          │
│    (Supabase repositories, external service clients)         │
├─────────────────────────────────────────────────────────────┤
│                   Application Layer                          │
│         (Use cases, services, ports/protocols)               │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│           (Entities, value objects, rules)                   │
└─────────────────────────────────────────────────────────────┘
```

**Dependency Rule:** Dependencies point inward (Domain <- Application <- Adapters <- API)

---

## Conclusion

The modularization architecture is sound, but critical compatibility issues must be fixed before production deployment. The main risks are:

1. **Runtime crashes** from missing import modules
2. **API contract violations** between old and new services
3. **Route ambiguity** from duplicate files

Fixing these 3 critical issues should be the immediate priority.
