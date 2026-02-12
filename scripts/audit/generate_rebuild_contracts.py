#!/usr/bin/env python3
"""Generate rebuild contracts for API modules and frontend state modules."""

from __future__ import annotations

import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
API_PREFIX = "/api"
METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_path(*parts: str) -> str:
    path = "/".join(part.strip("/") for part in parts if part is not None)
    if not path:
        return "/"
    normalized = "/" + path
    normalized = re.sub(r"/{2,}", "/", normalized)
    if normalized != "/" and normalized.endswith("/"):
        normalized = normalized[:-1]
    return normalized


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_router_specs(registry_path: Path) -> list[dict[str, Any]]:
    tree = ast.parse(read_text(registry_path), filename=str(registry_path))
    specs: list[dict[str, Any]] = []
    list_node: ast.List | None = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "_ROUTER_SPECS" in targets and isinstance(node.value, ast.List):
                list_node = node.value
                break
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "_ROUTER_SPECS":
                if isinstance(node.value, ast.List):
                    list_node = node.value
                    break

    if list_node is None:
        return specs

    for elt in list_node.elts:
        try:
            if not isinstance(elt, ast.Tuple) or len(elt.elts) != 3:
                continue
            module_name = ast.literal_eval(elt.elts[0])
            attr_name = ast.literal_eval(elt.elts[1])
            required = ast.literal_eval(elt.elts[2])
            specs.append(
                {
                    "module": module_name,
                    "attr_name": attr_name,
                    "required": bool(required),
                }
            )
        except Exception:
            continue
    return specs


def parse_router_prefixes(module_tree: ast.Module) -> dict[str, str]:
    router_prefixes: dict[str, str] = {}
    for node in module_tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        if not isinstance(node.value.func, ast.Name) or node.value.func.id != "APIRouter":
            continue
        prefix = ""
        for kw in node.value.keywords:
            if kw.arg == "prefix":
                try:
                    prefix = ast.literal_eval(kw.value)
                except Exception:
                    prefix = ""
        router_prefixes[target.id] = prefix
    return router_prefixes


def parse_decorator_path(dec: ast.Call) -> str:
    if dec.args:
        first = dec.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    for kw in dec.keywords:
        if kw.arg in {"path", "url"}:
            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                return kw.value.value
    return "/"


def parse_decorator_kw(dec: ast.Call, key: str) -> str | int | None:
    for kw in dec.keywords:
        if kw.arg != key:
            continue
        if isinstance(kw.value, ast.Name):
            return kw.value.id
        if isinstance(kw.value, ast.Constant):
            return kw.value.value
        return ast.unparse(kw.value) if hasattr(ast, "unparse") else None
    return None


def parse_endpoints(module_tree: ast.Module, router_prefixes: dict[str, str]) -> list[dict[str, Any]]:
    endpoints: list[dict[str, Any]] = []
    for node in module_tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        handler_name = node.name
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            if not isinstance(dec.func, ast.Attribute):
                continue
            method = dec.func.attr.lower()
            if method not in METHODS:
                continue
            router_name = None
            if isinstance(dec.func.value, ast.Name):
                router_name = dec.func.value.id
            if not router_name:
                continue
            prefix = router_prefixes.get(router_name, "")
            route_path = parse_decorator_path(dec)
            full_path = normalize_path(API_PREFIX, prefix, route_path)
            endpoints.append(
                {
                    "handler": handler_name,
                    "method": method.upper(),
                    "router_name": router_name,
                    "router_prefix": prefix,
                    "route_path": route_path,
                    "full_path": full_path,
                    "line": node.lineno,
                    "response_model": parse_decorator_kw(dec, "response_model"),
                    "status_code": parse_decorator_kw(dec, "status_code"),
                }
            )
    return endpoints


