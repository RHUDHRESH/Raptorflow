import pytest

pytest.skip("Legacy test archived; superseded by canonical test suite.", allow_module_level=True)

﻿"""
Test script to verify DatabaseTool workspace isolation.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from .agents.tools.database import DatabaseTool
from .agents.tools.registry import get_tool_registry


async def test_database_tool_workspace_isolation():
    """Test that DatabaseTool enforces workspace_id filtering."""
    print("Testing DatabaseTool workspace isolation...")

    try:
        # Create tool instance
        tool = DatabaseTool()
        print(f"Γ£ô DatabaseTool instantiated: {tool.name}")

        # Test 1: Query without workspace_id should fail
        print("\nTesting query without workspace_id...")
        try:
            result1 = await tool.arun(
                table="foundations", workspace_id="", limit=5  # Empty workspace_id
            )
            if not result1.success and "workspace_id is required" in result1.error:
                print("Γ£ô Query without workspace_id properly rejected")
            else:
                print("Γ£ù Query without workspace_id not properly rejected")
                return False
        except Exception as e:
            print(f"Γ£ù Unexpected error: {e}")
            return False

        # Test 2: Query with valid workspace_id should succeed
        print("\nTesting query with valid workspace_id...")
        tool.set_workspace_id("test-workspace-123")
        result2 = await tool.arun(
            table="foundations", workspace_id="test-workspace-123", limit=5
        )

        if result2.success:
            data = result2.data
            print(f"Γ£ô Query succeeded")
            print(f"Γ£ô Table: {data['table']}")
            print(f"Γ£ô Workspace ID: {data['workspace_id']}")
            print(f"Γ£ô Total count: {data['total_count']}")

            # Verify all results have the correct workspace_id
            all_correct_workspace = all(
                item.get("workspace_id") == "test-workspace-123"
                for item in data["data"]
            )

            if all_correct_workspace:
                print("Γ£ô All results filtered by workspace_id")
            else:
                print("Γ£ù Some results have incorrect workspace_id")
                return False

            # Test 3: Query with filters should work
            print("\nTesting query with filters...")
            result3 = await tool.arun(
                table="moves",
                workspace_id="test-workspace-123",
                filters={"status": "draft"},
                limit=10,
            )

            if result3.success:
                filtered_data = result3.data
                print(f"Γ£ô Filtered query succeeded")

                # Verify all results have the filter value
                all_filtered = all(
                    item.get("status") == "draft" for item in filtered_data["data"]
                )

                if all_filtered:
                    print("Γ£ô All results match filter criteria")
                else:
                    print("Γ£ù Some results don't match filter criteria")
                    return False
            else:
                print(f"Γ£ù Filtered query failed: {result3.error}")
                return False

        else:
            print(f"Γ£ù Query with workspace_id failed: {result2.error}")
            return False

        # Test 4: Query with invalid table should fail
        print("\nTesting query with invalid table...")
        result4 = await tool.arun(
            table="invalid_table", workspace_id="test-workspace-123", limit=5
        )

        if not result4.success and "Invalid table" in result4.error:
            print("Γ£ô Invalid table properly rejected")
        else:
            print("Γ£ù Invalid table not properly rejected")
            return False

        # Test 5: Verify available tables
        tables = tool.get_available_tables()
        expected_tables = [
            "foundations",
            "icp_profiles",
            "moves",
            "campaigns",
            "muse_assets",
            "blackbox_strategies",
            "daily_wins",
            "agent_executions",
        ]

        if all(table in tables for table in expected_tables):
            print(f"Γ£ô All expected tables available: {tables}")
        else:
            missing = [t for t in expected_tables if t not in tables]
            print(f"Γ£ù Missing tables: {missing}")
            return False

        return True

    except Exception as e:
        print(f"Γ£ù DatabaseTool test failed: {e}")
        return False


async def test_workspace_isolation_explanation():
    """Test workspace isolation explanation."""
    print("\nTesting workspace isolation explanation...")

    try:
        tool = DatabaseTool()
        explanation = tool.explain_workspace_isolation()

        if "workspace_id" in explanation and "RLS policies" in explanation:
            print("Γ£ô Workspace isolation explanation is comprehensive")
            print(
                f"Γ£ô Key points: workspace_id filtering, RLS policies, no cross-workspace leakage"
            )
            return True
        else:
            print("Γ£ù Workspace isolation explanation is incomplete")
            return False

    except Exception as e:
        print(f"Γ£ù Explanation test failed: {e}")
        return False


async def main():
    """Run all DatabaseTool tests."""
    print("=== DatabaseTool Workspace Isolation Tests ===\n")

    # Test workspace isolation
    isolation_test = await test_database_tool_workspace_isolation()

    # Test explanation
    explanation_test = await test_workspace_isolation_explanation()

    # Summary
    print("\n=== Test Summary ===")
    print(f"Workspace Isolation: {'Γ£ô' if isolation_test else 'Γ£ù'}")
    print(f"Explanation: {'Γ£ô' if explanation_test else 'Γ£ù'}")

    if isolation_test and explanation_test:
        print("\nΓ£à All DatabaseTool tests passed!")
        return True
    else:
        print("\nΓ¥î Some DatabaseTool tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
