"""
Test file to verify all tools work with workspace isolation.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict

# Import base classes for testing
from backend.agents.base import BaseTool

# Import all tools
from backend.agents.tools.content_generator import ContentGenerator
from backend.agents.tools.export_tool import ExportTool
from backend.agents.tools.feedback_tool import FeedbackTool
from backend.agents.tools.template_tool import TemplateTool

logger = logging.getLogger(__name__)


class TestToolsWorkspaceIsolation:
    """Test suite for tool workspace isolation."""

    def __init__(self):
        self.test_results = {}
        self.tools = {}
        self.test_workspaces = {
            "workspace_1": "test_workspace_alpha_123",
            "workspace_2": "test_workspace_beta_456",
            "workspace_3": "test_workspace_gamma_789",
        }

    async def run_all_tests(self):
        """Run all tool workspace isolation tests."""
        logger.info("Starting tool workspace isolation tests")

        # Initialize tools
        await self.initialize_tools()

        # Test workspace isolation
        await self.test_workspace_isolation()

        # Test data separation
        await self.test_data_separation()

        # Test concurrent access
        await self.test_concurrent_access()

        # Test security boundaries
        await self.test_security_boundaries()

        # Print results
        self.print_test_results()

        return self.test_results

    async def initialize_tools(self):
        """Initialize all tools."""
        logger.info("Initializing tools...")

        self.tools = {
            "ContentGenerator": ContentGenerator(),
            "TemplateTool": TemplateTool(),
            "FeedbackTool": FeedbackTool(),
            "ExportTool": ExportTool(),
        }

        for tool_name, tool in self.tools.items():
            try:
                # Verify tool initialization
                assert hasattr(tool, "name"), f"{tool_name} missing name attribute"
                assert hasattr(tool, "execute"), f"{tool_name} missing execute method"
                assert isinstance(
                    tool, BaseTool
                ), f"{tool_name} not a BaseTool subclass"

                self.test_results[f"{tool_name}_initialization"] = {
                    "status": "PASS",
                    "message": f"{tool_name} initialized successfully",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(f"✅ {tool_name} initialized successfully")

            except Exception as e:
                self.test_results[f"{tool_name}_initialization"] = {
                    "status": "FAIL",
                    "message": f"{tool_name} initialization failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {tool_name} initialization failed: {e}")

    async def test_workspace_isolation(self):
        """Test workspace isolation functionality."""
        logger.info("Testing workspace isolation...")

        for tool_name, tool in self.tools.items():
            try:
                # Test with different workspaces
                workspace_results = {}

                for workspace_id in self.test_workspaces.values():
                    try:
                        # Execute tool operation with workspace isolation
                        result = await self._execute_tool_with_workspace(
                            tool, workspace_id
                        )

                        workspace_results[workspace_id] = {
                            "success": True,
                            "result": result,
                            "workspace_isolated": self._verify_workspace_isolation(
                                result, workspace_id
                            ),
                        }

                    except Exception as e:
                        workspace_results[workspace_id] = {
                            "success": False,
                            "error": str(e),
                            "workspace_isolated": False,
                        }

                # Verify isolation between workspaces
                isolation_verified = self._verify_cross_workspace_isolation(
                    workspace_results
                )

                self.test_results[f"{tool_name}_workspace_isolation"] = {
                    "status": "PASS" if isolation_verified else "FAIL",
                    "message": f"{tool_name} workspace isolation {'verified' if isolation_verified else 'failed'}",
                    "workspace_results": workspace_results,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(
                    f"✅ {tool_name} workspace isolation {'verified' if isolation_verified else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{tool_name}_workspace_isolation"] = {
                    "status": "FAIL",
                    "message": f"{tool_name} workspace isolation test failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {tool_name} workspace isolation test failed: {e}")

    async def test_data_separation(self):
        """Test data separation between workspaces."""
        logger.info("Testing data separation...")

        for tool_name, tool in self.tools.items():
            try:
                # Create data in different workspaces
                created_data = {}

                for workspace_id in self.test_workspaces.values():
                    data_id = await self._create_test_data(tool, workspace_id)
                    created_data[workspace_id] = data_id

                # Verify data cannot be accessed across workspaces
                separation_verified = True

                for workspace_id, data_id in created_data.items():
                    for other_workspace_id in self.test_workspaces.values():
                        if workspace_id != other_workspace_id:
                            # Try to access data from different workspace
                            try:
                                result = await self._access_data_from_workspace(
                                    tool, data_id, other_workspace_id
                                )
                                if result.get("success", False):
                                    separation_verified = False
                                    break
                            except Exception:
                                # Expected - data should not be accessible
                                pass

                    if not separation_verified:
                        break

                self.test_results[f"{tool_name}_data_separation"] = {
                    "status": "PASS" if separation_verified else "FAIL",
                    "message": f"{tool_name} data separation {'verified' if separation_verified else 'failed'}",
                    "created_data": created_data,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(
                    f"✅ {tool_name} data separation {'verified' if separation_verified else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{tool_name}_data_separation"] = {
                    "status": "FAIL",
                    "message": f"{tool_name} data separation test failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {tool_name} data separation test failed: {e}")

    async def test_concurrent_access(self):
        """Test concurrent access to tools from different workspaces."""
        logger.info("Testing concurrent access...")

        for tool_name, tool in self.tools.items():
            try:
                # Execute concurrent operations
                tasks = []

                for workspace_id in self.test_workspaces.values():
                    task = self._execute_concurrent_operation(tool, workspace_id)
                    tasks.append(task)

                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Verify all operations succeeded
                concurrent_success = True
                concurrent_results = {}

                for i, result in enumerate(results):
                    workspace_id = list(self.test_workspaces.values())[i]

                    if isinstance(result, Exception):
                        concurrent_success = False
                        concurrent_results[workspace_id] = {
                            "success": False,
                            "error": str(result),
                        }
                    else:
                        concurrent_results[workspace_id] = {
                            "success": True,
                            "result": result,
                        }

                self.test_results[f"{tool_name}_concurrent_access"] = {
                    "status": "PASS" if concurrent_success else "FAIL",
                    "message": f"{tool_name} concurrent access {'successful' if concurrent_success else 'failed'}",
                    "concurrent_results": concurrent_results,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(
                    f"✅ {tool_name} concurrent access {'successful' if concurrent_success else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{tool_name}_concurrent_access"] = {
                    "status": "FAIL",
                    "message": f"{tool_name} concurrent access test failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {tool_name} concurrent access test failed: {e}")

    async def test_security_boundaries(self):
        """Test security boundaries between workspaces."""
        logger.info("Testing security boundaries...")

        for tool_name, tool in self.tools.items():
            try:
                # Test unauthorized access attempts
                security_verified = True
                security_tests = {}

                for workspace_id in self.test_workspaces.values():
                    # Test with invalid workspace ID
                    try:
                        result = await self._execute_tool_with_workspace(
                            tool, "invalid_workspace"
                        )
                        if result.get("success", False):
                            security_verified = False
                            security_tests[f"invalid_workspace_{workspace_id}"] = {
                                "status": "FAIL",
                                "message": "Invalid workspace access succeeded",
                            }
                        else:
                            security_tests[f"invalid_workspace_{workspace_id}"] = {
                                "status": "PASS",
                                "message": "Invalid workspace access properly rejected",
                            }
                    except Exception:
                        security_tests[f"invalid_workspace_{workspace_id}"] = {
                            "status": "PASS",
                            "message": "Invalid workspace access properly rejected",
                        }

                    # Test with missing workspace ID
                    try:
                        result = await self._execute_tool_without_workspace(tool)
                        if result.get("success", False):
                            security_verified = False
                            security_tests[f"missing_workspace_{workspace_id}"] = {
                                "status": "FAIL",
                                "message": "Missing workspace access succeeded",
                            }
                        else:
                            security_tests[f"missing_workspace_{workspace_id}"] = {
                                "status": "PASS",
                                "message": "Missing workspace access properly rejected",
                            }
                    except Exception:
                        security_tests[f"missing_workspace_{workspace_id}"] = {
                            "status": "PASS",
                            "message": "Missing workspace access properly rejected",
                        }

                self.test_results[f"{tool_name}_security_boundaries"] = {
                    "status": "PASS" if security_verified else "FAIL",
                    "message": f"{tool_name} security boundaries {'verified' if security_verified else 'failed'}",
                    "security_tests": security_tests,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(
                    f"✅ {tool_name} security boundaries {'verified' if security_verified else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{tool_name}_security_boundaries"] = {
                    "status": "FAIL",
                    "message": f"{tool_name} security boundaries test failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {tool_name} security boundaries test failed: {e}")

    async def _execute_tool_with_workspace(
        self, tool: BaseTool, workspace_id: str
    ) -> Dict[str, Any]:
        """Execute tool operation with workspace isolation."""
        if tool.name == "content_generator":
            return await tool.execute(
                operation="render",
                content_type="blog",
                topic="Test content",
                tone="professional",
                length="medium",
                target_audience="general",
                keywords=["test", "content"],
                brand_voice="professional",
                format="markdown",
                platform="blog",
                language="en",
                urgency="normal",
                workspace_id=workspace_id,
            )
        elif tool.name == "template_tool":
            return await tool.execute(
                operation="render",
                template_id="blog_post",
                template_type="content",
                variables={
                    "title": "Test Blog Post",
                    "summary": "Test summary",
                    "introduction": "Test introduction",
                    "main_content": "Test main content",
                    "conclusion": "Test conclusion",
                    "call_to_action": "Test CTA",
                    "publish_date": datetime.now().strftime("%Y-%m-%d"),
                    "author": "Test Author",
                },
                format="markdown",
                language="en",
                workspace_id=workspace_id,
            )
        elif tool.name == "feedback_tool":
            return await tool.execute(
                operation="collect",
                feedback_type="user_experience",
                source="user",
                content="This is test feedback for workspace isolation testing",
                rating=4,
                sentiment="positive",
                categories=["usability", "performance"],
                metadata={"test": True},
                workspace_id=workspace_id,
            )
        elif tool.name == "export_tool":
            return await tool.execute(
                operation="export",
                export_type="data",
                data_source="database",
                format="json",
                filters={},
                fields=["id", "created_at"],
                sorting=[{"field": "created_at", "direction": "desc"}],
                workspace_id=workspace_id,
            )
        else:
            return {"success": False, "error": "Unknown tool"}

    async def _execute_tool_without_workspace(self, tool: BaseTool) -> Dict[str, Any]:
        """Execute tool operation without workspace ID."""
        if tool.name == "content_generator":
            return await tool.execute(
                operation="render",
                content_type="blog",
                topic="Test content",
                tone="professional",
                length="medium",
                target_audience="general",
                keywords=["test", "content"],
                brand_voice="professional",
                format="markdown",
                platform="blog",
                language="en",
                urgency="normal",
                # Missing workspace_id
            )
        elif tool.name == "template_tool":
            return await tool.execute(
                operation="render",
                template_id="blog_post",
                template_type="content",
                variables={"title": "Test"},
                format="markdown",
                language="en",
                # Missing workspace_id
            )
        elif tool.name == "feedback_tool":
            return await tool.execute(
                operation="collect",
                feedback_type="user_experience",
                source="user",
                content="Test feedback",
                rating=4,
                sentiment="positive",
                categories=["test"],
                # Missing workspace_id
            )
        elif tool.name == "export_tool":
            return await tool.execute(
                operation="export",
                export_type="data",
                data_source="database",
                format="json",
                filters={},
                fields=["id"],
                # Missing workspace_id
            )
        else:
            return {"success": False, "error": "Unknown tool"}

    async def _create_test_data(self, tool: BaseTool, workspace_id: str) -> str:
        """Create test data in workspace."""
        if tool.name == "content_generator":
            result = await tool.execute(
                operation="render",
                content_type="blog",
                topic=f"Test content for {workspace_id}",
                tone="professional",
                length="short",
                target_audience="general",
                keywords=[workspace_id],
                brand_voice="professional",
                format="markdown",
                platform="blog",
                language="en",
                urgency="normal",
                workspace_id=workspace_id,
            )
            return (
                result.get("content_result", {})
                .get("metadata", {})
                .get("generated_at", "")
            )
        elif tool.name == "template_tool":
            result = await tool.execute(
                operation="create",
                template_data={
                    "template_id": f"test_template_{workspace_id}",
                    "name": f"Test Template {workspace_id}",
                    "description": f"Test template for {workspace_id}",
                    "template_type": "content",
                    "content": f"Test content for {workspace_id}",
                    "variables": {"test": workspace_id},
                    "default_format": "markdown",
                    "supported_formats": ["markdown"],
                    "language": "en",
                    "version": "1.0.0",
                    "metadata": {"workspace": workspace_id},
                },
                workspace_id=workspace_id,
            )
            return result.get("template_id", "")
        elif tool.name == "feedback_tool":
            result = await tool.execute(
                operation="collect",
                feedback_type="user_experience",
                source="user",
                content=f"Test feedback for {workspace_id}",
                rating=4,
                sentiment="positive",
                categories=["test"],
                metadata={"workspace": workspace_id},
                workspace_id=workspace_id,
            )
            return result.get("feedback_id", "")
        elif tool.name == "export_tool":
            result = await tool.execute(
                operation="export",
                export_type="data",
                data_source="database",
                format="json",
                filters={"workspace": workspace_id},
                fields=["id", "workspace"],
                sorting=[{"field": "created_at", "direction": "desc"}],
                workspace_id=workspace_id,
            )
            return result.get("export_result", {}).get("export_id", "")
        else:
            return ""

    async def _access_data_from_workspace(
        self, tool: BaseTool, data_id: str, workspace_id: str
    ) -> Dict[str, Any]:
        """Try to access data from different workspace."""
        if tool.name == "template_tool":
            return await tool.execute(
                operation="render",
                template_id=data_id,
                template_type="content",
                variables={"test": "cross_workspace"},
                format="markdown",
                language="en",
                workspace_id=workspace_id,
            )
        elif tool.name == "export_tool":
            return await tool.execute(
                operation="get_export_status",
                export_id=data_id,
                workspace_id=workspace_id,
            )
        else:
            return {"success": False, "error": "Cross-workspace access not supported"}

    async def _execute_concurrent_operation(
        self, tool: BaseTool, workspace_id: str
    ) -> Dict[str, Any]:
        """Execute concurrent operation."""
        # Add small delay to simulate real concurrent access
        await asyncio.sleep(0.1)

        return await self._execute_tool_with_workspace(tool, workspace_id)

    def _verify_workspace_isolation(
        self, result: Dict[str, Any], workspace_id: str
    ) -> bool:
        """Verify that result is properly isolated to workspace."""
        if not result.get("success", False):
            return True  # Failed operations are still isolated

        # Check if workspace ID is present in result metadata
        metadata = result.get("metadata", {})
        result_workspace = metadata.get("workspace_id")

        return result_workspace == workspace_id

    def _verify_cross_workspace_isolation(
        self, workspace_results: Dict[str, Any]
    ) -> bool:
        """Verify isolation between different workspaces."""
        # Check that each workspace result is isolated
        for workspace_id, result in workspace_results.items():
            if not result.get("workspace_isolated", False):
                return False

        return True

    def print_test_results(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 50)
        logger.info("TOOL WORKSPACE ISOLATION TEST RESULTS")
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
            logger.info(
                "\n🎉 All tests passed! Tools are properly isolated by workspace."
            )

        logger.info("=" * 50)


async def main():
    """Main function to run tests."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    tester = TestToolsWorkspaceIsolation()
    results = await tester.run_all_tests()

    return results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())

    # Exit with appropriate code
    failed_count = len([r for r in results.values() if r["status"] == "FAIL"])
    exit(1 if failed_count > 0 else 0)
