# Renovation Roadmap

## Phase 1: Demolition

- Remove legacy archives, stale orchestrator tracks, and duplicate roots.
- Keep only runtime modules and required infrastructure configs.
- Establish one canonical documentation root.

## Phase 2: Baseline Stabilization

- Verify backend health, auth health, and assets flow in Docker.
- Verify Supabase migrations are fully applied.
- Regenerate inventory and route maps into `documentation/generated/`.

## Phase 3: Modular Rebuild

- Define feature contracts module by module.
- Rebuild state boundaries explicitly (frontend stores and backend services).
- Add tests per module before extending behavior.

## Phase 4: Production Hardening

- CI job alignment with new module boundaries.
- Security and auth verification pass.
- Release checklist with rollback and migration notes.
