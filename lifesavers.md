# Backend Modularization Plan

## Overview
Break the entire backend into modular, single-responsibility pieces for testability, maintainability, and deployability.

## Principles
- **Maximum granularity** - 1 service per file, 1 agent per file, 1 schema per file
- **Flat by endpoint** - each API endpoint becomes its own package
- **Clean break** - no backward compatibility, all imports rebuilt from scratch
- **All at once** - full backend in one refactor

---

## PHASE 1: Infrastructure Migration (from `core/`) - ✅ COMPLETED

### Tasks
- [X] Move `core/db_pool.py` → `infrastructure/database/pool.py`
- [X] Move `core/redis_mgr.py` → `infrastructure/cache/redis.py`
- [X] Move `core/supabase_mgr.py` → `infrastructure/database/supabase.py`
- [X] Move `core/storage_mgr.py` → `infrastructure/storage/manager.py`
- [X] Move `core/query_monitor.py` → `infrastructure/database/monitor.py`
- [X] Move `core/cache_decorator.py` → `infrastructure/cache/decorator.py`
- [X] Move `core/async_tasks.py` → `infrastructure/tasks/async_tasks.py`
- [X] Delete empty `core/` directory
- [X] Update all imports referencing old `core/` paths

---

## PHASE 2: Services Modularization - ✅ COMPLETED

### Tasks
- [X] Create `services/bcm/__init__.py` (re-exports)
- [X] Create `services/bcm/service.py` (from `services/bcm_service.py`)
- [X] Create `services/bcm/synthesizer.py` (from `services/bcm_synthesizer.py`)
- [X] Create `services/bcm/reducer.py` (from `services/bcm_reducer.py`)
- [X] Create `services/bcm/templates.py` (from `services/business_context_templates.py`)
- [X] Create `services/bcm/generation_logger.py` (from `services/bcm_generation_logger.py`)
- [X] Create `services/campaign/service.py` (from `services/campaign_service.py`)
- [X] Create `services/move/service.py` (from `services/move_service.py`)
- [X] Create `services/asset/service.py` (from `services/asset_service.py`)
- [X] Create `services/email/service.py` (from `services/email_service.py`)
- [X] Create `services/auth/service.py` (from `services/auth_service.py`)
- [X] Create `services/cached_queries/service.py` (from `services/cached_queries.py`)
- [X] Update all imports referencing old `services/` paths

---

## PHASE 3: Agents Modularization - ✅ COMPLETED

### Tasks
- [X] Create `agents/muse/__init__.py`
- [X] Create `agents/muse/orchestrator.py` (from `agents/langgraph_muse_orchestrator.py`)
- [X] Create `agents/campaign_moves/orchestrator.py` (from `agents/langgraph_campaign_moves_orchestrator.py`)
- [X] Create `agents/context/orchestrator.py` (from `agents/langgraph_context_orchestrator.py`)
- [X] Create `agents/optional/orchestrator.py` (from `agents/langgraph_optional_orchestrator.py`)
- [X] Create `agents/runtime/profiles.py` (from `agents/ai_runtime_profiles.py`)
- [X] Update all imports referencing old `agents/` paths

---

## PHASE 4: API/Schemas Modularization - ⚠️ SKIPPED

Not completed due to time constraints. API endpoints remain flat but services/agents/infrastructure are now modular.

---

## Summary

### Completed Modularizations:
- ✅ **Infrastructure**: `core/` → `infrastructure/database/`, `infrastructure/cache/`, `infrastructure/storage/`, `infrastructure/tasks/`
- ✅ **Services**: Flat files → Domain packages (`services/bcm/`, `services/campaign/`, `services/move/`, etc.)
- ✅ **Agents**: Flat files → Domain packages (`agents/muse/`, `agents/campaign_moves/`, `agents/context/`, etc.)
- ✅ **API**: Flat files → Domain packages (`api/v1/workspaces/`, `api/v1/campaigns/`, etc.)

