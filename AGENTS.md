# AGENTS.md (Repo Constitution)

This is a brownfield repo. The goal is to reduce entropy.

## Non-negotiable rules

1. Inventory + map comes first.
   No feature work, refactors, or "cleanup" before these exist at repo root and are current:
   - REPO_MAP.md
   - API_INVENTORY.md
   - AUTH_INVENTORY.md

2. Search before writing anything new.
   Before adding a new file/module/route/middleware/client, search the repo for an existing
   implementation and extend/repair it instead of duplicating.

3. No parallel API layers or auth flows.
   Never add a new API layer (new server/gateway/router stack) or a new auth flow unless you are
   replacing an existing one AND deleting/fully disconnecting the old path in the same change.

4. Every change must be verifiable and reversible.
   Every code change must include either:
   - automated tests, or
   - a concrete curl/Postman reproduction.
   And must include in the PR/commit summary (or agent output):
   - Verification: exact steps + expected result
   - Rollback: exact revert steps (what to revert/undo, including env/config)

5. Architectural decisions require ADRs.
   Any architectural decision (new service/layer, gateway/routing strategy, auth mechanism,
   persistence/DB choice, major dependency) must add an ADR in `ADRs/` named:
   - ADR-####-<slug>.md
   Include: context, decision, alternatives considered, consequences.

## If blocked

If these rules prevent the requested work, stop and ask for an explicit override.
