#!/usr/bin/env python3
"""
STEP 2: LINE-SPAN ENDPOINT SCANNER
Parses AST for FastAPI/APIRouter route decorators and captures line spans.
"""

import ast
import csv
import json
import os
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Endpoint:
    """Represents a single API endpoint."""

    file_path: str
    router_name: str
    method: str
    path: str
    handler: str
    decorator_line: int
    handler_start_line: int
    handler_end_line: int
    tags: List[str] = field(default_factory=list)
    response_model: Optional[str] = None
    status_code: Optional[int] = None
    auth_required: bool = True
    db_tables: List[str] = field(default_factory=list)
    external_calls: List[str] = field(default_factory=list)


class EndpointScanner(ast.NodeVisitor):
    """AST visitor to extract FastAPI route information."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.endpoints: List[Endpoint] = []
        self.current_class = None
        self.current_function = None
        self.indent_stack = []

    def scan(self, source: str) -> List[Endpoint]:
        """Parse source code and extract endpoints."""
        tree = ast.parse(source, filename=self.file_path)
        self.visit(tree)
        return self.endpoints

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions to find handlers."""
        func_name = node.name
        func_start = node.lineno
        func_end = node.end_lineno or node.lineno

        # Look for route decorator on this function
        for decorator in node.decorator_list:
            endpoint = self._extract_from_decorator(
                decorator, func_name, func_start, func_end, node
            )
            if endpoint:
                endpoint.handler_start_line = func_start
                endpoint.handler_end_line = func_end
                self.endpoints.append(endpoint)

        # Continue visiting child nodes
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Handle async function definitions."""
        self.visit_FunctionDef(node)

    def _extract_from_decorator(
        self,
        decorator: ast.AST,
        func_name: str,
        func_start: int,
        func_end: int,
        node: ast.FunctionDef,
    ) -> Optional[Endpoint]:
        """Extract endpoint info from a decorator."""

        # Check for router decorators: @router.get, @router.post, etc.
        if isinstance(decorator, ast.Attribute):
            if decorator.attr in (
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
            ):
                method = decorator.attr.upper()
                # Get path from decorator arguments
                path = self._get_path_from_decorator(decorator)
                router_name = self._get_router_name(decorator)

                # Get tags and other kwargs
                tags = self._get_tags_from_decorator(decorator)
                response_model = self._get_response_model_from_decorator(decorator)

                return Endpoint(
                    file_path=self.file_path,
                    router_name=router_name,
                    method=method,
                    path=path,
                    handler=func_name,
                    decorator_line=decorator.lineno,
                    handler_start_line=func_start,
                    handler_end_line=func_end,
                    tags=tags,
                    response_model=response_model,
                )

        # Check for app decorators: @app.get, @app.post, etc.
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr in (
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "options",
                    "head",
                ):
                    method = decorator.func.attr.upper()
                    path = self._get_path_from_call_args(decorator)
                    router_name = "app"

                    return Endpoint(
                        file_path=self.file_path,
                        router_name=router_name,
                        method=method,
                        path=path,
                        handler=func_name,
                        decorator_line=decorator.lineno,
                        handler_start_line=func_start,
                        handler_end_line=func_end,
                        tags=self._get_tags_from_call_args(decorator),
                        response_model=self._get_response_model_from_call_args(
                            decorator
                        ),
                    )

        return None

    def _get_path_from_decorator(self, decorator: ast.Attribute) -> str:
        """Extract path from router decorator like @router.get('/path')."""
        if isinstance(decorator, ast.Attribute):
            # Check if there's a Call node
            if hasattr(decorator, "ctx") and isinstance(decorator.ctx, ast.Load):
                pass

        # Look for path in parent Call node
        for node in ast.walk(decorator):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value.startswith("/"):
                    return node.value
            elif isinstance(node, ast.Str):  # Python 3.7/3.8 compat
                if node.s.startswith("/"):
                    return node.s

        return ""

    def _get_path_from_call_args(self, decorator: ast.Call) -> str:
        """Extract path from app.get('/path', ...) style decorators."""
        if decorator.args:
            for arg in decorator.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if arg.value.startswith("/"):
                        return arg.value
                elif isinstance(arg, ast.Str) and arg.s.startswith("/"):
                    return arg.s

        # Check keyword arguments
        for kw in decorator.keywords:
            if kw.arg == "path":
                if isinstance(kw.value, ast.Constant):
                    return kw.value.value
                elif isinstance(kw.value, ast.Str):
                    return kw.value.s

        return ""

    def _get_router_name(self, decorator: ast.Attribute) -> str:
        """Extract the router variable name."""
        if isinstance(decorator, ast.Attribute):
            if isinstance(decorator.value, ast.Name):
                return decorator.value.id
        return "unknown"

    def _get_tags_from_decorator(self, decorator: ast.Attribute) -> List[str]:
        """Extract tags from decorator."""
        tags = []
        for node in ast.walk(decorator):
            if isinstance(node, ast.Constant) and isinstance(node.value, list):
                tags = node.value
            elif isinstance(node, ast.Str):
                if node.s not in (
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "options",
                    "head",
                ):
                    if not node.s.startswith("/"):
                        tags.append(node.s)
        return tags

    def _get_response_model_from_decorator(
        self, decorator: ast.Attribute
    ) -> Optional[str]:
        """Extract response_model from decorator."""
        for node in ast.walk(decorator):
            if isinstance(node, ast.keyword):
                if node.arg == "response_model":
                    if isinstance(node.value, ast.Name):
                        return node.value.id
                    elif isinstance(node.value, ast.Constant):
                        return str(node.value.value)
        return None

    def _get_tags_from_call_args(self, decorator: ast.Call) -> List[str]:
        """Extract tags from call-style decorator."""
        tags = []
        for kw in decorator.keywords:
            if kw.arg == "tags":
                if isinstance(kw.value, ast.List):
                    for elem in kw.value.elts:
                        if isinstance(elem, ast.Constant):
                            tags.append(elem.value)
                        elif isinstance(elem, ast.Str):
                            tags.append(elem.s)
        return tags

    def _get_response_model_from_call_args(self, decorator: ast.Call) -> Optional[str]:
        """Extract response_model from call-style decorator."""
        for kw in decorator.keywords:
            if kw.arg == "response_model":
                if isinstance(kw.value, ast.Name):
                    return kw.value.id
                elif isinstance(kw.value, ast.Constant):
                    return str(kw.value.value)
        return None


def scan_file(file_path: str) -> List[Endpoint]:
    """Scan a single Python file for endpoints."""
    try:
        # Use utf-8-sig to safely strip BOMs that break ast.parse
        with open(file_path, "r", encoding="utf-8-sig") as f:
            source = f.read()

        scanner = EndpointScanner(file_path)
        return scanner.scan(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {file_path}: {e}")
        return []


def scan_directory(
    directory: str, extensions: Tuple[str] = (".py",)
) -> Dict[str, List[Endpoint]]:
    """Scan all Python files in a directory recursively."""
    endpoints_by_file = {}
    directory_path = Path(directory)

    for py_file in directory_path.rglob("*.py"):
        file_endpoints = scan_file(str(py_file))
        if file_endpoints:
            endpoints_by_file[str(py_file)] = file_endpoints

    return endpoints_by_file


def detect_db_tables(file_path: str, source: str) -> List[str]:
    """Detect database table references in source code."""
    tables = []

    # Common patterns for table access
    patterns = [
        r'\.table\s*\(\s*["\']([^"\']+)["\']',
        r'\.from_\s*\(\s*["\']([^"\']+)["\']',
        r'table_name\s*=\s*["\']([^"\']+)["\']',
        r'Table\s*\(\s*["\']([^"\']+)["\']',
    ]

    import re

    for pattern in patterns:
        matches = re.findall(pattern, source)
        tables.extend(matches)

    return list(set(tables))


def detect_external_calls(source: str) -> List[str]:
    """Detect external service calls in source code."""
    external = []

    # Common external service patterns
    patterns = [
        r"from\s+(supabase|requests|httpx|vertexai|google\.)",
        r"import\s+(supabase|requests|httpx|vertexai)",
        r"phonepe|resend|openai|anthropic",
    ]

    import re

    for pattern in patterns:
        matches = re.findall(pattern, source, re.IGNORECASE)
        external.extend(matches)

    return list(set(external))


def enrich_endpoints(
    endpoints_by_file: Dict[str, List[Endpoint]]
) -> Dict[str, List[Endpoint]]:
    """Enrich endpoints with DB table and external call info."""
    for file_path, endpoints in endpoints_by_file.items():
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                source = f.read()

            tables = detect_db_tables(file_path, source)
            external = detect_external_calls(source)

            for endpoint in endpoints:
                endpoint.db_tables = tables
                endpoint.external_calls = external
        except Exception:
            pass

    return endpoints_by_file


def save_json(endpoints_by_file: Dict[str, List[Endpoint]], output_path: str):
    """Save endpoints to JSON file."""
    output = {
        "scan_metadata": {
            "total_files": len(endpoints_by_file),
            "total_endpoints": sum(len(eps) for eps in endpoints_by_file.values()),
        },
        "endpoints_by_file": {
            fp: [asdict(ep) for ep in eps] for fp, eps in endpoints_by_file.items()
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"JSON output saved to {output_path}")


def save_csv(endpoints_by_file: Dict[str, List[Endpoint]], output_path: str):
    """Save endpoints to CSV file."""
    fieldnames = [
        "file_path",
        "router_name",
        "method",
        "path",
        "handler",
        "decorator_line",
        "handler_start_line",
        "handler_end_line",
        "tags",
        "response_model",
        "status_code",
        "auth_required",
        "db_tables",
        "external_calls",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for file_path, endpoints in sorted(endpoints_by_file.items()):
            for ep in sorted(endpoints, key=lambda x: (x.file_path, x.decorator_line)):
                row = asdict(ep)
                row["file_path"] = file_path
                row["tags"] = "|".join(ep.tags) if ep.tags else ""
                row["db_tables"] = "|".join(ep.db_tables) if ep.db_tables else ""
                row["external_calls"] = (
                    "|".join(ep.external_calls) if ep.external_calls else ""
                )
                writer.writerow(row)

    print(f"CSV output saved to {output_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan FastAPI endpoints with line spans"
    )
    parser.add_argument(
        "directory", nargs="?", default="backend", help="Directory to scan"
    )
    parser.add_argument(
        "--output-json", default="docs/static_endpoints.json", help="JSON output path"
    )
    parser.add_argument(
        "--output-csv", default="docs/route_catalog.csv", help="CSV output path"
    )
    parser.add_argument(
        "--enrich", action="store_true", help="Enrich with DB/external info"
    )

    args = parser.parse_args()

    print(f"Scanning directory: {args.directory}")
    endpoints_by_file = scan_directory(args.directory)

    if args.enrich:
        print("Enriching endpoints with DB/external info...")
        endpoints_by_file = enrich_endpoints(endpoints_by_file)

    total_endpoints = sum(len(eps) for eps in endpoints_by_file.values())
    print(f"Found {total_endpoints} endpoints in {len(endpoints_by_file)} files")

    save_json(endpoints_by_file, args.output_json)
    save_csv(endpoints_by_file, args.output_csv)

    return 0


if __name__ == "__main__":
    sys.exit(main())
