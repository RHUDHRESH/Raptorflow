#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 3: ICP Profiles Table
Tests if ICP table exists and enforces max 1 primary per workspace
No "graceful failures" - either it works or it's broken
"""

import asyncio
import os
import sys
from dataclasses import dataclass
from typing import Optional

# Try to import Supabase
try:
    from supabase import Client, create_client
except ImportError:
    print("FAIL: Supabase client not installed")
    sys.exit(1)


@dataclass
class TestResult:
    test_name: str
    passed: bool
    details: str
    evidence: Optional[str] = None


class ICPTester:
    def __init__(self):
        # Try to get Supabase credentials
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not self.supabase_url or not self.supabase_key:
            print("FAIL: SUPABASE_URL or SUPABASE_ANON_KEY not set")
            sys.exit(1)

        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.results = []

    def add_result(
        self, test_name: str, passed: bool, details: str, evidence: str = None
    ):
        self.results.append(TestResult(test_name, passed, details, evidence))
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name} - {details}")
        if evidence:
            print(f"  Evidence: {evidence}")

    async def test_icp_table_exists(self):
        """Test if icp_profiles table actually exists"""
        try:
            # Test icp_profiles table
            result = (
                self.client.table("icp_profiles")
                .select("count", count="exact")
                .execute()
            )
            if hasattr(result, "data") and result.data is not None:
                self.add_result(
                    "ICP profiles table exists",
                    True,
                    f"Query returned data: {result.data}",
                )
            else:
                self.add_result(
                    "ICP profiles table exists", False, "Query failed or returned None"
                )
        except Exception as e:
            # Check if it's a "relation does not exist" error
            if "does not exist" in str(e).lower() or "relation" in str(e).lower():
                self.add_result(
                    "ICP profiles table exists", False, "Table does not exist", str(e)
                )
            else:
                self.add_result(
                    "ICP profiles table exists", False, f"Unexpected error: {str(e)}"
                )

    async def test_workspace_id_column(self):
        """Test if workspace_id column exists"""
        try:
            result = (
                self.client.table("icp_profiles")
                .select("workspace_id", count="exact")
                .execute()
            )
            if hasattr(result, "data") and result.data is not None:
                self.add_result(
                    "ICP has workspace_id column",
                    True,
                    "workspace_id column selectable",
                )
            else:
                self.add_result(
                    "ICP has workspace_id column",
                    False,
                    "workspace_id column not selectable",
                )
        except Exception as e:
            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                self.add_result(
                    "ICP has workspace_id column",
                    False,
                    "workspace_id column does not exist",
                    str(e),
                )
            else:
                self.add_result(
                    "ICP has workspace_id column",
                    False,
                    f"Error checking column: {str(e)}",
                )

    async def test_is_primary_column(self):
        """Test if is_primary column exists"""
        try:
            result = (
                self.client.table("icp_profiles")
                .select("is_primary", count="exact")
                .execute()
            )
            if hasattr(result, "data") and result.data is not None:
                self.add_result(
                    "ICP has is_primary column", True, "is_primary column selectable"
                )
            else:
                self.add_result(
                    "ICP has is_primary column",
                    False,
                    "is_primary column not selectable",
                )
        except Exception as e:
            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                self.add_result(
                    "ICP has is_primary column",
                    False,
                    "is_primary column does not exist",
                    str(e),
                )
            else:
                self.add_result(
                    "ICP has is_primary column",
                    False,
                    f"Error checking column: {str(e)}",
                )

    async def test_unique_primary_constraint(self):
        """Test if unique constraint on (workspace_id, is_primary) exists"""
        try:
            # Check if the unique index exists
            result = self.client.rpc(
                "get_indexes", {"table_name": "icp_profiles"}
            ).execute()

            has_unique_constraint = False
            if hasattr(result, "data") and result.data:
                for index in result.data:
                    index_def = str(index).lower()
                    if (
                        "unique" in index_def
                        and "is_primary" in index_def
                        and "workspace_id" in index_def
                    ):
                        has_unique_constraint = True
                        break

            if has_unique_constraint:
                self.add_result(
                    "ICP has unique primary constraint",
                    True,
                    "Unique constraint on (workspace_id, is_primary) found",
                )
            else:
                self.add_result(
                    "ICP has unique primary constraint",
                    False,
                    "Unique constraint not found - multiple primaries possible",
                )
        except Exception as e:
            # Try alternative method - check index name
            try:
                # The index should be named idx_icp_profiles_unique_primary
                result = (
                    self.client.table("pg_indexes")
                    .select("*")
                    .eq("tablename", "icp_profiles")
                    .execute()
                )
                if hasattr(result, "data") and result.data:
                    for index in result.data:
                        if "unique_primary" in str(index.get("indexname", "")).lower():
                            self.add_result(
                                "ICP has unique primary constraint",
                                True,
                                "Found idx_icp_profiles_unique_primary index",
                            )
                            return

                self.add_result(
                    "ICP has unique primary constraint",
                    False,
                    "Cannot verify constraint: " + str(e),
                )
            except:
                self.add_result(
                    "ICP has unique primary constraint",
                    False,
                    f"Cannot verify constraint: {str(e)}",
                )

    async def test_jsonb_structure(self):
        """Test if required JSONB columns exist"""
        required_jsonb = [
            "demographics",
            "psychographics",
            "behaviors",
            "market_sophistication",
            "scores",
        ]

        for column in required_jsonb:
            try:
                result = (
                    self.client.table("icp_profiles")
                    .select(column, count="exact")
                    .execute()
                )
                if hasattr(result, "data") and result.data is not None:
                    self.add_result(
                        f"ICP has {column} JSONB", True, f"{column} column exists"
                    )
                else:
                    self.add_result(
                        f"ICP has {column} JSONB", False, f"{column} column not found"
                    )
            except Exception as e:
                if "column" in str(e).lower() and "does not exist" in str(e).lower():
                    self.add_result(
                        f"ICP has {column} JSONB",
                        False,
                        f"{column} column does not exist",
                        str(e),
                    )
                else:
                    self.add_result(
                        f"ICP has {column} JSONB",
                        False,
                        f"Error checking {column}: {str(e)}",
                    )

    async def test_vector_column(self):
        """Test if summary_embedding vector column exists"""
        try:
            result = (
                self.client.table("icp_profiles")
                .select("summary_embedding", count="exact")
                .execute()
            )
            if hasattr(result, "data") and result.data is not None:
                self.add_result(
                    "ICP has summary_embedding vector",
                    True,
                    "Vector column exists for semantic search",
                )
            else:
                self.add_result(
                    "ICP has summary_embedding vector", False, "Vector column not found"
                )
        except Exception as e:
            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                self.add_result(
                    "ICP has summary_embedding vector",
                    False,
                    "Vector column does not exist",
                    str(e),
                )
            else:
                self.add_result(
                    "ICP has summary_embedding vector",
                    False,
                    f"Error checking vector: {str(e)}",
                )

    async def test_rls_policy(self):
        """Test if RLS policy exists for icp_profiles"""
        try:
            result = self.client.table("icp_profiles").select("*").execute()

            if hasattr(result, "data") and len(result.data) > 0:
                self.add_result(
                    "ICP RLS policy active",
                    False,
                    "Got data without authentication - RLS might be disabled",
                    f"Returned {len(result.data)} rows",
                )
            else:
                self.add_result(
                    "ICP RLS policy active",
                    True,
                    "No data returned without auth (RLS working)",
                )
        except Exception as e:
            if "row-level security" in str(e).lower() or "permission" in str(e).lower():
                self.add_result(
                    "ICP RLS policy active",
                    True,
                    "Got RLS/permission error (expected)",
                    str(e),
                )
            else:
                self.add_result(
                    "ICP RLS policy active", False, f"Unexpected error: {str(e)}"
                )

    async def run_all_tests(self):
        """Run all verification tests"""
        print("=" * 60)
        print("CYNICAL VERIFICATION - Task 3: ICP Profiles Table")
        print("=" * 60)

        await self.test_icp_table_exists()
        await self.test_workspace_id_column()
        await self.test_is_primary_column()
        await self.test_unique_primary_constraint()
        await self.test_jsonb_structure()
        await self.test_vector_column()
        await self.test_rls_policy()

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print(f"Tests passed: {passed}/{total}")

        if passed == total:
            print("✓ ALL TESTS PASSED - Task 3 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 3 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = ICPTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
