# Module Usage Report
**Generated**: 2024 (Phase 1 Discovery)
**Purpose**: Identify used vs unused components/modules for restructure

## Executive Summary

**Total Components Analyzed**: 150+
**Orphaned/Unused**: 15+ components
**Disconnected Modules**: 3 (cloud-scraper, cognitive, conductor)
**Duplicate Components**: 6 confirmed duplicates
**Test Files in Wrong Location**: 46 files

## Critical Findings

### ✅ USED Components (Keep)

**Effects (Active Usage):**
- `src/components/effects/CustomCursor.tsx` - Used in `layout.tsx`
- `src/components/effects/MagneticButton.tsx` - Used in `EnhancedHero.tsx`, `EnhancedFeatures.tsx`
- `src/components/effects/SmoothScroll.tsx` - Used in `layout.tsx`
- `src/components/effects/GrainEffect.tsx` - Used in `layout.tsx`
- `src/components/effects/TextReveal.tsx` - Exported from effects/index.ts
- `src/components/effects/LottieCompass.tsx` - Used in landing components
- `src/components/effects/FloatingElements.tsx` - Used in landing components
- `src/components/effects/RevealOnScroll.tsx` - Used in landing components
- `src/components/effects/ParallaxImage.tsx` - Exported from effects/index.ts
- `src/components/effects/AnimatedCounter.tsx` - Exported from effects/index.ts

**Landing Components (Active):**
- All components in `src/components/landing/` are used in landing/marketing pages
- `EnhancedHero.tsx`, `EnhancedFeatures.tsx`, `Navbar.tsx`, `Footer.tsx`, etc.

**UI Components (Blueprint System - Active):**
- All Blueprint* components in `src/components/ui/` are part of design system
- Used throughout dashboard and authenticated app

**Feature Components (Active):**
- `src/components/bcm/` - Used in dashboard
- `src/components/campaigns/` - Used in campaigns pages
- `src/components/foundation/` - Used in foundation pages
- `src/components/moves/` - Used in moves pages
- `src/components/muse/` - Used in muse pages

### ❌ UNUSED Components (Delete Candidates)

**Root-Level Orphans (NO imports found):**
1. `src/components/AgentChat.tsx` - 18KB, no imports
2. `src/components/AgentManagement.tsx` - 22KB, no imports
3. `src/components/WorkflowBuilder.tsx` - 27KB, no imports
4. `src/components/InteractiveHero.tsx` - 2KB, no imports (likely superseded by EnhancedHero)
5. `src/components/Button.jsx` - 1KB, legacy component
6. `src/components/Card.jsx` - 544 bytes, legacy component
7. `src/components/Input.jsx` - 1KB, legacy component
8. `src/components/Magnetic.jsx` - 939 bytes, legacy component
9. `src/components/Preloader.jsx` - 3KB, legacy JSX version
10. `src/components/RevealText.jsx` - 1KB, legacy JSX version
11. `src/components/ScrambleText.jsx` - 1KB, legacy component
12. `src/components/SpotlightCard.jsx` - 1KB, legacy component

**Status**: All above have ZERO import references in `src/` directory

### 🔄 DUPLICATE Components (Consolidation Required)

**1. MagneticButton (2 versions)**
- ✅ `src/components/effects/MagneticButton.tsx` (USED - 90 lines)
- ❌ `src/components/ui/MagneticButton.tsx` (UNUSED - 234 lines, more complex)
- **Action**: Keep effects version (actively imported), delete ui version
- **Imports to update**: None (all use effects version)

**2. CustomCursor (3 versions!)**
- ✅ `src/components/effects/CustomCursor.tsx` (USED in layout.tsx)
- ❌ `src/components/CustomCursor.jsx` (legacy JSX, 3KB)
- ❌ `src/components/ui/CustomCursor.tsx` (3KB, unused)
- **Action**: Keep effects version, delete other two
- **Imports to update**: None (layout.tsx uses correct version)

**3. Preloader (2 versions)**
- `src/components/Preloader.jsx` (legacy JSX)
- `src/components/ui/Preloader.tsx` (modern TS)
- **Status**: Need to verify which is used (if any)

**4. CompassLogo (2 versions)**
- `src/components/compass/CompassLogo.tsx` (semantic location)
- `src/components/ui/CompassLogo.tsx` (design system location)
- **Action**: Need to check imports to determine canonical version

**5. ErrorBoundary (2 versions)**
- `src/components/error/ErrorBoundary.tsx`
- `src/components/ui/ErrorBoundary.tsx`
- **Action**: Check imports, consolidate to one location

## Disconnected Modules Analysis

