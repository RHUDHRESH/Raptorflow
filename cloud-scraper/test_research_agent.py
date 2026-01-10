"""
Research Agent Test Suite
Test the intelligent research agent with Saveetha Engineering College case study
"""

import asyncio
import json
import os
from datetime import datetime, timezone

from intelligent_research_agent import IntelligentResearchAgent, ResearchDepth
from research_agent_config import get_config, validate_config


async def test_research_agent():
    """Test the research agent with Saveetha Engineering College startups"""

    print("🧠 Testing Intelligent Research Agent")
    print("=" * 60)

    # Validate configuration
    if not validate_config():
        print("❌ Configuration validation failed")
        print("Please set VERTEX_AI_PROJECT_ID environment variable")
        return

    # Check if Vertex AI credentials are available
    project_id = os.getenv("VERTEX_AI_PROJECT_ID")
    if not project_id or project_id == "your-project-id":
        print("❌ Vertex AI project ID not configured")
        print("Set environment variable: VERTEX_AI_PROJECT_ID=your-project-id")
        return

    try:
        # Initialize the research agent
        print("🚀 Initializing Research Agent...")
        agent = IntelligentResearchAgent(project_id=project_id)

        # Test queries for Saveetha Engineering College
        test_queries = [
            {
                "query": "Saveetha Engineering College startups and entrepreneurship programs",
                "depth": "light",
                "description": "Basic research on Saveetha startups",
            },
            {
                "query": "Comprehensive analysis of Saveetha Technology Business Incubator and student ventures",
                "depth": "deep",
                "description": "Deep research on STBI and student companies",
            },
            {
                "query": "Compare Saveetha Engineering College startup ecosystem with other Chennai engineering colleges",
                "depth": "comparative",
                "description": "Comparative analysis of startup ecosystems",
            },
        ]

        results = []

        for i, test_case in enumerate(test_queries):
            print(f"\n📊 Test Case {i+1}: {test_case['description']}")
            print(f"Query: {test_case['query']}")
            print(f"Depth: {test_case['depth']}")
            print("-" * 50)

            try:
                # Execute research
                start_time = datetime.now()
                result = await agent.research(
                    query=test_case["query"], depth=test_case["depth"]
                )

                # Record results
                results.append(
                    {
                        "test_case": test_case,
                        "result": result,
                        "execution_time": (datetime.now() - start_time).total_seconds(),
                    }
                )

                # Display results
                print(f"✅ Research completed successfully!")
                print(f"📊 Confidence: {result.confidence_score:.1%}")
                print(f"⏱️  Processing time: {result.processing_time:.2f}s")
                print(f"💰 Estimated cost: ${result.cost_estimate:.6f}")
                print(f"🤖 Model usage: {result.model_usage}")

                # Show key findings
                if result.findings and isinstance(result.findings, dict):
                    key_findings = result.findings.get("key_findings", [])
                    if key_findings:
                        print(f"🎯 Key findings:")
                        for j, finding in enumerate(key_findings[:3]):
                            print(f"  {j+1}. {finding}")

                # Generate reports
                print(f"📄 Generating reports...")

                json_report = await agent.report_generator.generate_json_report(result)
                ppt_outline = await agent.report_generator.generate_ppt_outline(result)
                pdf_content = await agent.report_generator.generate_pdf_content(result)

                # Save test results
                test_filename = f"test_{i+1}_saveetha_research"

                with open(f"{test_filename}_report.json", "w") as f:
                    json.dump(json_report, f, indent=2)

                with open(f"{test_filename}_presentation.json", "w") as f:
                    json.dump(ppt_outline, f, indent=2)

                with open(f"{test_filename}_pdf.json", "w") as f:
                    json.dump(pdf_content, f, indent=2)

                print(f"💾 Reports saved: {test_filename}_*.json")

            except Exception as e:
                print(f"❌ Test case failed: {str(e)}")
                results.append(
                    {
                        "test_case": test_case,
                        "error": str(e),
                        "execution_time": (datetime.now() - start_time).total_seconds(),
                    }
                )

        # Generate summary report
        await generate_test_summary(results, agent)

    except Exception as e:
        print(f"❌ Agent initialization failed: {str(e)}")
        print("Make sure Vertex AI is properly configured with valid credentials")


