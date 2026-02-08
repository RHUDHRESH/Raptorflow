#!/usr/bin/env python3
"""
CI static check: detect duplicate API endpoint registrations.

Scans backend/api/v1/*.py for APIRouter definitions and their route
decorators, then reports any path+method collisions.

Usage:
    python scripts/check_duplicate_endpoints.py
    # Exit code 0 = no duplicates, 1 = duplicates found

Add to CI:
    - name: Check duplicate endpoints
      run: python scripts/check_duplicate_endpoints.py
"""

import ast
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = REPO_ROOT / "backend"
REGISTRY_PATH = BACKEND_ROOT / "api" / "registry.py"

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def _extract_router_prefixes(tree: ast.AST) -> dict[str, str]:
    """Return mapping of router variable name -> prefix."""
    prefixes: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Call):
            continue

        func = node.value.func
        func_name = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else ""
        if func_name != "APIRouter":
            continue

        target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if not target_names:
            continue

        prefix = ""
        for kw in node.value.keywords:
            if kw.arg == "prefix" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                prefix = kw.value.value
        for name in target_names:
            prefixes[name] = prefix
    return prefixes


def _extract_router_includes(tree: ast.AST) -> dict[str, list[str]]:
    """Return mapping parent_router_var -> [child_router_vars]."""
    includes: dict[str, list[str]] = defaultdict(list)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            continue
        call = node.value
        if not isinstance(call.func, ast.Attribute) or call.func.attr != "include_router":
            continue
        if not isinstance(call.func.value, ast.Name):
            continue
        parent = call.func.value.id
        if not call.args:
            continue
        if not isinstance(call.args[0], ast.Name):
            continue
        child = call.args[0].id
        includes[parent].append(child)
    return includes


def _effective_prefix(router_name: str, prefixes: dict[str, str], includes: dict[str, list[str]]) -> str:
    """Compute router prefix including any parent include_router composition."""
    prefix = prefixes.get(router_name, "")
    for parent, children in includes.items():
        if router_name in children:
            prefix = _effective_prefix(parent, prefixes, includes) + prefix
            break
    return prefix


def extract_routes(filepath: Path) -> list[tuple[str, str, str, int]]:
    """Extract (method, effective_path, file, lineno) from a Python file."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return []

    prefixes = _extract_router_prefixes(tree)
    includes = _extract_router_includes(tree)

    routes: list[tuple[str, str, str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)):
                continue
            if decorator.func.attr not in HTTP_METHODS:
                continue
            if not isinstance(decorator.func.value, ast.Name):
                continue

            router_name = decorator.func.value.id
            if not decorator.args:
                continue
            arg0 = decorator.args[0]
            if not (isinstance(arg0, ast.Constant) and isinstance(arg0.value, str)):
                continue

            method = decorator.func.attr.upper()
            path = arg0.value
            router_prefix = _effective_prefix(router_name, prefixes, includes)
            full_path = f"{router_prefix}{path}".rstrip("/") or "/"
            rel = filepath.relative_to(BACKEND_ROOT)
            routes.append((method, full_path, str(rel), node.lineno))

    return routes


def _parse_registry_for_module_paths() -> list[Path]:
    """Parse backend/api/registry.py and return module filepaths mounted by UNIVERSAL_ROUTERS."""
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Missing registry: {REGISTRY_PATH}")

    source = REGISTRY_PATH.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source, filename=str(REGISTRY_PATH))

    v1_modules: set[str] = set()
    domains_modules: set[Path] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "domains.auth.router":
                domains_modules.add(BACKEND_ROOT / "domains" / "auth" / "router.py")

            if node.module == "backend.api.v1":
                for alias in node.names:
                    # e.g. `from backend.api.v1 import campaigns` or `import config as config_router`
                    v1_modules.add(alias.name)

            if node.module == "backend.api.v1" and any(a.name == "config" for a in node.names):
                v1_modules.add("config")

    module_paths: list[Path] = []
    for mod in sorted(v1_modules):
        module_paths.append(BACKEND_ROOT / "api" / "v1" / f"{mod}.py")
    module_paths.extend(sorted(domains_modules))

    # Filter missing files (in case registry is out of sync)
    return [p for p in module_paths if p.exists()]


def main() -> int:
    all_routes: list[tuple[str, str, str, int]] = []
    module_files = _parse_registry_for_module_paths()
    if not module_files:
        print("FAIL: no module files detected from backend/api/registry.py")
        return 2

    for py_file in module_files:
        all_routes.extend(extract_routes(py_file))

    # Group by (method, path)
    endpoint_map: dict[tuple[str, str], list[tuple[str, int]]] = defaultdict(list)
    for method, path, file, lineno in all_routes:
        endpoint_map[(method, path)].append((file, lineno))

    duplicates = {k: v for k, v in endpoint_map.items() if len(v) > 1}

    if not duplicates:
        print(
            f"OK: {len(all_routes)} endpoints scanned across {len(module_files)} mounted modules, no duplicates found."
        )
        return 0

    print(f"FAIL: {len(duplicates)} duplicate endpoint(s) found:\n")
    for (method, path), locations in sorted(duplicates.items()):
        print(f"  {method} {path}")
        for file, lineno in locations:
            print(f"    - {file}:{lineno}")
        print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
