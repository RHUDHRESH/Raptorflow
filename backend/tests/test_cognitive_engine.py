"""
Test Suite for Cognitive Engine

Comprehensive test suite for all cognitive components.
Implements PROMPTS 82-89 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import logging
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from caching import CognitiveCache
from context import CognitiveContextBuilder
from critic import AdversarialCritic

# Import cognitive engine components
from engine import CognitiveEngine
from execution import PlanExecutor
from fallback import FallbackHandler
from hitl import ApprovalGate
from .models import CognitiveResult, ExecutionPlan, PerceivedInput, ReflectionResult
from monitoring import CognitiveMonitor
from parallel import ParallelExecutor
from perception import PerceptionModule
from pipeline import CognitivePipeline
from planning import PlanningModule
from reflection import ReflectionModule
from retry import RetryManager
from traces import CognitiveTracer

# Test configuration
TEST_TIMEOUT = 30
TEST_WORKSPACE_ID = "test_workspace"
TEST_USER_ID = "test_user"

# Mock data
SAMPLE_TEXT = "This is a test text for cognitive processing."
SAMPLE_CONTEXT = {
    "icp_id": "test_icp",
    "session_id": "test_session",
    "user_preferences": {"language": "en"}
}

class TestPerceptionModule:
    """Test suite for Perception Module (PROMPTS 1-12)."""

    @pytest.fixture
    def perception_module(self):
        """Create perception module for testing."""
        return PerceptionModule()

    @pytest.mark.asyncio
    async def test_entity_extraction(self, perception_module):
        """Test entity extraction (PROMPT 1)."""
        text = "Apple Inc. announced a $1M investment in 2024."

        result = await perception_module.extract_entities(text)

        assert len(result.entities) > 0
        assert any(entity.type.name == "COMPANY" for entity in result.entities)

        # Check for money entity
        money_entities = [e for e in result.entities if e.type.name == "MONEY"]
        assert len(money_entities) > 0
        assert "$1M" in [e.text for e in money_entities]

    @pytest.mark.asyncio
    async def test_intent_detection(self, perception_module):
        """Test intent detection (PROMPT 2)."""
        text = "Create a marketing campaign for our new product launch"

        result = await perception_module.detect_intent(text)

        assert result.intent_type is not None
        assert result.confidence > 0.5
        assert result.intent_type.name == "CREATE"

    @pytest.mark.asyncio
    async def test_sentiment_analysis(self, perception_module):
        """Test sentiment analysis (PROMPT 3)."""
        text = "I love this amazing product! It's fantastic!"

        result = await perception_module.analyze_sentiment(text)

        assert result.sentiment is not None
        assert result.sentiment.name in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
        assert result.confidence > 0.5

    @pytest.mark.asyncio
    async def test_urgency_classification(self, perception_module):
        """Test urgency classification (PROMPT 4)."""
        text = "This is extremely urgent and requires immediate attention!"

        result = await perception_module.classify_urgency(text)

        assert result.urgency is not None
        assert result.urgency.name in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert result.confidence > 0.5

    @pytest.mark.asyncio
    async def test_preprocessing(self, perception_module):
        """Test text preprocessing (PROMPT 10)."""
        text = "  This is a test   with extra spaces  "

        result = await perception_module.preprocess(text)

        assert result.clean_text == "This is a test with extra spaces"
        assert result.normalized_text == result.clean_text.lower()

    @pytest.mark.asyncio
    async def test_clarification_detection(self, perception_module):
        """Test clarification detection (PROMPT 11)."""
        text = "We need to do something about this"

        result = await perception_detector.detect_clarification_needs(text)

        assert len(result.clarifications) > 0
        assert any("something" in clarification.question.lower() for clarification in result.clarifications)

    @pytest.mark.asyncio
    async def test_multimodal_perception(self, perception_module):
        """Test multimodal perception (PROMPT 12)."""
        # Mock multimodal data
        image_data = b"fake_image_data"

        result = await perception_module.analyze_image(image_data)

        assert result.analysis is not None
        assert "image" in result.analysis.lower()

class TestPlanningModule:
    """Test suite for Planning Module (PROMPTS 13-24)."""

    @pytest.fixture
    def planning_module(self):
        """Create planning module for testing."""
        return PlanningModule()

    @pytest.mark.asyncio
    async def test_task_decomposition(self, planning_module):
        """Test task decomposition (PROMPT 13)."""
        goal = "Create a comprehensive marketing strategy"

        result = await planning_module.decompose_task(goal)

        assert len(result.subtasks) > 0
        assert all(subtask.description for subtask in result.subtasks)

    @pytest.mark.asyncio
    async def test_step_planning(self, planning_module):
        """Test step planning (PROMPT 14)."""
        subtasks = [
            {"description": "Research market trends"},
            {"description": "Create content calendar"},
            {"description": "Set up analytics"}
        ]

        result = await planning_module.plan_steps(subtasks)

        assert len(result.steps) == len(subtasks)
        assert all(step.description for step in result.steps)

    @pytest.mark.asyncio
    async def test_cost_estimation(self, planning_module):
        """Test cost estimation (PROMPT 15)."""
        steps = [
            {"description": "Research market trends", "estimated_tokens": 1000},
            {"description": "Create content calendar", "estimated_tokens": 500}
        ]

        result = await planning_module.estimate_costs(steps)

        assert result.total_cost_usd > 0
        assert result.total_tokens == 1500

    @pytest.mark.asyncio
    async def test_risk_assessment(self, planning_module):
        """Test risk assessment (PROMPT 16)."""
        steps = [
            {"description": "High-risk activity", "risk_level": "HIGH"},
            {"description": "Low-risk activity", "risk_level": "LOW"}
        ]

        result = await planning_module.assess_risks(steps)

        assert len(result.risks) == 2
        assert any(risk.level.name == "HIGH" for risk in result.risks)

    @pytest.mark.asyncio
    async def test_replanning(self, planning_module):
        """Test dynamic replanning (PROMPT 22)."""
        failed_step = {"description": "Failed step", "error": "Network error"}

        result = await planning_module.replan_for_failure(
            failed_step,
            available_alternatives=["alternative_approach", "retry_later"]
        )

        assert result.strategy is not None
        assert result.new_plan is not None

    @pytest.mark.asyncio
    async def test_checkpoints(self, planning_module):
        """Plan checkpoints (PROMPT 23)."""
        plan = ExecutionPlan(
            goal="Test goal",
            steps=[],
            total_cost=CostEstimate(total_tokens=100, total_cost_usd=0.1),
            total_time_seconds=60,
            risk_level="LOW"
        )

        checkpoint_id = await planning_module.create_checkpoint(plan)

        assert checkpoint_id is not None
        assert checkpoint_id.startswith("checkpoint_")

    @pytest.mark.asyncio
    async def test_budget_tracking(self, planning_module):
        """Budget tracking (PROMPT 24)."""
        user_id = TEST_USER_ID
        budget_limit = 10.0

        tracker = planning_module.create_budget_tracker(user_id, budget_limit)

        # Test budget check
        can_spend = await tracker.check_budget(5.0)
        assert can_spend

        # Test budget deduction
        await tracker.deduct_budget(2.0)
        remaining = await tracker.get_remaining_budget()
        assert remaining == 8.0

    @pytest.mark.asyncio
    async def test_plan_templates(self, planning_module):
        """Plan templates (PROMPT 25)."""
        templates = planning_module.get_available_templates()

        assert len(templates) > 0
        assert any(template.category.value == "content_creation" for template in templates)

class TestReflectionModule:
    """Test suite for Reflection Module (PROMPTS 34-41)."""

    @pytest.fixture
    def reflection_module(self):
        """Create reflection module for testing."""
        return ReflectionModule()

    @pytest.mark.asyncio
    async def test_fact_checking(self, reflection_module):
        """Test fact checking (PROMPT 34)."""
        content = "The company was founded in 2020 and has 100 employees."
        source_material = "Company founded in 2020 with 100 employees."

        result = await reflection_module.check_facts(content, source_material)

        assert result.verified_claims > 0
        assert result.unverified_claims == 0

    @pytest.mark.asyncio
    async def test_plagiarism_detection(self, reflection_module):
        """Test plagiarism detection (PROMPT 36)."""
        content = "This is original content."

        result = await reflection_module.check_plagiarism(content)

        assert result.originality_score > 0.8
        assert result.similarity_score > 0.8

    @pytest.mark.asyncio
    async def test_learning_mechanism(self, reflection_module):
        """Test learning mechanism (PROMPT 40)."""
        feedback = "This was good, but could be better."

        result = await reflection_module.learn_from_feedback(
            output="Original output",
            feedback=feedback
        )

        assert result.improvements_suggested is not None
        assert result.learning_confidence > 0.5

class TestAdversarialCritic:
    """Test suite for Adversarial Critic (PROMPTS 57-60)."""

    @pytest.fixture
    def adversarial_critic(self):
        """Create adversarial critic for testing."""
        return AdversarialCritic()

    @pytest.mark.asyncio
    async def test_failure_mode_analysis(self, adversarial_critic):
        """Test failure mode analysis (PROMPT 57)."""
        content = "This is a perfect solution with no issues."

        result = await adversarial_critic.analyze_failure_modes(content)

        assert len(result.failure_modes) > 0
        assert any(failure_mode.severity.name in ["LOW", "MEDIUM", "HIGH", "CRITICAL"] for failure_mode in result.failure_modes)

    @pytest.mark.asyncio
    async def test_edge_case_testing(self, adversarial_critic):
        """Test edge case testing (PROMPT 58)."""
        test_cases = [
            {"input": "", "expected": "error"},
            {"input": "Normal input", "expected": "success"},
            {"input": "Special characters: !@#$%^&*()", "expected": "success"}
        ]

        for test_case in test_cases:
            result = await adversarial_critic.test_edge_cases(test_case["input"])

            if test_case["expected"] == "error":
                assert len(result.issues) > 0
            else:
                assert len(result.issues) == 0

    @pytest.mark.asyncio
    async def test_competitor_lens(self, adversarial_critic):
        """Test competitor lens (PROMPT 59)."""
        content = "Our product is the best in the market."

        result = await adversarial_critic.analyze_as_competitor(content)

        assert len(result.insights) > 0
        assert any(insight.severity.name in ["LOW", "MEDIUM", "HIGH", "CRITICAL"] for insight in result.insights)

    @pytest.mark.asyncio
    async def test_customer_lens(self, adversarial_critic):
        """Test customer lens (PROMPT 60)."""
        content = "This product meets all customer needs."

        result = await adversarial_critic.analyze_as_customer(content)

        assert len(result.insights) > 0
        assert result.trust_score > 0.5

class TestIntegrationComponents:
    """Test suite for Integration Components (PROMPTS 62-70)."""

    @pytest.fixture
    def cognitive_pipeline(self):
        """Create cognitive pipeline for testing."""
        return CognitivePipeline(
            perception_module=PerceptionModule(),
            planning_module=PlanningModule(),
            reflection_module=ReflectionModule(),
            approval_gate=ApprovalGate(),
            adversarial_critic=AdversarialCritic()
        )

    @pytest.mark.asyncio
    async def test_pipeline_orchestration(self, cognitive_pipeline):
        """Test pipeline orchestration (PROMPT 62)."""
        text = "Test input for pipeline"

        result = await cognitive_pipeline.run_pipeline(
            text=text,
            workspace_id=TEST_WORKSPACE_ID,
            user_id=TEST_USER_ID
        )

        assert result.status in ["completed", "failed"]
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_context_building(self):
        """Test context building (PROMPT 63)."""
        context = await context_builder.build_context(
            workspace_id=TEST_WORKSPACE_ID,
            user_id=TEST_USER_ID
        )

        assert context.workspace_id == TEST_WORKSPACE_ID
        assert context.user_id == TEST_USER_ID
        assert context.foundation_data is not None

    @pytest.mark.asyncio
    async def test_plan_execution(self):
        """Test plan execution (PROMPT 64)."""
        plan = ExecutionPlan(
            goal="Test goal",
            steps=[],
            total_cost=CostEstimate(total_tokens=100, total_cost_usd=0.1),
            total_time_seconds=60,
            risk_level="LOW"
        )

        executor = PlanExecutor()
        result = await executor.execute_plan(plan, TEST_WORKSPACE_ID, TEST_USER_ID)

        assert result.status in ["completed", "failed"]
        assert result.total_execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_monitoring(self):
        """Test monitoring (PROMPT 65)."""
        monitor = CognitiveMonitor()

        # Test monitoring start
        await monitor.start_monitoring()

        # Test metrics collection
        stats = monitor.get_monitoring_stats()
        assert stats["total_traces"] >= 0

    @pytest.mark.asyncio
    async def test_tracing(self):
        """Test tracing (PROMPT 66)."""
        tracer = CognitiveTracer()

        # Test trace creation
        trace_id = await tracer.start_trace(
            execution_id="test_execution",
            workspace_id=TEST_WORKSPACE_ID,
            user_id=TEST_USER_ID
        )

        assert trace_id is not None

        # Test trace completion
        await tracer.end_trace(trace_id, "completed")

        # Get trace summary
        summary = await tracer.get_trace_summary(trace_id)
        assert summary["total_events"] >= 0

    @pytest.mark.asyncio
    async def test_caching(self):
        """Test caching (PROMPT 67)."""
        cache = CognitiveCache()

        # Test cache set and get
        await cache.set("test_key", "test_value")
        value = await cache.get("test_key")

        assert value == "test_value"

        # Test cache stats
        stats = cache.get_cache_stats()
        assert stats["total_cached_items"] >= 1

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test parallel execution (PROMPT 68)."""
        plan = ExecutionPlan(
            goal="Test parallel execution",
            steps=[
                PlanStep(id="step1", description="Step 1"),
                PlanStep(id="step2", description="Step 2"),
                PlanStep(id="step3", description="Step 3")
            ],
            total_cost=CostEstimate(total_tokens=100, total_cost_usd=0.1),
            total_time_seconds=60,
            risk_level="LOW"
        )

        executor = ParallelExecutor()
        result = await executor.execute_parallel(
            plan, TEST_WORKSPACE_ID, TEST_USER_ID,
            mode="parallel"
        )

        assert result.total_tasks == 3
        assert result.completed_tasks >= 0

    @pytest.mark.asyncio
    async def test_retry_mechanisms(self):
        """Test retry mechanisms (PROMPT 69)."""
        retry_manager = RetryManager()

        # Test retry with backoff
        call_count = 0

        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Simulated failure")
            return "success"

        result = await retry_manager.retry_with_backoff(failing_function)

        assert result.success
        assert result.total_attempts <= 3

    @pytest.mark.asyncio
    async def test_fallback_handling(self):
        """Test fallback handling (PROMPT 70)."""
        fallback_handler = FallbackHandler()

        # Test error handling
        error = Exception("Test error")

        result = await fallback_handler.handle_failure(
            error=error,
            context={"test": True}
        )

        assert result is not None
        assert result.total_time_ms >= 0

