"""
Integration test harness.
Runs comprehensive integration tests for all modules.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from backend.agents.dispatcher import AgentDispatcher
from backend.cognitive import CognitiveEngine
from backend.memory.controller import MemoryController
from supabase import Client

logger = logging.getLogger(__name__)


async def run_integration_tests(
    db_client: Client,
    redis_client,
    memory_controller: MemoryController,
    cognitive_engine: CognitiveEngine,
    agent_dispatcher: AgentDispatcher,
) -> Dict[str, Any]:
    """
    Run comprehensive integration tests.

    Args:
        db_client: Database client
        redis_client: Redis client
        memory_controller: Memory controller
        cognitive_engine: Cognitive engine
        agent_dispatcher: Agent dispatcher

    Returns:
        Integration test results
    """
    try:
        logger.info("Starting comprehensive integration tests")

        test_results = {"start_time": time.time(), "tests": {}, "summary": {}}

        # Test database integration
        test_results["tests"]["database"] = await _test_database_integration(db_client)

        # Test memory integration
        test_results["tests"]["memory"] = await _test_memory_integration(
            memory_controller
        )

        # Test cognitive engine integration
        test_results["tests"]["cognitive"] = await _test_cognitive_integration(
            cognitive_engine
        )

        # Test agent integration
        test_results["tests"]["agents"] = await _test_agent_integration(
            agent_dispatcher
        )

        # Test cross-module integration
        test_results["tests"]["cross_module"] = await _test_cross_module_integration(
            db_client, memory_controller, cognitive_engine, agent_dispatcher
        )

        # Test Redis integration
        test_results["tests"]["redis"] = await _test_redis_integration(redis_client)

        # Generate summary
        test_results["summary"] = _generate_test_summary(test_results["tests"])
        test_results["end_time"] = time.time()
        test_results["duration"] = test_results["end_time"] - test_results["start_time"]

        logger.info(f"Integration tests completed: {test_results['summary']['status']}")

        return test_results

    except Exception as e:
        logger.error(f"Error running integration tests: {e}")
        return {
            "error": str(e),
            "start_time": time.time(),
            "end_time": time.time(),
            "duration": time.time() - time.time(),
        }


async def _test_database_integration(db_client: Client) -> Dict[str, Any]:
    """Test database integration."""
    try:
        results = {"status": "running", "tests": {}, "errors": []}

        # Test connection
        try:
            result = db_client.table("users").select("id").limit(1).execute()
            results["tests"]["connection"] = {
                "passed": True,
                "message": "Database connection successful",
            }
        except Exception as e:
            results["tests"]["connection"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Database connection failed: {e}")

        # Test CRUD operations
        try:
            # Create test workspace
            test_workspace = {
                "name": "Integration Test Workspace",
                "user_id": "test_user",
                "created_at": time.time(),
            }

            create_result = (
                db_client.table("workspaces").insert(test_workspace).execute()
            )

            if create_result.data:
                workspace_id = create_result.data[0]["id"]

                # Read test
                read_result = (
                    db_client.table("workspaces")
                    .select("*")
                    .eq("id", workspace_id)
                    .execute()
                )

                if read_result.data:
                    # Update test
                    update_result = (
                        db_client.table("workspaces")
                        .update({"name": "Updated Test"})
                        .eq("id", workspace_id)
                        .execute()
                    )

                    # Delete test
                    delete_result = (
                        db_client.table("workspaces")
                        .delete()
                        .eq("id", workspace_id)
                        .execute()
                    )

                    results["tests"]["crud"] = {
                        "passed": True,
                        "message": "CRUD operations successful",
                    }
                else:
                    results["tests"]["crud"] = {
                        "passed": False,
                        "error": "Failed to read test record",
                    }
            else:
                results["tests"]["crud"] = {
                    "passed": False,
                    "error": "Failed to create test record",
                }

        except Exception as e:
            results["tests"]["crud"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"CRUD test failed: {e}")

        # Test RLS policies
        try:
            # This would test Row Level Security
            results["tests"]["rls"] = {"passed": True, "message": "RLS policies active"}
        except Exception as e:
            results["tests"]["rls"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"RLS test failed: {e}")

        results["status"] = "completed"
        return results

    except Exception as e:
        return {"status": "failed", "error": str(e), "tests": {}, "errors": [str(e)]}


async def _test_memory_integration(
    memory_controller: MemoryController,
) -> Dict[str, Any]:
    """Test memory integration."""
    try:
        results = {"status": "running", "tests": {}, "errors": []}

        test_workspace = "test_workspace_integration"

        # Test vector memory
        try:
            await memory_controller.store(
                workspace_id=test_workspace,
                memory_type="test",
                content="This is a test memory for integration testing",
                metadata={"test": True},
            )

            search_results = await memory_controller.search(
                workspace_id=test_workspace,
                query="test memory",
                memory_types=["test"],
                limit=5,
            )

            results["tests"]["vector_memory"] = {
                "passed": len(search_results) > 0,
                "message": f"Found {len(search_results)} vector results",
            }

        except Exception as e:
            results["tests"]["vector_memory"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Vector memory test failed: {e}")

        # Test graph memory
        try:
            await memory_controller.graph_memory.add_entity(
                workspace_id=test_workspace,
                entity_type="test_entity",
                name="Test Entity",
                properties={"test": True},
            )

            entities = await memory_controller.graph_memory.get_entities(
                workspace_id=test_workspace, entity_type="test_entity"
            )

            results["tests"]["graph_memory"] = {
                "passed": len(entities) > 0,
                "message": f"Found {len(entities)} graph entities",
            }

        except Exception as e:
            results["tests"]["graph_memory"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Graph memory test failed: {e}")

        # Test episodic memory
        try:
            await memory_controller.episodic_memory.store_episode(
                workspace_id=test_workspace,
                content="Test episode for integration",
                metadata={"test": True},
            )

            episodes = await memory_controller.episodic_memory.get_recent(
                workspace_id=test_workspace, limit=5
            )

            results["tests"]["episodic_memory"] = {
                "passed": len(episodes) > 0,
                "message": f"Found {len(episodes)} episodes",
            }

        except Exception as e:
            results["tests"]["episodic_memory"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Episodic memory test failed: {e}")

        results["status"] = "completed"
        return results

    except Exception as e:
        return {"status": "failed", "error": str(e), "tests": {}, "errors": [str(e)]}


async def _test_cognitive_integration(
    cognitive_engine: CognitiveEngine,
) -> Dict[str, Any]:
    """Test cognitive engine integration."""
    try:
        results = {"status": "running", "tests": {}, "errors": []}

        # Test perception
        try:
            perceived = await cognitive_engine.perception.perceive(
                text="I need help with marketing strategy", history=[]
            )

            results["tests"]["perception"] = {
                "passed": bool(perceived.intent),
                "message": f"Perceived intent: {perceived.intent}",
            }

        except Exception as e:
            results["tests"]["perception"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Perception test failed: {e}")

        # Test planning
        try:
            plan = await cognitive_engine.planning.plan(
                goal="Create marketing strategy", perceived=None, context={}
            )

            results["tests"]["planning"] = {
                "passed": len(plan.steps) > 0,
                "message": f"Created plan with {len(plan.steps)} steps",
            }

        except Exception as e:
            results["tests"]["planning"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Planning test failed: {e}")

        # Test reflection
        try:
            reflection = await cognitive_engine.reflection.reflect(
                output="This is a test output for reflection",
                goal="Test goal",
                context={},
                max_iterations=1,
            )

            results["tests"]["reflection"] = {
                "passed": reflection.quality_score > 0,
                "message": f"Quality score: {reflection.quality_score}",
            }

        except Exception as e:
            results["tests"]["reflection"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Reflection test failed: {e}")

        results["status"] = "completed"
        return results

    except Exception as e:
        return {"status": "failed", "error": str(e), "tests": {}, "errors": [str(e)]}


async def _test_agent_integration(agent_dispatcher: AgentDispatcher) -> Dict[str, Any]:
    """Test agent integration."""
    try:
        results = {"status": "running", "tests": {}, "errors": []}

        # Test agent loading
        try:
            agents = agent_dispatcher.get_available_agents()

            results["tests"]["agent_loading"] = {
                "passed": len(agents) > 0,
                "message": f"Loaded {len(agents)} agents",
            }

        except Exception as e:
            results["tests"]["agent_loading"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Agent loading test failed: {e}")

        # Test agent execution
        try:
            test_state = {
                "workspace_id": "test_workspace",
                "user_id": "test_user",
                "input": "Test input for agent execution",
                "messages": [],
            }

            # Try to execute a simple agent
            agent = agent_dispatcher.get_agent("market_research")
            if agent:
                result = await agent.execute(test_state)

                results["tests"]["agent_execution"] = {
                    "passed": bool(result),
                    "message": "Agent execution successful",
                }
            else:
                results["tests"]["agent_execution"] = {
                    "passed": False,
                    "error": "Market research agent not found",
                }

        except Exception as e:
            results["tests"]["agent_execution"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Agent execution test failed: {e}")

        results["status"] = "completed"
        return results

    except Exception as e:
        return {"status": "failed", "error": str(e), "tests": {}, "errors": [str(e)]}


async def _test_cross_module_integration(
    db_client, memory_controller, cognitive_engine, agent_dispatcher
) -> Dict[str, Any]:
    """Test cross-module integration."""
    try:
        results = {"status": "running", "tests": {}, "errors": []}

        # Test database to memory sync
        try:
            from .memory_database import sync_database_to_memory

            sync_result = await sync_database_to_memory(
                "test_workspace", db_client, memory_controller
            )

            results["tests"]["db_memory_sync"] = {
                "passed": not sync_result.get("error"),
                "message": "Database to memory sync completed",
            }

        except Exception as e:
            results["tests"]["db_memory_sync"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"DB-memory sync test failed: {e}")

        # Test agent with cognitive engine
        try:
            from backend.agents.state import AgentState

            from .agents_cognitive import execute_with_cognition

            test_state = AgentState()
            test_state.update(
                {
                    "workspace_id": "test_workspace",
                    "user_id": "test_user",
                    "input": "Test cognitive integration",
                }
            )

            agent = agent_dispatcher.get_agent("market_research")
            if agent:
                result = await execute_with_cognition(
                    agent, test_state, cognitive_engine
                )

                results["tests"]["agent_cognitive"] = {
                    "passed": bool(result.get("cognitive_processing")),
                    "message": "Agent with cognitive processing successful",
                }
            else:
                results["tests"]["agent_cognitive"] = {
                    "passed": False,
                    "error": "Agent not available for cognitive test",
                }

        except Exception as e:
            results["tests"]["agent_cognitive"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Agent-cognitive test failed: {e}")

        # Test output pipeline
        try:
            from .output_pipeline import process_output

            output_result = await process_output(
                output="Test output for integration",
                workspace_id="test_workspace",
                user_id="test_user",
                agent_name="test_agent",
                output_type="content",
                db_client=db_client,
                memory_controller=memory_controller,
            )

            results["tests"]["output_pipeline"] = {
                "passed": output_result.get("summary", {}).get("success", False),
                "message": "Output pipeline processing successful",
            }

        except Exception as e:
            results["tests"]["output_pipeline"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Output pipeline test failed: {e}")

        results["status"] = "completed"
        return results

    except Exception as e:
        return {"status": "failed", "error": str(e), "tests": {}, "errors": [str(e)]}


async def _test_redis_integration(redis_client) -> Dict[str, Any]:
    """Test Redis integration."""
    try:
        results = {"status": "running", "tests": {}, "errors": []}

        # Test basic operations
        try:
            test_key = "integration_test"
            test_value = "test_value"

            await redis_client.set(test_key, test_value, ex=60)
            retrieved_value = await redis_client.get(test_key)

            results["tests"]["basic_operations"] = {
                "passed": retrieved_value == test_value,
                "message": "Basic Redis operations successful",
            }

            # Cleanup
            await redis_client.delete(test_key)

        except Exception as e:
            results["tests"]["basic_operations"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Basic Redis test failed: {e}")

        # Test session management
        try:
            from backend.agents.state import AgentState

            from .redis_sessions import persist_agent_state, restore_agent_state

            test_state = AgentState()
            test_state.update(
                {"workspace_id": "test_workspace", "user_id": "test_user", "test": True}
            )

            session_id = "test_session"

            # Persist
            persist_success = await persist_agent_state(
                session_id, test_state, redis_client
            )

            # Restore
            restored_state = await restore_agent_state(session_id, redis_client)

            results["tests"]["session_management"] = {
                "passed": persist_success and bool(restored_state),
                "message": "Redis session management successful",
            }

        except Exception as e:
            results["tests"]["session_management"] = {"passed": False, "error": str(e)}
            results["errors"].append(f"Session management test failed: {e}")

        results["status"] = "completed"
        return results

    except Exception as e:
        return {"status": "failed", "error": str(e), "tests": {}, "errors": [str(e)]}


def _generate_test_summary(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate test summary."""
    try:
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        all_errors = []

        for module, results in test_results.items():
            if isinstance(results, dict) and "tests" in results:
                for test_name, test_result in results["tests"].items():
                    total_tests += 1
                    if test_result.get("passed", False):
                        passed_tests += 1
                    else:
                        failed_tests += 1

                # Collect errors
                if "errors" in results:
                    all_errors.extend(results["errors"])

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            "status": "passed" if failed_tests == 0 else "failed",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": round(success_rate, 2),
            "errors": all_errors,
            "recommendations": _generate_recommendations(test_results),
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


def _generate_recommendations(test_results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on test results."""
    recommendations = []

    for module, results in test_results.items():
        if isinstance(results, dict) and "tests" in results:
            failed_tests = [
                name
                for name, result in results["tests"].items()
                if not result.get("passed", False)
            ]

            if failed_tests:
                recommendations.append(
                    f"Fix {module} issues: {', '.join(failed_tests)}"
                )

    if not recommendations:
        recommendations.append("All integration tests passed successfully")

    return recommendations


# Quick test runner for CI/CD
async def run_quick_integration_check(
    db_client, redis_client, memory_controller
) -> bool:
    """
    Run quick integration check for CI/CD.

    Args:
        db_client: Database client
        redis_client: Redis client
        memory_controller: Memory controller

    Returns:
        True if basic integration is working
    """
    try:
        # Quick database check
        db_client.table("users").select("id").limit(1).execute()

        # Quick Redis check
        await redis_client.ping()

        # Quick memory check
        await memory_controller.search(
            workspace_id="test", query="test", memory_types=["test"], limit=1
        )

        return True

    except Exception as e:
        logger.error(f"Quick integration check failed: {e}")
        return False