### New Structure:
```
backend/
├── infrastructure/
│   ├── database/    (pool, supabase, monitor)
│   ├── cache/       (redis, decorator)
│   ├── storage/     (manager)
│   ├── tasks/       (async_tasks)
│   └── rate_limiting/
├── services/
│   ├── bcm/         (service, synthesizer, reducer, templates, generation_logger)
│   ├── campaign/    (service)
│   ├── move/        (service)
│   ├── asset/       (service)
│   ├── email/       (service)
│   ├── auth/        (service)
│   └── cached_queries/
├── agents/
│   ├── muse/        (orchestrator)
│   ├── campaign_moves/
│   ├── context/
│   ├── optional/
│   └── runtime/     (profiles)
└── api/v1/          (modularized by endpoint)
```
backend/
├── infrastructure/
│   ├── database/    (pool, supabase, monitor)
│   ├── cache/       (redis, decorator)
│   ├── storage/    (manager)
│   ├── tasks/      (async_tasks)
│   └── rate_limiting/
├── services/
│   ├── bcm/        (service, synthesizer, reducer, templates, generation_logger)
│   ├── campaign/    (service)
│   ├── move/       (service)
│   ├── asset/      (service)
│   ├── email/      (service)
│   ├── auth/       (service)
│   └── cached_queries/
├── agents/
│   ├── muse/       (orchestrator)
│   ├── campaign_moves/
│   ├── context/
│   ├── optional/
│   └── runtime/    (profiles)
└── api/v1/         (flat - not modularized)
```

---

## PHASE 4: API/Schemas Modularization - ✅ COMPLETED

### Tasks
- [X] Create `api/v1/workspaces/` package with routes.py
- [X] Create `api/v1/campaigns/` package with routes.py
- [X] Create `api/v1/moves/` package with routes.py
- [X] Create `api/v1/assets/` package with routes.py
- [X] Create `api/v1/context/` package with routes.py
- [X] Create `api/v1/muse/` package with routes.py
- [X] Create `api/v1/auth/` package with routes.py
- [X] Create `api/v1/communications/` package with routes.py
- [X] Create `api/v1/foundation/` package with routes.py
- [X] Create `api/v1/health/` package with routes.py
- [X] Create `api/v1/scraper/` package with routes.py
- [X] Create `api/v1/search/` package with routes.py
- [X] Create `api/v1/bcm_feedback/` package with routes.py
- [X] Create `api/v1/workspace_guard/` package with routes.py (helpers, no router)
- [X] Update imports in API files

---

## PHASE 5: Testing & Validation

### Tasks
- [ ] Run existing test suite
- [ ] Fix all broken import statements
- [ ] Run linter (ruff/flake8)
- [ ] Run type checker (pyright/mypy)
- [ ] Verify all endpoints still work (manual or automated)
- [ ] Update any documentation references

---

## File Mapping Reference

### Core → Infrastructure
| Old Path | New Path |
|----------|----------|
| `core/db_pool.py` | `infrastructure/database/pool.py` |
| `core/redis_mgr.py` | `infrastructure/cache/redis.py` |
| `core/supabase_mgr.py` | `infrastructure/database/supabase.py` |
| `core/storage_mgr.py` | `infrastructure/storage/manager.py` |
| `core/query_monitor.py` | `infrastructure/database/monitor.py` |
| `core/cache_decorator.py` | `infrastructure/cache/decorator.py` |
| `core/async_tasks.py` | `infrastructure/tasks/async_tasks.py` |

### Services → Domain Packages
| Old Path | New Path |
|----------|----------|
| `services/bcm_service.py` | `services/bcm/service.py` |
| `services/bcm_synthesizer.py` | `services/bcm/synthesizer.py` |
| `services/bcm_reducer.py` | `services/bcm/reducer.py` |
| `services/business_context_templates.py` | `services/bcm/templates.py` |
| `services/bcm_generation_logger.py` | `services/bcm/generation_logger.py` |
| `services/campaign_service.py` | `services/campaign/service.py` |
| `services/move_service.py` | `services/move/service.py` |
| `services/asset_service.py` | `services/asset/service.py` |
| `services/email_service.py` | `services/email/service.py` |
| `services/auth_service.py` | `services/auth/service.py` |
| `services/cached_queries.py` | `services/cached_queries/service.py` |

---

## How to Edit This Plan

1. **Mark task in progress**: Change `[ ]` to `[o]`
2. **Mark task done**: Change `[ ]` to `[X]`
3. **Add new task**: Add `[ ] Description` on appropriate line
4. **Remove task**: Delete the line
5. **Reorder**: Cut and paste lines

---

## Notes
- Each new package should have an `__init__.py` that re-exports the public API
- Keep imports clean: `from backend.services.bcm import BCMService`
- Tests should mirror the new structure
- Consider adding `__all__` to each module for explicit exports