class TestProtocolComponents:
    """Test suite for Protocol Components (PROMPTS 72-78)."""

    @pytest.fixture
    def message_format(self):
        """Create message format for testing."""
        return MessageFormat()

    def test_message_creation(self, message_format):
        """Test message creation (PROMPT 72)."""
        message = message_format.create_request(
            from_agent="agent1",
            to_agent="agent2",
            payload={"test": "data"},
            priority="normal"
        )

        assert message.from_agent == "agent1"
        assert message.to_agent == "agent2"
        assert message.message_type == MessageType.REQUEST
        assert message.priority.value == "normal"

    @pytest.fixture
    def agent_handoff(self):
        """Create agent handoff for testing."""
        return AgentHandoff()

    @pytest.mark.asyncio
    async def test_handoff_protocol(self, agent_handoff):
        """Test handoff protocol (PROMPT 73)."""
        result = await agent_handoff.initiate_handoff(
            from_agent="agent1",
            to_agent="agent2",
            handoff_type="forward",
            reason="capability_mismatch",
            task_data={"task": "test task"},
            session_data={"session": "test"}
        )

        assert result.status in ["accepted", "rejected"]
        assert result.from_agent == "agent1"
        assert result.to_agent == "agent2"

    @pytest.fixture
    def error_handler(self):
        """Create error handler for testing."""
        return ErrorHandler()

    @pytest.mark.asyncio
    async def test_error_handling(self, error_handler):
        """Test error handling (PROMPT 74)."""
        error = Exception("Test error")

        result = await error_handler.handle_error(
            error=error,
            context={"test": True}
        )

        assert result is not None
        assert result.total_attempts >= 0

    @pytest.fixture
    def schema_registry(self):
        """Create schema registry for testing."""
        return SchemaRegistry()

    def test_schema_validation(self, schema_registry):
        """Test schema validation (PROMPT 75)."""
        schema = schema_registry.get_schema("cognitive_input_v1")

        valid_data = {
            "text": "Test text",
            "context": {}
        }

        result = schema_registry.validate_data(valid_data, "cognitive_input_v1")

        assert result["valid"]

    @pytest.fixture
    def version_manager(self):
        """Create version manager for testing."""
        return VersionManager()

    def test_version_management(self, version_manager):
        """Test version management (PROMPT 76)."""
        # Test version comparison
        comparison = version_manager.compare_versions("1.0.0", "1.1.0")

        assert comparison == 0  # Same version
        comparison = version_manager.compare_versions("1.0.0", "2.0.0")
        assert comparison == -1  # 1.0.0 < 2.0.0

    @pytest.fixture
    def service_discovery(self):
        """Create service discovery for testing."""
        return ServiceDiscovery()

    @pytest.mark.asyncio
    async def test_service_discovery(self, service_discovery):
        """Test service discovery (PROMPT 77)."""
        service = ServiceRegistration(
            service_id="test_service",
            name="Test Service",
            service_type=ServiceType.AGENT,
            version="1.0.0",
            status=ServiceStatus.ACTIVE,
            endpoints=[],
            capabilities=["test_capability"],
            dependencies=[],
            health_check_url="http://localhost:8000/health",
            health_check_interval=30
        )

        await service_discovery.register_service(service)

        discovered = service_discovery.discover_services()

        assert len(discovered) >= 1
        assert discovered[0].service_id == "test_service"

    @pytest.fixture
    def rule_engine(self):
        """Create rule engine for testing."""
        return RuleEngine()

    def test_routing_rules(self, rule_engine):
        """Test routing rules (PROMPT 78)."""
        # Add test rule
        rule = RoutingRule(
            rule_id="test_rule",
            name="Test Rule",
            description="Test routing rule",
            rule_type=RuleType.CONTENT_BASED,
            priority=RulePriority.NORMAL,
            conditions=[
                {"field": "content_type", "operator": "equals", "value": "test"}
            ],
            actions=[
                {"type": RuleAction.ROUTE_TO.value, "agent": "test_agent"}
            ],
            enabled=True
        )

        rule_engine.add_rule(rule)

        rules = rule_engine.get_engine("default").get_rules()

        assert len(rules) >= 1
        assert rules[0].name == "Test Rule"

