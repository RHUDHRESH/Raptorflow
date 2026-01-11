"""
Test file to verify all specialist agents can be instantiated.
"""

import asyncio
import logging
from datetime import datetime

# Import base classes for testing
from agents.base import BaseAgent
from agents.specialists.analytics_agent import AnalyticsAgent
from agents.specialists.blackbox_strategist import BlackboxStrategist

# Import all specialist agents
from agents.specialists.content_creator import ContentCreator
from agents.specialists.market_research import MarketResearch
from agents.specialists.move_strategist import MoveStrategist
from agents.state import AgentState

logger = logging.getLogger(__name__)


class TestSpecialistAgents:
    """Test suite for specialist agents."""

    def __init__(self):
        self.test_results = {}
        self.agents = {}

    async def run_all_tests(self):
        """Run all specialist agent tests."""
        logger.info("Starting specialist agent instantiation tests")

        # Test agent instantiation
        await self.test_agent_instantiation()

        # Test agent properties
        await self.test_agent_properties()

        # Test agent methods
        await self.test_agent_methods()

        # Print results
        self.print_test_results()

        return self.test_results

    async def test_agent_instantiation(self):
        """Test that all specialist agents can be instantiated."""
        logger.info("Testing agent instantiation...")

        agent_classes = {
            "ContentCreator": ContentCreator,
            "MoveStrategist": MoveStrategist,
            "MarketResearch": MarketResearch,
            "AnalyticsAgent": AnalyticsAgent,
            "BlackboxStrategist": BlackboxStrategist,
        }

        for agent_name, agent_class in agent_classes.items():
            try:
                agent = agent_class()
                self.agents[agent_name] = agent

                # Verify it's a BaseAgent subclass
                assert isinstance(
                    agent, BaseAgent
                ), f"{agent_name} is not a BaseAgent subclass"

                # Verify required attributes
                assert hasattr(agent, "name"), f"{agent_name} missing name attribute"
                assert hasattr(
                    agent, "description"
                ), f"{agent_name} missing description attribute"
                assert hasattr(
                    agent, "model_tier"
                ), f"{agent_name} missing model_tier attribute"
                assert hasattr(agent, "tools"), f"{agent_name} missing tools attribute"

                self.test_results[f"{agent_name}_instantiation"] = {
                    "status": "PASS",
                    "message": f"{agent_name} instantiated successfully",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(f"✅ {agent_name} instantiated successfully")

            except Exception as e:
                self.test_results[f"{agent_name}_instantiation"] = {
                    "status": "FAIL",
                    "message": f"{agent_name} instantiation failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {agent_name} instantiation failed: {e}")

    async def test_agent_properties(self):
        """Test agent properties and configurations."""
        logger.info("Testing agent properties...")

        for agent_name, agent in self.agents.items():
            try:
                # Test system prompt
                system_prompt = agent.get_system_prompt()
                assert isinstance(
                    system_prompt, str
                ), f"{agent_name} system prompt not a string"
                assert len(system_prompt) > 100, f"{agent_name} system prompt too short"

                # Test agent metadata
                assert agent.name, f"{agent_name} has empty name"
                assert agent.description, f"{agent_name} has empty description"
                assert agent.model_tier, f"{agent_name} has no model tier"
                assert isinstance(agent.tools, list), f"{agent_name} tools not a list"

                self.test_results[f"{agent_name}_properties"] = {
                    "status": "PASS",
                    "message": f"{agent_name} properties valid",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info(f"✅ {agent_name} properties valid")

            except Exception as e:
                self.test_results[f"{agent_name}_properties"] = {
                    "status": "FAIL",
                    "message": f"{agent_name} properties test failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ {agent_name} properties test failed: {e}")

    async def test_agent_methods(self):
        """Test agent-specific methods."""
        logger.info("Testing agent methods...")

        # Test ContentCreator methods
        if "ContentCreator" in self.agents:
            try:
                agent = self.agents["ContentCreator"]
                templates = agent.get_content_templates()
                assert isinstance(
                    templates, dict
                ), "ContentCreator templates not a dict"
                assert len(templates) > 0, "ContentCreator has no templates"

                guidelines = agent.get_platform_guidelines()
                assert isinstance(
                    guidelines, dict
                ), "ContentCreator guidelines not a dict"

                factors = agent.get_optimization_factors()
                assert isinstance(factors, dict), "ContentCreator factors not a dict"

                self.test_results["ContentCreator_methods"] = {
                    "status": "PASS",
                    "message": "ContentCreator methods working",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info("✅ ContentCreator methods working")

            except Exception as e:
                self.test_results["ContentCreator_methods"] = {
                    "status": "FAIL",
                    "message": f"ContentCreator methods failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ ContentCreator methods failed: {e}")

        # Test MoveStrategist methods
        if "MoveStrategist" in self.agents:
            try:
                agent = self.agents["MoveStrategist"]
                templates = agent.get_move_templates()
                assert isinstance(
                    templates, dict
                ), "MoveStrategist templates not a dict"

                objectives = agent.get_objective_templates()
                assert isinstance(
                    objectives, dict
                ), "MoveStrategist objectives not a dict"

                risk_matrix = agent.get_risk_matrix()
                assert isinstance(
                    risk_matrix, dict
                ), "MoveStrategist risk matrix not a dict"

                self.test_results["MoveStrategist_methods"] = {
                    "status": "PASS",
                    "message": "MoveStrategist methods working",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info("✅ MoveStrategist methods working")

            except Exception as e:
                self.test_results["MoveStrategist_methods"] = {
                    "status": "FAIL",
                    "message": f"MoveStrategist methods failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ MoveStrategist methods failed: {e}")

        # Test MarketResearch methods
        if "MarketResearch" in self.agents:
            try:
                agent = self.agents["MarketResearch"]
                templates = agent.get_research_templates()
                assert isinstance(
                    templates, dict
                ), "MarketResearch templates not a dict"

                reliability = agent.get_source_reliability()
                assert isinstance(
                    reliability, dict
                ), "MarketResearch reliability not a dict"

                geo_modifiers = agent.get_geographic_modifiers()
                assert isinstance(
                    geo_modifiers, dict
                ), "MarketResearch geo modifiers not a dict"

                self.test_results["MarketResearch_methods"] = {
                    "status": "PASS",
                    "message": "MarketResearch methods working",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info("✅ MarketResearch methods working")

            except Exception as e:
                self.test_results["MarketResearch_methods"] = {
                    "status": "FAIL",
                    "message": f"MarketResearch methods failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ MarketResearch methods failed: {e}")

        # Test AnalyticsAgent methods
        if "AnalyticsAgent" in self.agents:
            try:
                agent = self.agents["AnalyticsAgent"]
                templates = agent.get_analysis_templates()
                assert isinstance(
                    templates, dict
                ), "AnalyticsAgent templates not a dict"

                source_configs = agent.get_data_source_configs()
                assert isinstance(
                    source_configs, dict
                ), "AnalyticsAgent source configs not a dict"

                benchmarks = agent.get_metric_benchmarks()
                assert isinstance(
                    benchmarks, dict
                ), "AnalyticsAgent benchmarks not a dict"

                self.test_results["AnalyticsAgent_methods"] = {
                    "status": "PASS",
                    "message": "AnalyticsAgent methods working",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info("✅ AnalyticsAgent methods working")

            except Exception as e:
                self.test_results["AnalyticsAgent_methods"] = {
                    "status": "FAIL",
                    "message": f"AnalyticsAgent methods failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ AnalyticsAgent methods failed: {e}")

        # Test BlackboxStrategist methods
        if "BlackboxStrategist" in self.agents:
            try:
                agent = self.agents["BlackboxStrategist"]
                templates = agent.get_challenge_templates()
                assert isinstance(
                    templates, dict
                ), "BlackboxStrategist templates not a dict"

                frameworks = agent.get_strategic_frameworks()
                assert isinstance(
                    frameworks, dict
                ), "BlackboxStrategist frameworks not a dict"

                models = agent.get_thinking_models()
                assert isinstance(models, list), "BlackboxStrategist models not a list"

                self.test_results["BlackboxStrategist_methods"] = {
                    "status": "PASS",
                    "message": "BlackboxStrategist methods working",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.info("✅ BlackboxStrategist methods working")

            except Exception as e:
                self.test_results["BlackboxStrategist_methods"] = {
                    "status": "FAIL",
                    "message": f"BlackboxStrategist methods failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }

                logger.error(f"❌ BlackboxStrategist methods failed: {e}")

    def print_test_results(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 50)
        logger.info("SPECIALIST AGENT TEST RESULTS")
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
            logger.info("\n🎉 All tests passed! Specialist agents are ready for use.")

        logger.info("=" * 50)


async def main():
    """Main function to run tests."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    tester = TestSpecialistAgents()
    results = await tester.run_all_tests()

    return results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())

    # Exit with appropriate code
    failed_count = len([r for r in results.values() if r["status"] == "FAIL"])
    exit(1 if failed_count > 0 else 0)
