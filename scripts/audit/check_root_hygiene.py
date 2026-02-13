#!/usr/bin/env python3
"""Fail CI if forbidden legacy root files/folders reappear."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_ROOT_ENTRIES = {
    ".gcloud",
    ".idea",
    ".logs",
    ".next",
    ".pre-commit-cache",
    ".venv",
    ".zencoder",
    ".zenflow",
    "archive",
    "components",
    "conductor",
    "Instruction",
    "prompts",
    "rhudhreshr_json",
    "docs",
    "index.html",
    "vite.config.js",
    "jsconfig.json",
    "ecosystem.config.js",
    ".prettierrc",
    "tsconfig.tsbuildinfo",
}


def _tracked_root_entries() -> set[str]:
    """Return the set of root-level entries tracked by git.

    CI runs this check on a clean checkout; locally devs may have generated
    build artifacts (e.g. Next.js output) that should not fail hygiene as long
    as they are not tracked.
    """

    try:
        result = subprocess.run(
            ["git", "ls-tree", "--name-only", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return {line.strip() for line in result.stdout.splitlines() if line.strip()}
    except Exception:
        return set()


def main() -> int:
    root_entries = {p.name for p in ROOT.iterdir()}
    tracked = _tracked_root_entries()
    if tracked:
        # Only flag forbidden items if they are actually tracked in git.
        violations = sorted(FORBIDDEN_ROOT_ENTRIES.intersection(root_entries).intersection(tracked))
    else:
        violations = sorted(FORBIDDEN_ROOT_ENTRIES.intersection(root_entries))

    if not violations:
        print("Root hygiene check passed.")
        return 0

    print("Root hygiene check failed.")
    print("Forbidden root entries found:")
    for item in violations:
        print(f"- {item}")
    print("")
    print("Remove these entries or update scripts/audit/check_root_hygiene.py")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
