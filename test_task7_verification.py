#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 7: Move Tasks Table
Tests if move_tasks table has workspace isolation and proper structure
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


class MoveTasksTableTester:
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

    def test_move_tasks_migration_exists(self):
        """Test if move_tasks migration files exist"""
        required_files = ["20240105_move_tasks.sql", "20240105_move_tasks_rls.sql"]

        for file_name in required_files:
            file_path = os.path.join(self.supabase_path, file_name)
            if os.path.exists(file_path):
                self.add_result(
                    f"Move tasks migration {file_name} exists",
                    True,
                    f"Migration file found",
                )
            else:
                self.add_result(
                    f"Move tasks migration {file_name} exists",
                    False,
                    f"Migration file missing",
                )

    def test_move_tasks_table_structure(self):
        """Test if move_tasks table has required columns"""
        migration_file = os.path.join(self.supabase_path, "20240105_move_tasks.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_columns = [
                ("id", "id UUID PRIMARY KEY DEFAULT gen_random_uuid()"),
                (
                    "workspace_id",
                    "workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE",
                ),
                (
                    "move_id",
                    "move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE",
                ),
                ("title", "title TEXT NOT NULL"),
                ("description", "description TEXT"),
                ("category", "category TEXT NOT NULL"),
                ("priority", "priority INTEGER DEFAULT 3"),
                ("status", "status TEXT DEFAULT 'todo'"),
                ("objective", "objective TEXT NOT NULL"),
                ("requirements", "requirements JSONB DEFAULT '[]'"),
                ("deliverables", "deliverables JSONB DEFAULT '[]'"),
                ("estimated_hours", "estimated_hours DECIMAL(5,2) DEFAULT 0.00"),
                ("dependencies", "dependencies JSONB DEFAULT '[]'"),
                ("blocking_tasks", "blocking_tasks JSONB DEFAULT '[]'"),
                (
                    "assigned_to",
                    "assigned_to UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                (
                    "created_by",
                    "created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL",
                ),
                ("start_date", "start_date TIMESTAMPTZ"),
                ("due_date", "due_date TIMESTAMPTZ"),
                ("completed_at", "completed_at TIMESTAMPTZ"),
                ("progress_percentage", "progress_percentage INTEGER DEFAULT 0"),
                ("actual_hours", "actual_hours DECIMAL(5,2) DEFAULT 0.00"),
                ("completion_notes", "completion_notes TEXT"),
                ("ai_suggestion", "ai_suggestion TEXT"),
                ("ai_confidence", "ai_confidence DECIMAL(3,2) DEFAULT 0.00"),
                ("ai_generated_at", "ai_generated_at TIMESTAMPTZ"),
                ("content", "content TEXT"),
                ("assets", "assets JSONB DEFAULT '[]'"),
                ("tags", "tags JSONB DEFAULT '[]'"),
                ("quality_score", "quality_score DECIMAL(3,2) DEFAULT 0.00"),
                ("review_status", "review_status TEXT DEFAULT 'pending'"),
                ("review_notes", "review_notes TEXT"),
                (
                    "reviewed_by",
                    "reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                ("reviewed_at", "reviewed_at TIMESTAMPTZ"),
                ("completion_rate", "completion_rate DECIMAL(3,2) DEFAULT 0.00"),
                ("quality_rating", "quality_rating DECIMAL(3,2) DEFAULT 0.00"),
                ("satisfaction_score", "satisfaction_score DECIMAL(3,2) DEFAULT 0.00"),
                ("created_at", "created_at TIMESTAMPTZ DEFAULT NOW()"),
                ("updated_at", "updated_at TIMESTAMPTZ DEFAULT NOW()"),
            ]

            for column_name, column_pattern in required_columns:
                if column_pattern in content:
                    self.add_result(
                        f"Move tasks table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"Move tasks table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for workspace_id constraint
            if "workspace_id UUID NOT NULL REFERENCES workspaces(id)" in content:
                self.add_result(
                    "Move tasks table has workspace_id constraint",
                    True,
                    "Foreign key constraint found",
                )
            else:
                self.add_result(
                    "Move tasks table has workspace_id constraint",
                    False,
                    "Foreign key constraint missing",
                )

            # Check for move_id constraint
            if "move_id UUID NOT NULL REFERENCES moves(id)" in content:
                self.add_result(
                    "Move tasks table has move_id constraint",
                    True,
                    "Foreign key constraint to moves table found",
                )
            else:
                self.add_result(
                    "Move tasks table has move_id constraint",
                    False,
                    "Foreign key constraint to moves table missing",
                )

            # Check for RLS enablement
            if "ALTER TABLE public.move_tasks ENABLE ROW LEVEL SECURITY" in content:
                self.add_result(
                    "Move tasks table has RLS enabled", True, "RLS enablement found"
                )
            else:
                self.add_result(
                    "Move tasks table has RLS enabled", False, "RLS enablement missing"
                )

            # Check for vector index
            if "ivfflat (content_embedding vector_cosine_ops)" in content:
                self.add_result(
                    "Move tasks table has vector index",
                    True,
                    "Vector index for semantic search found",
                )
            else:
                self.add_result(
                    "Move tasks table has vector index", False, "Vector index missing"
                )

            # Check for unique constraint
            if "idx_move_tasks_unique_title" in content:
                self.add_result(
                    "Move tasks table has unique title constraint",
                    True,
                    "Unique constraint on title per move found",
                )
            else:
                self.add_result(
                    "Move tasks table has unique title constraint",
                    False,
                    "Unique constraint missing",
                )

        except Exception as e:
            self.add_result(
                "Move tasks table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_rls_policies(self):
        """Test if RLS policies are correctly defined"""
        rls_file = os.path.join(self.supabase_path, "20240105_move_tasks_rls.sql")

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
        migration_file = os.path.join(self.supabase_path, "20240105_move_tasks.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            jsonb_columns = [
                "requirements",
                "deliverables",
                "dependencies",
                "blocking_tasks",
                "assets",
                "tags",
            ]

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
        migration_file = os.path.join(self.supabase_path, "20240105_move_tasks.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            # Check move_id relationship
            if (
                "move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE"
                in content
            ):
                self.add_result(
                    "Move ID foreign key correct",
                    True,
                    "move_id references moves(id) with CASCADE",
                )
            else:
                self.add_result(
                    "Move ID foreign key correct",
                    False,
                    "move_id foreign key missing or incorrect",
                )

            # Check assigned_to relationship
            if "assigned_to UUID REFERENCES users(id) ON DELETE SET NULL" in content:
                self.add_result(
                    "Assigned to foreign key correct",
                    True,
                    "assigned_to references users(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Assigned to foreign key correct",
                    False,
                    "assigned_to foreign key missing or incorrect",
                )

            # Check created_by relationship
            if (
                "created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL"
                in content
            ):
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

            # Check reviewed_by relationship
            if "reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL" in content:
                self.add_result(
                    "Reviewed by foreign key correct",
                    True,
                    "reviewed_by references users(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Reviewed by foreign key correct",
                    False,
                    "reviewed_by foreign key missing or incorrect",
                )

        except Exception as e:
            self.add_result(
                "Foreign key relationships verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_business_constraints(self):
        """Test if business constraints are implemented"""
        migration_file = os.path.join(self.supabase_path, "20240105_move_tasks.sql")

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

            # Check hours constraints
            if (
                "CHECK (estimated_hours >= 0)" in content
                and "CHECK (actual_hours >= 0)" in content
            ):
                self.add_result(
                    "Hours constraints implemented",
                    True,
                    "Hours >= 0 constraints found",
                )
            else:
                self.add_result(
                    "Hours constraints implemented",
                    False,
                    "Hours >= 0 constraints missing",
                )

            # Check quality score constraints
            if "CHECK (quality_score >= 0 AND quality_score <= 1)" in content:
                self.add_result(
                    "Quality score constraint implemented",
                    True,
                    "Quality score range constraint found",
                )
            else:
                self.add_result(
                    "Quality score constraint implemented",
                    False,
                    "Quality score range constraint missing",
                )

        except Exception as e:
            self.add_result(
                "Business constraints verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_indexes_created(self):
        """Test if required indexes are created"""
        migration_file = os.path.join(self.supabase_path, "20240105_move_tasks.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_indexes = [
                "idx_move_tasks_workspace_id",
                "idx_move_tasks_move_id",
                "idx_move_tasks_category",
                "idx_move_tasks_status",
                "idx_move_tasks_priority",
                "idx_move_tasks_assigned_to",
                "idx_move_tasks_due_date",
                "idx_move_tasks_created_at",
                "idx_move_tasks_created_by",
                "idx_move_tasks_tags",
                "idx_move_tasks_dependencies",
                "idx_move_tasks_blocking_tasks",
                "idx_move_tasks_content_embedding",
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
        print("CYNICAL VERIFICATION - Task 7: Move Tasks Table")
        print("=" * 60)

        self.test_move_tasks_migration_exists()
        self.test_move_tasks_table_structure()
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
            print("✓ ALL TESTS PASSED - Task 7 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 7 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = MoveTasksTableTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