### cloud-scraper/ (ORPHANED - 180+ files)

**Evidence**:
- 56 references found, ALL within cloud-scraper/ itself
- Only external reference: `.idea/` folder (IDE metadata, not code)
- No imports in `src/`, `backend/`, or root scripts
- Standalone scraping/research system with own requirements.txt

**Files**: 180+ Python scripts, databases, reports, configs
**Size**: ~50MB+ with databases
**Status**: **COMPLETELY DISCONNECTED**

**Recommendation**: Move entire directory to `archive/cloud-scraper/`

**Rationale**:
- Not integrated into main RaptorFlow application
- Has own deployment configs (docker-compose.search.yml, etc.)
- Appears to be experimental research automation tool
- May have value for reference but not part of core app

### cognitive/ (EMPTY - 1 file)

**Contents**: Only `__init__.py` (216 bytes)
**Evidence**: 36 import references found, but ALL are in test files for deleted cognitive system

**Test files referencing cognitive (all appear obsolete)**:
- `test_cognitive_engine.py`
- `test_cognitive_integration.py`
- `red_team_cognitive_analysis.py`
- `debug_*.py` scripts (debug_entity, debug_intent, debug_optimization, debug_planning)

**Status**: **EMPTY MODULE, TESTS ARE OBSOLETE**

**Recommendation**: 
1. DELETE `cognitive/` directory (empty except __init__.py)
2. MOVE cognitive test files to `archive/tests/obsolete/cognitive/`

### conductor/ (DOCS ONLY - 0 code files)

**Contents**:
- Documentation files only: DEV.md, product.md, tech-stack.md, workflow.md, tracks.md
- `archive/` subdirectory (empty)
- `code_styleguides/` subdirectory (empty)
- `tracks/` subdirectory (empty)
- `setup_state.json` (56 bytes)

**Status**: **DOCUMENTATION ARCHIVE, NO CODE**

**Recommendation**: Move to `docs/archive/conductor/` (historical project docs)

**Rationale**: Appears to be development guidelines/workflow docs from earlier project phase

## Test Files Audit

### Root-Level Test Files (46 files - WRONG LOCATION)

**Categories**:

**1. Database Connection Tests (7 files - REDUNDANT)**
- `test_db_conn.py`
- `test_db_conn_direct.py`
- `test_db_conn_env.py`
- `test_db_conn_pooler_5432.py`
- `test_db_conn_secret.py`
- `test_database_simple.py`
- `test_supabase.py`
**Action**: Keep 1 best version, delete others, move to `backend/tests/integration/`

**2. Cognitive System Tests (11 files - OBSOLETE)**
All tests for deleted cognitive module:
- `test_cognitive_engine.py`
- `test_cognitive_integration.py`
- `test_entity_extractor.py`
- `test_intent_detector.py`
- `test_memory_*.py` (5 files)
- `test_planning_*.py` (3 files)
- `test_perception_module.py`
- `test_reflection_module.py`
**Action**: Move to `archive/tests/obsolete/cognitive/`

**3. Task Verification Tests (12 files - ORGANIZE)**
- `test_task1_verification.py` through `test_task12_verification.py`
**Action**: Move to `backend/tests/verification/`

**4. Integration Tests (8 files - ORGANIZE)**
- `test_app_integration.py`
- `test_app_integration_fixed.py`
- `test_complete_integration.py`
- `test_all_endpoints.py`
- `test_integration.py`
- `test_integration_simple.py`
- `test_api_endpoints.py`
- `test_middleware_only.py`
**Action**: Move to `backend/tests/integration/`, consolidate duplicates

**5. Agent/Structure Tests (4 files - ORGANIZE)**
- `test_agent_imports.py`
- `test_agent_structure.py`
- `test_agent_system.py`
- `test_basic_structure.py`
**Action**: Move to `backend/tests/unit/`

**6. Service Tests (misc)**
- `test_gemini_*.py` (4 files)
- `test_vertex_ai.py`
- `test_redis_*.py` (2 files)
- `test_bcm_templates.py`
- `test_cost_estimator.py`
- `test_system.py`
**Action**: Move to `backend/tests/integration/`

## Root Directory Clutter Analysis

### Test Artifacts (DELETE - 20+ files)
**JSON Reports**:
- `advanced_image_analysis_results.json`
- `business_file_test_report.json`
- `business_images_analysis.json`
- `business_images_download_report.json`
- `business_ocr_test_report.json`
- `comprehensive_ocr_test_report.json`
- `dependency_test_results.json`
- `enhanced_ocr_test_report.json`
- `production_readiness_report.json`
- `quick_tactical_download_report.json`
- `red_team_report.json`
- `secure_verification_report.json`
- `tactical_content_analysis.json`
- `tactical_content_generation_report.json`
- `tactical_download_report.json`
- `test_businesscontext.json`
- `undeniable_inference_proof.json`
- `verification_report.json`
- `working_ocr_test_report.json`

