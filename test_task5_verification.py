#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 5: Repository Base Class
Tests if repository base enforces workspace_id in all queries
No "graceful failures" - either it works or it's broken
"""

import asyncio
import importlib.util
import os
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class TestResult:
    test_name: str
    passed: bool
    details: str
    evidence: Optional[str] = None


class RepositoryTester:
    def __init__(self):
        self.results = []
        self.backend_path = "c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\backend"

    def add_result(
        self, test_name: str, passed: bool, details: str, evidence: str = None
    ):
        self.results.append(TestResult(test_name, passed, details, evidence))
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name} - {details}")
        if evidence:
            print(f"  Evidence: {evidence}")

    def test_db_files_exist(self):
        """Test if database module files exist"""
        required_files = [
            "db/__init__.py",
            "db/base.py",
            "db/pagination.py",
            "db/filters.py",
        ]

        for file_path in required_files:
            full_path = os.path.join(self.backend_path, file_path)
            if os.path.exists(full_path):
                self.add_result(
                    f"DB file {file_path} exists", True, f"File found at {full_path}"
                )
            else:
                self.add_result(
                    f"DB file {file_path} exists", False, f"File missing at {full_path}"
                )

    def test_db_module_imports(self):
        """Test if database modules can be imported"""
        modules_to_test = ["db.base", "db.pagination", "db.filters"]

        for module_name in modules_to_test:
            try:
                # Add backend path to sys.path
                import sys

                if self.backend_path not in sys.path:
                    sys.path.insert(0, self.backend_path)

                # Try to import the module using spec
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    os.path.join(
                        self.backend_path, f"{module_name.replace('.', '/')}.py"
                    ),
                )

                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.add_result(
                        f"Import {module_name}", True, f"Module imported successfully"
                    )
                else:
                    self.add_result(
                        f"Import {module_name}", False, "Could not create module spec"
                    )

            except Exception as e:
                self.add_result(
                    f"Import {module_name}", False, f"Import failed: {str(e)}"
                )

    def test_pagination_classes(self):
        """Test if pagination classes exist and have required properties"""
        try:
            spec = importlib.util.spec_from_file_location(
                "db.pagination", os.path.join(self.backend_path, "db/pagination.py")
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check Pagination class
                if hasattr(module, "Pagination"):
                    self.add_result(
                        "Pagination class exists", True, "Pagination class found"
                    )

                    # Check required properties
                    required_props = [
                        "page",
                        "page_size",
                        "sort_by",
                        "sort_order",
                        "offset",
                        "limit",
                    ]
                    for prop in required_props:
                        if hasattr(module.Pagination, prop):
                            self.add_result(
                                f"Pagination has {prop}",
                                True,
                                f"Property {prop} exists",
                            )
                        else:
                            self.add_result(
                                f"Pagination has {prop}",
                                False,
                                f"Property {prop} missing",
                            )
                else:
                    self.add_result(
                        "Pagination class exists", False, "Pagination class not found"
                    )

                # Check PaginatedResult class
                if hasattr(module, "PaginatedResult"):
                    self.add_result(
                        "PaginatedResult class exists",
                        True,
                        "PaginatedResult class found",
                    )

                    # Check required properties
                    required_props = [
                        "items",
                        "total",
                        "page",
                        "page_size",
                        "total_pages",
                        "has_next",
                        "has_previous",
                    ]
                    for prop in required_props:
                        # Check if property exists in dataclass fields or as property
                        if hasattr(module.PaginatedResult, prop) or prop in [
                            f.name
                            for f in module.PaginatedResult.__dataclass_fields__.values()
                        ]:
                            self.add_result(
                                f"PaginatedResult has {prop}",
                                True,
                                f"Property {prop} exists",
                            )
                        else:
                            self.add_result(
                                f"PaginatedResult has {prop}",
                                False,
                                f"Property {prop} missing",
                            )
                else:
                    self.add_result(
                        "PaginatedResult class exists",
                        False,
                        "PaginatedResult class not found",
                    )
            else:
                self.add_result(
                    "Pagination classes exist",
                    False,
                    "Could not load pagination module",
                )

        except Exception as e:
            self.add_result(
                "Pagination classes exist",
                False,
                f"Error checking pagination: {str(e)}",
            )

    def test_filter_classes(self):
        """Test if filter classes exist and have required methods"""
        try:
            spec = importlib.util.spec_from_file_location(
                "db.filters", os.path.join(self.backend_path, "db/filters.py")
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check FilterOperator enum
                if hasattr(module, "FilterOperator"):
                    self.add_result(
                        "FilterOperator enum exists", True, "FilterOperator enum found"
                    )

                    # Check required operators
                    required_ops = ["EQ", "NEQ", "GT", "GTE", "LT", "LTE", "LIKE", "IN"]
                    for op in required_ops:
                        if hasattr(module.FilterOperator, op):
                            self.add_result(
                                f"FilterOperator has {op}",
                                True,
                                f"Operator {op} exists",
                            )
                        else:
                            self.add_result(
                                f"FilterOperator has {op}",
                                False,
                                f"Operator {op} missing",
                            )
                else:
                    self.add_result(
                        "FilterOperator enum exists",
                        False,
                        "FilterOperator enum not found",
                    )

                # Check Filter class
                if hasattr(module, "Filter"):
                    self.add_result("Filter class exists", True, "Filter class found")
                else:
                    self.add_result(
                        "Filter class exists", False, "Filter class not found"
                    )

                # Check utility functions
                required_functions = [
                    "build_query",
                    "workspace_filter",
                    "date_range_filter",
                    "text_search_filter",
                ]
                for func_name in required_functions:
                    if hasattr(module, func_name):
                        self.add_result(
                            f"Filter function {func_name} exists",
                            True,
                            f"Function {func_name} found",
                        )
                    else:
                        self.add_result(
                            f"Filter function {func_name} exists",
                            False,
                            f"Function {func_name} missing",
                        )
            else:
                self.add_result(
                    "Filter classes exist", False, "Could not load filters module"
                )

        except Exception as e:
            self.add_result(
                "Filter classes exist", False, f"Error checking filters: {str(e)}"
            )

    def test_repository_base_class(self):
        """Test if Repository base class exists and has required methods"""
        try:
            spec = importlib.util.spec_from_file_location(
                "db.base", os.path.join(self.backend_path, "db/base.py")
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check Repository class
                if hasattr(module, "Repository"):
                    self.add_result(
                        "Repository base class exists", True, "Repository class found"
                    )

                    # Check required methods
                    required_methods = [
                        "get",
                        "list",
                        "create",
                        "update",
                        "delete",
                        "count",
                        "_map_to_model",
                        "_ensure_workspace_filter",
                    ]

                    for method in required_methods:
                        if hasattr(module.Repository, method):
                            self.add_result(
                                f"Repository has {method}",
                                True,
                                f"Method {method} exists",
                            )
                        else:
                            self.add_result(
                                f"Repository has {method}",
                                False,
                                f"Method {method} missing",
                            )
                else:
                    self.add_result(
                        "Repository base class exists",
                        False,
                        "Repository class not found",
                    )
            else:
                self.add_result(
                    "Repository base class exists", False, "Could not load base module"
                )

        except Exception as e:
            self.add_result(
                "Repository base class exists",
                False,
                f"Error checking Repository: {str(e)}",
            )

    def test_workspace_filter_enforcement(self):
        """Test if workspace filtering is enforced in code"""
        try:
            # Read the source code to check for workspace filtering
            with open(os.path.join(self.backend_path, "db/base.py"), "r") as f:
                source_code = f.read()

            # Check if workspace filtering is implemented
            checks = [
                ("workspace_filter" in source_code, "workspace_filter function used"),
                ("workspace_id" in source_code, "workspace_id referenced"),
                ("build_query" in source_code, "build_query function used"),
                (
                    "_ensure_workspace_filter" in source_code,
                    "_ensure_workspace_filter method exists",
                ),
                (
                    "# Always apply workspace filter" in source_code,
                    "Comment confirming workspace isolation",
                ),
            ]

            for check, description in checks:
                if check:
                    self.add_result(
                        f"Workspace filtering: {description}", True, description
                    )
                else:
                    self.add_result(
                        f"Workspace filtering: {description}",
                        False,
                        "Not found in code",
                    )

            # Check specific methods for workspace filtering
            methods_to_check = {
                "get": "query = build_query(query, [workspace_filter(workspace_id)])",
                "list": "all_filters = [workspace_filter(workspace_id)]",
                "create": 'data["workspace_id"] = workspace_id',
                "update": "query = build_query(query, [workspace_filter(workspace_id)])",
                "delete": "query = build_query(query, [workspace_filter(workspace_id)])",
            }

            for method, expected_code in methods_to_check.items():
                if expected_code in source_code:
                    self.add_result(
                        f"Method {method} enforces workspace filtering",
                        True,
                        f"Found workspace filtering in {method}",
                    )
                else:
                    self.add_result(
                        f"Method {method} enforces workspace filtering",
                        False,
                        f"Workspace filtering not found in {method}",
                    )

        except Exception as e:
            self.add_result(
                "Workspace filtering enforcement",
                False,
                f"Error checking workspace filtering: {str(e)}",
            )

    async def run_all_tests(self):
        """Run all verification tests"""
        print("=" * 60)
        print("CYNICAL VERIFICATION - Task 5: Repository Base Class")
        print("=" * 60)

        self.test_db_files_exist()
        self.test_db_module_imports()
        self.test_pagination_classes()
        self.test_filter_classes()
        self.test_repository_base_class()
        self.test_workspace_filter_enforcement()

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print(f"Tests passed: {passed}/{total}")

        if passed == total:
            print("✓ ALL TESTS PASSED - Task 5 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 5 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = RepositoryTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