def build_api_contract() -> dict[str, Any]:
    registry_path = ROOT / "backend" / "api" / "registry.py"
    specs = parse_router_specs(registry_path)
    modules: list[dict[str, Any]] = []

    for spec in specs:
        module_name = spec["module"]
        module_file = ROOT / "backend" / "api" / "v1" / f"{module_name}.py"
        module_data: dict[str, Any] = {
            "module": module_name,
            "file": str(module_file.relative_to(ROOT)).replace("\\", "/"),
            "attr_name": spec["attr_name"],
            "required": spec["required"],
            "registered": module_file.exists(),
            "routers": [],
            "endpoints": [],
        }
        if module_file.exists():
            tree = ast.parse(read_text(module_file), filename=str(module_file))
            prefixes = parse_router_prefixes(tree)
            module_data["routers"] = [
                {"name": name, "prefix": prefix} for name, prefix in sorted(prefixes.items())
            ]
            module_data["endpoints"] = parse_endpoints(tree, prefixes)
        modules.append(module_data)

    all_endpoints = sum(len(m["endpoints"]) for m in modules)
    return {
        "generated_at": now_iso(),
        "api_prefix": API_PREFIX,
        "registry_file": str(registry_path.relative_to(ROOT)).replace("\\", "/"),
        "module_count": len(modules),
        "endpoint_count": all_endpoints,
        "modules": modules,
    }


def _extract_type_body(content: str, type_name: str) -> str:
    candidates = [
        re.compile(rf"interface\s+{re.escape(type_name)}\b"),
        re.compile(rf"type\s+{re.escape(type_name)}\s*=\s*"),
    ]
    start_idx = -1
    for pat in candidates:
        m = pat.search(content)
        if m:
            start_idx = m.end()
            break
    if start_idx == -1:
        return ""

    brace_start = content.find("{", start_idx)
    if brace_start == -1:
        return ""

    depth = 0
    for idx in range(brace_start, len(content)):
        ch = content[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return content[brace_start + 1 : idx]
    return ""


def parse_interface_members(content: str, interface_name: str) -> tuple[list[str], list[str]]:
    body = _extract_type_body(content, interface_name)
    if not body:
        return [], []

    state_fields: list[str] = []
    action_fields: list[str] = []

    members: list[str] = []
    depth = 0
    chunk = ""
    for ch in body:
        if ch in "{([":
            depth += 1
        elif ch in "})]":
            depth -= 1

        if ch == ";" and depth == 0:
            member = re.sub(r"\s+", " ", chunk).strip()
            if member:
                members.append(member)
            chunk = ""
            continue
        chunk += ch

    for member in members:
        if member.startswith("//"):
            continue
        match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+)$", member)
        if not match:
            continue
        name = match.group(1)
        type_expr = match.group(2)
        if "=>" in type_expr:
            action_fields.append(name)
        else:
            state_fields.append(name)
    return state_fields, action_fields


def find_consumers(hook_name: str, file_exclude: str) -> list[str]:
    consumers: list[str] = []
    for path in (ROOT / "src").rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if rel == file_exclude:
            continue
        text = read_text(path)
        if hook_name in text:
            consumers.append(rel)
    return sorted(consumers)


