#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 10: Blackbox Strategies Table
Tests if blackbox_strategies table has workspace isolation and proper structure
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


class BlackboxStrategiesTableTester:
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

    def test_blackbox_strategies_migration_exists(self):
        """Test if blackbox_strategies migration files exist"""
        required_files = [
            "20240108_blackbox_strategies.sql",
            "20240108_blackbox_strategies_rls.sql",
        ]

        for file_name in required_files:
            file_path = os.path.join(self.supabase_path, file_name)
            if os.path.exists(file_path):
                self.add_result(
                    f"Blackbox strategies migration {file_name} exists",
                    True,
                    f"Migration file found",
                )
            else:
                self.add_result(
                    f"Blackbox strategies migration {file_name} exists",
                    False,
                    f"Migration file missing",
                )

    def test_blackbox_strategies_table_structure(self):
        """Test if blackbox_strategies table has required columns"""
        migration_file = os.path.join(
            self.supabase_path, "20240108_blackbox_strategies.sql"
        )

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_columns = [
                ("id", "id UUID PRIMARY KEY DEFAULT gen_random_uuid()"),
                (
                    "workspace_id",
                    "workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE",
                ),
                ("name", "name TEXT NOT NULL"),
                ("description", "description TEXT"),
                ("strategy_type", "strategy_type TEXT NOT NULL"),
                ("category", "category TEXT NOT NULL"),
                ("status", "status TEXT DEFAULT 'draft'"),
                ("priority", "priority INTEGER DEFAULT 3"),
                ("objective", "objective TEXT NOT NULL"),
                ("hypothesis", "hypothesis TEXT"),
                ("approach", "approach TEXT"),
                ("expected_outcome", "expected_outcome TEXT"),
                ("success_criteria", "success_criteria JSONB DEFAULT '[]'"),
                ("is_blackbox", "is_blackbox BOOLEAN DEFAULT TRUE"),
                ("blackbox_level", "blackbox_level TEXT DEFAULT 'partial'"),
                ("uncertainty_level", "uncertainty_level TEXT DEFAULT 'high'"),
                ("learning_approach", "learning_approach TEXT"),
                ("implementation_steps", "implementation_steps JSONB DEFAULT '[]'"),
                ("required_resources", "required_resources JSONB DEFAULT '[]'"),
                ("time_investment", "time_investment INTEGER DEFAULT 0"),
                ("budget_estimate", "budget_estimate DECIMAL(10,2) DEFAULT 0.00"),
                ("target_audience", "target_audience TEXT"),
                ("target_market", "target_market TEXT"),
                (
                    "target_icp_profile_id",
                    "target_icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL",
                ),
                (
                    "foundation_id",
                    "foundation_id UUID REFERENCES foundations(id) ON DELETE SET NULL",
                ),
                (
                    "campaign_id",
                    "campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL",
                ),
                ("test_design", "test_design JSONB DEFAULT '{}'"),
                ("test_duration_days", "test_duration_days INTEGER DEFAULT 30"),
                ("control_group", "control_group TEXT"),
                ("test_metrics", "test_metrics JSONB DEFAULT '[]'"),
                ("actual_results", "actual_results JSONB DEFAULT '{}'"),
                ("success_rate", "success_rate DECIMAL(5,2) DEFAULT 0.00"),
                ("roi_measured", "roi_measured DECIMAL(5,2) DEFAULT 0.00"),
                (
                    "conversion_improvement",
                    "conversion_improvement DECIMAL(5,2) DEFAULT 0.00",
                ),
                ("key_insights", "key_insights JSONB DEFAULT '[]'"),
                ("unexpected_outcomes", "unexpected_outcomes JSONB DEFAULT '[]'"),
                ("refinements", "refinements JSONB DEFAULT '[]'"),
                ("lessons_learned", "lessons_learned TEXT"),
                ("ai_suggestion", "ai_suggestion TEXT"),
                ("ai_confidence", "ai_confidence DECIMAL(3,2) DEFAULT 0.00"),
                ("ai_generated_at", "ai_generated_at TIMESTAMPTZ"),
                (
                    "ai_optimization_score",
                    "ai_optimization_score DECIMAL(3,2) DEFAULT 0.00",
                ),
                ("risk_level", "risk_level TEXT DEFAULT 'medium'"),
                ("risk_factors", "risk_factors JSONB DEFAULT '[]'"),
                ("mitigation_strategies", "mitigation_strategies JSONB DEFAULT '[]'"),
                ("compliance_check", "compliance_check BOOLEAN DEFAULT FALSE"),
                ("documentation", "documentation TEXT"),
                ("case_study", "case_study TEXT"),
                ("shareable_insights", "shareable_insights JSONB DEFAULT '[]'"),
                ("publication_status", "publication_status TEXT DEFAULT 'internal'"),
                ("views", "views INTEGER DEFAULT 0"),
                ("downloads", "downloads INTEGER DEFAULT 0"),
                ("shares", "shares INTEGER DEFAULT 0"),
                ("adoption_rate", "adoption_rate DECIMAL(5,2) DEFAULT 0.00"),
                ("satisfaction_score", "satisfaction_score DECIMAL(3,2) DEFAULT 0.00"),
                ("tags", "tags JSONB DEFAULT '[]'"),
                ("keywords", "keywords JSONB DEFAULT '[]'"),
                ("attributes", "attributes JSONB DEFAULT '{}'"),
                ("metadata", "metadata JSONB DEFAULT '{}'"),
                ("version", "version INTEGER DEFAULT 1"),
                ("is_latest", "is_latest BOOLEAN DEFAULT TRUE"),
                ("version_notes", "version_notes TEXT"),
                (
                    "created_by",
                    "created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL",
                ),
                (
                    "updated_by",
                    "updated_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                (
                    "reviewed_by",
                    "reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                (
                    "approved_by",
                    "approved_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                ("created_at", "created_at TIMESTAMPTZ DEFAULT NOW()"),
                ("updated_at", "updated_at TIMESTAMPTZ DEFAULT NOW()"),
                ("tested_at", "tested_at TIMESTAMPTZ"),
                ("published_at", "published_at TIMESTAMPTZ"),
                ("archived_at", "archived_at TIMESTAMPTZ"),
            ]

            for column_name, column_pattern in required_columns:
                if column_pattern in content:
                    self.add_result(
                        f"Blackbox strategies table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"Blackbox strategies table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for workspace_id constraint
            if "workspace_id UUID NOT NULL REFERENCES workspaces(id)" in content:
                self.add_result(
                    "Blackbox strategies table has workspace_id constraint",
                    True,
                    "Foreign key constraint found",
                )
            else:
                self.add_result(
                    "Blackbox strategies table has workspace_id constraint",
                    False,
                    "Foreign key constraint missing",
                )

            # Check for RLS enablement
            if (
                "ALTER TABLE public.blackbox_strategies ENABLE ROW LEVEL SECURITY"
                in content
            ):
                self.add_result(
                    "Blackbox strategies table has RLS enabled",
                    True,
                    "RLS enablement found",
                )
            else:
                self.add_result(
                    "Blackbox strategies table has RLS enabled",
                    False,
                    "RLS enablement missing",
                )

            # Check for vector index
            if "ivfflat (content_embedding vector_cosine_ops)" in content:
                self.add_result(
                    "Blackbox strategies table has vector index",
                    True,
                    "Vector index for semantic search found",
                )
            else:
                self.add_result(
                    "Blackbox strategies table has vector index",
                    False,
                    "Vector index missing",
                )

            # Check for unique constraint
            if "idx_blackbox_strategies_unique_name" in content:
                self.add_result(
                    "Blackbox strategies table has unique name constraint",
                    True,
                    "Unique constraint on name per workspace found",
                )
            else:
                self.add_result(
                    "Blackbox strategies table has unique name constraint",
                    False,
                    "Unique constraint missing",
                )

        except Exception as e:
            self.add_result(
                "Blackbox strategies table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_rls_policies(self):
        """Test if RLS policies are correctly defined"""
        rls_file = os.path.join(
            self.supabase_path, "20240108_blackbox_strategies_rls.sql"
        )

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
        migration_file = os.path.join(
            self.supabase_path, "20240108_blackbox_strategies.sql"
        )

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            jsonb_columns = [
                "success_criteria",
                "implementation_steps",
                "required_resources",
                "test_design",
                "test_metrics",
                "actual_results",
                "key_insights",
                "unexpected_outcomes",
                "refinements",
                "risk_factors",
                "mitigation_strategies",
                "shareable_insights",
                "tags",
                "keywords",
                "attributes",
                "metadata",
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
        migration_file = os.path.join(
            self.supabase_path, "20240108_blackbox_strategies.sql"
        )

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

            # Check target_icp_profile_id relationship
            if (
                "target_icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Target ICP Profile foreign key correct",
                    True,
                    "target_icp_profile_id references icp_profiles(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Target ICP Profile foreign key correct",
                    False,
                    "target_icp_profile_id foreign key missing or incorrect",
                )

            # Check campaign_id relationship
            if (
                "campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Campaign ID foreign key correct",
                    True,
                    "campaign_id references campaigns(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Campaign ID foreign key correct",
                    False,
                    "campaign_id foreign key missing or incorrect",
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

        except Exception as e:
            self.add_result(
                "Foreign key relationships verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_business_constraints(self):
        """Test if business constraints are implemented"""
        migration_file = os.path.join(
            self.supabase_path, "20240108_blackbox_strategies.sql"
        )

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

            # Check time investment constraint
            if "CHECK (time_investment >= 0)" in content:
                self.add_result(
                    "Time investment constraint implemented",
                    True,
                    "Time investment >= 0 constraint found",
                )
            else:
                self.add_result(
                    "Time investment constraint implemented",
                    False,
                    "Time investment >= 0 constraint missing",
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

            # Check rate constraints
            rate_constraints = [
                "CHECK (success_rate >= 0 AND success_rate <= 100)",
                "CHECK (roi_measured >= 0)",
                "CHECK (conversion_improvement >= 0 AND conversion_improvement <= 100)",
                "CHECK (adoption_rate >= 0 AND adoption_rate <= 100)",
            ]

            all_rate_constraints = all(
                constraint in content for constraint in rate_constraints
            )

            if all_rate_constraints:
                self.add_result(
                    "Rate constraints implemented", True, "All rate constraints found"
                )
            else:
                self.add_result(
                    "Rate constraints implemented",
                    False,
                    "Some rate constraints missing",
                )

            # Check satisfaction score constraint
            if "CHECK (satisfaction_score >= 0 AND satisfaction_score <= 1)" in content:
                self.add_result(
                    "Satisfaction score constraint implemented",
                    True,
                    "Satisfaction score range constraint found",
                )
            else:
                self.add_result(
                    "Satisfaction score constraint implemented",
                    False,
                    "Satisfaction score range constraint missing",
                )

        except Exception as e:
            self.add_result(
                "Business constraints verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_indexes_created(self):
        """Test if required indexes are created"""
        migration_file = os.path.join(
            self.supabase_path, "20240108_blackbox_strategies.sql"
        )

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_indexes = [
                "idx_blackbox_strategies_workspace_id",
                "idx_blackbox_strategies_strategy_type",
                "idx_blackbox_strategies_category",
                "idx_blackbox_strategies_status",
                "idx_blackbox_strategies_priority",
                "idx_blackbox_strategies_blackbox_level",
                "idx_blackbox_strategies_uncertainty_level",
                "idx_blackbox_strategies_is_blackbox",
                "idx_blackbox_strategies_created_at",
                "idx_blackbox_strategies_created_by",
                "idx_blackbox_strategies_tested_at",
                "idx_blackbox_strategies_published_at",
                "idx_blackbox_strategies_success_rate",
                "idx_blackbox_strategies_roi_measured",
                "idx_blackbox_strategies_foundation_id",
                "idx_blackbox_strategies_icp_profile_id",
                "idx_blackbox_strategies_campaign_id",
                "idx_blackbox_strategies_is_latest",
                "idx_blackbox_strategies_tags",
                "idx_blackbox_strategies_keywords",
                "idx_blackbox_strategies_attributes",
                "idx_blackbox_strategies_content_embedding",
                "idx_blackbox_strategies_unique_name",
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
        print("CYNICAL VERIFICATION - Task 10: Blackbox Strategies Table")
        print("=" * 60)

        self.test_blackbox_strategies_migration_exists()
        self.test_blackbox_strategies_table_structure()
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
            print("✓ ALL TESTS PASSED - Task 10 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 10 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = BlackboxStrategiesTableTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