class TestAPIEndpoints:
    """Test suite for API Endpoints (PROMPT 79)."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_process_endpoint(self, client):
        """Test main processing endpoint."""
        response = await client.post(
            "/api/v1/cognitive/process",
            json={
                "text": SAMPLE_TEXT,
                "workspace_id": TEST_WORKSPACE_ID,
                "user_id": TEST_USER_ID
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"]
        assert "request_id" in data
        assert "processing_time_ms" in data

    @pytest.mark.asyncio
    async def test_perception_endpoint(self, client):
        """Test perception endpoint."""
        response = await client.post(
            "/api/v1/cognitive/perception",
            json={
                "text": SAMPLE_TEXT,
                "context": SAMPLE_CONTEXT
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"]
        assert "perceived_input" in data
        assert "processing_time_ms" in data

    @pytest.mark.asyncio
    async def test_planning_endpoint(self, client):
        """Test planning endpoint."""
        response = await client.post(
            "/api/v1/cognitive/planning",
            json={
                "text": SAMPLE_TEXT,
                "context": SAMPLE_CONTEXT
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"]
        assert "execution_plan" in data

    @pytest.mark.asyncio
    async def test_reflection_endpoint(self, client):
        """Test reflection endpoint."""
        response = await client.post(
            "/api/v1/cognitive/reflection",
            json={
                "output": "Test output",
                "goal": "Test goal",
                "context": SAMPLE_CONTEXT
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"]
        assert "reflection_result" in data

    @pytest.mark.asyncio
    async def test_critic_endpoint(self, client):
        """Test critic endpoint."""
        response = await client.post(
            "/api/v1/cognitive/critic",
            json={
                "content": SAMPLE_TEXT,
                "context": SAMPLE_CONTEXT
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"]
        assert "critic_result" in data

    @pytest.mark.asyncio
    async def test_approvals_endpoint(self, client):
        """Test approvals endpoint."""
        response = await client.get(
            "/api/v1/cognitive/approvals"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"]
        assert "pending_approvals" in data

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["healthy", "unhealthy"]
        assert "components" in data

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = await client.get("/metrics")

        assert response.status_code == 200
        data = response.json()

        assert data["success"]
        assert "total_requests" in data
        assert "component_metrics" in data

class TestPerformanceBenchmarks:
    """Test suite for Performance Benchmarks (PROMPTS 90-94)."""

    @pytest.fixture
    def cognitive_engine(self):
        """Create cognitive engine for benchmarking."""
        return CognitiveEngine()

    @pytest.mark.asyncio
    async def test_processing_speed(self, cognitive_engine):
        """Test processing speed."""
        import time

        start_time = time.time()

        # Process multiple requests
        requests = [SAMPLE_TEXT] * 10]

        for request_text in requests:
            await cognitive_engine.process(
                request_text=request_text,
                workspace_id=TEST_WORKSPACE_ID,
                user_id=TEST_USER_ID
            )

        end_time = time.time()

        processing_time = (end_time - start_time) * 1000  # Convert to ms
        avg_time = processing_time / len(requests)

        # Benchmark: Should process under 100ms per request on average
        assert avg_time < 100, f"Average processing time: {avg_time:.2f}ms"

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, cognitive_engine):
        """Test concurrent processing."""
        import time

        start_time = time.time()

        # Process multiple requests concurrently
        tasks = []
        for i in range(5):
            task = cognitive_engine.process(
                request_text=f"Request {i+1}",
                workspace_id=TEST_WORKSPACE_ID,
                user_id=TEST_USER_ID
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

        end_time = time.time()

        processing_time = (end_time - start_time) * 1000  # Convert to ms
        avg_time = processing_time / len(tasks)

        # Benchmark: Should handle concurrent requests efficiently
        assert avg_time < 200, f"Average concurrent processing time: {avg_time:.2f}ms"

    @pytest.mark.asyncio
    async def test_memory_usage(self, cognitive_engine):
        """Test memory usage."""
        import gc

        import psutil

        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info.rss

        # Process multiple requests
        for i in range(10):
            await cognitive_engine.process(
                request_text=f"Memory test {i+1}",
                workspace_id=TEST_WORKSPACE_ID,
                user_id=TEST_USER_ID
            )

        # Get final memory usage
        final_memory = process.memory_info.rss
        memory_increase = final_memory - initial_memory

        # Benchmark: Memory increase should be reasonable
        assert memory_increase < 100 * 1024 * 1024, f"Memory increase: {memory_increase} bytes"

    @pytest.mark.asyncio
    async def test_error_recovery(self, cognitive_engine):
        """Test error recovery mechanisms."""
        # Mock error scenario
        with patch.object(cognitive_engine, side_effect=Exception("Test error")):
            result = await cognitive_engine.process(
                request_text=SAMPLE_TEXT,
                workspace_id=TEST_WORKSPACE_ID,
                user_id=TEST_USER_ID
            )

            # Should handle error gracefully
            assert result is not None
            assert result.error is not None

class TestSupportingInfrastructure:
    """Test suite for Supporting Infrastructure (PROMPTS 95-100)."""

    def test_config_loading(self):
        """Test configuration loading."""
        # Test if config files can be loaded
        config_path = os.path.join(os.path.dirname(__file__), "config")
        if os.path.exists(config_path):
            assert os.path.isfile(os.path.join(config_path, "cognitive_config.json"))

    def test_logging_setup(self):
        """Test logging setup."""
        # Test if logging is properly configured
        logger.info("Test logging setup check")
        assert logger.level == logging.INFO

    def test_health_checks(self):
        """Test health check endpoints."""
        # Test if health checks are available
        assert hasattr(app, "router")
        for route in app.router.routes:
            if route.path == "/health":
                return True
        return False

    def test_documentation_availability(self):
        """Test documentation availability."""
        # Test if docs are available
        assert hasattr(app, "docs_url")
        assert app.docs_url is not None

    def test_error_handling(self):
        """Test error handling."""
        # Test if error handlers are registered
        assert hasattr(app, "exception_handlers")
        assert len(app.exception_handlers) > 0

class TestEndToEndVerification:
    """Test suite for End-to-End Verification (PROMPT 100)."""

    @pytest.fixture
    def cognitive_engine(self):
        """Create cognitive engine for E2E testing."""
        return CognitiveEngine()

    @pytest.mark.asyncio
    async def test_full_pipeline_flow(self, cognitive_engine):
        """Test complete pipeline flow."""
        # Test with real data
        real_text = "Create a comprehensive marketing strategy for our new AI-powered analytics platform targeting enterprise customers in the financial services sector with a focus on real-time data processing and advanced visualization capabilities."

        result = await cognitive_engine.process(
            text=real_text,
            workspace_id="e2e_test_workspace",
            user_id="e2e_test_user"
        )

        # Verify complete pipeline
        assert result.status == "completed"
        assert result.cognitive_result is not None

        # Verify all stages executed
        assert result.cognitive_result.perceived_input is not None
        assert result.cognitive_result.execution_plan is not None
        assert result.cognitive_result.reflection_result is not None

        # Verify metrics
        assert result.cognitive_result.total_tokens_used > 0
        assert result.cognitive_result.total_cost_usd >= 0.0
        assert result.cognitive_result.processing_time_seconds > 0

    @pytest.mark.asyncio
    async def test_error_recovery_flow(self, cognitive_engine):
        """Test error recovery in full flow."""
        # Mock error in perception
        with patch.object(perception_module.perceive, side_effect=Exception("Perception error")):
            result = await cognitive_engine.process(
                text="Test error recovery",
                workspace_id="e2e_test_workspace",
                user_id="e2e_test_user"
            )

            # Should handle error gracefully
            assert result is not None
            assert result.error is not None

    @pytest.mark.asyncio
    async def test_approval_workflow(self, cognitive_engine):
        """Test approval workflow integration."""
        # Mock approval requirement
        with patch.object(cognitive_engine, side_effect=lambda: result: CognitiveResult(
                result.requires_approval = True
            )):
                result = await cognitive_engine.process(
                    text="Test approval workflow",
                    workspace_id="e2e_test_workspace",
                    user_id="e2e_test_user"
                )

                # Should trigger approval
                assert result.cognitive_result.requires_approval
                assert result.cognitive_result.approval_gate_id is not None

    @pytest.mark.asyncio
    async def test_quality_metrics(self, cognitive_engine):
        """Test quality metrics collection."""
        # Process multiple requests
        for i in range(5):
            await cognitive_engine.process(
                text=f"Quality test {i+1}",
                workspace_id="e2e_test_workspace",
                user_id="e2e_test_user"
            )

        # Check if metrics are collected
        stats = cognitive_monitor.get_monitoring_stats()
        assert stats["total_requests"] >= 5
        assert "average_processing_time_ms" in stats

    @pytest.mark.asyncio
    async def test_service_integration(self, cognitive_engine):
        """Test service discovery integration."""
        # Test if services are discoverable
        services = service_registry.get_default_instance().get_component_stats()
        assert services["total_services"] >= 0

        # Test if routing works
        rules = rule_engine.get_engine("default").get_rule_stats()
        assert rules["total_rules"] >= 0

# Test configuration
pytest.fixture(scope="session")
def test_database():
    """Setup test database connection."""
    # This would setup test database connection
    pass

@pytest.fixture(scope="session")
def test_cache():
    """Setup test cache."""
    # This would setup test cache
    pass

# Run tests
if __name__name__ == "__main__":
    pytest.main([TestPerceptionModule, TestPlanningModule, TestReflectionModule, TestAdversarialCritic,
                     TestIntegrationComponents, TestProtocolComponents, TestAPIEndpoints,
                     TestPerformanceBenchmarks, TestSupportingInfrastructure, TestEndToEndVerification],
                     database=test_database, cache=test_cache)
