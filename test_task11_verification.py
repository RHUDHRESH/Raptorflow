#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 11: Daily Wins Table
Tests if daily_wins table has workspace isolation and proper structure
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


class DailyWinsTableTester:
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

    def test_daily_wins_migration_exists(self):
        """Test if daily_wins migration files exist"""
        required_files = ["20240109_daily_wins.sql", "20240109_daily_wins_rls.sql"]

        for file_name in required_files:
            file_path = os.path.join(self.supabase_path, file_name)
            if os.path.exists(file_path):
                self.add_result(
                    f"Daily wins migration {file_name} exists",
                    True,
                    f"Migration file found",
                )
            else:
                self.add_result(
                    f"Daily wins migration {file_name} exists",
                    False,
                    f"Migration file missing",
                )

    def test_daily_wins_table_structure(self):
        """Test if daily_wins table has required columns"""
        migration_file = os.path.join(self.supabase_path, "20240109_daily_wins.sql")

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
                ("win_type", "win_type TEXT NOT NULL"),
                ("category", "category TEXT NOT NULL"),
                ("significance_level", "significance_level TEXT DEFAULT 'medium'"),
                ("achievement_date", "achievement_date DATE NOT NULL"),
                ("achievement_context", "achievement_context TEXT"),
                ("challenge_overcome", "challenge_overcome TEXT"),
                ("approach_taken", "approach_taken TEXT"),
                ("impact_description", "impact_description TEXT"),
                ("quantitative_impact", "quantitative_impact JSONB DEFAULT '{}'"),
                ("qualitative_impact", "qualitative_impact JSONB DEFAULT '{}'"),
                ("business_value", "business_value DECIMAL(10,2) DEFAULT 0.00"),
                ("time_saved_hours", "time_saved_hours DECIMAL(5,2) DEFAULT 0.00"),
                ("cost_saved", "cost_saved DECIMAL(10,2) DEFAULT 0.00"),
                ("team_members", "team_members JSONB DEFAULT '[]'"),
                (
                    "collaboration_level",
                    "collaboration_level TEXT DEFAULT 'individual'",
                ),
                ("recognition_given", "recognition_given JSONB DEFAULT '[]'"),
                (
                    "foundation_id",
                    "foundation_id UUID REFERENCES foundations(id) ON DELETE SET NULL",
                ),
                (
                    "icp_profile_id",
                    "icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL",
                ),
                (
                    "campaign_id",
                    "campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL",
                ),
                ("move_id", "move_id UUID REFERENCES moves(id) ON DELETE SET NULL"),
                (
                    "move_task_id",
                    "move_task_id UUID REFERENCES move_tasks(id) ON DELETE SET NULL",
                ),
                (
                    "blackbox_strategy_id",
                    "blackbox_strategy_id UUID REFERENCES blackbox_strategies(id) ON DELETE SET NULL",
                ),
                ("key_learnings", "key_learnings JSONB DEFAULT '[]'"),
                ("skills_gained", "skills_gained JSONB DEFAULT '[]'"),
                ("insights_discovered", "insights_discovered JSONB DEFAULT '[]'"),
                ("best_practices", "best_practices JSONB DEFAULT '[]'"),
                ("next_steps", "next_steps JSONB DEFAULT '[]'"),
                ("opportunities_created", "opportunities_created JSONB DEFAULT '[]'"),
                (
                    "repeatability_score",
                    "repeatability_score DECIMAL(3,2) DEFAULT 0.00",
                ),
                ("scalability_potential", "scalability_potential TEXT"),
                ("satisfaction_level", "satisfaction_level INTEGER DEFAULT 5"),
                ("motivation_boost", "motivation_boost INTEGER DEFAULT 5"),
                ("confidence_gain", "confidence_gain INTEGER DEFAULT 5"),
                ("celebration_notes", "celebration_notes TEXT"),
                ("documentation", "documentation TEXT"),
                ("case_study", "case_study TEXT"),
                ("shareable_story", "shareable_story TEXT"),
                ("publication_status", "publication_status TEXT DEFAULT 'internal'"),
                ("ai_suggestion", "ai_suggestion TEXT"),
                ("ai_confidence", "ai_confidence DECIMAL(3,2) DEFAULT 0.00"),
                ("ai_generated_at", "ai_generated_at TIMESTAMPTZ"),
                ("ai_insights", "ai_insights JSONB DEFAULT '{}'"),
                ("views", "views INTEGER DEFAULT 0"),
                ("shares", "shares INTEGER DEFAULT 0"),
                ("likes", "likes INTEGER DEFAULT 0"),
                ("comments_count", "comments_count INTEGER DEFAULT 0"),
                ("inspiration_score", "inspiration_score DECIMAL(3,2) DEFAULT 0.00"),
                ("tags", "tags JSONB DEFAULT '[]'"),
                ("keywords", "keywords JSONB DEFAULT '[]'"),
                ("attributes", "attributes JSONB DEFAULT '{}'"),
                ("metadata", "metadata JSONB DEFAULT '{}'"),
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
                ("created_at", "created_at TIMESTAMPTZ DEFAULT NOW()"),
                ("updated_at", "updated_at TIMESTAMPTZ DEFAULT NOW()"),
                ("celebrated_at", "celebrated_at TIMESTAMPTZ"),
                ("published_at", "published_at TIMESTAMPTZ"),
                ("archived_at", "archived_at TIMESTAMPTZ"),
            ]

            for column_name, column_pattern in required_columns:
                if column_pattern in content:
                    self.add_result(
                        f"Daily wins table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"Daily wins table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for workspace_id constraint
            if "workspace_id UUID NOT NULL REFERENCES workspaces(id)" in content:
                self.add_result(
                    "Daily wins table has workspace_id constraint",
                    True,
                    "Foreign key constraint found",
                )
            else:
                self.add_result(
                    "Daily wins table has workspace_id constraint",
                    False,
                    "Foreign key constraint missing",
                )

            # Check for RLS enablement
            if "ALTER TABLE public.daily_wins ENABLE ROW LEVEL SECURITY" in content:
                self.add_result(
                    "Daily wins table has RLS enabled", True, "RLS enablement found"
                )
            else:
                self.add_result(
                    "Daily wins table has RLS enabled", False, "RLS enablement missing"
                )

            # Check for vector index
            if "ivfflat (content_embedding vector_cosine_ops)" in content:
                self.add_result(
                    "Daily wins table has vector index",
                    True,
                    "Vector index for semantic search found",
                )
            else:
                self.add_result(
                    "Daily wins table has vector index", False, "Vector index missing"
                )

            # Check for unique constraint
            if "idx_daily_wins_unique_title_date" in content:
                self.add_result(
                    "Daily wins table has unique title-date constraint",
                    True,
                    "Unique constraint on title per date per workspace found",
                )
            else:
                self.add_result(
                    "Daily wins table has unique title-date constraint",
                    False,
                    "Unique constraint missing",
                )

        except Exception as e:
            self.add_result(
                "Daily wins table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_rls_policies(self):
        """Test if RLS policies are correctly defined"""
        rls_file = os.path.join(self.supabase_path, "20240109_daily_wins_rls.sql")

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
        migration_file = os.path.join(self.supabase_path, "20240109_daily_wins.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            jsonb_columns = [
                "quantitative_impact",
                "qualitative_impact",
                "team_members",
                "recognition_given",
                "key_learnings",
                "skills_gained",
                "insights_discovered",
                "best_practices",
                "next_steps",
                "opportunities_created",
                "ai_insights",
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
        migration_file = os.path.join(self.supabase_path, "20240109_daily_wins.sql")

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

            # Check move_id relationship
            if "move_id UUID REFERENCES moves(id) ON DELETE SET NULL" in content:
                self.add_result(
                    "Move ID foreign key correct",
                    True,
                    "move_id references moves(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Move ID foreign key correct",
                    False,
                    "move_id foreign key missing or incorrect",
                )

            # Check move_task_id relationship
            if (
                "move_task_id UUID REFERENCES move_tasks(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Move task ID foreign key correct",
                    True,
                    "move_task_id references move_tasks(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Move task ID foreign key correct",
                    False,
                    "move_task_id foreign key missing or incorrect",
                )

            # Check blackbox_strategy_id relationship
            if (
                "blackbox_strategy_id UUID REFERENCES blackbox_strategies(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Blackbox strategy ID foreign key correct",
                    True,
                    "blackbox_strategy_id references blackbox_strategies(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Blackbox strategy ID foreign key correct",
                    False,
                    "blackbox_strategy_id foreign key missing or incorrect",
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
        migration_file = os.path.join(self.supabase_path, "20240109_daily_wins.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            # Check significance level constraint
            if (
                "CHECK (significance_level IN ('low', 'medium', 'high', 'critical'))"
                in content
            ):
                self.add_result(
                    "Significance level constraint implemented",
                    True,
                    "Significance level enum constraint found",
                )
            else:
                self.add_result(
                    "Significance level constraint implemented",
                    False,
                    "Significance level enum constraint missing",
                )

            # Check collaboration level constraint
            if (
                "CHECK (collaboration_level IN ('individual', 'team', 'cross_team', 'external'))"
                in content
            ):
                self.add_result(
                    "Collaboration level constraint implemented",
                    True,
                    "Collaboration level enum constraint found",
                )
            else:
                self.add_result(
                    "Collaboration level constraint implemented",
                    False,
                    "Collaboration level enum constraint missing",
                )

            # Check value constraints
            value_constraints = [
                "CHECK (business_value >= 0)",
                "CHECK (time_saved_hours >= 0)",
                "CHECK (cost_saved >= 0)",
            ]

            all_value_constraints = all(
                constraint in content for constraint in value_constraints
            )

            if all_value_constraints:
                self.add_result(
                    "Value constraints implemented", True, "All value constraints found"
                )
            else:
                self.add_result(
                    "Value constraints implemented",
                    False,
                    "Some value constraints missing",
                )

            # Check score constraints
            score_constraints = [
                "CHECK (repeatability_score >= 0 AND repeatability_score <= 1)",
                "CHECK (satisfaction_level >= 1 AND satisfaction_level <= 10)",
                "CHECK (motivation_boost >= 1 AND motivation_boost <= 10)",
                "CHECK (confidence_gain >= 1 AND confidence_gain <= 10)",
                "CHECK (inspiration_score >= 0 AND inspiration_score <= 1)",
            ]

            all_score_constraints = all(
                constraint in content for constraint in score_constraints
            )

            if all_score_constraints:
                self.add_result(
                    "Score constraints implemented", True, "All score constraints found"
                )
            else:
                self.add_result(
                    "Score constraints implemented",
                    False,
                    "Some score constraints missing",
                )

            # Check AI confidence constraint
            if "CHECK (ai_confidence >= 0 AND ai_confidence <= 1)" in content:
                self.add_result(
                    "AI confidence constraint implemented",
                    True,
                    "AI confidence range constraint found",
                )
            else:
                self.add_result(
                    "AI confidence constraint implemented",
                    False,
                    "AI confidence range constraint missing",
                )

        except Exception as e:
            self.add_result(
                "Business constraints verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_indexes_created(self):
        """Test if required indexes are created"""
        migration_file = os.path.join(self.supabase_path, "20240109_daily_wins.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_indexes = [
                "idx_daily_wins_workspace_id",
                "idx_daily_wins_win_type",
                "idx_daily_wins_category",
                "idx_daily_wins_significance_level",
                "idx_daily_wins_achievement_date",
                "idx_daily_wins_created_at",
                "idx_daily_wins_created_by",
                "idx_daily_wins_celebrated_at",
                "idx_daily_wins_published_at",
                "idx_daily_wins_business_value",
                "idx_daily_wins_satisfaction_level",
                "idx_daily_wins_motivation_boost",
                "idx_daily_wins_confidence_gain",
                "idx_daily_wins_foundation_id",
                "idx_daily_wins_icp_profile_id",
                "idx_daily_wins_campaign_id",
                "idx_daily_wins_move_id",
                "idx_daily_wins_move_task_id",
                "idx_daily_wins_blackbox_strategy_id",
                "idx_daily_wins_collaboration_level",
                "idx_daily_wins_views",
                "idx_daily_wins_inspiration_score",
                "idx_daily_wins_tags",
                "idx_daily_wins_keywords",
                "idx_daily_wins_attributes",
                "idx_daily_wins_content_embedding",
                "idx_daily_wins_unique_title_date",
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
        print("CYNICAL VERIFICATION - Task 11: Daily Wins Table")
        print("=" * 60)

        self.test_daily_wins_migration_exists()
        self.test_daily_wins_table_structure()
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
            print("✓ ALL TESTS PASSED - Task 11 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 11 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = DailyWinsTableTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
