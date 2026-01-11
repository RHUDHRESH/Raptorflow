"""
Test file to verify workflows execute correctly with LangGraph integration.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

# Import base classes
from agents.base import BaseAgent
from agents.specialists.analytics_agent import AnalyticsAgent
from agents.specialists.blackbox_strategist import BlackboxStrategist
from agents.specialists.campaign_planner import CampaignPlanner
from agents.specialists.content_creator import ContentCreator
from agents.specialists.icp_architect import ICPArchitect
from agents.specialists.market_research import MarketResearch
from agents.specialists.move_strategist import MoveStrategist

# Import agent classes
from agents.specialists.onboarding_orchestrator import OnboardingOrchestrator

# Import workflow classes
from agents.workflows.base_workflow import BaseWorkflow
from agents.workflows.content_workflow import ContentWorkflow
from agents.workflows.onboarding_workflow import OnboardingWorkflow
from agents.workflows.strategy_workflow import StrategyWorkflow

logger = logging.getLogger(__name__)


class TestLangGraphWorkflows:
    """Test suite for LangGraph workflow integration."""

    def __init__(self):
        self.test_results = {}
        self.workflows = {}
        self.agent_registry = {}
        self.test_workspaces = {
            "workspace_1": "test_workflow_alpha_123",
            "workspace_2": "test_workflow_beta_456",
            "workspace_3": "test_workflow_gamma_789",
        }

    async def run_all_tests(self):
        """Run all LangGraph workflow tests."""
        logger.info("Starting LangGraph workflow tests")

        # Initialize agent registry
        await self._initialize_agent_registry()

        # Initialize workflows
        await self._initialize_workflows()

        # Test workflow initialization
        await self.test_workflow_initialization()

        # Test workflow execution
        await self.test_workflow_execution()

        # Test state persistence
        await self.test_state_persistence()

        # Test concurrent execution
        await self.test_concurrent_execution()

        # Test error handling
        await self.test_error_handling()

        # Print results
        self.print_test_results()

        return self.test_results

    async def _initialize_agent_registry(self):
        """Initialize agent registry for testing."""
        logger.info("Initializing agent registry...")

        self.agent_registry = {
            "OnboardingOrchestrator": OnboardingOrchestrator(),
            "ContentCreator": ContentCreator(),
            "MoveStrategist": MoveStregist(),
            "MarketResearch": MarketResearch(),
            "BlackboxStrategist": BlackboxStrategist(),
            "AnalyticsAgent": AnalyticsAgent(),
            "CampaignPlanner": CampaignPlanner(),
            "ICPArchitect": ICPArchitect(),
        }

        logger.info(
            f"Initialized agent registry with {len(self.agent_registry)} agents"
        )

    async def _initialize_workflows(self):
        """Initialize all workflows."""
        logger.info("Initializing workflows...")

        workflows = {
            "onboarding": OnboardingWorkflow(),
            "content": ContentWorkflow(),
            "strategy": StrategyWorkflow(),
        }

        for workflow_name, workflow in workflows.items():
            try:
                success = workflow.initialize(self.agent_registry)
                if success:
                    self.workflows[workflow_name] = workflow
                    logger.info(f"✅ {workflow_name} workflow initialized successfully")
                else:
                    logger.error(f"❌ {workflow_name} workflow initialization failed")
            except Exception as e:
                logger.error(f"❌ {workflow_name} workflow initialization error: {e}")

        logger.info(f"Initialized {len(self.workflows)} workflows")

    async def test_workflow_initialization(self):
        """Test workflow initialization."""
        logger.info("Testing workflow initialization...")

        for workflow_name, workflow in self.workflows.items():
            try:
                # Check if workflow is initialized
                is_initialized = workflow.is_initialized

                # Check if workflow has configuration
                has_config = workflow.config is not None

                # Check if graph is built (if LangGraph available)
                has_graph = workflow.graph is not None

                success = is_initialized and has_config

                self.test_results[f"{workflow_name}_initialization"] = {
                    "status": "PASS" if success else "FAIL",
                    "message": f"{workflow_name} initialization {'successful' if success else 'failed'}",
                    "is_initialized": is_initialized,
                    "has_config": has_config,
                    "has_graph": has_graph,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(
                    f"✅ {workflow_name} initialization {'successful' if success else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{workflow_name}_initialization"] = {
                    "status": "FAIL",
                    "message": f"{workflow_name} initialization failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {workflow_name} initialization failed: {e}")

    async def test_workflow_execution(self):
        """Test workflow execution."""
        logger.info("Testing workflow execution...")

        for workflow_name, workflow in self.workflows.items():
            try:
                # Prepare test data
                test_data = self._prepare_test_data(workflow_name)

                # Execute workflow
                result_state = await workflow.execute(test_data)

                # Verify execution success
                execution_success = result.status.value == "completed"

                # Verify result data
                has_result_data = bool(result.shared_data)
                has_completion_data = "workflow_completion" in result.shared_data

                self.test_results[f"{workflow_name}_execution"] = {
                    "status": "PASS" if execution_success else "FAIL",
                    "message": f"{workflow_name} execution {'successful' if execution_success else 'failed'}",
                    "execution_success": execution_success,
                    "has_result_data": has_result_data,
                    "has_completion_data": has_completion_data,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(
                    f"✅ {workflow_name} execution {'successful' if execution_success else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{workflow_name}_execution"] = {
                    "status": "fail",
                    "message": f"{workflow_name} execution failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {workflow_name} execution failed: {e}")

    def _prepare_test_data(self, workflow_name: str) -> Dict[str, Any]:
        """Prepare test data for workflow execution."""
        base_data = {
            "user_id": f"test_user_{workflow_name}",
            "workspace_id": self.test_workspaces["workspace_1"],
            "session_id": f"test_session_{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        }

        if workflow_name == "onboarding":
            return {
                **base_data,
                "content_type": "onboarding",
                "user_message": "I want to start onboarding",
                "target_audience": "general",
                "business_objectives": ["growth", "efficiency", "brand_awareness"],
                "time_horizon": "medium_term",
                "risk_tolerance": "moderate",
            }

        elif workflow_name == "content":
            return {
                **base_data,
                "content_type": "blog",
                "content_topic": f"Test content for {workflow_name}",
                "target_audience": "marketing",
                "content_tone": "professional",
                "content_length": "medium",
                "distribution_channels": ["blog", "social", "email"],
                "optimization_level": "standard",
            }

        elif workflow_name == "strategy":
            return {
                **base_data,
                "strategy_type": "competitive_advantage",
                "business_objectives": ["growth", "innovation", "market_leadership"],
                "time_horizon": "long_term",
                "risk_tolerance": "moderate",
                "resource_constraints": {"budget": "medium", "team": "small"},
                "stakeholders": ["executive", "marketing", "sales"],
            }

        return base_data

    async def test_state_persistence(self):
        """Test workflow state persistence."""
        logger.info("Testing state persistence...")

        for workflow_name, workflow in self.workflows.items():
            try:
                # Execute workflow
                test_data = self._prepare_test_data(workflow_name)
                result_state = await workflow.execute(test_data)

                # Wait a moment for state to be saved
                await asyncio.sleep(0.1)

                # Create new workflow instance
                new_workflow = workflow.__class__()
                new_workflow.initialize(self.agent_registry)

                # Check if state persisted
                state_persisted = new_workflow.get_status().status.value == "completed"

                # Check if data persisted
                data_persisted = bool(new_workflow.get_shared_data())

                self.test_results[f"{workflow_name}_state_persistence"] = {
                    "status": "PASS" if state_persisted and data_persisted else "FAIL",
                    "message": f"{workflow_name} state persistence {'successful' if state_persisted else 'failed'}",
                    "state_persisted": state_persisted,
                    "data_persisted": data_persisted,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(
                    f"✅ {workflow_name} state persistence {'successful' if state_persisted and data_persisted else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{workflow_name}_state_persistence"] = {
                    "status": "FAIL",
                    "message": f"{workflow_name} state persistence failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {workflow_name} state persistence failed: {e}")

    async def test_concurrent_execution(self):
        """Test concurrent workflow execution."""
        logger.info("Testing concurrent workflow execution...")

        # Create multiple workflow instances
        workflows = []
        for workflow_name in self.workflows.keys():
            workflow = workflow.__class__()
            workflow.initialize(self.agent_registry)
            workflows.append(workflow)

        # Prepare test data for each workflow
        test_data_list = []
        for i, workflow_name in enumerate(self.workflows.keys()):
            test_data = self._prepare_test_data(workflow_name)
            test_data["concurrent_id"] = i
            test_data_list.append(test_data)

        # Execute workflows concurrently
        tasks = []
        for i, (workflow, test_data) in enumerate(zip(workflows, test_data_list)):
            task = workflow.execute(test_data)
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Analyze results
        successful_count = 0
        failed_count = 0
        concurrent_results = {}

        for i, result in enumerate(results):
            workflow_name = list(self.workflows.keys())[i]

            if isinstance(result, Exception):
                failed_count += 1
                concurrent_results[workflow_name] = {
                    "success": False,
                    "error": str(result),
                }
            else:
                workflow_state = result
                success = workflow_state.status.value == "completed"

                if success:
                    successful_count += 1
                else:
                    failed_count += 1

                concurrent_results[workflow_name] = {
                    "success": success,
                    "status": workflow_state.status.value,
                    "has_data": bool(workflow_state.shared_data),
                    "concurrent_id": test_data_list[i].get("concurrent_id"),
                }

        concurrent_success = failed_count == 0

        self.test_results["concurrent_execution"] = {
            "status": "PASS" if concurrent_success else "FAIL",
            "message": f"Concurrent execution {'successful' if concurrent_success else 'failed'}",
            "total_workflows": len(workflows),
            "successful_count": successful_count,
            "failed_count": failed_count,
            "concurrent_results": concurrent_results,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"✅ Concurrent execution {'successful' if concurrent_success else 'failed'}"
        )

    async def test_error_handling(self):
        """Test workflow error handling."""
        logger.info("Testing error handling...")

        for workflow_name, workflow in self.workflows.items():
            try:
                # Test with invalid data
                invalid_data = {
                    "user_id": "",  # Missing user_id
                    "workspace_id": "",  # Missing workspace_id
                    "content_type": "invalid_type",  # Invalid content type
                }

                # Should fail validation
                result = await workflow.execute(invalid_data)

                # Should fail
                error_handled = not result.success or result.status.value == "failed"

                self.test_results[f"{workflow_name}_error_handling"] = {
                    "status": "PASS" if error_handled else "FAIL",
                    "message": f"{workflow_name} error handling {'successful' if error_handled else 'failed'}",
                    "error_handled": error_handled,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(
                    f"✅ {workflow_name} error handling {'successful' if error_handled else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{workflow_name}_error_handling"] = {
                    "status": "FAIL",
                    "message": f"{workflow_name} error handling failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {workflow_name} error handling failed: {e}")

    def print_test_results(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 50)
        logger.info("LANGGRAPH WORKFLOW TEST RESULTS")
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
                "\n🎉 All tests passed! LangGraph workflows are working correctly."
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
    tester = TestLangGraphWorkflows()
    results = await tester.run_all_tests()

    return results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())

    # Exit with appropriate code
    failed_count = len([r for r in results.values() if r["status"] == "FAIL"])
    exit(1 if failed_count > 0 else 0)