async def generate_test_summary(results, agent):
    """Generate comprehensive test summary"""

    print(f"\n📊 TEST SUMMARY REPORT")
    print("=" * 60)

    successful_tests = [r for r in results if "error" not in r]
    failed_tests = [r for r in results if "error" in r]

    print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed tests: {len(failed_tests)}")

    if successful_tests:
        # Calculate statistics
        total_time = sum(r["execution_time"] for r in successful_tests)
        avg_confidence = sum(
            r["result"].confidence_score for r in successful_tests
        ) / len(successful_tests)
        total_cost = sum(r["result"].cost_estimate for r in successful_tests)

        print(f"\n📈 Performance Statistics:")
        print(f"  ⏱️  Total time: {total_time:.2f}s")
        print(f"  📊 Average confidence: {avg_confidence:.1%}")
        print(f"  💰 Total cost: ${total_cost:.6f}")
        print(f"  🚀 Average time per test: {total_time/len(successful_tests):.2f}s")

        # Model usage statistics
        model_usage = await agent.get_usage_statistics()
        print(f"\n🤖 Model Usage Statistics:")
        for model, usage in model_usage.items():
            if model != "percentages" and model != "total_requests":
                percentage = model_usage.get("percentages", {}).get(model, 0)
                print(f"  {model}: {usage} uses ({percentage:.1f}%)")

    if failed_tests:
        print(f"\n❌ Failed Test Details:")
        for i, test in enumerate(failed_tests):
            print(f"  {i+1}. {test['test_case']['description']}")
            print(f"     Error: {test['error']}")

    # Save comprehensive summary
    summary_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "successful": len(successful_tests),
            "failed": len(failed_tests),
            "success_rate": len(successful_tests) / len(results) if results else 0,
        },
        "model_usage": await agent.get_usage_statistics() if successful_tests else {},
    }

    with open("research_agent_test_summary.json", "w") as f:
        json.dump(summary_data, f, indent=2)

    print(f"\n💾 Complete summary saved to: research_agent_test_summary.json")


async def test_model_hierarchy():
    """Test the Gemini model hierarchy and cost optimization"""

    print("\n🤖 TESTING MODEL HIERARCHY")
    print("=" * 40)

    project_id = os.getenv("VERTEX_AI_PROJECT_ID")
    if not project_id or project_id == "your-project-id":
        print("❌ Vertex AI project ID not configured")
        return

    try:
        agent = IntelligentResearchAgent(project_id=project_id)

        # Test different complexity levels
        complexity_tests = [
            {
                "query": "What is Saveetha Engineering College?",
                "expected_model": "flashlight",
            },
            {
                "query": "Analyze the startup ecosystem at Saveetha Engineering College and identify key success factors",
                "expected_model": "flash",
            },
            {
                "query": "Comprehensive comparative analysis of Saveetha Engineering College's innovation ecosystem versus peer institutions with strategic recommendations for ecosystem enhancement",
                "expected_model": "ultra",
            },
        ]

        for i, test in enumerate(complexity_tests):
            print(f"\n🧪 Complexity Test {i+1}:")
            print(f"Query: {test['query'][:80]}...")
            print(f"Expected primary model: {test['expected_model']}")

            try:
                result = await agent.research(test["query"], "light")

                # Check model usage
                primary_model = max(result.model_usage.items(), key=lambda x: x[1])[0]
                print(f"✅ Primary model used: {primary_model}")
                print(f"📊 Model usage: {result.model_usage}")
                print(f"💰 Cost: ${result.cost_estimate:.6f}")

            except Exception as e:
                print(f"❌ Test failed: {str(e)}")

        # Show final usage statistics
        final_stats = await agent.get_usage_statistics()
        print(f"\n📊 Final Model Usage Statistics:")
        for model, usage in final_stats.items():
            if model != "percentages" and model != "total_requests":
                percentage = final_stats.get("percentages", {}).get(model, 0)
                print(f"  {model}: {usage} uses ({percentage:.1f}%)")

        # Verify cost optimization (85% flashlight, 10% flash, 5% ultra)
        percentages = final_stats.get("percentages", {})
        flashlight_pct = percentages.get("flashlight", 0)
        flash_pct = percentages.get("flash", 0)
        ultra_pct = percentages.get("ultra", 0)

        print(f"\n💰 Cost Optimization Analysis:")
        print(
            f"  Flashlight (85% target): {flashlight_pct:.1f}% {'✅' if 75 <= flashlight_pct <= 95 else '⚠️'}"
        )
        print(
            f"  Flash (10% target): {flash_pct:.1f}% {'✅' if 5 <= flash_pct <= 15 else '⚠️'}"
        )
        print(
            f"  Ultra (5% target): {ultra_pct:.1f}% {'✅' if 0 <= ultra_pct <= 10 else '⚠️'}"
        )

    except Exception as e:
        print(f"❌ Model hierarchy test failed: {str(e)}")


async def main():
    """Main test execution"""

    print("🚀 INTELLIGENT RESEARCH AGENT TEST SUITE")
    print("=" * 60)
    print("Testing Vertex AI integration with Gemini model hierarchy")
    print("A→A→P→A→P inference pattern")
    print("=" * 60)

    # Check configuration
    config = get_config()
    print(f"📋 Configuration loaded")
    print(f"  Project: {config['vertex_ai']['project_id']}")
    print(f"  Location: {config['vertex_ai']['location']}")

    # Run tests
    try:
        await test_research_agent()
        await test_model_hierarchy()

        print(f"\n🎉 ALL TESTS COMPLETED!")
        print("=" * 60)
        print("📁 Check generated files:")
        print("  - test_*_report.json (JSON reports)")
        print("  - test_*_presentation.json (PPT outlines)")
        print("  - test_*_pdf.json (PDF content)")
        print("  - research_agent_test_summary.json (Complete summary)")

    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
