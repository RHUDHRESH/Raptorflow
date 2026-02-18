#!/usr/bin/env python3
"""Generate documentation contract files used by smoke tests.

The generator intentionally keeps output deterministic and focused on
entrypoints/module boundaries so it can run in CI as a contract guard.
"""

from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "documentation"


def _git_ls_files(prefix: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", prefix],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _build_repo_map() -> str:
    return f"""# RaptorFlow Repository Map

Last updated: {_today()}

## Runtime Entry Points

- Frontend app shell: `src/app/layout.tsx`
- Frontend landing route: `src/app/page.tsx`
- Frontend API proxy: `src/app/api/[...path]/route.ts`
- Frontend middleware: `src/middleware.ts`
- Backend ASGI entrypoint: `backend/main.py`
- Backend app factory: `backend/app_factory.py`
- Backend router registry: `backend/api/registry.py`

## Backend Modules

- API system routes: `backend/api/system.py`
- API domain routes (modular): `backend/api/v1/*/routes.py`
- AI hub kernel: `backend/ai/hub/`
- BCM core: `backend/bcm/core/`

## Frontend Modules

- Shell routes: `src/app/(shell)/`
- Public routes: `src/app/(public)/`
- Auth routes: `src/app/login/`, `src/app/signup/`, `src/app/auth/`
- Client stores: `src/stores/`

## Test Surface

- Backend tests: `backend/tests/`
- Frontend/e2e tests: `tests/`

## Documentation Contracts

- `documentation/REPO_MAP.md`
- `documentation/API_INVENTORY.md`
- `documentation/AUTH_INVENTORY.md`
- `documentation/AI_HUB_BEDROCK.md`
"""


def _build_api_inventory() -> str:
    route_modules = sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in (ROOT / "backend" / "api" / "v1").glob("*/routes.py")
    )
    groups = [f"- `{m}`" for m in route_modules]
    groups_text = "\n".join(groups) if groups else "- _no route modules discovered_"
    return f"""# API Inventory

Last updated: {_today()}

## Canonical Prefixes

- System routes: `/`, `/health`, mirrored under `/api/*`
- Product/API routes: `/api/*`
- AI Hub routes: `/api/ai/hub/v1/*`

## AI Hub Public Contract

- `GET /api/ai/hub/v1/health`
- `GET /api/ai/hub/v1/capabilities`
- `GET /api/ai/hub/v1/policies`
- `POST /api/ai/hub/v1/tasks/run`
- `POST /api/ai/hub/v1/tasks/run-async`
- `GET /api/ai/hub/v1/jobs/{{job_id}}`
- `GET /api/ai/hub/v1/tasks/{{run_id}}/context`
- `GET /api/ai/hub/v1/tasks/{{run_id}}/trace`
- `POST /api/ai/hub/v1/feedback`
- `POST /api/ai/hub/v1/evals/execute`

## Registered Route Module Files

{groups_text}

## Proxy Boundary

Frontend proxy route:

- `src/app/api/[...path]/route.ts`
"""


def _build_auth_inventory() -> str:
    auth_files = [
        "src/app/login/page.tsx",
        "src/app/signup/page.tsx",
        "src/app/auth/callback/route.ts",
        "src/middleware.ts",
        "src/stores/authStore.ts",
        "src/lib/supabase/client.ts",
        "src/lib/supabase/middleware.ts",
        "backend/api/v1/auth/routes.py",
    ]
    bullets = "\n".join(f"- `{path}`" for path in auth_files)
    return f"""# Auth Inventory

Last updated: {_today()}

## Auth Surface Files

{bullets}

## Backend Auth Endpoints

- `GET /api/auth/health`
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `POST /api/auth/refresh`
- `POST /api/auth/verify`
- `GET /api/auth/me`
- `POST /api/auth/reset-password`
"""


def _write_or_check(path: Path, content: str, check: bool) -> bool:
    normalized = content.replace("\r\n", "\n").rstrip() + "\n"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    current = current.replace("\r\n", "\n")

    if check:
        return current == normalized

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify generated content matches files without writing.",
    )
    args = parser.parse_args()

    outputs = {
        DOCS / "REPO_MAP.md": _build_repo_map(),
        DOCS / "API_INVENTORY.md": _build_api_inventory(),
        DOCS / "AUTH_INVENTORY.md": _build_auth_inventory(),
    }

    all_ok = True
    for path, content in outputs.items():
        ok = _write_or_check(path, content, check=args.check)
        if args.check and not ok:
            print(f"Out of date: {path.relative_to(ROOT)}")
            all_ok = False
        elif not args.check:
            print(f"Wrote {path.relative_to(ROOT)}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
