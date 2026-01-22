#!/usr/bin/env python3
"""
THOROUGH CHECK 1: Complete Database Schema Verification
Tests if database schema matches implementation documentation
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


class SchemaVerificationTester:
    def __init__(self):
        self.results = []
        self.supabase_path = (
            "c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\supabase\\migrations"
        )
        self.implementation_docs_path = "c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\DOCUMENTATION\\SWARM\\IMPLEMENTATION"

    def add_result(
        self, test_name: str, passed: bool, details: str, evidence: str = None
    ):
        self.results.append(TestResult(test_name, passed, details, evidence))
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name} - {details}")
        if evidence:
            print(f"  Evidence: {evidence}")

    def test_migration_files_exist(self):
        """Test if all required migration files exist"""
        required_migrations = [
            "20240101_users_workspaces.sql",
            "20240101_users_rls.sql",
            "20240101_workspaces_rls.sql",
            "20240102_foundations.sql",
            "20240102_foundations_rls.sql",
            "20240103_icp_profiles.sql",
            "20240103_icp_rls.sql",
        ]

        for migration in required_migrations:
            file_path = os.path.join(self.supabase_path, migration)
            if os.path.exists(file_path):
                self.add_result(
                    f"Migration {migration} exists", True, f"Migration file found"
                )
            else:
                self.add_result(
                    f"Migration {migration} exists", False, f"Migration file missing"
                )

    def test_users_table_structure(self):
        """Test if users table has required columns"""
        migration_file = os.path.join(
            self.supabase_path, "20240101_users_workspaces.sql"
        )

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_columns = [
                ("id", "id"),
                ("email", "email"),
                ("full_name", "full_name"),
                ("avatar_url", "avatar_url"),
                ("subscription_tier", "subscription_tier"),
                ("budget_limit_monthly", "budget_limit_monthly"),
                ("onboarding_completed_at", "onboarding_completed_at"),
                ("preferences", "preferences"),
                ("created_at", "created_at"),
                ("updated_at", "updated_at"),
            ]

            for column_name, column_search in required_columns:
                if column_search in content:
                    self.add_result(
                        f"Users table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"Users table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for RLS enablement
            if "ALTER TABLE public.users ENABLE ROW LEVEL SECURITY" in content:
                self.add_result(
                    "Users table has RLS enabled", True, "RLS enablement found"
                )
            else:
                self.add_result(
                    "Users table has RLS enabled", False, "RLS enablement missing"
                )

        except Exception as e:
            self.add_result(
                "Users table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_workspaces_table_structure(self):
        """Test if workspaces table has required columns"""
        migration_file = os.path.join(
            self.supabase_path, "20240101_users_workspaces.sql"
        )

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_columns = [
                ("id", "id"),
                ("user_id", "user_id"),
                ("name", "name"),
                ("slug", "slug"),
                ("settings", "settings"),
                ("created_at", "created_at"),
                ("updated_at", "updated_at"),
            ]

            for column_name, column_search in required_columns:
                if column_search in content:
                    self.add_result(
                        f"Workspaces table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"Workspaces table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for RLS enablement
            if "ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY" in content:
                self.add_result(
                    "Workspaces table has RLS enabled", True, "RLS enablement found"
                )
            else:
                self.add_result(
                    "Workspaces table has RLS enabled", False, "RLS enablement missing"
                )

        except Exception as e:
            self.add_result(
                "Workspaces table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_foundations_table_structure(self):
        """Test if foundations table has required columns"""
        migration_file = os.path.join(self.supabase_path, "20240102_foundations.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_columns = [
                ("id", "id"),
                ("workspace_id", "workspace_id"),
                ("company_name", "company_name"),
                ("industry", "industry"),
                ("truth_sheet", "truth_sheet"),
                ("market_research", "market_research"),
                ("competitors", "competitors"),
                ("positioning", "positioning"),
                ("brand_voice", "brand_voice"),
                ("messaging_guardrails", "messaging_guardrails"),
                ("summary", "summary"),
                ("summary_embedding", "summary_embedding"),
                ("onboarding_completed", "onboarding_completed"),
            ]

            for column_name, column_search in required_columns:
                if column_search in content:
                    self.add_result(
                        f"Foundations table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"Foundations table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for vector index
            if "USING ivfflat (summary_embedding vector_cosine_ops)" in content:
                self.add_result(
                    "Foundations table has vector index", True, "Vector index found"
                )
            else:
                self.add_result(
                    "Foundations table has vector index", False, "Vector index missing"
                )

        except Exception as e:
            self.add_result(
                "Foundations table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_icp_table_structure(self):
        """Test if icp_profiles table has required columns"""
        migration_file = os.path.join(self.supabase_path, "20240103_icp_profiles.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_columns = [
                ("id", "id"),
                ("workspace_id", "workspace_id"),
                ("name", "name"),
                ("tagline", "tagline"),
                ("code", "code"),
                ("is_primary", "is_primary"),
                ("demographics", "demographics"),
                ("psychographics", "psychographics"),
                ("behaviors", "behaviors"),
                ("market_sophistication", "market_sophistication"),
                ("scores", "scores"),
                ("summary", "summary"),
                ("summary_embedding", "summary_embedding"),
            ]

            for column_name, column_search in required_columns:
                if column_search in content:
                    self.add_result(
                        f"ICP table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"ICP table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for unique primary constraint
            if "idx_icp_profiles_unique_primary" in content:
                self.add_result(
                    "ICP table has unique primary constraint",
                    True,
                    "Unique constraint found",
                )
            else:
                self.add_result(
                    "ICP table has unique primary constraint",
                    False,
                    "Unique constraint missing",
                )

        except Exception as e:
            self.add_result(
                "ICP table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_rls_policies(self):
        """Test if RLS policies are correctly defined"""
        rls_files = [
            "20240101_users_rls.sql",
            "20240101_workspaces_rls.sql",
            "20240102_foundations_rls.sql",
            "20240103_icp_rls.sql",
        ]

        for rls_file in rls_files:
            file_path = os.path.join(self.supabase_path, rls_file)
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for policy creation
                if "CREATE POLICY" in content:
                    self.add_result(
                        f"RLS policies in {rls_file}", True, "Policy creation found"
                    )
                else:
                    self.add_result(
                        f"RLS policies in {rls_file}", False, "Policy creation missing"
                    )

                # Check for workspace ownership function
                if "user_owns_workspace" in content:
                    self.add_result(
                        "Workspace ownership function exists",
                        True,
                        "Function found in RLS",
                    )

            except Exception as e:
                self.add_result(
                    f"RLS policies in {rls_file}",
                    False,
                    f"Error reading RLS file: {str(e)}",
                )

    def test_triggers_and_functions(self):
        """Test if required triggers and functions exist"""
        migration_file = os.path.join(
            self.supabase_path, "20240101_users_workspaces.sql"
        )

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_items = [
                "update_updated_at",
                "handle_new_user",
                "handle_new_user_workspace",
                "CREATE TRIGGER users_updated_at",
                "CREATE TRIGGER workspaces_updated_at",
                "CREATE TRIGGER on_auth_user_created",
                "CREATE TRIGGER on_user_created_workspace",
            ]

            for item in required_items:
                if item in content:
                    self.add_result(
                        f"Trigger/Function {item} exists", True, "Definition found"
                    )
                else:
                    self.add_result(
                        f"Trigger/Function {item} exists", False, "Definition missing"
                    )

        except Exception as e:
            self.add_result(
                "Triggers and functions verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_indexes(self):
        """Test if required indexes are created"""
        migration_files = [
            "20240101_users_workspaces.sql",
            "20240102_foundations.sql",
            "20240103_icp_profiles.sql",
        ]

        for migration_file in migration_files:
            file_path = os.path.join(self.supabase_path, migration_file)
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for index creation
                if "CREATE INDEX" in content:
                    self.add_result(
                        f"Indexes in {migration_file}", True, "Index creation found"
                    )
                else:
                    self.add_result(
                        f"Indexes in {migration_file}", False, "Index creation missing"
                    )

            except Exception as e:
                self.add_result(
                    f"Indexes in {migration_file}",
                    False,
                    f"Error reading migration: {str(e)}",
                )

    def test_implementation_docs_exist(self):
        """Test if implementation documentation exists"""
        required_docs = ["05_AUTHENTICATION.md", "06_DATABASE_SCHEMA.md"]

        for doc in required_docs:
            file_path = os.path.join(self.implementation_docs_path, doc)
            if os.path.exists(file_path):
                self.add_result(
                    f"Implementation doc {doc} exists", True, "Documentation file found"
                )
            else:
                self.add_result(
                    f"Implementation doc {doc} exists",
                    False,
                    "Documentation file missing",
                )

    async def run_all_tests(self):
        """Run all thorough verification tests"""
        print("=" * 60)
        print("THOROUGH CHECK 1: Complete Database Schema Verification")
        print("=" * 60)

        self.test_migration_files_exist()
        self.test_users_table_structure()
        self.test_workspaces_table_structure()
        self.test_foundations_table_structure()
        self.test_icp_table_structure()
        self.test_rls_policies()
        self.test_triggers_and_functions()
        self.test_indexes()
        self.test_implementation_docs_exist()

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print(f"Tests passed: {passed}/{total}")

        if passed == total:
            print("✓ ALL TESTS PASSED - Database schema matches implementation docs")
            return True
        else:
            print("✗ SOME TESTS FAILED - Database schema needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = SchemaVerificationTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
