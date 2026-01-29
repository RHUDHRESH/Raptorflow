"""
Test file to verify workflow state persists correctly.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Import base classes
from .agents.base import BaseAgent
from .agents.specialists.analytics_agent import AnalyticsAgent
from .agents.specialists.blackbox_strategist import BlackboxStrategist
from .agents.specialists.campaign_planner import CampaignPlanner
from .agents.specialists.content_creator import ContentCreator
from .agents.specialists.icp_architect import ICPArchitect
from .agents.specialists.market_research import MarketResearch
from .agents.specialists.move_strategist import MoveStrategist

# Import agent classes
from .agents.specialists.onboarding_orchestrator import OnboardingOrchestrator

# Import workflow classes
from .agents.workflows.base_workflow import (
    BaseWorkflow,
    WorkflowState,
    WorkflowStatus,
)
from .agents.workflows.content_workflow import ContentWorkflow
from .agents.workflows.onboarding_workflow import OnboardingWorkflow
from .agents.workflows.strategy_workflow import StrategyWorkflow

logger = logging.getLogger(__name__)


class TestWorkflowStatePersistence:
    """Test suite for workflow state persistence."""

    def __init__(self):
        self.test_results = {}
        self.workflows = {}
        self.agent_registry = {}
        self.test_workspaces = {
            "workspace_1": "test_state_alpha_123",
            "workspace_2": "test_state_beta_456",
            "workspace_3": "test_state_gamma_789",
        }
        self.memory_store = {}  # Simulated memory store

    async def run_all_tests(self):
        """Run all state persistence tests."""
        logger.info("Starting workflow state persistence tests")

        # Initialize agent registry
        await self._initialize_agent_registry()

        # Initialize workflows
        await self._initialize_workflows()

        # Test state saving
        await self._test_state_saving()

        # Test state loading
        await self._test_state_loading()

        # Test state recovery
        await self._test_state_recovery()

        # Test state consistency
        await self._test_state_consistency()

        # Test concurrent state access
        await self._test_concurrent_state_access()

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
                    logger.info(
                        f"Γ£à {workflow_name} workflow initialized successfully"
                    )
                else:
                    logger.error(f"Γ¥î {workflow_name} workflow initialization failed")
            except Exception as e:
                logger.error(f"Γ¥î {workflow_name} workflow initialization error: {e}")

        logger.info(f"Initialized {len(self.workflows)} workflows")

    async def _test_state_saving(self):
        """Test state saving functionality."""
        logger.info("Testing state saving...")

        for workflow_name, workflow in self.workflows.items():
            try:
                # Execute workflow to completion
                test_data = self._prepare_test_data(workflow_name)
                result_state = await workflow.execute(test_data)

                # Save state
                workflow.save_state()

                # Verify state is saved
                state_saved = workflow.get_status().value != WorkflowStatus.PENDING
                state_data = workflow.get_shared_data()

                # Verify state data integrity
                data_integrity = self._verify_state_integrity(workflow_state)

                self.test_results[f"{workflow_name}_state_saving"] = {
                    "status": "PASS" if state_saved and data_integrity else "FAIL",
                    "message": f"{workflow_name} state saving {'successful' if state_saved and data_integrity else 'failed'}",
                    "state_saved": state_saved,
                    "data_integrity": data_integrity,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(
                    f"Γ£à {workflow_name} state saving {'successful' if state_saved and data_integrity else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{workflow_name}_state_saving"] = {
                    "status": "FAIL",
                    "message": f"{workflow_name} state saving failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"Γ¥î {workflow_name} state saving failed: {e}")

    def _verify_state_integrity(self, workflow_state: WorkflowState) -> bool:
        """Verify state data integrity."""
        try:
            # Check required fields
            required_fields = [
                "workflow_id",
                "status",
                "start_time",
                "progress",
                "current_node",
                "shared_data",
                "execution_history",
            ]

            for field in required_fields:
                if not hasattr(workflow_state, field) or workflow_state[field] is None:
                    return False

            # Check data types
            if not isinstance(workflow_state.status, WorkflowStatus):
                return False

            # Check timestamp format
            if workflow_state.start_time:
                try:
                    datetime.fromisoformat(workflow_state.start_time)
                except ValueError:
                    return False

            # Check shared data is dict
            if not isinstance(workflow_state.shared_data, dict):
                return False

            return True

        except Exception as e:
            logger.error(f"State integrity check failed: {e}")
            return False

    async def _test_state_loading(self):
        """Test state loading functionality."""
        logger.info("Testing state loading...")

        for workflow_name, workflow in self.workflows.items():
            try:
                # Create new workflow instance
                new_workflow = workflow.__class__()
                new_workflow.initialize(self.agent_registry)

                # Check if state persisted from previous save
                state_loaded = new_workflow.get_status().value != WorkflowStatus.PENDING
                state_data = new_workflow.get_shared_data()

                # Verify data integrity
                data_integrity = self._verify_state_integrity(new_workflow.state)

                # Check if data matches saved state
                if workflow_state and state_data:
                    original_state = workflow_state
                    saved_state = new_workflow.state

                    # Compare key fields
                    fields_match = (
                        original_state.workflow_id == saved_state.workflow_id
                        and original_state.status == saved_state.status
                        and original_state.progress == saved_state.progress
                        and original_state.shared_data == saved_state.shared_data
                    )

                    self.test_results[f"{workflow_name}_state_loading"] = {
                        "status": "PASS" if fields_match else "FAIL",
                        "message": f"{workflow_name} state loading {'successful' if fields_match else 'failed'}",
                        "fields_match": fields_match,
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    self.test_results[f"{workflow_name}_state_loading"] = {
                        "status": "FAIL",
                        "message": f"{workflow_name} state loading failed - no saved state found",
                        "timestamp": datetime.now().isoformat(),
                    }

                logger.info(
                    f"Γ£à {workflow_name} state loading {'successful' if fields_match else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{workflow_name}_state_loading"] = {
                    "status": "FAIL",
                    "message": f"{workflow_name} state loading failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"Γ¥î {workflow_name} state loading failed: {e}")

    async def _test_state_recovery(self):
        """Test state recovery after interruption."""
        logger.info("Testing state recovery...")

        for workflow_name, workflow in self.workflows.items():
            try:
                # Simulate workflow interruption
                workflow.cancel()

                # Create new workflow instance
                new_workflow = workflow.__class__()
                new_workflow.initialize(self.agent_registry)

                # Check if state can be recovered
                state_recovered = (
                    new_workflow.get_status().value != WorkflowStatus.PENDING
                )
                state_data = new_workflow.get_shared_data()

                # Check if data integrity is maintained
                data_integrity = self._verify_state_integrity(new_workflow.state)

                self.test_results[f"{workflow_name}_state_recovery"] = {
                    "status": "PASS" if state_recovered and data_integrity else "FAIL",
                    "message": f"{workflow_name} state recovery {'successful' if state_recovered and data_integrity else 'failed'}",
                    "state_recovered": state_recovered,
                    "data_integrity": data_integrity,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(
                    f"Γ£à {workflow_name} state recovery {'successful' if state_recovered and data_integrity else 'failed'}"
                )

            except Exception as e:
                self.test_results[f"{workflow_name}_state_recovery"] = {
                    "status": "FAIL",
                    "message": f"{workflow_name} state recovery failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"Γ¥î {workflow_name} state recovery failed: {e}")

    async def _test_state_consistency(self):
        """Test state consistency across workflow instances."""
        logger.info("Testing state consistency...")

        try:
            # Create multiple workflow instances
            workflow_instances = []

            for workflow_name in self.workflows.keys():
                workflow = workflow.__class__()
                workflow.initialize(self.agent_registry)
                workflow_instances.append(workflow)

            # Execute all workflows to completion
            tasks = []
            for workflow in workflow_instances:
                test_data = self._prepare_test_data(workflow.name)
                task = workflow.execute(test_data)
                tasks.append(task)

            # Wait for all to complete
            await asyncio.gather(*tasks)

            # Compare states
            states = [task.get() for task in tasks]

            # Check if all workflows completed successfully
            all_completed = all(
                state.status.value == WorkflowStatus.COMPLETED for state in states
            )

            # Check state consistency across instances
            state_consistency = self._compare_workflow_states(states)

            self.test_results["state_consistency"] = {
                "status": "PASS" if all_completed and state_consistency else "FAIL",
                "message": f"State consistency {'verified' if state_consistency else 'failed'}",
                "all_completed": all_completed,
                "state_consistency": state_consistency,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"Γ£à State consistency {'verified' if state_consistency else 'failed'}"
            )

        except Exception as e:
            self.test_results["state_consistency"] = {
                "status": "FAIL",
                "message": f"State consistency test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"Γ¥î State consistency test failed: {e}")

    def _compare_workflow_states(self, states: List[WorkflowState]) -> bool:
        """Compare workflow states for consistency."""
        if not states:
            return False

        # Get the first state as reference
        reference_state = states[0]

        # Compare all states
        for state in states[1:]:
            if not self._compare_states(reference_state, state):
                return False

        return True

    def _compare_states(self, state1: WorkflowState, state2: WorkflowState) -> bool:
        """Compare two workflow states."""
        try:
            # Compare basic fields
            if state1.workflow_id != state2.workflow_id:
                return False

            if state1.status != state2.status:
                return False

            if state1.progress != state2.progress:
                return False

            if state1.current_node != state2.current_node:
                return False

            # Compare shared data
            if state1.shared_data != state2.shared_data:
                return False

            # Compare execution history
            if len(state1.execution_history) != len(state2.execution_history):
                return False

            # Compare timestamps
            if state1.start_time != state2.start_time:
                return False

            return True

        except Exception as e:
            logger.error(f"State comparison failed: {e}")
            return False

    def _prepare_test_data(self, workflow_name: str) -> Dict[str, Any]:
        """Prepare test data for state persistence testing."""
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

    def print_test_results(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 50)
        logger.info("WORKFLOW STATE PERSISTENCE TEST RESULTS")
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
            status_icon = "Γ£à" if result["status"] == "PASS" else "Γ¥î"
            logger.info(f"{status_icon} {test_name}: {result['message']}")

        if failed_tests > 0:
            logger.info(
                f"\nΓÜá∩╕Å  {failed_tests} tests failed. Please review the errors above."
            )
        else:
            logger.info(
                "\n≡ƒÄë All tests passed! Workflow state persistence is working correctly."
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
    tester = TestWorkflowStatePersistence()
    results = await tester.run_all_tests()

    return results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())

    # Exit with appropriate code
    failed_count = len([r for r in results.values() if r["status"] == "FAIL"])
    exit(1 if failed_count > 0 else 0)
