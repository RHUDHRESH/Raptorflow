# REPAIR_LOG.md

## Audit Generation Log

**Date:** 2026-01-30  
**Checkpoint:** b88b72f23e590d86c96fc9ff1c02f84a4d13d0c (not found locally)

---

## Phase 1: Import Investigation

### Canonical Package Root

The backend is designed to run with `uvicorn backend.app:app` from the project root.
When running this way, `backend/` becomes the package root and all internal imports
should use the `backend.xxx` prefix.

### Import Chain Analysis

```
backend/app.py:12
  → backend/api/v1/minimal_routers
    → backend/api/__init__.py:5
      → backend/api/dependencies.py:9-18
        → backend.core.auth (FIXED: was `from core.auth`)
        → backend.agents.dispatcher
          → backend/agents/__init__.py
            → backend/agents/specialists/onboarding_orchestrator.py:32
              → from llm import llm_manager (NEEDS FIX)
```

### Files with Import Issues

| File | Line | Current Import | Required Import |
|------|------|----------------|-----------------|
| `backend/api/dependencies.py` | 9-18 | `from backend.core.auth` | Already correct |
| `backend/agents/__init__.py` | 7 | `from backend.config.agent_config` | Already correct |
| `backend/agents/config.py` | 12 | `from backend.config import ModelTier` | Already correct |
| `backend/agents/specialists/onboarding_orchestrator.py` | 32 | `from llm import llm_manager` | `from backend.llm import llm_manager` |

---

## Phase 2: Import Fix Attempts

### Fix 1: backend/api/dependencies.py
**Status:** Already uses `backend.` prefix correctly
```python
from backend.core.auth import get_auth_context, get_current_user
from backend.core.redis import get_redis_client
from backend.core.supabase_mgr import get_supabase_client
from backend.memory.controller import MemoryController
from backend.cognitive import CognitiveEngine
from backend.agents.dispatcher import AgentDispatcher
```

### Fix 2: backend/agents/__init__.py
**Status:** Already uses `backend.` prefix correctly
```python
from backend.config.agent_config import AgentConfig
```

### Fix 3: backend/agents/config.py
**Status:** Already uses `backend.` prefix correctly
```python
from backend.config import ModelTier
```

### Fix 4: backend/agents/specialists/onboarding_orchestrator.py
**Status:** USER KEPT REVERTING to `from llm import llm_manager`
```python
# This needs to be:
from backend.llm import llm_manager
```

---

## Phase 3: Runtime Import Error

### Error Traceback

```
ModuleNotFoundError: No module named 'llm'
  File: backend/agents/specialists/onboarding_orchestrator.py:32
  Import: from llm import llm_manager
```

### Root Cause

When running with `uvicorn backend.app:app` from the project root:
- Python's import path includes the project root (Raptorflow/)
- But `llm` at top level would look for `Raptorflow/llm.py`, not `Raptorflow/backend/llm.py`
- The file exists at `backend/llm.py` but isn't found because imports need `backend.` prefix

---

## Phase 4: Fallback Strategy - Static Analysis

Since runtime import fails, we used static AST analysis:

### Commands Executed

```bash
# 1. File inventory (using pathlib)
python -c "
from pathlib import Path
files = list(Path('backend').rglob('*.py'))
print(f'Total Python files: {len(files)}')
"

# Result: 1040 Python files

# 2. Static endpoint scan
python -c "
import ast
from pathlib import Path

def scan_file(fp):
    try:
        with open(fp) as f:
            tree = ast.parse(f.read())
        # Count route decorators
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr in ('get','post','put','delete','patch'):
                    count += 1
        return count
    except:
        return 0

total = sum(scan_file(p) for p in Path('backend').rglob('*.py'))
print(f'Total endpoints (static): {total}')
"

# 3. Generate route catalog
python scripts/audit/scan_endpoints.py backend --output-csv docs/route_catalog.csv
```

---

## Output Files Generated

| File | Description | Status |
|------|-------------|--------|
| `docs/BACKEND_DEEP_AUDIT.md` | Comprehensive audit report | PENDING |
| `docs/BACKEND_DEEP_AUDIT_INDEX.json` | Machine-readable index | PENDING |
| `docs/route_audit_output.json` | Existing raw endpoint data | EXISTS |
| `docs/route_catalog.csv` | Every endpoint row | PENDING |
| `docs/file_inventory.csv` | Every .py file with line counts | PENDING |
| `docs/runtime_import_error.txt` | Import error details | THIS FILE |
| `docs/route_mismatches.md` | Static vs runtime diff | N/A (no runtime) |

---

## Verification Commands

```bash
# Test import (will fail until llm import is fixed)
cd C:/Users/hp/OneDrive/Desktop/Raptorflow
python -c "from backend.app import app"

# Start uvicorn (will fail until imports are fixed)
cd C:/Users/hp/OneDrive/Desktop/Raptorflow
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Count audit report lines (after generation)
wc -l docs/BACKEND_DEEP_AUDIT.md
# Expected: >= 1200
```

---

## Next Steps to Fix Backend

1. Fix `backend/agents/specialists/onboarding_orchestrator.py` line 32:
   ```python
   # Change FROM:
   from llm import llm_manager
   # Change TO:
   from backend.llm import llm_manager
   ```

