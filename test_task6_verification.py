#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 6: Moves Table
Tests if moves table has workspace isolation and proper structure
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


class MovesTableTester:
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

    def test_moves_migration_exists(self):
        """Test if moves migration files exist"""
        required_files = ["20240104_moves.sql", "20240104_moves_rls.sql"]

        for file_name in required_files:
            file_path = os.path.join(self.supabase_path, file_name)
            if os.path.exists(file_path):
                self.add_result(
                    f"Moves migration {file_name} exists", True, f"Migration file found"
                )
            else:
                self.add_result(
                    f"Moves migration {file_name} exists",
                    False,
                    f"Migration file missing",
                )

    def test_moves_table_structure(self):
        """Test if moves table has required columns"""
        migration_file = os.path.join(self.supabase_path, "20240104_moves.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_columns = [
                ("id", "id UUID PRIMARY KEY DEFAULT gen_random_uuid()"),
                (
                    "workspace_id",
                    "workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE",
                ),
                ("title", "title TEXT NOT NULL"),
                ("description", "description TEXT"),
                ("category", "category TEXT NOT NULL"),
                ("priority", "priority INTEGER DEFAULT 3"),
                ("status", "status TEXT DEFAULT 'draft'"),
                ("objective", "objective TEXT NOT NULL"),
                ("target_audience", "target_audience TEXT"),
                ("success_metrics", "success_metrics JSONB DEFAULT '[]'"),
                ("timeline_days", "timeline_days INTEGER DEFAULT 30"),
                ("budget_estimate", "budget_estimate DECIMAL(10,2) DEFAULT 0.00"),
                ("content", "content TEXT"),
                ("assets", "assets JSONB DEFAULT '[]'"),
                ("tags", "tags JSONB DEFAULT '[]'"),
                (
                    "foundation_id",
                    "foundation_id UUID REFERENCES foundations(id) ON DELETE SET NULL",
                ),
                (
                    "icp_profile_id",
                    "icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL",
                ),
                ("progress_percentage", "progress_percentage INTEGER DEFAULT 0"),
                ("start_date", "start_date TIMESTAMPTZ"),
                ("target_date", "target_date TIMESTAMPTZ"),
                ("completion_date", "completion_date TIMESTAMPTZ"),
                ("ai_suggestion", "ai_suggestion TEXT"),
                ("ai_confidence", "ai_confidence DECIMAL(3,2) DEFAULT 0.00"),
                ("ai_generated_at", "ai_generated_at TIMESTAMPTZ"),
                ("views", "views INTEGER DEFAULT 0"),
                ("clicks", "clicks INTEGER DEFAULT 0"),
                ("conversions", "conversions INTEGER DEFAULT 0"),
                ("revenue_impact", "revenue_impact DECIMAL(10,2) DEFAULT 0.00"),
                ("created_at", "created_at TIMESTAMPTZ DEFAULT NOW()"),
                ("updated_at", "updated_at TIMESTAMPTZ DEFAULT NOW()"),
                (
                    "created_by",
                    "created_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                (
                    "updated_by",
                    "updated_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
            ]

            for column_name, column_pattern in required_columns:
                if column_pattern in content:
                    self.add_result(
                        f"Moves table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"Moves table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for workspace_id in constraints
            if "workspace_id UUID NOT NULL REFERENCES workspaces(id)" in content:
                self.add_result(
                    "Moves table has workspace_id constraint",
                    True,
                    "Foreign key constraint found",
                )
            else:
                self.add_result(
                    "Moves table has workspace_id constraint",
                    False,
                    "Foreign key constraint missing",
                )

            # Check for RLS enablement
            if "ALTER TABLE public.moves ENABLE ROW LEVEL SECURITY" in content:
                self.add_result(
                    "Moves table has RLS enabled", True, "RLS enablement found"
                )
            else:
                self.add_result(
                    "Moves table has RLS enabled", False, "RLS enablement missing"
                )

            # Check for vector index
            if "ivfflat (content_embedding vector_cosine_ops)" in content:
                self.add_result(
                    "Moves table has vector index",
                    True,
                    "Vector index for semantic search found",
                )
            else:
                self.add_result(
                    "Moves table has vector index", False, "Vector index missing"
                )

            # Check for unique constraint
            if "idx_moves_unique_title" in content:
                self.add_result(
                    "Moves table has unique title constraint",
                    True,
                    "Unique constraint on title per workspace found",
                )
            else:
                self.add_result(
                    "Moves table has unique title constraint",
                    False,
                    "Unique constraint missing",
                )

        except Exception as e:
            self.add_result(
                "Moves table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_rls_policies(self):
        """Test if RLS policies are correctly defined"""
        rls_file = os.path.join(self.supabase_path, "20240104_moves_rls.sql")

        try:
            with open(rls_file, "r") as f:
                content = f.read()

            # Check for policy creation
            if "CREATE POLICY" in content:
                self.add_result("RLS policies created", True, "Policy creation found")
            else:
                self.add_result(
                    "RLS policies created", False, "Policy creation missing"
                )

            # Check for all CRUD operations
            required_operations = ["SELECT", "INSERT", "UPDATE", "DELETE"]
            for op in required_operations:
                if f"FOR {op}" in content:
                    self.add_result(f"RLS has {op} policy", True, f"{op} policy found")
                else:
                    self.add_result(
                        f"RLS has {op} policy", False, f"{op} policy missing"
                    )

            # Check for workspace ownership function usage
            if "user_owns_workspace" in content:
                self.add_result(
                    "RLS uses workspace ownership function",
                    True,
                    "user_owns_workspace function found",
                )
            else:
                self.add_result(
                    "RLS uses workspace ownership function",
                    False,
                    "Workspace ownership function missing",
                )

        except Exception as e:
            self.add_result(
                "RLS policies verification", False, f"Error reading RLS file: {str(e)}"
            )

    def test_jsonb_columns(self):
        """Test if JSONB columns are properly defined"""
        migration_file = os.path.join(self.supabase_path, "20240104_moves.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            jsonb_columns = ["success_metrics", "assets", "tags"]

            for column in jsonb_columns:
                if f"{column} JSONB" in content:
                    self.add_result(
                        f"JSONB column {column} exists",
                        True,
                        f"JSONB column definition found",
                    )
                else:
                    self.add_result(
                        f"JSONB column {column} exists",
                        False,
                        f"JSONB column definition missing",
                    )

        except Exception as e:
            self.add_result(
                "JSONB columns verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_foreign_key_relationships(self):
        """Test if foreign key relationships are correct"""
        migration_file = os.path.join(self.supabase_path, "20240104_moves.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            # Check foundation_id relationship
            if (
                "foundation_id UUID REFERENCES foundations(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Foundation ID foreign key correct",
                    True,
                    "foundation_id references foundations(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Foundation ID foreign key correct",
                    False,
                    "foundation_id foreign key missing or incorrect",
                )

            # Check icp_profile_id relationship
            if (
                "icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "ICP Profile ID foreign key correct",
                    True,
                    "icp_profile_id references icp_profiles(id) with SET NULL",
                )
            else:
                self.add_result(
                    "ICP Profile ID foreign key correct",
                    False,
                    "icp_profile_id foreign key missing or incorrect",
                )

            # Check created_by and updated_by relationships
            if "created_by UUID REFERENCES users(id) ON DELETE SET NULL" in content:
                self.add_result(
                    "Created by foreign key correct",
                    True,
                    "created_by references users(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Created by foreign key correct",
                    False,
                    "created_by foreign key missing or incorrect",
                )

        except Exception as e:
            self.add_result(
                "Foreign key relationships verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_business_constraints(self):
        """Test if business constraints are implemented"""
        migration_file = os.path.join(self.supabase_path, "20240104_moves.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            # Check priority constraint
            if "CHECK (priority >= 1 AND priority <= 4)" in content:
                self.add_result(
                    "Priority constraint implemented",
                    True,
                    "Priority range constraint found",
                )
            else:
                self.add_result(
                    "Priority constraint implemented",
                    False,
                    "Priority range constraint missing",
                )

            # Check timeline constraint
            if "CHECK (timeline_days > 0)" in content:
                self.add_result(
                    "Timeline constraint implemented",
                    True,
                    "Timeline days > 0 constraint found",
                )
            else:
                self.add_result(
                    "Timeline constraint implemented",
                    False,
                    "Timeline days > 0 constraint missing",
                )

            # Check progress constraint
            if (
                "CHECK (progress_percentage >= 0 AND progress_percentage <= 100)"
                in content
            ):
                self.add_result(
                    "Progress constraint implemented",
                    True,
                    "Progress percentage range constraint found",
                )
            else:
                self.add_result(
                    "Progress constraint implemented",
                    False,
                    "Progress percentage range constraint missing",
                )

            # Check budget constraint
            if "CHECK (budget_estimate >= 0)" in content:
                self.add_result(
                    "Budget constraint implemented",
                    True,
                    "Budget estimate >= 0 constraint found",
                )
            else:
                self.add_result(
                    "Budget constraint implemented",
                    False,
                    "Budget estimate >= 0 constraint missing",
                )

        except Exception as e:
            self.add_result(
                "Business constraints verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_indexes_created(self):
        """Test if required indexes are created"""
        migration_file = os.path.join(self.supabase_path, "20240104_moves.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_indexes = [
                "idx_moves_workspace_id",
                "idx_moves_category",
                "idx_moves_tags",
                "idx_moves_status",
                "idx_moves_priority",
                "idx_moves_target_date",
                "idx_moves_created_at",
                "idx_moves_content_embedding",
            ]

            for index_name in required_indexes:
                if index_name in content:
                    self.add_result(
                        f"Index {index_name} created", True, f"Index creation found"
                    )
                else:
                    self.add_result(
                        f"Index {index_name} created", False, f"Index creation missing"
                    )

        except Exception as e:
            self.add_result(
                "Indexes verification", False, f"Error reading migration: {str(e)}"
            )

    async def run_all_tests(self):
        """Run all verification tests"""
        print("=" * 60)
        print("CYNICAL VERIFICATION - Task 6: Moves Table")
        print("=" * 60)

        self.test_moves_migration_exists()
        self.test_moves_table_structure()
        self.test_rls_policies()
        self.test_jsonb_columns()
        self.test_foreign_key_relationships()
        self.test_business_constraints()
        self.test_indexes_created()

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print(f"Tests passed: {passed}/{total}")

        if passed == total:
            print("✓ ALL TESTS PASSED - Task 6 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 6 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = MovesTableTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