**Database Files** (20+ .db files):
- `cost_optimization.db`
- All in cloud-scraper/ subdirectory

**Build Logs** (10+ .txt files):
- `backend_log.txt`
- `build-*.txt` (7 files)
- `devserver.err`, `devserver.out`
- `eslint_report.txt`
- `flake8_report.txt`
- `typescript_report.txt`
- `tsc-*.txt` (2 files)

**Debug Scripts** (30+ .py files):
- `debug_*.py` (6 files)
- `query_*.py`, `verify_*.py`, `reset_*.py`, `show_*.py`
- `apply_migrations.py`, `final_*.py`, `production_*.py`

**Misc Files**:
- `null` (corrupted file?)
- `error_screenshot.png`
- `homepage-screenshot.png`
- `scrape_test_screenshot.png`
- `page-content.html`
- `real_scraping_demo.html`
- `test-evidence.pdf`
- `test-upload.txt`
- `search_results.txt` (empty)
- `index.html` (606 bytes)

### Empty/Legacy Directories (DELETE)
- `.agent/` - Empty
- `.claude/` - Empty
- `.gemini/` - Empty
- `.opencode/` - Empty
- `.zenflow/` - Empty
- `.git-rewrite/` - Git artifacts
- `.pre-commit-cache/` - Generated
- `components/` at root - Empty or legacy
- `config/` at root - Need to verify usage

## Import Path Analysis

### Correct Import Patterns (Maintain)
```typescript
// Effects
import { CustomCursor } from "@/components/effects/CustomCursor";
import { MagneticButton } from "@/components/effects/MagneticButton";

// UI Components
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintCard } from "@/components/ui/BlueprintCard";

// Feature Components
import { BCMStatusPanel } from "@/components/bcm/BCMStatusPanel";
import { MovesWizard } from "@/components/moves/MovesWizard";
```

### Incorrect/Legacy Patterns (None Found!)
No imports found for root-level components - they're truly orphaned.

## Recommended Actions Summary

### PHASE 1: DELETE (Safe - No imports)
1. Delete 12 root-level component files (AgentChat, WorkflowBuilder, etc.)
2. Delete 2 duplicate CustomCursor files
3. Delete 1 duplicate MagneticButton (ui version)
4. Delete empty AI assistant folders (.agent, .claude, .gemini, etc.)
5. Delete all test artifacts (.json reports, .db files, .txt logs)
6. Delete debug/verify scripts (30+ files)
7. Delete `cognitive/` directory

### PHASE 2: MOVE TO ARCHIVE
1. Move `cloud-scraper/` → `archive/cloud-scraper/`
2. Move `conductor/` → `docs/archive/conductor/`
3. Move cognitive tests → `archive/tests/obsolete/cognitive/`
4. Move test artifacts → `archive/test-artifacts/`

### PHASE 3: ORGANIZE TESTS
1. Create `backend/tests/` structure
2. Move 46 test files to appropriate subdirectories
3. Consolidate duplicate tests
4. Delete obsolete tests

### PHASE 4: VERIFY & CONSOLIDATE
1. Check CompassLogo usage, consolidate
2. Check ErrorBoundary usage, consolidate
3. Check Preloader usage, consolidate
4. Verify `config/` at root is unused, delete or move

## Risk Assessment

**Low Risk (Safe to Delete)**:
- Root-level orphaned components (zero imports)
- Empty directories
- Test artifacts
- Debug scripts

**Medium Risk (Verify First)**:
- Duplicate components (check all import paths)
- Test file consolidation (ensure no data loss)

**High Risk (Careful)**:
- cloud-scraper deletion (large codebase, may have business value)
- Config directory changes (may affect Docker/deployment)

## Next Steps

1. Create backup branch: `git checkout -b backup/pre-restructure-$(date +%Y%m%d)`
2. Execute Phase 1 deletions (safe, no imports)
3. Execute Phase 2 archival (preserve for reference)
4. Execute Phase 3 test organization
5. Verify build still works
6. Commit as "Phase 1-3: Cleanup orphaned code"

---

**Total Files to Delete**: ~100+ files
**Total Files to Archive**: ~200+ files  
**Total Files to Move/Organize**: ~50+ files
**Root Directory Reduction**: From 200+ items to ~20 essential files
