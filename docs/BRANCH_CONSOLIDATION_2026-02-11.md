# Branch Consolidation Report (2026-02-11)

## Baseline

- Branch audited: `main`
- Integration commit: `681cce0f7`
- Remote fetch status: blocked in this environment (`Could not resolve host: github.com`)

## What Was Integrated

- Current working tree consolidation was committed directly to `main` in:
  - `681cce0f7` - `chore: consolidate runtime stack and remove legacy cloud-scraper`
- This commit absorbed the active local consolidation snapshot and includes:
  - canonical inventory/map refresh (`REPO_MAP.md`, `API_INVENTORY.md`, `AUTH_INVENTORY.md`)
  - backend middleware/dependency hardening
  - proxy routing fix to canonical `/api/*` backend paths
  - migration of root test/debug scripts into `backend/tests/**` and `src/tests/**`
  - hard removal of legacy `cloud-scraper/`

## Unmerged Branch Triage Policy

Branches were reviewed against current architecture constraints:

- reject branches that reintroduce auth/payment stacks
- reject branches that add parallel API layers
- reject stale/high-divergence branches unless they provide unique, safe fixes
- keep `main` as source of truth after integration commit above

Result:
- no additional branch merge was performed after `681cce0f7`
- unmerged branches were either duplicate aliases, stale, or architecturally regressive

## Duplicate Branch Prune (Completed)

Deleted local duplicate aliases:

- `780ab30c`
- `b7fd0327`
- `c4d92699`
- `cascade/1-the-problems-you-still-have-multiple-ff539c`
- `cascade/all-bakcned-infra-lyaers-consolidated-f7efc3`
- `cascade/i-have-the-following-verification-7bc43b`
- `cascade/i-have-the-following-verification-b28c60`
- `cascade/i-have-the-following-verification-dc87b4`
- `cascade/i-need-backend-streamlined-and-1ea7f6`
- `cascade/new-cascade-f873e0`
- `cascade/ultraplan-ultraplan-delete-all-auth-a1edf9`
- `codex/add-swarm_learning-module-and-apis` (already merged ancestor)

## Prune Blocked by Linked Worktrees

These duplicates could not be deleted because they are currently checked out by linked worktrees under `.windsurf/worktrees/...`:

- `cascade/business-context-json-dynamically-when-dc9f8f`
- `cascade/for-the-fianl-time-orgnaize-everything-b538f6`
- `cascade/handoff-guide-md-ultraplan-to-get-this-9107b5`
- `cascade/i-m-going-to-finish-the-audit-output-by-c1b50b`
- `cascade/i-want-you-to-help-me-consolidate-and-93c0c3`
- `cascade/service-consolidation-implementation-ab8947`
- `cascade/ultraplan-and-organize-the-app-f88180`
- `cascade/ultraplan-and-orgnaize-the-app-exgtemly-0b1f25`
- `cascade/ultraplan-i-i-want-you-to-organize-all-a36e43`
- `cascade/you-are-in-ultraplan-mode-your-job-is-cf97e1`

To prune these, remove their linked worktrees first, then re-run `git branch -D <branch>`.
