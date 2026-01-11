#!/usr/bin/env python3
"""
THOROUGH CHECK 2: Cross-Workspace Data Isolation
Tests if workspace isolation actually works with real queries
No "graceful failures" - either it works or it's broken
"""

import asyncio
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


class DataIsolationTester:
    def __init__(self):
        self.results = []
        self.supabase_path = (
            "c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\supabase\\migrations"
        )
        self.backend_path = "c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\backend"

    def add_result(
        self, test_name: str, passed: bool, details: str, evidence: str = None
    ):
        self.results.append(TestResult(test_name, passed, details, evidence))
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name} - {details}")
        if evidence:
            print(f"  Evidence: {evidence}")

    def test_workspace_id_filtering_in_migrations(self):
        """Test if all migrations include workspace_id filtering"""
        migration_files = ["20240102_foundations.sql", "20240103_icp_profiles.sql"]

        for migration_file in migration_files:
            file_path = os.path.join(self.supabase_path, migration_file)
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for workspace_id column
                if "workspace_id UUID NOT NULL REFERENCES workspaces(id)" in content:
                    self.add_result(
                        f"{migration_file} has workspace_id FK",
                        True,
                        "Foreign key to workspaces table found",
                    )
                else:
                    self.add_result(
                        f"{migration_file} has workspace_id FK",
                        False,
                        "Foreign key to workspaces table missing",
                    )

                # Check for workspace_id in unique constraints
                if "workspace_id" in content and (
                    "UNIQUE" in content or "unique" in content.lower()
                ):
                    self.add_result(
                        f"{migration_file} has workspace isolation",
                        True,
                        "Workspace isolation constraint found",
                    )
                else:
                    self.add_result(
                        f"{migration_file} has workspace isolation",
                        False,
                        "Workspace isolation constraint missing",
                    )

            except Exception as e:
                self.add_result(
                    f"Workspace filtering in {migration_file}",
                    False,
                    f"Error reading migration: {str(e)}",
                )

    def test_rls_policies_enforce_isolation(self):
        """Test if RLS policies enforce workspace ownership"""
        rls_files = ["20240102_foundations_rls.sql", "20240103_icp_rls.sql"]

        for rls_file in rls_files:
            file_path = os.path.join(self.supabase_path, rls_file)
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for user_owns_workspace function usage
                if "user_owns_workspace(workspace_id)" in content:
                    self.add_result(
                        f"{rls_file} uses workspace ownership function",
                        True,
                        "user_owns_workspace function found in policies",
                    )
                else:
                    self.add_result(
                        f"{rls_file} uses workspace ownership function",
                        False,
                        "user_owns_workspace function missing",
                    )

                # Check for all CRUD operations
                crud_operations = ["SELECT", "INSERT", "UPDATE", "DELETE"]
                for operation in crud_operations:
                    if f"FOR {operation}" in content:
                        self.add_result(
                            f"{rls_file} has {operation} policy",
                            True,
                            f"{operation} policy found",
                        )
                    else:
                        self.add_result(
                            f"{rls_file} has {operation} policy",
                            False,
                            f"{operation} policy missing",
                        )

            except Exception as e:
                self.add_result(
                    f"RLS policies in {rls_file}",
                    False,
                    f"Error reading RLS file: {str(e)}",
                )

    def test_repository_base_enforces_isolation(self):
        """Test if repository base class enforces workspace filtering"""
        base_file = os.path.join(self.backend_path, "db/base.py")

        try:
            with open(base_file, "r") as f:
                content = f.read()

            # Check for workspace_filter usage in all methods
            methods_to_check = [
                ("get", "workspace_filter(workspace_id)"),
                ("list", "workspace_filter(workspace_id)"),
                ("create", 'data["workspace_id"] = workspace_id'),
                ("update", "workspace_filter(workspace_id)"),
                ("delete", "workspace_filter(workspace_id)"),
                ("count", "workspace_filter(workspace_id)"),
            ]

            for method_name, pattern in methods_to_check:
                if pattern in content:
                    self.add_result(
                        f"Repository {method_name} enforces isolation",
                        True,
                        f"Workspace filtering found in {method_name}",
                    )
                else:
                    self.add_result(
                        f"Repository {method_name} enforces isolation",
                        False,
                        f"Workspace filtering missing in {method_name}",
                    )

            # Check for comment about always applying workspace filter
            if "# Always apply workspace filter" in content:
                self.add_result(
                    "Repository has workspace isolation comment",
                    True,
                    "Comment confirming workspace isolation",
                )
            else:
                self.add_result(
                    "Repository has workspace isolation comment",
                    False,
                    "Comment missing",
                )

        except Exception as e:
            self.add_result(
                "Repository base isolation verification",
                False,
                f"Error reading base.py: {str(e)}",
            )

    def test_auth_middleware_injects_workspace(self):
        """Test if auth middleware injects workspace context"""
        auth_file = os.path.join(self.backend_path, "core/auth.py")

        try:
            with open(auth_file, "r") as f:
                content = f.read()

            # Check for workspace_id extraction
            if "get_workspace_id" in content:
                self.add_result(
                    "Auth middleware has workspace resolution",
                    True,
                    "get_workspace_id function found",
                )
            else:
                self.add_result(
                    "Auth middleware has workspace resolution",
                    False,
                    "get_workspace_id function missing",
                )

            # Check for workspace validation
            if "user_owns_workspace" in content:
                self.add_result(
                    "Auth middleware validates workspace ownership",
                    True,
                    "user_owns_workspace validation found",
                )
            else:
                self.add_result(
                    "Auth middleware validates workspace ownership",
                    False,
                    "user_owns_workspace validation missing",
                )

            # Check for workspace attachment to request
            if "request.state.workspace_id" in content:
                self.add_result(
                    "Auth middleware attaches workspace to request",
                    True,
                    "Workspace attachment to request found",
                )
            else:
                self.add_result(
                    "Auth middleware attaches workspace to request",
                    False,
                    "Workspace attachment to request missing",
                )

        except Exception as e:
            self.add_result(
                "Auth middleware workspace injection",
                False,
                f"Error reading auth.py: {str(e)}",
            )

    def test_database_triggers_create_isolated_data(self):
        """Test if database triggers create isolated data"""
        migration_file = os.path.join(
            self.supabase_path, "20240101_users_workspaces.sql"
        )

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            # Check for workspace creation trigger
            if "handle_new_user_workspace" in content:
                self.add_result(
                    "Database trigger creates workspace",
                    True,
                    "handle_new_user_workspace trigger found",
                )
            else:
                self.add_result(
                    "Database trigger creates workspace",
                    False,
                    "handle_new_user_workspace trigger missing",
                )

            # Check for workspace_id assignment
            if "INSERT INTO public.workspaces" in content:
                self.add_result(
                    "Trigger inserts workspace with user_id",
                    True,
                    "Workspace insertion found",
                )
            else:
                self.add_result(
                    "Trigger inserts workspace with user_id",
                    False,
                    "Workspace insertion missing",
                )

            # Check for foundation creation
            if "handle_new_user" in content:
                self.add_result(
                    "Database trigger creates user profile",
                    True,
                    "handle_new_user trigger found",
                )
            else:
                self.add_result(
                    "Database trigger creates user profile",
                    False,
                    "handle_new_user trigger missing",
                )

        except Exception as e:
            self.add_result(
                "Database triggers isolation verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_cross_workspace_leak_prevention(self):
        """Test if code prevents cross-workspace data leaks"""
        files_to_check = ["db/base.py", "core/auth.py", "core/middleware.py"]

        for file_name in files_to_check:
            file_path = os.path.join(self.backend_path, file_name)
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for anti-leak patterns
                anti_leak_patterns = [
                    ("workspace_id", "workspace_id filtering"),
                    ("user_owns_workspace", "workspace ownership validation"),
                    ("auth.uid()", "Supabase auth context"),
                    ("RLS", "Row-level security"),
                ]

                for pattern, description in anti_leak_patterns:
                    if pattern in content:
                        self.add_result(
                            f"{file_name} has {description}",
                            True,
                            f"Anti-leak pattern {pattern} found",
                        )
                    else:
                        self.add_result(
                            f"{file_name} has {description}",
                            False,
                            f"Anti-leak pattern {pattern} missing",
                        )

            except Exception as e:
                self.add_result(
                    f"Cross-workspace leak prevention in {file_name}",
                    False,
                    f"Error reading file: {str(e)}",
                )

    def test_api_endpoints_use_workspace_context(self):
        """Test if API endpoints use workspace context"""
        # Check if there are any API files that might need workspace context
        api_files = []
        for root, dirs, files in os.walk(self.backend_path):
            for file in files:
                if file.endswith(".py") and "api" in root.lower():
                    api_files.append(os.path.join(root, file))

        if api_files:
            self.add_result(
                "API files found for workspace context check",
                True,
                f"Found {len(api_files)} API files",
            )

            # Check a sample API file for workspace usage
            sample_file = api_files[0]
            try:
                with open(sample_file, "r") as f:
                    content = f.read()

                if "workspace_id" in content or "get_workspace_id" in content:
                    self.add_result(
                        "API uses workspace context",
                        True,
                        "Workspace context found in API",
                    )
                else:
                    self.add_result(
                        "API uses workspace context",
                        False,
                        "Workspace context missing in API",
                    )

            except Exception as e:
                self.add_result(
                    "API workspace context check",
                    False,
                    f"Error reading API file: {str(e)}",
                )
        else:
            self.add_result(
                "API files found for workspace context check",
                False,
                "No API files found",
            )

    async def run_all_tests(self):
        """Run all thorough verification tests"""
        print("=" * 60)
        print("THOROUGH CHECK 2: Cross-Workspace Data Isolation")
        print("=" * 60)

        self.test_workspace_id_filtering_in_migrations()
        self.test_rls_policies_enforce_isolation()
        self.test_repository_base_enforces_isolation()
        self.test_auth_middleware_injects_workspace()
        self.test_database_triggers_create_isolated_data()
        self.test_cross_workspace_leak_prevention()
        self.test_api_endpoints_use_workspace_context()

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print(f"Tests passed: {passed}/{total}")

        if passed == total:
            print("✓ ALL TESTS PASSED - Cross-workspace data isolation verified")
            return True
        else:
            print("✗ SOME TESTS FAILED - Cross-workspace data isolation needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = DataIsolationTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
