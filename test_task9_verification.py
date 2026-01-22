#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 9: Muse Assets Table
Tests if muse_assets table has workspace isolation and proper structure
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


class MuseAssetsTableTester:
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

    def test_muse_assets_migration_exists(self):
        """Test if muse_assets migration files exist"""
        required_files = ["20240107_muse_assets.sql", "20240107_muse_assets_rls.sql"]

        for file_name in required_files:
            file_path = os.path.join(self.supabase_path, file_name)
            if os.path.exists(file_path):
                self.add_result(
                    f"Muse assets migration {file_name} exists",
                    True,
                    f"Migration file found",
                )
            else:
                self.add_result(
                    f"Muse assets migration {file_name} exists",
                    False,
                    f"Migration file missing",
                )

    def test_muse_assets_table_structure(self):
        """Test if muse_assets table has required columns"""
        migration_file = os.path.join(self.supabase_path, "20240107_muse_assets.sql")

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
                ("asset_type", "asset_type TEXT NOT NULL"),
                ("category", "category TEXT NOT NULL"),
                ("status", "status TEXT DEFAULT 'draft'"),
                ("priority", "priority INTEGER DEFAULT 3"),
                ("content", "content TEXT"),
                ("content_type", "content_type TEXT"),
                ("content_size", "content_size INTEGER DEFAULT 0"),
                ("content_url", "content_url TEXT"),
                ("content_hash", "content_hash TEXT"),
                ("file_name", "file_name TEXT"),
                ("file_extension", "file_extension TEXT"),
                ("mime_type", "mime_type TEXT"),
                ("dimensions", "dimensions JSONB DEFAULT '{}'"),
                ("ai_generated", "ai_generated BOOLEAN DEFAULT FALSE"),
                ("ai_model", "ai_model TEXT"),
                ("ai_prompt", "ai_prompt TEXT"),
                ("ai_parameters", "ai_parameters JSONB DEFAULT '{}'"),
                ("ai_confidence", "ai_confidence DECIMAL(3,2) DEFAULT 0.00"),
                ("ai_processing_time", "ai_processing_time INTEGER"),
                ("ai_generated_at", "ai_generated_at TIMESTAMPTZ"),
                ("inspiration_source", "inspiration_source TEXT"),
                ("inspiration_context", "inspiration_context JSONB DEFAULT '{}'"),
                ("creative_brief", "creative_brief TEXT"),
                ("style_preferences", "style_preferences JSONB DEFAULT '{}'"),
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
                    "parent_asset_id",
                    "parent_asset_id UUID REFERENCES muse_assets(id) ON DELETE SET NULL",
                ),
                ("usage_count", "usage_count INTEGER DEFAULT 0"),
                ("download_count", "download_count INTEGER DEFAULT 0"),
                ("share_count", "share_count INTEGER DEFAULT 0"),
                ("view_count", "view_count INTEGER DEFAULT 0"),
                ("like_count", "like_count INTEGER DEFAULT 0"),
                ("conversion_rate", "conversion_rate DECIMAL(5,2) DEFAULT 0.00"),
                ("quality_score", "quality_score DECIMAL(3,2) DEFAULT 0.00"),
                ("moderation_status", "moderation_status TEXT DEFAULT 'pending'"),
                ("moderation_notes", "moderation_notes TEXT"),
                (
                    "moderated_by",
                    "moderated_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                ("moderated_at", "moderated_at TIMESTAMPTZ"),
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
                    "approved_by",
                    "approved_by UUID REFERENCES users(id) ON DELETE SET NULL",
                ),
                ("created_at", "created_at TIMESTAMPTZ DEFAULT NOW()"),
                ("updated_at", "updated_at TIMESTAMPTZ DEFAULT NOW()"),
                ("published_at", "published_at TIMESTAMPTZ"),
                ("archived_at", "archived_at TIMESTAMPTZ"),
            ]

            for column_name, column_pattern in required_columns:
                if column_pattern in content:
                    self.add_result(
                        f"Muse assets table has {column_name} column",
                        True,
                        f"Column definition found",
                    )
                else:
                    self.add_result(
                        f"Muse assets table has {column_name} column",
                        False,
                        f"Column definition missing",
                    )

            # Check for workspace_id constraint
            if "workspace_id UUID NOT NULL REFERENCES workspaces(id)" in content:
                self.add_result(
                    "Muse assets table has workspace_id constraint",
                    True,
                    "Foreign key constraint found",
                )
            else:
                self.add_result(
                    "Muse assets table has workspace_id constraint",
                    False,
                    "Foreign key constraint missing",
                )

            # Check for parent_asset_id constraint
            if (
                "parent_asset_id UUID REFERENCES muse_assets(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Muse assets table has parent asset constraint",
                    True,
                    "Self-referencing foreign key found",
                )
            else:
                self.add_result(
                    "Muse assets table has parent asset constraint",
                    False,
                    "Self-referencing foreign key missing",
                )

            # Check for RLS enablement
            if "ALTER TABLE public.muse_assets ENABLE ROW LEVEL SECURITY" in content:
                self.add_result(
                    "Muse assets table has RLS enabled", True, "RLS enablement found"
                )
            else:
                self.add_result(
                    "Muse assets table has RLS enabled", False, "RLS enablement missing"
                )

            # Check for vector index
            if "ivfflat (content_embedding vector_cosine_ops)" in content:
                self.add_result(
                    "Muse assets table has vector index",
                    True,
                    "Vector index for semantic search found",
                )
            else:
                self.add_result(
                    "Muse assets table has vector index", False, "Vector index missing"
                )

            # Check for unique constraints
            unique_constraints = [
                "idx_muse_assets_unique_content_hash",
                "idx_muse_assets_unique_title",
            ]

            for constraint in unique_constraints:
                if constraint in content:
                    self.add_result(
                        f"Muse assets table has {constraint}",
                        True,
                        f"Unique constraint found",
                    )
                else:
                    self.add_result(
                        f"Muse assets table has {constraint}",
                        False,
                        f"Unique constraint missing",
                    )

        except Exception as e:
            self.add_result(
                "Muse assets table structure verification",
                False,
                f"Error reading migration: {str(e)}",
            )

    def test_rls_policies(self):
        """Test if RLS policies are correctly defined"""
        rls_file = os.path.join(self.supabase_path, "20240107_muse_assets_rls.sql")

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
        migration_file = os.path.join(self.supabase_path, "20240107_muse_assets.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            jsonb_columns = [
                "dimensions",
                "ai_parameters",
                "inspiration_context",
                "style_preferences",
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
        migration_file = os.path.join(self.supabase_path, "20240107_muse_assets.sql")

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

            # Check parent_asset_id relationship
            if (
                "parent_asset_id UUID REFERENCES muse_assets(id) ON DELETE SET NULL"
                in content
            ):
                self.add_result(
                    "Parent asset ID foreign key correct",
                    True,
                    "parent_asset_id references muse_assets(id) with SET NULL",
                )
            else:
                self.add_result(
                    "Parent asset ID foreign key correct",
                    False,
                    "parent_asset_id foreign key missing or incorrect",
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
        migration_file = os.path.join(self.supabase_path, "20240107_muse_assets.sql")

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

            # Check content size constraint
            if "CHECK (content_size >= 0)" in content:
                self.add_result(
                    "Content size constraint implemented",
                    True,
                    "Content size >= 0 constraint found",
                )
            else:
                self.add_result(
                    "Content size constraint implemented",
                    False,
                    "Content size >= 0 constraint missing",
                )

            # Check usage count constraints
            usage_constraints = [
                "CHECK (usage_count >= 0)",
                "CHECK (download_count >= 0)",
                "CHECK (share_count >= 0)",
                "CHECK (view_count >= 0)",
                "CHECK (like_count >= 0)",
            ]

            all_usage_constraints = all(
                constraint in content for constraint in usage_constraints
            )

            if all_usage_constraints:
                self.add_result(
                    "Usage count constraints implemented",
                    True,
                    "All usage count constraints found",
                )
            else:
                self.add_result(
                    "Usage count constraints implemented",
                    False,
                    "Some usage count constraints missing",
                )

            # Check quality score constraint
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
        migration_file = os.path.join(self.supabase_path, "20240107_muse_assets.sql")

        try:
            with open(migration_file, "r") as f:
                content = f.read()

            required_indexes = [
                "idx_muse_assets_workspace_id",
                "idx_muse_assets_asset_type",
                "idx_muse_assets_category",
                "idx_muse_assets_status",
                "idx_muse_assets_priority",
                "idx_muse_assets_ai_generated",
                "idx_muse_assets_content_hash",
                "idx_muse_assets_created_at",
                "idx_muse_assets_created_by",
                "idx_muse_assets_published_at",
                "idx_muse_assets_usage_count",
                "idx_muse_assets_quality_score",
                "idx_muse_assets_foundation_id",
                "idx_muse_assets_icp_profile_id",
                "idx_muse_assets_campaign_id",
                "idx_muse_assets_move_id",
                "idx_muse_assets_parent_asset_id",
                "idx_muse_assets_is_latest",
                "idx_muse_assets_tags",
                "idx_muse_assets_keywords",
                "idx_muse_assets_attributes",
                "idx_muse_assets_content_embedding",
                "idx_muse_assets_unique_content_hash",
                "idx_muse_assets_unique_title",
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
        print("CYNICAL VERIFICATION - Task 9: Muse Assets Table")
        print("=" * 60)

        self.test_muse_assets_migration_exists()
        self.test_muse_assets_table_structure()
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
            print("✓ ALL TESTS PASSED - Task 9 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 9 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = MuseAssetsTableTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
