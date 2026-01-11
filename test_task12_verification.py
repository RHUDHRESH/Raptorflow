#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 12: Agent Executions Table
Tests if agent_executions table has workspace isolation and proper structure
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


class AgentExecutionsTableTester:
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

    def test_agent_executions_migration_exists(self):
        """Test if agent_executions migration files exist"""
        required_files = [
            "20240110_agent_executions.sql",
            "20240110_agent_executions_rls.sql",
        ]

        for file_name in required_files:
            file_path = os.path.join(self.supabase_path, file_name)
            if os.path.exists(file_path):
                self.add_result(
                    f"Agent executions migration {file_name} exists",
                    True,
                    f"Migration file found",
                )
            else:
                self.add_result(
                    f"Agent executions migration {file_name} exists",
                    False,
                    f"Migration file missing",
                )

    def test_agent_executions_table_structure(self):
        """Test if agent_executions table has required columns"""
        migration_file = os.path.join(
            self.supabase_path, "20240110_agent_executions.sql"
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
                ("execution_name", "execution_name TEXT NOT NULL"),
                ("description", "description TEXT"),
                ("agent_type", "agent_type TEXT NOT NULL"),
                ("agent_name", "agent_name TEXT NOT NULL"),
                ("execution_type", "execution_type TEXT NOT NULL"),
                ("status", "status TEXT DEFAULT 'pending'"),
                ("task_description", "task_description TEXT NOT NULL"),
                ("input_data", "input_data JSONB DEFAULT '{}'"),
                ("output_data", "output_data JSONB DEFAULT '{}'"),
                ("parameters", "parameters JSONB DEFAULT '{}'"),
                ("context", "context JSONB DEFAULT '{}'"),
                ("started_at", "started_at TIMESTAMPTZ"),
                ("completed_at", "completed_at TIMESTAMPTZ"),
                ("duration_ms", "duration_ms INTEGER"),
                ("estimated_duration_ms", "estimated_duration_ms INTEGER"),
                ("timeout_ms", "timeout_ms INTEGER DEFAULT 300000"),
                ("tokens_used", "tokens_used INTEGER DEFAULT 0"),
                ("cost_estimate", "cost_estimate DECIMAL(10,6) DEFAULT 0.000000"),
                ("memory_usage_mb", "memory_usage_mb DECIMAL(8,2) DEFAULT 0.00"),
                ("cpu_usage_percent", "cpu_usage_percent DECIMAL(5,2) DEFAULT 0.00"),
                ("confidence_score", "confidence_score DECIMAL(3,2) DEFAULT 0.00"),
                ("quality_score", "quality_score DECIMAL(3,2) DEFAULT 0.00"),
                ("accuracy_score", "accuracy_score DECIMAL(3,2) DEFAULT 0.00"),
                ("completeness_score", "completeness_score DECIMAL(3,2) DEFAULT 0.00"),
                ("error_message", "error_message TEXT"),
                ("error_type", "error_type TEXT"),
                ("error_details", "error_details JSONB DEFAULT '{}'"),
                ("retry_count", "retry_count INTEGER DEFAULT 0"),
                ("max_retries", "max_retries INTEGER DEFAULT 3"),
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
                (
                    "muse_asset_id",
                    "muse_asset_id UUID REFERENCES muse_assets(id) ON DELETE SET NULL",
                ),
                (
                    "initiated_by",
                    "initiated_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL",
                ),
                (
                    "reviewed_by",
                    "reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                (
                    "approved_by",
                    "approved_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                ("user_feedback", "user_feedback TEXT"),
                ("user_rating", "user_rating INTEGER"),
                ("user_comments", "user_comments TEXT"),
                ("auto_feedback", "auto_feedback JSONB DEFAULT '{}'"),
                ("learnings", "learnings JSONB DEFAULT '[]'"),
                ("improvements_suggested", "improvements_suggested JSONB DEFAULT '[]'"),
                ("performance_insights", "performance_insights JSONB DEFAULT '{}'"),
                ("cache_key", "cache_key TEXT"),
                ("cache_ttl", "cache_ttl INTEGER DEFAULT 3600"),
                ("is_cached", "is_cached BOOLEAN DEFAULT FALSE"),
                ("cache_hit", "cache_hit BOOLEAN DEFAULT FALSE"),
                ("monitoring_data", "monitoring_data JSONB DEFAULT '{}'"),
                ("metrics", "metrics JSONB DEFAULT '{}'"),
                ("benchmarks", "benchmarks JSONB DEFAULT '{}'"),
                ("tags", "tags JSONB DEFAULT '[]'"),
                ("keywords", "keywords JSONB DEFAULT '[]'"),
                ("attributes", "attributes JSONB DEFAULT '{}'"),
                ("metadata", "metadata JSONB DEFAULT '{}'"),
                ("version", "version INTEGER DEFAULT 1"),
                ("is_latest", "is_latest BOOLEAN DEFAULT TRUE"),
                ("version_notes", "version_notes TEXT"),
                ("created_at", "created_at TIMESTAMPTZ DEFAULT NOW()"),
                ("updated_at", "updated_at TIMESTAMPTZ DEFAULT NOW()"),
                ("reviewed_at", "reviewed_at TIMESTAMPTZ"),
                ("approved_at", "approved_at TIMESTAMPTZ"),
                ("archived_at", "archived_at TIMESTAMPTZ"),
            ]

            for column_name, column_pattern in required_columns:
                if column_pattern in content:
                    self.add_result(
                        f"Agent executions table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"Agent executions table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for workspace_id constraint
            if "workspace_id UUID NOT NULL REFERENCES workspaces(id)" in content:
                self.add_result(
                    "Agent executions table has workspace_id constraint",
                    True,
                    "Foreign key constraint found",
                )
            else:
                self.add_result(
                    "Agent executions table has workspace_id constraint",
                    False,
                    "Foreign key constraint missing",
                )

            # Check for RLS enablement
            if (
                "ALTER TABLE public.agent_executions ENABLE ROW LEVEL SECURITY"
                in content
            ):
                self.add_result(
                    "Agent executions table has RLS enabled",
                    True,
                    "RLS enablement found",
                )
            else:
                self.add_result(
                    "Agent executions table has RLS enabled",
                    False,
                    "RLS enablement missing",
                )

            # Check for vector index
            if "ivfflat (content_embedding vector_cosine_ops)" in content:
                self.add_result(
                    "Agent executions table has vector index",
                    True,
                    "Vector index for semantic search found",
                )
            else:
                self.add_result(
                    "Agent executions table has vector index",
                    False,
                    "Vector index missing",
                )

            # Check for unique constraint
            if "idx_agent_executions_unique_name" in content:
                self.add_result(
                    "Agent executions table has unique name constraint",
                    True,
                    "Unique constraint on name per workspace found",
                )
            else:
                self.add_result(
                    "Agent executions table has unique name constraint",
                    False,
                    "Unique constraint missing",
                )

        except Exception as e:
            self.add_result(
                "Agent executions table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_rls_policies(self):
        """Test if RLS policies are correctly defined"""
        rls_file = os.path.join(self.supabase_path, "20240110_agent_executions_rls.sql")

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
            self.supabase_path, "20240110_agent_executions.sql"
        )

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            jsonb_columns = [
                "input_data",
                "output_data",
                "parameters",
                "context",
                "error_details",
                "auto_feedback",
                "learnings",
                "improvements_suggested",
                "performance_insights",
                "monitoring_data",
                "metrics",
                "benchmarks",
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
            self.supabase_path, "20240110_agent_executions.sql"
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

            # Check muse_asset_id relationship
            if (
                "muse_asset_id UUID REFERENCES muse_assets(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Muse asset ID foreign key correct",
                    True,
                    "muse_asset_id references muse_assets(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Muse asset ID foreign key correct",
                    False,
                    "muse_asset_id foreign key missing or incorrect",
                )

            # Check initiated_by relationship
            if (
                "initiated_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Initiated by foreign key correct",
                    True,
                    "initiated_by references users(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Initiated by foreign key correct",
                    False,
                    "initiated_by foreign key missing or incorrect",
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
            self.supabase_path, "20240110_agent_executions.sql"
        )

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            # Check execution type constraint
            if (
                "CHECK (execution_type IN ('analysis', 'generation', 'optimization', 'research', 'validation', 'planning'))"
                in content
            ):
                self.add_result(
                    "Execution type constraint implemented",
                    True,
                    "Execution type enum constraint found",
                )
            else:
                self.add_result(
                    "Execution type constraint implemented",
                    False,
                    "Execution type enum constraint missing",
                )

            # Check status constraint
            if (
                "CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout'))"
                in content
            ):
                self.add_result(
                    "Status constraint implemented",
                    True,
                    "Status enum constraint found",
                )
            else:
                self.add_result(
                    "Status constraint implemented",
                    False,
                    "Status enum constraint missing",
                )

            # Check timing constraints
            timing_constraints = [
                "CHECK (duration_ms >= 0)",
                "CHECK (estimated_duration_ms >= 0)",
                "CHECK (timeout_ms > 0)",
            ]

            all_timing_constraints = all(
                constraint in content for constraint in timing_constraints
            )

            if all_timing_constraints:
                self.add_result(
                    "Timing constraints implemented",
                    True,
                    "All timing constraints found",
                )
            else:
                self.add_result(
                    "Timing constraints implemented",
                    False,
                    "Some timing constraints missing",
                )

            # Check resource constraints
            resource_constraints = [
                "CHECK (tokens_used >= 0)",
                "CHECK (cost_estimate >= 0)",
                "CHECK (memory_usage_mb >= 0)",
                "CHECK (cpu_usage_percent >= 0 AND cpu_usage_percent <= 100)",
            ]

            all_resource_constraints = all(
                constraint in content for constraint in resource_constraints
            )

            if all_resource_constraints:
                self.add_result(
                    "Resource constraints implemented",
                    True,
                    "All resource constraints found",
                )
            else:
                self.add_result(
                    "Resource constraints implemented",
                    False,
                    "Some resource constraints missing",
                )

            # Check score constraints
            score_constraints = [
                "CHECK (confidence_score >= 0 AND confidence_score <= 1)",
                "CHECK (quality_score >= 0 AND quality_score <= 1)",
                "CHECK (accuracy_score >= 0 AND accuracy_score <= 1)",
                "CHECK (completeness_score >= 0 AND completeness_score <= 1)",
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

            # Check retry constraints
            if (
                "CHECK (retry_count >= 0 AND retry_count <= max_retries)" in content
                and "CHECK (max_retries >= 0)" in content
            ):
                self.add_result(
                    "Retry constraints implemented",
                    True,
                    "Retry count constraints found",
                )
            else:
                self.add_result(
                    "Retry constraints implemented",
                    False,
                    "Retry count constraints missing",
                )

            # Check user rating constraint
            if "CHECK (user_rating >= 1 AND user_rating <= 5)" in content:
                self.add_result(
                    "User rating constraint implemented",
                    True,
                    "User rating range constraint found",
                )
            else:
                self.add_result(
                    "User rating constraint implemented",
                    False,
                    "User rating range constraint missing",
                )

            # Check cache constraints
            if "CHECK (cache_ttl >= 0)" in content:
                self.add_result(
                    "Cache TTL constraint implemented",
                    True,
                    "Cache TTL >= 0 constraint found",
                )
            else:
                self.add_result(
                    "Cache TTL constraint implemented",
                    False,
                    "Cache TTL >= 0 constraint missing",
                )

            # Check version constraint
            if "CHECK (version >= 1)" in content:
                self.add_result(
                    "Version constraint implemented",
                    True,
                    "Version >= 1 constraint found",
                )
            else:
                self.add_result(
                    "Version constraint implemented",
                    False,
                    "Version >= 1 constraint missing",
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
            self.supabase_path, "20240110_agent_executions.sql"
        )

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_indexes = [
                "idx_agent_executions_workspace_id",
                "idx_agent_executions_agent_type",
                "idx_agent_executions_agent_name",
                "idx_agent_executions_execution_type",
                "idx_agent_executions_status",
                "idx_agent_executions_started_at",
                "idx_agent_executions_created_at",
                "idx_agent_executions_initiated_by",
                "idx_agent_executions_completed_at",
                "idx_agent_executions_duration_ms",
                "idx_agent_executions_tokens_used",
                "idx_agent_executions_cost_estimate",
                "idx_agent_executions_confidence_score",
                "idx_agent_executions_quality_score",
                "idx_agent_executions_accuracy_score",
                "idx_agent_executions_foundation_id",
                "idx_agent_executions_icp_profile_id",
                "idx_agent_executions_campaign_id",
                "idx_agent_executions_move_id",
                "idx_agent_executions_move_task_id",
                "idx_agent_executions_blackbox_strategy_id",
                "idx_agent_executions_muse_asset_id",
                "idx_agent_executions_cache_key",
                "idx_agent_executions_is_cached",
                "idx_agent_executions_user_rating",
                "idx_agent_executions_is_latest",
                "idx_agent_executions_tags",
                "idx_agent_executions_keywords",
                "idx_agent_executions_attributes",
                "idx_agent_executions_content_embedding",
                "idx_agent_executions_unique_name",
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
        print("CYNICAL VERIFICATION - Task 12: Agent Executions Table")
        print("=" * 60)

        self.test_agent_executions_migration_exists()
        self.test_agent_executions_table_structure()
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
            print("✓ ALL TESTS PASSED - Task 12 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 12 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = AgentExecutionsTableTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
