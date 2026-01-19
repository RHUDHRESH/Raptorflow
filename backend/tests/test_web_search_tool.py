"""
Test script to verify WebSearchTool functionality.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.agents.tools.registry import get_tool_registry
from backend.agents.tools.web_search import WebSearchTool


async def test_web_search_tool():
    """Test that WebSearchTool searches and returns results."""
    print("Testing WebSearchTool functionality...")

    try:
        # Create tool instance
        tool = WebSearchTool()
        print(f"✓ WebSearchTool instantiated: {tool.name}")

        # Set workspace context
        tool.set_workspace_id("test-workspace-123")
        print(f"✓ Workspace ID set: {tool.workspace_id}")

        # Test search with valid query
        print("\nTesting search with valid query...")
        result1 = await tool.arun(
            query="artificial intelligence marketing",
            max_results=5,
            engines=["google", "bing"],
        )

        if result1.success:
            data = result1.data
            print(f"✓ Search succeeded")
            print(f"✓ Query: {data['query']}")
            print(f"✓ Results count: {data['total_results']}")
            print(f"✓ Search time: {data['search_time_ms']}ms")

            # Check result structure
            if "results" in data and data["results"]:
                first_result = data["results"][0]
                print(f"✓ First result title: {first_result['title']}")
                print(f"✓ First result engine: {first_result['engine']}")
                print(
                    f"✓ Has snippet: {'Yes' if first_result.get('snippet') else 'No'}"
                )
            else:
                print("✗ No results in data")
                return False
        else:
            print(f"✗ Search failed: {result1.error}")
            return False

        # Test with invalid query
        print("\nTesting search with invalid query...")
        result2 = await tool.arun(query="ab", max_results=5)  # Too short

        if not result2.success and "at least 3 characters" in result2.error:
            print("✓ Invalid query properly rejected")
        else:
            print("✗ Invalid query not properly rejected")
            return False

        # Test available engines
        engines = tool.get_available_engines()
        print(f"✓ Available engines: {engines}")

        return True

    except Exception as e:
        print(f"✗ WebSearchTool test failed: {e}")
        return False


async def test_tool_registry():
    """Test that ToolRegistry includes WebSearchTool."""
    print("\nTesting ToolRegistry integration...")

    try:
        registry = get_tool_registry()

        # Check if WebSearchTool is registered
        web_search_tool = registry.get("web_search")
        if web_search_tool:
            print("✓ WebSearchTool found in registry")
        else:
            print("✗ WebSearchTool not found in registry")
            return False

        # Check category
        search_tools = registry.get_by_category("search")
        if any(tool.name == "web_search" for tool in search_tools):
            print("✓ WebSearchTool found in search category")
        else:
            print("✗ WebSearchTool not found in search category")
            return False

        # Check registry stats
        stats = registry.get_registry_stats()
        print(
            f"✓ Registry stats: {stats['total_tools']} tools, {stats['total_categories']} categories"
        )

        return True

    except Exception as e:
        print(f"✗ ToolRegistry test failed: {e}")
        return False


async def main():
    """Run all WebSearchTool tests."""
    print("=== WebSearchTool Verification Tests ===\n")

    # Test WebSearchTool directly
    search_test = await test_web_search_tool()

    # Test ToolRegistry integration
    registry_test = await test_tool_registry()

    # Summary
    print("\n=== Test Summary ===")
    print(f"WebSearchTool Direct: {'✓' if search_test else '✗'}")
    print(f"ToolRegistry Integration: {'✓' if registry_test else '✗'}")

    if search_test and registry_test:
        print("\n✅ All WebSearchTool tests passed!")
        return True
    else:
        print("\n❌ Some WebSearchTool tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
