#!/usr/bin/env python3
"""Fail CI if forbidden legacy root files/folders reappear."""

from __future__ import annotations

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


def main() -> int:
    root_entries = {p.name for p in ROOT.iterdir()}
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
