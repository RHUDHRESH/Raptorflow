"""
Test file to verify tool registry manages tools correctly.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

# Import base classes for testing
from backend.agents.base import BaseTool

# Import all tools
from backend.agents.tools.content_generator import ContentGenerator
from backend.agents.tools.export_tool import ExportTool
from backend.agents.tools.feedback_tool import FeedbackTool

# Import tool registry
from backend.agents.tools.registry import ToolRegistry
from backend.agents.tools.template_tool import TemplateTool

logger = logging.getLogger(__name__)


class TestToolRegistry:
    """Test suite for tool registry functionality."""

    def __init__(self):
        self.test_results = {}
        self.registry = ToolRegistry()
        self.test_tools = {}

    async def run_all_tests(self):
        """Run all tool registry tests."""
        logger.info("Starting tool registry tests")

        # Initialize test tools
        await self.initialize_test_tools()

        # Test tool registration
        await self.test_tool_registration()

        # Test tool retrieval
        await self.test_tool_retrieval()

        # Test tool categories
        await self.test_tool_categories()

        # Test tool discovery
        await self.test_tool_discovery()

        # Test tool removal
        await self.test_tool_removal()

        # Test concurrent access
        await self.test_concurrent_registry_access()

        # Print results
        self.print_test_results()

        return self.test_results

    async def initialize_test_tools(self):
        """Initialize test tools."""
        logger.info("Initializing test tools...")

        self.test_tools = {
            "ContentGenerator": ContentGenerator(),
            "TemplateTool": TemplateTool(),
            "FeedbackTool": FeedbackTool(),
            "ExportTool": ExportTool(),
        }

        for tool_name, tool in self.test_tools.items():
            try:
                # Verify tool is a BaseTool subclass
                assert isinstance(
                    tool, BaseTool
                ), f"{tool_name} is not a BaseTool subclass"

                # Register tool
                self.registry.register_tool(tool)

                self.test_results[f"{tool_name}_initialization"] = {
                    "status": "PASS",
                    "message": f"{tool_name} initialized and registered successfully",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(f"✅ {tool_name} initialized and registered successfully")

            except Exception as e:
                self.test_results[f"{tool_name}_initialization"] = {
                    "status": "FAIL",
                    "message": f"{tool_name} initialization failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {tool_name} initialization failed: {e}")

    async def test_tool_registration(self):
        """Test tool registration functionality."""
        logger.info("Testing tool registration...")

        try:
            # Test registering tools
            registered_tools = self.registry.get_all_tools()

            # Verify all test tools are registered
            expected_tools = set(self.test_tools.keys())
            actual_tools = set(tool.name for tool in registered_tools)

            registration_success = expected_tools.issubset(actual_tools)

            # Test duplicate registration
            duplicate_tool = ContentGenerator()
            original_count = len(self.registry.get_all_tools())

            try:
                self.registry.register_tool(duplicate_tool)
                duplicate_handled = len(self.registry.get_all_tools()) == original_count
            except Exception:
                duplicate_handled = True  # Exception is expected

            # Test invalid tool registration
            invalid_tool_handled = False
            try:
                self.registry.register_tool("not_a_tool")
                invalid_tool_handled = False
            except Exception:
                invalid_tool_handled = True  # Exception is expected

            self.test_results["tool_registration"] = {
                "status": (
                    "PASS"
                    if registration_success
                    and duplicate_handled
                    and invalid_tool_handled
                    else "FAIL"
                ),
                "message": f"Tool registration {'successful' if registration_success else 'failed'}",
                "expected_tools": list(expected_tools),
                "actual_tools": list(actual_tools),
                "duplicate_handled": duplicate_handled,
                "invalid_tool_handled": invalid_tool_handled,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Tool registration {'successful' if registration_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["tool_registration"] = {
                "status": "FAIL",
                "message": f"Tool registration test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Tool registration test failed: {e}")

    async def test_tool_retrieval(self):
        """Test tool retrieval functionality."""
        logger.info("Testing tool retrieval...")

        try:
            retrieval_results = {}

            for tool_name in self.test_tools.keys():
                try:
                    # Test get by name
                    tool = self.registry.get_tool(tool_name)
                    retrieval_success = tool is not None and tool.name == tool_name

                    # Test get by class
                    tool_class = self.test_tools[tool_name].__class__
                    tool_by_class = self.registry.get_tool_by_class(tool_class)
                    class_retrieval_success = (
                        tool_by_class is not None and tool_by_class.name == tool_name
                    )

                    # Test get non-existent tool
                    non_existent = self.registry.get_tool("non_existent_tool")
                    non_existent_success = non_existent is None

                    retrieval_results[tool_name] = {
                        "by_name": retrieval_success,
                        "by_class": class_retrieval_success,
                        "non_existent": non_existent_success,
                        "overall": retrieval_success
                        and class_retrieval_success
                        and non_existent_success,
                    }

                except Exception as e:
                    retrieval_results[tool_name] = {"error": str(e), "overall": False}

            # Check overall retrieval success
            overall_success = all(
                result.get("overall", False) for result in retrieval_results.values()
            )

            self.test_results["tool_retrieval"] = {
                "status": "PASS" if overall_success else "FAIL",
                "message": f"Tool retrieval {'successful' if overall_success else 'failed'}",
                "retrieval_results": retrieval_results,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Tool retrieval {'successful' if overall_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["tool_retrieval"] = {
                "status": "FAIL",
                "message": f"Tool retrieval test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Tool retrieval test failed: {e}")

    async def test_tool_categories(self):
        """Test tool categorization functionality."""
        logger.info("Testing tool categories...")

        try:
            # Test getting tools by category
            categories = self.registry.get_categories()

            # Verify categories exist
            categories_exist = len(categories) > 0

            # Test getting tools in each category
            category_results = {}

            for category in categories:
                try:
                    tools_in_category = self.registry.get_tools_by_category(category)
                    category_results[category] = {
                        "tool_count": len(tools_in_category),
                        "tools": [tool.name for tool in tools_in_category],
                        "success": True,
                    }
                except Exception as e:
                    category_results[category] = {"error": str(e), "success": False}

            # Test category assignment
            category_assignment_success = True
            for tool_name, tool in self.test_tools.items():
                tool_categories = self.registry.get_tool_categories(tool.name)
                if not tool_categories:
                    category_assignment_success = False
                    break

            self.test_results["tool_categories"] = {
                "status": (
                    "PASS"
                    if categories_exist and category_assignment_success
                    else "FAIL"
                ),
                "message": f"Tool categories {'successful' if categories_exist and category_assignment_success else 'failed'}",
                "categories": categories,
                "category_results": category_results,
                "category_assignment_success": category_assignment_success,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Tool categories {'successful' if categories_exist and category_assignment_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["tool_categories"] = {
                "status": "FAIL",
                "message": f"Tool categories test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Tool categories test failed: {e}")

    async def test_tool_discovery(self):
        """Test tool discovery functionality."""
        logger.info("Testing tool discovery...")

        try:
            discovery_results = {}

            # Test search functionality
            search_terms = ["content", "template", "feedback", "export", "generate"]

            for search_term in search_terms:
                try:
                    search_results = self.registry.search_tools(search_term)
                    discovery_results[f"search_{search_term}"] = {
                        "term": search_term,
                        "results": [tool.name for tool in search_results],
                        "count": len(search_results),
                        "success": True,
                    }
                except Exception as e:
                    discovery_results[f"search_{search_term}"] = {
                        "error": str(e),
                        "success": False,
                    }

            # Test tool metadata
            metadata_results = {}

            for tool_name in self.test_tools.keys():
                try:
                    metadata = self.registry.get_tool_metadata(tool_name)
                    metadata_success = metadata is not None and isinstance(
                        metadata, dict
                    )

                    metadata_results[tool_name] = {
                        "metadata_success": metadata_success,
                        "metadata_keys": (
                            list(metadata.keys()) if metadata_success else []
                        ),
                        "success": metadata_success,
                    }
                except Exception as e:
                    metadata_results[tool_name] = {"error": str(e), "success": False}

            # Test tool capabilities
            capabilities_results = {}

            for tool_name in self.test_tools.keys():
                try:
                    capabilities = self.registry.get_tool_capabilities(tool_name)
                    capabilities_success = capabilities is not None and isinstance(
                        capabilities, dict
                    )

                    capabilities_results[tool_name] = {
                        "capabilities_success": capabilities_success,
                        "capability_count": (
                            len(capabilities) if capabilities_success else 0
                        ),
                        "success": capabilities_success,
                    }
                except Exception as e:
                    capabilities_results[tool_name] = {
                        "error": str(e),
                        "success": False,
                    }

            # Overall discovery success
            search_success = all(
                result.get("success", False) for result in discovery_results.values()
            )
            metadata_success = all(
                result.get("success", False) for result in metadata_results.values()
            )
            capabilities_success = all(
                result.get("success", False) for result in capabilities_results.values()
            )

            overall_success = (
                search_success and metadata_success and capabilities_success
            )

            self.test_results["tool_discovery"] = {
                "status": "PASS" if overall_success else "FAIL",
                "message": f"Tool discovery {'successful' if overall_success else 'failed'}",
                "search_results": discovery_results,
                "metadata_results": metadata_results,
                "capabilities_results": capabilities_results,
                "overall_success": overall_success,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Tool discovery {'successful' if overall_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["tool_discovery"] = {
                "status": "FAIL",
                "message": f"Tool discovery test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Tool discovery test failed: {e}")

    async def test_tool_removal(self):
        """Test tool removal functionality."""
        logger.info("Testing tool removal...")

        try:
            removal_results = {}

            # Create a temporary tool for removal testing
            temp_tool = ContentGenerator()
            temp_tool.name = "temp_removal_test_tool"

            # Register temporary tool
            self.registry.register_tool(temp_tool)

            # Verify tool is registered
            before_removal = self.registry.get_tool("temp_removal_test_tool")
            before_success = before_removal is not None

            # Remove tool
            removal_success = self.registry.unregister_tool("temp_removal_test_tool")

            # Verify tool is removed
            after_removal = self.registry.get_tool("temp_removal_test_tool")
            after_success = after_removal is None

            # Test removing non-existent tool
            non_existent_removal = self.registry.unregister_tool("non_existent_tool")
            non_existent_success = not non_existent_removal  # Should return False

            # Test removing by class
            temp_tool_2 = ContentGenerator()
            temp_tool_2.name = "temp_removal_test_tool_2"
            self.registry.register_tool(temp_tool_2)

            class_removal_success = self.registry.unregister_tool_by_class(
                ContentGenerator
            )

            removal_results = {
                "before_removal": before_success,
                "removal_success": removal_success,
                "after_removal": after_success,
                "non_existent_success": non_existent_success,
                "class_removal_success": class_removal_success,
                "overall": before_success
                and removal_success
                and after_success
                and non_existent_success,
            }

            self.test_results["tool_removal"] = {
                "status": "PASS" if removal_results["overall"] else "FAIL",
                "message": f"Tool removal {'successful' if removal_results["overall"] else 'failed'}",
                "removal_results": removal_results,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Tool removal {'successful' if removal_results["overall"] else 'failed'}"
            )

        except Exception as e:
            self.test_results["tool_removal"] = {
                "status": "FAIL",
                "message": f"Tool removal test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Tool removal test failed: {e}")

    async def test_concurrent_registry_access(self):
        """Test concurrent access to tool registry."""
        logger.info("Testing concurrent registry access...")

        try:
            # Create concurrent tasks
            tasks = []

            # Concurrent registration tasks
            for i in range(5):
                task = self._concurrent_registration_task(f"concurrent_tool_{i}")
                tasks.append(task)

            # Concurrent retrieval tasks
            for i in range(5):
                task = self._concurrent_retrieval_task()
                tasks.append(task)

            # Concurrent search tasks
            for i in range(5):
                task = self._concurrent_search_task("content")
                tasks.append(task)

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze results
            successful_tasks = 0
            failed_tasks = 0
            task_results = {}

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_tasks += 1
                    task_results[f"task_{i}"] = {"success": False, "error": str(result)}
                else:
                    successful_tasks += 1
                    task_results[f"task_{i}"] = {"success": True, "result": result}

            concurrent_success = failed_tasks == 0  # All tasks should succeed

            # Clean up any tools created during concurrent test
            await self._cleanup_concurrent_test_tools()

            self.test_results["concurrent_registry_access"] = {
                "status": "PASS" if concurrent_success else "FAIL",
                "message": f"Concurrent registry access {'successful' if concurrent_success else 'failed'}",
                "total_tasks": len(tasks),
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "task_results": task_results,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Concurrent registry access {'successful' if concurrent_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["concurrent_registry_access"] = {
                "status": "FAIL",
                "message": f"Concurrent registry access test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Concurrent registry access test failed: {e}")

    async def _concurrent_registration_task(self, tool_name: str) -> Dict[str, Any]:
        """Concurrent registration task."""
        try:
            # Create temporary tool
            temp_tool = ContentGenerator()
            temp_tool.name = tool_name

            # Register tool
            self.registry.register_tool(temp_tool)

            # Verify registration
            retrieved_tool = self.registry.get_tool(tool_name)

            return {
                "tool_name": tool_name,
                "registered": retrieved_tool is not None,
                "tool_id": id(retrieved_tool) if retrieved_tool else None,
            }
        except Exception as e:
            return {"tool_name": tool_name, "error": str(e), "registered": False}

    async def _concurrent_retrieval_task(self) -> Dict[str, Any]:
        """Concurrent retrieval task."""
        try:
            # Get all tools
            all_tools = self.registry.get_all_tools()

            # Get a specific tool
            content_tool = self.registry.get_tool("ContentGenerator")

            return {
                "all_tools_count": len(all_tools),
                "content_tool_found": content_tool is not None,
                "content_tool_name": content_tool.name if content_tool else None,
            }
        except Exception as e:
            return {"error": str(e), "all_tools_count": 0, "content_tool_found": False}

    async def _concurrent_search_task(self, search_term: str) -> Dict[str, Any]:
        """Concurrent search task."""
        try:
            # Search for tools
            search_results = self.registry.search_tools(search_term)

            return {
                "search_term": search_term,
                "results_count": len(search_results),
                "result_names": [tool.name for tool in search_results],
            }
        except Exception as e:
            return {"search_term": search_term, "error": str(e), "results_count": 0}

    async def _cleanup_concurrent_test_tools(self):
        """Clean up tools created during concurrent test."""
        # Remove any tools created during concurrent test
        for i in range(5):
            tool_name = f"concurrent_tool_{i}"
            try:
                self.registry.unregister_tool(tool_name)
            except Exception:
                pass  # Ignore cleanup errors

    def print_test_results(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 50)
        logger.info("TOOL REGISTRY TEST RESULTS")
        logger.info("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = len(
            [r for r in self.test_results.values() if r["status"] == "PASS"]
        )
        failed_tests = total_tests - passed_tests

        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        logger.info("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            logger.info(f"{status_icon} {test_name}: {result['message']}")

        if failed_tests > 0:
            logger.info(
                f"\n⚠️  {failed_tests} tests failed. Please review the errors above."
            )
        else:
            logger.info("\n🎉 All tests passed! Tool registry is working correctly.")

        logger.info("=" * 50)


async def main():
    """Main function to run tests."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    tester = TestToolRegistry()
    results = await tester.run_all_tests()

    return results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())

    # Exit with appropriate code
    failed_count = len([r for r in results.values() if r["status"] == "FAIL"])
    exit(1 if failed_count > 0 else 0)
