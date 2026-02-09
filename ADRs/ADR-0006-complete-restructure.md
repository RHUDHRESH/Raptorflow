# ADR-0006: Complete Repository Restructure

## Status
Accepted (2026-02-09)

## Context
The RaptorFlow repository accumulated significant entropy over multiple development phases:
- 200+ files in root directory (test scripts, reports, debug tools, build logs)
- 3 disconnected modules (`cloud-scraper/`, `cognitive/`, `conductor/`) with zero imports from main app
- 16+ duplicate frontend components (e.g., CustomCursor in 3 locations, MagneticButton in 2)
- 46+ test files scattered in root instead of organized test directories
- Multiple duplicate config files (2 ESLint configs, 2 Tailwind configs, 2 Vitest configs)
- Empty AI assistant directories (`.agent/`, `.claude/`, `.gemini/`, `.opencode/`, `.zenflow/`)

## Decision
Perform a complete repository restructure following these principles:

1. **Archive disconnected modules** — Move `cloud-scraper/` (180+ files) to `archive/`, move `conductor/` (docs only) to `docs/archive/`, delete empty `cognitive/`
2. **Delete orphaned components** — Remove 13 frontend components with zero import references
3. **Consolidate duplicates** — Keep one canonical version of each duplicated component (CustomCursor, MagneticButton, CompassLogo)
4. **Organize tests** — Create `backend/tests/{unit,integration,verification}/` and move 46+ root test files
5. **Clean root directory** — Move all test artifacts, reports, logs, debug scripts to `archive/test-artifacts/`
6. **Remove duplicate configs** — Keep single canonical version of each config file
7. **Fix pre-existing type errors** — Repair BCMStatusPanel.tsx (corrupted JSX) and MuseChat.tsx (missing function)

## Alternatives Considered
- **Gradual cleanup**: Lower risk but would take weeks and leave the repo messy during transition
- **Documentation only**: Would map the mess but not fix it
- **New repository**: Too disruptive, loses git history

## Consequences

### Positive
- Root directory reduced from 200+ to ~30 essential files
- Zero duplicate components remaining
- All test files properly organized
- TypeScript compiles with 0 errors
- Clear module boundaries for all frontend components
- Comprehensive documentation of what was removed and why

### Negative
- Any external tooling referencing deleted paths will break
- Branches diverged from before the restructure will have merge conflicts
- Historical test scripts are harder to find (in `archive/`)

### Risks Mitigated
- Backup branch `backup/pre-restructure-2024` created before changes
- Full change log in `REPO_MAP.md` "What Was Removed" section
- `MODULE_USAGE_REPORT.md` documents every deletion decision with evidence