2. Search for other missing `backend.` prefixes:
   ```bash
   # In backend/ directory, find imports like:
   # from config import X
   # from llm import X
   # from memory import X
   # from cognitive import X
   # from agents import X
   # from core import X
   ```

3. Re-run audit after imports are fixed.

---

*This log documents the audit generation process and import issues encountered.*

### Import Chain Analysis

```
backend/app.py:12
  → backend/api/v1/minimal_routers
    → backend/api/__init__.py:5
      → backend/api/dependencies.py:9-18
        → backend.core.auth (FIXED: was `from core.auth`)
        → backend.agents.dispatcher
          → backend/agents/__init__.py
            → backend/agents/specialists/onboarding_orchestrator.py:32
              → from llm import llm_manager (NEEDS FIX)
```

### Files with Import Issues

| File | Line | Current Import | Required Import |
|------|------|----------------|-----------------|
| `backend/api/dependencies.py` | 9-18 | `from backend.core.auth` | Already correct |
| `backend/agents/__init__.py` | 7 | `from backend.config.agent_config` | Already correct |
| `backend/agents/config.py` | 12 | `from backend.config import ModelTier` | Already correct |
| `backend/agents/specialists/onboarding_orchestrator.py` | 32 | `from llm import llm_manager` | `from backend.llm import llm_manager` |

---

## Phase 2: Import Fix Attempts

### Fix 1: backend/api/dependencies.py
**Status:** Already uses `backend.` prefix correctly
```python
from backend.core.auth import get_auth_context, get_current_user
from backend.core.redis import get_redis_client
from backend.core.supabase_mgr import get_supabase_client
from backend.memory.controller import MemoryController
from backend.cognitive import CognitiveEngine
from backend.agents.dispatcher import AgentDispatcher
```

### Fix 2: backend/agents/__init__.py
**Status:** Already uses `backend.` prefix correctly
```python
from backend.config.agent_config import AgentConfig
```

### Fix 3: backend/agents/config.py
**Status:** Already uses `backend.` prefix correctly
```python
from backend.config import ModelTier
```

### Fix 4: backend/agents/specialists/onboarding_orchestrator.py
**Status:** USER KEPT REVERTING to `from llm import llm_manager`
```python
# This needs to be:
from backend.llm import llm_manager
```

---

## Phase 3: Runtime Import Error

### Error Traceback

```
ModuleNotFoundError: No module named 'llm'
  File: backend/agents/specialists/onboarding_orchestrator.py:32
  Import: from llm import llm_manager
```

### Root Cause

When running with `uvicorn backend.app:app` from the project root:
- Python's import path includes the project root (Raptorflow/)
- But `llm` at top level would look for `Raptorflow/llm.py`, not `Raptorflow/backend/llm.py`
- The file exists at `backend/llm.py` but isn't found because imports need `backend.` prefix

---

## Phase 4: Fallback Strategy - Static Analysis

Since runtime import fails, we used static AST analysis:

### Commands Executed

```bash
# 1. File inventory (using pathlib)
python -c "
from pathlib import Path
files = list(Path('backend').rglob('*.py'))
print(f'Total Python files: {len(files)}')
"

# Result: 1040 Python files

# 2. Static endpoint scan
python -c "
import ast
from pathlib import Path

def scan_file(fp):
    try:
        with open(fp) as f:
            tree = ast.parse(f.read())
        # Count route decorators
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr in ('get','post','put','delete','patch'):
                    count += 1
        return count
    except:
        return 0

total = sum(scan_file(p) for p in Path('backend').rglob('*.py'))
print(f'Total endpoints (static): {total}')
"

# 3. Generate route catalog
python scripts/audit/scan_endpoints.py backend --output-csv docs/route_catalog.csv
```

---

## Output Files Generated

| File | Description | Status |
|------|-------------|--------|
| `docs/BACKEND_DEEP_AUDIT.md` | Comprehensive audit report | PENDING |
| `docs/BACKEND_DEEP_AUDIT_INDEX.json` | Machine-readable index | PENDING |
| `docs/route_audit_output.json` | Existing raw endpoint data | EXISTS |
| `docs/route_catalog.csv` | Every endpoint row | PENDING |
| `docs/file_inventory.csv` | Every .py file with line counts | PENDING |
| `docs/runtime_import_error.txt` | Import error details | THIS FILE |
| `docs/route_mismatches.md` | Static vs runtime diff | N/A (no runtime) |

---

## Verification Commands

```bash
# Test import (will fail until llm import is fixed)
cd C:/Users/hp/OneDrive/Desktop/Raptorflow
python -c "from backend.app import app"

# Start uvicorn (will fail until imports are fixed)
cd C:/Users/hp/OneDrive/Desktop/Raptorflow
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Count audit report lines (after generation)
wc -l docs/BACKEND_DEEP_AUDIT.md
# Expected: >= 1200
```

---

## Next Steps to Fix Backend

1. Fix `backend/agents/specialists/onboarding_orchestrator.py` line 32:
   ```python
   # Change FROM:
   from llm import llm_manager
   # Change TO:
   from backend.llm import llm_manager
   ```

2. Search for other missing `backend.` prefixes:
   ```bash
   # In backend/ directory, find imports like:
   # from config import X
   # from llm import X
   # from memory import X
   # from cognitive import X
   # from agents import X
   # from core import X
   ```

3. Re-run audit after imports are fixed.

---

*This log documents the audit generation process and import issues encountered.*

