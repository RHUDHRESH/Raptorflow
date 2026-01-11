#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 8: Campaigns Table
Tests if campaigns table has workspace isolation and proper structure
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


class CampaignsTableTester:
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

    def test_campaigns_migration_exists(self):
        """Test if campaigns migration files exist"""
        required_files = ["20240106_campaigns.sql", "20240106_campaigns_rls.sql"]

        for file_name in required_files:
            file_path = os.path.join(self.supabase_path, file_name)
            if os.path.exists(file_path):
                self.add_result(
                    f"Campaigns migration {file_name} exists",
                    True,
                    f"Migration file found",
                )
            else:
                self.add_result(
                    f"Campaigns migration {file_name} exists",
                    False,
                    f"Migration file missing",
                )

    def test_campaigns_table_structure(self):
        """Test if campaigns table has required columns"""
        migration_file = os.path.join(self.supabase_path, "20240106_campaigns.sql")

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
                ("campaign_type", "campaign_type TEXT NOT NULL"),
                ("status", "status TEXT DEFAULT 'draft'"),
                ("priority", "priority INTEGER DEFAULT 3"),
                ("primary_goal", "primary_goal TEXT NOT NULL"),
                ("secondary_goals", "secondary_goals JSONB DEFAULT '[]'"),
                ("target_audience", "target_audience TEXT"),
                (
                    "target_icp_profile_id",
                    "target_icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL",
                ),
                ("start_date", "start_date TIMESTAMPTZ"),
                ("end_date", "end_date TIMESTAMPTZ"),
                ("duration_days", "duration_days INTEGER"),
                ("is_recurring", "is_recurring BOOLEAN DEFAULT FALSE"),
                ("recurrence_pattern", "recurrence_pattern TEXT"),
                ("next_run_date", "next_run_date TIMESTAMPTZ"),
                ("budget_total", "budget_total DECIMAL(10,2) DEFAULT 0.00"),
                ("budget_spent", "budget_spent DECIMAL(10,2) DEFAULT 0.00"),
                ("budget_currency", "budget_currency TEXT DEFAULT 'USD'"),
                ("cost_per_lead", "cost_per_lead DECIMAL(10,2) DEFAULT 0.00"),
                ("expected_roi", "expected_roi DECIMAL(5,2) DEFAULT 0.00"),
                ("headline", "headline TEXT"),
                ("tagline", "tagline TEXT"),
                ("body_content", "body_content TEXT"),
                ("call_to_action", "call_to_action TEXT"),
                ("value_proposition", "value_proposition TEXT"),
                ("key_messages", "key_messages JSONB DEFAULT '[]'"),
                ("assets", "assets JSONB DEFAULT '[]'"),
                ("brand_guidelines", "brand_guidelines JSONB DEFAULT '{}'"),
                ("creative_brief", "creative_brief TEXT"),
                ("channels", "channels JSONB DEFAULT '[]'"),
                ("distribution_list", "distribution_list JSONB DEFAULT '[]'"),
                ("platform_configs", "platform_configs JSONB DEFAULT '{}'"),
                ("target_metrics", "target_metrics JSONB DEFAULT '[]'"),
                ("current_metrics", "current_metrics JSONB DEFAULT '{}'"),
                ("conversion_rate", "conversion_rate DECIMAL(5,2) DEFAULT 0.00"),
                ("engagement_rate", "engagement_rate DECIMAL(5,2) DEFAULT 0.00"),
                ("click_through_rate", "click_through_rate DECIMAL(5,2) DEFAULT 0.00"),
                ("ai_suggestions", "ai_suggestions JSONB DEFAULT '{}'"),
                ("ai_confidence", "ai_confidence DECIMAL(3,2) DEFAULT 0.00"),
                ("ai_generated_at", "ai_generated_at TIMESTAMPTZ"),
                (
                    "ai_optimization_score",
                    "ai_optimization_score DECIMAL(3,2) DEFAULT 0.00",
                ),
                ("quality_score", "quality_score DECIMAL(3,2) DEFAULT 0.00"),
                ("compliance_status", "compliance_status TEXT DEFAULT 'pending'"),
                ("compliance_notes", "compliance_notes TEXT"),
                ("legal_review", "legal_review BOOLEAN DEFAULT FALSE"),
                (
                    "reviewed_by",
                    "reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                ("reviewed_at", "reviewed_at TIMESTAMPTZ"),
                ("analytics_data", "analytics_data JSONB DEFAULT '{}'"),
                ("a_b_test_results", "a_b_test_results JSONB DEFAULT '{}'"),
                ("performance_summary", "performance_summary TEXT"),
                ("lessons_learned", "lessons_learned TEXT"),
                ("tags", "tags JSONB DEFAULT '[]'"),
                ("category", "category TEXT"),
                ("industry", "industry TEXT"),
                ("campaign_season", "campaign_season TEXT"),
                (
                    "created_by",
                    "created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL",
                ),
                (
                    "updated_by",
                    "updated_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                (
                    "campaign_manager",
                    "campaign_manager UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                ("created_at", "created_at TIMESTAMPTZ DEFAULT NOW()"),
                ("updated_at", "updated_at TIMESTAMPTZ DEFAULT NOW()"),
                ("archived_at", "archived_at TIMESTAMPTZ"),
            ]

            for column_name, column_pattern in required_columns:
                if column_pattern in content:
                    self.add_result(
                        f"Campaigns table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"Campaigns table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for workspace_id constraint
            if "workspace_id UUID NOT NULL REFERENCES workspaces(id)" in content:
                self.add_result(
                    "Campaigns table has workspace_id constraint",
                    True,
                    "Foreign key constraint found",
                )
            else:
                self.add_result(
                    "Campaigns table has workspace_id constraint",
                    False,
                    "Foreign key constraint missing",
                )

            # Check for target_icp_profile_id constraint
            if (
                "target_icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Campaigns table has ICP profile constraint",
                    True,
                    "Foreign key constraint to ICP profiles found",
                )
            else:
                self.add_result(
                    "Campaigns table has ICP profile constraint",
                    False,
                    "Foreign key constraint to ICP profiles missing",
                )

            # Check for RLS enablement
            if "ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY" in content:
                self.add_result(
                    "Campaigns table has RLS enabled", True, "RLS enablement found"
                )
            else:
                self.add_result(
                    "Campaigns table has RLS enabled", False, "RLS enablement missing"
                )

            # Check for vector index
            if "ivfflat (content_embedding vector_cosine_ops)" in content:
                self.add_result(
                    "Campaigns table has vector index",
                    True,
                    "Vector index for semantic search found",
                )
            else:
                self.add_result(
                    "Campaigns table has vector index", False, "Vector index missing"
                )

            # Check for unique constraint
            if "idx_campaigns_unique_name" in content:
                self.add_result(
                    "Campaigns table has unique name constraint",
                    True,
                    "Unique constraint on name per workspace found",
                )
            else:
                self.add_result(
                    "Campaigns table has unique name constraint",
                    False,
                    "Unique constraint missing",
                )

        except Exception as e:
            self.add_result(
                "Campaigns table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_rls_policies(self):
        """Test if RLS policies are correctly defined"""
        rls_file = os.path.join(self.supabase_path, "20240106_campaigns_rls.sql")

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
        migration_file = os.path.join(self.supabase_path, "20240106_campaigns.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            jsonb_columns = [
                "secondary_goals",
                "key_messages",
                "assets",
                "brand_guidelines",
                "channels",
                "distribution_list",
                "platform_configs",
                "target_metrics",
                "current_metrics",
                "ai_suggestions",
                "analytics_data",
                "a_b_test_results",
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
        migration_file = os.path.join(self.supabase_path, "20240106_campaigns.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

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

            # Check updated_by relationship
            if "updated_by UUID REFERENCES users(id) ON DELETE SET NULL" in content:
                self.add_result(
                    "Updated by foreign key correct",
                    True,
                    "updated_by references users(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Updated by foreign key correct",
                    False,
                    "updated_by foreign key missing or incorrect",
                )

            # Check campaign_manager relationship
            if (
                "campaign_manager UUID REFERENCES users(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Campaign manager foreign key correct",
                    True,
                    "campaign_manager references users(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Campaign manager foreign key correct",
                    False,
                    "campaign_manager foreign key missing or incorrect",
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
        migration_file = os.path.join(self.supabase_path, "20240106_campaigns.sql")

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

            # Check duration constraint
            if "CHECK (duration_days > 0)" in content:
                self.add_result(
                    "Duration constraint implemented",
                    True,
                    "Duration days > 0 constraint found",
                )
            else:
                self.add_result(
                    "Duration constraint implemented",
                    False,
                    "Duration days > 0 constraint missing",
                )

            # Check budget constraints
            budget_constraints = [
                "CHECK (budget_total >= 0)",
                "CHECK (budget_spent >= 0)",
                "CHECK (budget_spent <= budget_total)",
            ]

            all_budget_constraints = all(
                constraint in content for constraint in budget_constraints
            )

            if all_budget_constraints:
                self.add_result(
                    "Budget constraints implemented",
                    True,
                    "All budget constraints found",
                )
            else:
                self.add_result(
                    "Budget constraints implemented",
                    False,
                    "Some budget constraints missing",
                )

            # Check rate constraints
            rate_constraints = [
                "CHECK (conversion_rate >= 0 AND conversion_rate <= 100)",
                "CHECK (engagement_rate >= 0 AND engagement_rate <= 100)",
                "CHECK (click_through_rate >= 0 AND click_through_rate <= 100)",
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

        except Exception as e:
            self.add_result(
                "Business constraints verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_indexes_created(self):
        """Test if required indexes are created"""
        migration_file = os.path.join(self.supabase_path, "20240106_campaigns.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_indexes = [
                "idx_campaigns_workspace_id",
                "idx_campaigns_campaign_type",
                "idx_campaigns_status",
                "idx_campaigns_priority",
                "idx_campaigns_start_date",
                "idx_campaigns_end_date",
                "idx_campaigns_created_at",
                "idx_campaigns_created_by",
                "idx_campaigns_campaign_manager",
                "idx_campaigns_target_icp_profile_id",
                "idx_campaigns_next_run_date",
                "idx_campaigns_tags",
                "idx_campaigns_channels",
                "idx_campaigns_target_metrics",
                "idx_campaigns_content_embedding",
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
        print("CYNICAL VERIFICATION - Task 8: Campaigns Table")
        print("=" * 60)

        self.test_campaigns_migration_exists()
        self.test_campaigns_table_structure()
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
            print("✓ ALL TESTS PASSED - Task 8 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 8 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = CampaignsTableTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