def build_frontend_state_contract() -> dict[str, Any]:
    stores: list[dict[str, Any]] = []
    stores_dir = ROOT / "src" / "stores"
    for path in sorted(stores_dir.glob("*.ts")):
        content = read_text(path)
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        hook_match = re.search(r"export const (use[A-Za-z0-9_]+Store)\s*=\s*create", content)
        hook_name = hook_match.group(1) if hook_match else path.stem

        generic_match = re.search(r"create<([A-Za-z0-9_]+)>", content)
        interface_name = generic_match.group(1) if generic_match else ""
        state_fields, action_fields = (
            parse_interface_members(content, interface_name) if interface_name else ([], [])
        )

        services = sorted(set(re.findall(r'from\s+"@/services/([^"]+)"', content)))
        stores.append(
            {
                "hook": hook_name,
                "file": rel,
                "interface": interface_name,
                "state_fields": state_fields,
                "action_fields": action_fields,
                "service_dependencies": services,
                "consumer_files": find_consumers(hook_name, rel),
            }
        )

    workspace_path = ROOT / "src" / "components" / "workspace" / "WorkspaceProvider.tsx"
    workspace_content = read_text(workspace_path)
    ws_state, ws_actions = parse_interface_members(workspace_content, "WorkspaceContextValue")
    workspace_hook = "useWorkspace"
    workspace_rel = str(workspace_path.relative_to(ROOT)).replace("\\", "/")

    return {
        "generated_at": now_iso(),
        "store_count": len(stores),
        "stores": stores,
        "workspace_context": {
            "hook": workspace_hook,
            "file": workspace_rel,
            "state_fields": ws_state,
            "action_fields": ws_actions,
            "storage_key": "raptorflow.workspace_id",
            "consumer_files": find_consumers(workspace_hook, workspace_rel),
        },
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_api_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# API Contract Map")
    lines.append("")
    lines.append(f"- Generated: `{payload['generated_at']}`")
    lines.append(f"- API Prefix: `{payload['api_prefix']}`")
    lines.append(f"- Modules: `{payload['module_count']}`")
    lines.append(f"- Endpoints: `{payload['endpoint_count']}`")
    lines.append("")
    for module in payload["modules"]:
        lines.append(f"## `{module['module']}`")
        lines.append("")
        lines.append(f"- File: `{module['file']}`")
        lines.append(f"- Required: `{module['required']}`")
        if module["routers"]:
            router_desc = ", ".join(
                f"`{r['name']}` -> `{r['prefix']}`" for r in module["routers"]
            )
            lines.append(f"- Routers: {router_desc}")
        if module["endpoints"]:
            lines.append("- Endpoints:")
            for ep in module["endpoints"]:
                lines.append(
                    f"  - `{ep['method']}` `{ep['full_path']}` ({ep['handler']}, router `{ep['router_name']}`)"
                )
        else:
            lines.append("- Endpoints: none")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_state_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Frontend State Map")
    lines.append("")
    lines.append(f"- Generated: `{payload['generated_at']}`")
    lines.append(f"- Zustand Stores: `{payload['store_count']}`")
    lines.append("")
    for store in payload["stores"]:
        lines.append(f"## `{store['hook']}`")
        lines.append("")
        lines.append(f"- File: `{store['file']}`")
        lines.append(f"- State Fields: `{', '.join(store['state_fields']) or '-'}`")
        lines.append(f"- Action Fields: `{', '.join(store['action_fields']) or '-'}`")
        lines.append(
            f"- Service Dependencies: `{', '.join(store['service_dependencies']) or '-'}`"
        )
        lines.append(f"- Consumer Files: `{len(store['consumer_files'])}`")
        lines.append("")

    ws = payload["workspace_context"]
    lines.append(f"## `{ws['hook']}`")
    lines.append("")
    lines.append(f"- File: `{ws['file']}`")
    lines.append(f"- State Fields: `{', '.join(ws['state_fields']) or '-'}`")
    lines.append(f"- Action Fields: `{', '.join(ws['action_fields']) or '-'}`")
    lines.append(f"- Storage Key: `{ws['storage_key']}`")
    lines.append(f"- Consumer Files: `{len(ws['consumer_files'])}`")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    contracts_dir = ROOT / "documentation" / "contracts"

    api_payload = build_api_contract()
    state_payload = build_frontend_state_contract()

    write_json(contracts_dir / "api-contract-map.json", api_payload)
    write_json(contracts_dir / "frontend-state-map.json", state_payload)
    write_api_markdown(contracts_dir / "api-contract-map.md", api_payload)
    write_state_markdown(contracts_dir / "frontend-state-map.md", state_payload)

    print("Wrote rebuild contracts:")
    print("- documentation/contracts/api-contract-map.json")
    print("- documentation/contracts/api-contract-map.md")
    print("- documentation/contracts/frontend-state-map.json")
    print("- documentation/contracts/frontend-state-map.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
