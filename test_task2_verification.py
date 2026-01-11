#!/usr/bin/env python3
"""
CYNICAL VERIFICATION - Task 2: Foundations Table
Tests if foundations table exists and enforces workspace isolation
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


class FoundationsTester:
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

    async def test_foundations_table_exists(self):
        """Test if foundations table actually exists"""
        try:
            # Test foundations table
            result = (
                self.client.table("foundations")
                .select("count", count="exact")
                .execute()
            )
            if hasattr(result, "data") and result.data is not None:
                self.add_result(
                    "Foundations table exists",
                    True,
                    f"Query returned data: {result.data}",
                )
            else:
                self.add_result(
                    "Foundations table exists", False, "Query failed or returned None"
                )
        except Exception as e:
            # Check if it's a "relation does not exist" error
            if "does not exist" in str(e).lower() or "relation" in str(e).lower():
                self.add_result(
                    "Foundations table exists", False, "Table does not exist", str(e)
                )
            else:
                self.add_result(
                    "Foundations table exists", False, f"Unexpected error: {str(e)}"
                )

    async def test_workspace_id_column_exists(self):
        """Test if workspace_id column exists"""
        try:
            # Try to select workspace_id specifically
            result = (
                self.client.table("foundations")
                .select("workspace_id", count="exact")
                .execute()
            )
            if hasattr(result, "data") and result.data is not None:
                self.add_result(
                    "Foundations has workspace_id column",
                    True,
                    "workspace_id column selectable",
                )
            else:
                self.add_result(
                    "Foundations has workspace_id column",
                    False,
                    "workspace_id column not selectable",
                )
        except Exception as e:
            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                self.add_result(
                    "Foundations has workspace_id column",
                    False,
                    "workspace_id column does not exist",
                    str(e),
                )
            else:
                self.add_result(
                    "Foundations has workspace_id column",
                    False,
                    f"Error checking column: {str(e)}",
                )

    async def test_unique_constraint(self):
        """Test if UNIQUE(workspace_id) constraint exists"""
        try:
            # This would require actual data insertion to test properly
            # For now, check if we can query the constraint
            result = self.client.rpc(
                "get_constraints", {"table_name": "foundations"}
            ).execute()

            has_unique = False
            if hasattr(result, "data") and result.data:
                for constraint in result.data:
                    if constraint.get(
                        "constraint_type"
                    ) == "u" and "workspace_id" in str(constraint):
                        has_unique = True
                        break

            if has_unique:
                self.add_result(
                    "Foundations has UNIQUE(workspace_id)",
                    True,
                    "Unique constraint found",
                )
            else:
                self.add_result(
                    "Foundations has UNIQUE(workspace_id)",
                    False,
                    "Unique constraint not found",
                )
        except Exception as e:
            # If we can't check constraints, at least verify the structure
            self.add_result(
                "Foundations has UNIQUE(workspace_id)",
                False,
                f"Cannot verify constraint: {str(e)}",
            )

    async def test_rls_policy_exists(self):
        """Test if RLS policy exists for foundations"""
        try:
            # Try to query without auth - should be blocked if RLS works
            result = self.client.table("foundations").select("*").execute()

            if hasattr(result, "data") and len(result.data) > 0:
                self.add_result(
                    "Foundations RLS policy active",
                    False,
                    "Got data without authentication - RLS might be disabled",
                    f"Returned {len(result.data)} rows",
                )
            else:
                self.add_result(
                    "Foundations RLS policy active",
                    True,
                    "No data returned without auth (RLS working)",
                )
        except Exception as e:
            if "row-level security" in str(e).lower() or "permission" in str(e).lower():
                self.add_result(
                    "Foundations RLS policy active",
                    True,
                    "Got RLS/permission error (expected)",
                    str(e),
                )
            else:
                self.add_result(
                    "Foundations RLS policy active",
                    False,
                    f"Unexpected error: {str(e)}",
                )

    async def test_jsonb_columns(self):
        """Test if JSONB columns exist for flexible data"""
        jsonb_columns = [
            "truth_sheet",
            "market_research",
            "competitors",
            "positioning",
            "brand_voice_examples",
            "messaging_guardrails",
            "soundbite_library",
            "message_hierarchy",
        ]

        for column in jsonb_columns:
            try:
                result = (
                    self.client.table("foundations")
                    .select(column, count="exact")
                    .execute()
                )
                if hasattr(result, "data") and result.data is not None:
                    self.add_result(
                        f"Foundations has {column} column",
                        True,
                        f"{column} column selectable",
                    )
                else:
                    self.add_result(
                        f"Foundations has {column} column",
                        False,
                        f"{column} column not selectable",
                    )
            except Exception as e:
                if "column" in str(e).lower() and "does not exist" in str(e).lower():
                    self.add_result(
                        f"Foundations has {column} column",
                        False,
                        f"{column} column does not exist",
                        str(e),
                    )
                else:
                    self.add_result(
                        f"Foundations has {column} column",
                        False,
                        f"Error checking {column}: {str(e)}",
                    )

    async def test_vector_column(self):
        """Test if summary_embedding vector column exists"""
        try:
            # Try to select the vector column
            result = (
                self.client.table("foundations")
                .select("summary_embedding", count="exact")
                .execute()
            )
            if hasattr(result, "data") and result.data is not None:
                self.add_result(
                    "Foundations has summary_embedding vector",
                    True,
                    "Vector column exists for semantic search",
                )
            else:
                self.add_result(
                    "Foundations has summary_embedding vector",
                    False,
                    "Vector column not found",
                )
        except Exception as e:
            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                self.add_result(
                    "Foundations has summary_embedding vector",
                    False,
                    "Vector column does not exist",
                    str(e),
                )
            else:
                self.add_result(
                    "Foundations has summary_embedding vector",
                    False,
                    f"Error checking vector: {str(e)}",
                )

    async def run_all_tests(self):
        """Run all verification tests"""
        print("=" * 60)
        print("CYNICAL VERIFICATION - Task 2: Foundations Table")
        print("=" * 60)

        await self.test_foundations_table_exists()
        await self.test_workspace_id_column_exists()
        await self.test_unique_constraint()
        await self.test_rls_policy_exists()
        await self.test_jsonb_columns()
        await self.test_vector_column()

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print(f"Tests passed: {passed}/{total}")

        if passed == total:
            print("✓ ALL TESTS PASSED - Task 2 verified empirically")
            return True
        else:
            print("✗ SOME TESTS FAILED - Task 2 needs fixes")
            for result in self.results:
                if not result.passed:
                    print(f"  FAILED: {result.test_name} - {result.details}")
            return False


if __name__ == "__main__":
    tester = FoundationsTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
