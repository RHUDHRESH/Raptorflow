# Tooling Catalog

## Core Developer Commands

- `npm run dev`: run frontend dev server.
- `npm run build`: lint, type-check, and production build.
- `npm run test`: run Vitest tests.
- `python -m pytest`: run Python tests.

## Container and Infra

- `docker build -t raptorflow:stabilized .`
- `docker run --env-file .env -p 3112:3000 -p 8112:8000 raptorflow:stabilized`
- `supabase migration list`
- `supabase db push --yes`

## Audit and Inventory Scripts

- `python scripts/audit/file_inventory.py`
- `python scripts/audit/scan_endpoints.py --enrich`
- `python scripts/audit/generate_rebuild_contracts.py`
- `python scripts/audit/check_root_hygiene.py`

Generated outputs now default to:

- `documentation/generated/file_inventory.csv`
- `documentation/generated/static_endpoints.json`
- `documentation/generated/route_catalog.csv`

## Git Hygiene

- Use branches for demolition/rebuild batches.
- Use `git rm` for explicit tracked cleanup.
- Use `git clean -fd` for untracked residue when intentional.
