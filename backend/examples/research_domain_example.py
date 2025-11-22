"""
Research Domain Example - Demonstrates end-to-end ICP workflow.

This example shows how to:
1. Use the research graph to build a complete ICP
2. Use the customer intelligence supervisor
3. Use individual agents standalone

Run this script to test the research domain implementation.
"""

import asyncio
import json
import logging
from typing import Any, Dict

from backend.graphs.research_graph import research_graph
from backend.agents.research.customer_intelligence_supervisor import customer_intelligence_supervisor
from backend.agents.research.icp_builder_agent import icp_builder_agent
from backend.models.persona import ICPRequest


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(data: Dict[str, Any], indent: int = 2) -> None:
    """Pretty print JSON result."""
    print(json.dumps(data, indent=indent, default=str))


async def example_1_research_graph() -> None:
    """
    Example 1: Use the research graph to build a complete ICP.

    This is the recommended approach as it orchestrates all agents
    in sequence with proper error handling and state management.
    """
    print_section("Example 1: Research Graph (Full Workflow)")

    # Define sample ICP request
    sample_request = {
        "company_name": "RaptorFlow",
        "industry": "B2B SaaS",
        "product_description": "AI-powered marketing operations platform that helps "
                              "businesses generate customer insights, create content, "
                              "and execute multi-channel campaigns",
        "target_market": "B2B SaaS companies, digital marketing agencies, and growth teams",
        "target_geo": "United States, Canada, UK",
    }

    logger.info("Starting research graph workflow...")
    print("Input payload:")
    print_result(sample_request)

    try:
        # Run the graph
        result = await research_graph.run(
            icp_request=sample_request,
            workspace_id="example-workspace-123",
            goal="Build comprehensive ICP for RaptorFlow target customers",
        )

        print("\nResearch Graph Result:")
        print(f"Success: {result.get('success')}")
        print(f"Correlation ID: {result.get('correlation_id')}")
        print(f"Errors: {len(result.get('errors', []))}")

        if result.get("success"):
            print("\n--- ICP Profile ---")
            icp = result.get("icp", {})
            print(f"Name: {icp.get('icp_name')}")
            print(f"Summary: {icp.get('executive_summary')}")
            print(f"Demographics: {icp.get('demographics')}")
            print(f"Pain Points: {len(icp.get('pain_points', []))}")
            print(f"Goals: {len(icp.get('goals', []))}")

            print("\n--- Tags ---")
            tags = result.get("tags", [])
            print(f"Total tags: {len(tags)}")
            print(f"Tags: {', '.join(tags[:10])}...")

            print("\n--- Persona Narrative ---")
            narrative = result.get("persona_narrative", {})
            print(f"Persona Name: {narrative.get('persona_name')}")
            print(f"Hook: {narrative.get('hook')}")
            print(f"\nNarrative:\n{narrative.get('narrative', '')[:300]}...")

            print("\n--- Categorized Pain Points ---")
            pain_points = result.get("categorized_pain_points", {})
            print(f"Operational: {pain_points.get('categories', {}).get('operational', 0)}")
            print(f"Financial: {pain_points.get('categories', {}).get('financial', 0)}")
            print(f"Strategic: {pain_points.get('categories', {}).get('strategic', 0)}")
            print(f"Total: {pain_points.get('total_pain_points', 0)}")

            print("\n--- Workflow History ---")
            for step in result.get("history", []):
                status_icon = "✓" if step.get("status") == "success" else "✗"
                print(f"{status_icon} {step.get('node')}: {step.get('status')}")

        else:
            print("\nErrors encountered:")
            for error in result.get("errors", []):
                print(f"  - {error}")

    except Exception as e:
        logger.error(f"Research graph failed: {e}", exc_info=True)


async def example_2_supervisor() -> None:
    """
    Example 2: Use the customer intelligence supervisor directly.

    This approach gives you more control over the workflow while
    still benefiting from orchestration and error handling.
    """
    print_section("Example 2: Customer Intelligence Supervisor")

    context = {
        "icp_request": {
            "company_name": "TechStartup Inc",
            "industry": "FinTech",
            "product_description": "AI-powered financial analytics platform for SMBs",
            "target_market": "Small to medium businesses in finance and accounting",
        }
    }

    logger.info("Starting supervisor workflow...")

    try:
        result = await customer_intelligence_supervisor.execute(
            goal="Build ICP for FinTech SMB customers",
            context=context,
        )

        print("Supervisor Result:")
        print(f"Success: {result.get('success')}")
        print(f"Steps completed: {len(result.get('steps', []))}")

        for step in result.get("steps", []):
            print(f"  - {step.get('step')}: {step.get('status')}")

        if result.get("icp"):
            print(f"\nICP Name: {result['icp'].get('icp_name')}")

    except Exception as e:
        logger.error(f"Supervisor failed: {e}", exc_info=True)


async def example_3_standalone_agent() -> None:
    """
    Example 3: Use an individual agent standalone.

    Use this approach when you only need one specific capability,
    such as building an ICP without tags or narrative.
    """
    print_section("Example 3: Standalone ICP Builder Agent")

    payload = {
        "company_name": "HealthTech Co",
        "industry": "Healthcare",
        "product_description": "Telemedicine platform for rural healthcare providers",
        "target_market": "Rural clinics and small healthcare practices",
        "target_geo": "United States (rural areas)",
    }

    logger.info("Building ICP with standalone agent...")

    try:
        result = await icp_builder_agent.execute(payload)

        print("ICP Builder Result:")
        print(f"Agent: {result.get('agent')}")

        output = result.get("output", {})
        print(f"\nICP Name: {output.get('icp_name')}")
        print(f"Executive Summary: {output.get('executive_summary')}")
        print(f"\nDemographics:")
        print_result(output.get("demographics", {}))
        print(f"\nPsychographics:")
        print_result(output.get("psychographics", {}))
        print(f"\nPain Points:")
        for i, pp in enumerate(output.get("pain_points", [])[:3], 1):
            print(f"  {i}. {pp}")

    except Exception as e:
        logger.error(f"ICP builder failed: {e}", exc_info=True)


async def main() -> None:
    """Run all examples."""
    print_section("Research Domain Implementation Examples")
    print("This script demonstrates the research domain workflow.")
    print("It shows three approaches: Graph, Supervisor, and Standalone Agent.")

    # Run examples sequentially
    await example_1_research_graph()
    await asyncio.sleep(1)  # Brief pause between examples

    await example_2_supervisor()
    await asyncio.sleep(1)

    await example_3_standalone_agent()

    print_section("Examples Complete")
    print("All research domain examples have been executed.")
    print("\nKey takeaways:")
    print("1. Use research_graph for complete end-to-end workflows")
    print("2. Use customer_intelligence_supervisor for custom orchestration")
    print("3. Use individual agents for specific tasks")
    print("\nRefer to the agent implementations for detailed documentation.")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
