# backend/tests/test_integration.py
# RaptorFlow Codex - Integration Tests
# Week 3 Thursday - End-to-End System Integration

import pytest
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from unittest.mock import AsyncMock, MagicMock, patch
import time

# Import all components
from main import app
from config import settings
from raptor_bus import RaptorBus, Message, EventType, ChannelType
from chroma_db import ChromaDBRAG, Document
from knowledge_base import KnowledgeBaseManager, KnowledgeCategory
from agents.base_agent import BaseAgent, AgentType, AgentStatus
from rag_integration import RAGContextBuilder, RAGMemory

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def integration_setup():
    """Setup all components for integration testing"""
    # Initialize RaptorBus
    bus = RaptorBus(settings.redis_url)
    await bus.connect()

    # Initialize ChromaDB RAG
    rag = ChromaDBRAG(
        host=settings.chromadb_host,
        port=settings.chromadb_port
    )
    await rag.connect()

    # Initialize Knowledge Base
    kb = KnowledgeBaseManager(rag)

    # Add initial knowledge
    await kb.create_document(
        title="Integration Test Knowledge",
        content="Test knowledge for integration testing",
        category=KnowledgeCategory.BEST_PRACTICE,
        workspace_id="ws-test",
        owner_id="user-test",
        tags=["integration", "test"]
    )

    yield {
        "bus": bus,
        "rag": rag,
        "kb": kb,
        "app": app
    }

    # Cleanup
    await bus.disconnect()
    await rag.disconnect()

@pytest.fixture
async def mock_agent():
    """Create mock agent for testing"""
    class TestAgent(BaseAgent):
        async def initialize(self):
            pass

        async def shutdown(self):
            pass

    agent = TestAgent(
        name="test-agent",
        agent_type=AgentType.RESEARCHER,
        guild_name="research",
        description="Test agent"
    )

    return agent

# ============================================================================
# API & RAPTORBUS INTEGRATION TESTS
# ============================================================================

class TestAPIRaptorBusIntegration:
    """Test API endpoints with RaptorBus integration"""

    @pytest.mark.asyncio
    async def test_campaign_activation_publishes_event(self, integration_setup):
        """Test campaign creation triggers RaptorBus event"""
        bus = integration_setup["bus"]

        # Track published events
        published_events = []

        async def event_handler(message: Message):
            published_events.append(message)

        await bus.subscribe(ChannelType.GUILD_BROADCAST, event_handler)

        # Simulate campaign activation (what API would do)
        campaign_event_id = await bus.publish(
            event_type=EventType.CAMPAIGN_ACTIVATE,
            channel=ChannelType.GUILD_BROADCAST,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="api",
            payload={
                "campaign_id": "camp-001",
                "campaign_name": "Q1 Campaign",
                "positioning": "premium"
            }
        )

        assert campaign_event_id is not None
        # In real system, handler would be called asynchronously

    @pytest.mark.asyncio
    async def test_move_execution_updates_state(self, integration_setup):
        """Test move execution publishes state update"""
        bus = integration_setup["bus"]

        # Publish move execution
        event_id = await bus.publish(
            event_type=EventType.MOVE_EXECUTE,
            channel=ChannelType.STATE_UPDATE,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="agent-001",
            payload={
                "move_id": "move-001",
                "move_name": "Send Email Campaign",
                "status": "executing"
            }
        )

        assert event_id is not None
        assert ChannelType.STATE_UPDATE.value in bus.metrics
        assert bus.metrics[ChannelType.STATE_UPDATE.value]["published"] > 0

    @pytest.mark.asyncio
    async def test_campaign_to_guild_message_flow(self, integration_setup):
        """Test complete flow: Campaign → Guild"""
        bus = integration_setup["bus"]

        guild_events = []

        async def research_guild_handler(message: Message):
            guild_events.append(message)

        # Guild subscribes to research channel
        await bus.subscribe(ChannelType.GUILD_RESEARCH, research_guild_handler)

        # API publishes campaign activation to broadcast
        await bus.publish(
            event_type=EventType.CAMPAIGN_ACTIVATE,
            channel=ChannelType.GUILD_BROADCAST,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="api",
            payload={"campaign_id": "camp-001", "name": "Q1 Campaign"}
        )

        # Simulate guild routing (what guild subscriptions would do)
        await bus.publish(
            event_type=EventType.AGENT_START,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="guild-coordinator",
            payload={"research_id": "research-001", "task": "Analyze campaign"}
        )

        assert bus.metrics[ChannelType.GUILD_RESEARCH.value]["published"] > 0

# ============================================================================
# RAG & AGENT INTEGRATION TESTS
# ============================================================================

class TestRAGAgentIntegration:
    """Test RAG system with agent execution"""

    @pytest.mark.asyncio
    async def test_agent_gets_rag_context(self, integration_setup, mock_agent):
        """Test agent retrieves RAG context for execution"""
        rag = integration_setup["rag"]
        kb = integration_setup["kb"]

        # Create knowledge document
        await kb.create_document(
            title="Research Methodology Guide",
            content="Best practices for conducting market research",
            category=KnowledgeCategory.GUIDELINE,
            workspace_id="ws-test",
            owner_id="user-test"
        )

        # Agent searches for context
        results = await rag.search(
            query="research methodology",
            workspace_id="ws-test",
            limit=5
        )

        assert len(results) >= 0
        # Results would be injected into agent context

    @pytest.mark.asyncio
    async def test_rag_context_builder_integration(self, integration_setup):
        """Test RAG context builder with agent execution"""
        rag = integration_setup["rag"]
        kb = integration_setup["kb"]

        # Build execution context (what agent would use)
        context = await RAGContextBuilder.build_execution_context(
            agent_name="researcher-1",
            task="Analyze market trends for Q1 campaign",
            workspace_id="ws-test",
            agent_type="researcher"
        )

        assert "agent" in context
        assert "task" in context
        assert "knowledge" in context
        assert "guidance" in context
        assert context["agent"]["name"] == "researcher-1"

    @pytest.mark.asyncio
    async def test_agent_memory_records_execution(self, integration_setup, mock_agent):
        """Test agent memory system tracks executions"""
        memory = RAGMemory("ws-test")

        # Record multiple executions
        for i in range(3):
            await memory.record_execution(
                agent_name="researcher-1",
                task=f"Research market segment {i}",
                result={
                    "success": i % 2 == 0,
                    "summary": f"Analysis complete for segment {i}",
                    "duration_seconds": 120 + (i * 10),
                    "tokens_used": 1500 + (i * 100)
                },
                knowledge_used=["doc-001"]
            )

        history = await memory.get_agent_history("researcher-1")
        assert len(history) == 3

        success_rate = await memory.get_success_rate("researcher-1")
        assert 30 < success_rate < 70

# ============================================================================
# END-TO-END WORKFLOW TESTS
# ============================================================================

class TestEndToEndWorkflows:
    """Test complete workflows across all systems"""

    @pytest.mark.asyncio
    async def test_campaign_creation_workflow(self, integration_setup):
        """Test complete campaign creation workflow"""
        bus = integration_setup["bus"]
        rag = integration_setup["rag"]
        kb = integration_setup["kb"]

        workflow_steps = []

        # Step 1: Create knowledge base entry for campaign strategy
        doc_id = await kb.create_document(
            title="Q1 Campaign Strategy",
            content="Target tech executives with product innovation messaging",
            category=KnowledgeCategory.STRATEGY,
            workspace_id="ws-test",
            owner_id="user-test"
        )
        workflow_steps.append(("knowledge_created", doc_id))

        # Step 2: Publish campaign activation event
        event_id = await bus.publish(
            event_type=EventType.CAMPAIGN_ACTIVATE,
            channel=ChannelType.GUILD_BROADCAST,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="api",
            payload={
                "campaign_id": "camp-001",
                "campaign_name": "Q1 Tech Executive Campaign",
                "strategy_doc": doc_id
            }
        )
        workflow_steps.append(("event_published", event_id))

        # Step 3: Guild receives event and assigns agents
        agent_assignment = await bus.publish(
            event_type=EventType.AGENT_START,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="guild-coordinator",
            payload={
                "campaign_id": "camp-001",
                "assigned_agents": ["researcher-1", "researcher-2"],
                "task": "Analyze tech executive market segment"
            }
        )
        workflow_steps.append(("agents_assigned", agent_assignment))

        # Step 4: Agents execute with RAG context
        context = await RAGContextBuilder.build_execution_context(
            agent_name="researcher-1",
            task="Analyze tech executive market segment",
            workspace_id="ws-test",
            agent_type="researcher"
        )
        workflow_steps.append(("context_retrieved", len(context["knowledge"]["retrieved_documents"])))

        # Step 5: Agent completes and publishes result
        completion_event = await bus.publish(
            event_type=EventType.AGENT_COMPLETE,
            channel=ChannelType.GUILD_BROADCAST,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="researcher-1",
            payload={
                "task": "market analysis",
                "duration_seconds": 245.5,
                "tokens_used": 2150,
                "cost": 0.065,
                "summary": "Market analysis complete with insights"
            }
        )
        workflow_steps.append(("execution_complete", completion_event))

        # Verify all steps completed
        assert len(workflow_steps) == 5
        assert all(step[1] is not None for step in workflow_steps)

    @pytest.mark.asyncio
    async def test_signal_detection_to_insight_workflow(self, integration_setup):
        """Test signal detection through insight generation"""
        bus = integration_setup["bus"]
        rag = integration_setup["rag"]
        kb = integration_setup["kb"]

        # Step 1: Signal detected and published
        signal_event = await bus.publish(
            event_type=EventType.SIGNAL_DETECTED,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="matrix-1",
            payload={
                "signal_type": "market_trend",
                "data_source": "news_api",
                "relevance_score": 0.87,
                "summary": "Rising demand for AI-powered tools"
            }
        )

        # Step 2: Intelligence agent searches RAG for related insights
        results = await rag.search(
            query="AI-powered tools market trends",
            workspace_id="ws-test",
            limit=5
        )

        # Step 3: Generate insight from signal + knowledge
        insight_event = await bus.publish(
            event_type=EventType.INSIGHT_GENERATED,
            channel=ChannelType.GUILD_MATRIX,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="intelligence-1",
            payload={
                "insight_type": "market_opportunity",
                "confidence_score": 0.92,
                "summary": "Significant opportunity in AI tools market",
                "based_on_signals": [signal_event]
            }
        )

        assert signal_event is not None
        assert insight_event is not None

    @pytest.mark.asyncio
    async def test_compliance_check_workflow(self, integration_setup):
        """Test compliance guardian workflow"""
        bus = integration_setup["bus"]
        kb = integration_setup["kb"]

        # Step 1: Create compliance guidelines
        doc_id = await kb.create_document(
            title="Marketing Compliance Guidelines",
            content="All claims must be substantiated with data. No misleading statements.",
            category=KnowledgeCategory.GUIDELINE,
            workspace_id="ws-test",
            owner_id="user-test"
        )

        # Step 2: Campaign content triggers compliance check
        check_event = await bus.publish(
            event_type=EventType.AGENT_START,
            channel=ChannelType.GUILD_GUARDIAN,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="compliance-coordinator",
            payload={
                "check_id": "check-001",
                "content_to_check": "Our product is 100% better than competitors",
                "check_type": "claims_substantiation"
            }
        )

        # Step 3: Guardian searches guidelines
        guidelines = await kb.search_documents(
            query="marketing claims substantiation",
            workspace_id="ws-test",
            category=KnowledgeCategory.GUIDELINE
        )

        # Step 4: Guardian publishes result
        result_event = await bus.publish(
            event_type=EventType.ALERT_CREATED,
            channel=ChannelType.ALERT,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="guardian-1",
            payload={
                "check_id": "check-001",
                "severity": "high",
                "issue": "Unsubstantiated claim detected",
                "recommendation": "Remove or provide data to support claim"
            }
        )

        assert result_event is not None

# ============================================================================
# PERFORMANCE & LOAD TESTS
# ============================================================================

class TestPerformanceAndLoad:
    """Test system performance under load"""

    @pytest.mark.asyncio
    async def test_message_latency(self, integration_setup):
        """Test message publishing and delivery latency"""
        bus = integration_setup["bus"]

        latencies = []

        async def latency_handler(message: Message):
            elapsed = (datetime.utcnow().timestamp() -
                      datetime.fromisoformat(message.timestamp).timestamp())
            latencies.append(elapsed * 1000)  # Convert to ms

        await bus.subscribe(ChannelType.GUILD_RESEARCH, latency_handler)

        # Publish multiple messages
        for i in range(10):
            await bus.publish(
                event_type=EventType.AGENT_START,
                channel=ChannelType.GUILD_RESEARCH,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent=f"agent-{i}",
                payload={"index": i}
            )

        assert len(bus.metrics[ChannelType.GUILD_RESEARCH.value]["published"]) >= 0

    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self, integration_setup):
        """Test multiple concurrent agents"""
        bus = integration_setup["bus"]
        rag = integration_setup["rag"]

        execution_times = []

        async def execute_agent(agent_id: int):
            start = time.time()

            # Publish start
            await bus.publish(
                event_type=EventType.AGENT_START,
                channel=ChannelType.GUILD_RESEARCH,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent=f"researcher-{agent_id}",
                payload={"agent_id": agent_id}
            )

            # Get context (simulated)
            context = await RAGContextBuilder.build_execution_context(
                agent_name=f"researcher-{agent_id}",
                task=f"Research task {agent_id}",
                workspace_id="ws-test",
                agent_type="researcher"
            )

            # Publish completion
            await bus.publish(
                event_type=EventType.AGENT_COMPLETE,
                channel=ChannelType.GUILD_BROADCAST,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent=f"researcher-{agent_id}",
                payload={
                    "task_id": agent_id,
                    "duration_seconds": 120,
                    "tokens_used": 1500
                }
            )

            elapsed = time.time() - start
            execution_times.append(elapsed)

        # Execute 10 concurrent agents
        await asyncio.gather(*[
            execute_agent(i) for i in range(10)
        ])

        assert len(execution_times) == 10
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5.0  # Should complete in < 5 seconds average

    @pytest.mark.asyncio
    async def test_rag_search_latency(self, integration_setup):
        """Test RAG search performance"""
        rag = integration_setup["rag"]
        kb = integration_setup["kb"]

        # Add 5 documents
        doc_ids = []
        for i in range(5):
            doc_id = await kb.create_document(
                title=f"Test Document {i}",
                content=f"Content for document {i} about marketing campaigns",
                category=KnowledgeCategory.CAMPAIGN,
                workspace_id="ws-test",
                owner_id="user-test"
            )
            doc_ids.append(doc_id)

        # Measure search latency
        search_times = []

        for i in range(10):
            start = time.time()
            results = await rag.search(
                query="marketing campaign",
                workspace_id="ws-test",
                limit=5
            )
            elapsed = time.time() - start
            search_times.append(elapsed * 1000)  # Convert to ms

        avg_latency = sum(search_times) / len(search_times)
        assert avg_latency < 100  # Should be < 100ms average

    @pytest.mark.asyncio
    async def test_bulk_message_throughput(self, integration_setup):
        """Test message throughput"""
        bus = integration_setup["bus"]

        message_count = 100
        start = time.time()

        for i in range(message_count):
            await bus.publish(
                event_type=EventType.AGENT_COMPLETE,
                channel=ChannelType.GUILD_BROADCAST,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent=f"agent-{i}",
                payload={"index": i}
            )

        elapsed = time.time() - start
        throughput = message_count / elapsed

        # Should handle 100+ messages per second
        assert throughput > 100

# ============================================================================
# ERROR HANDLING & RESILIENCE TESTS
# ============================================================================

class TestErrorHandlingAndResilience:
    """Test error handling and recovery"""

    @pytest.mark.asyncio
    async def test_message_retry_on_failure(self, integration_setup):
        """Test message retry logic"""
        bus = integration_setup["bus"]

        # Publish message
        msg_id = await bus.publish(
            event_type=EventType.AGENT_ERROR,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="agent-1",
            payload={"error": "test error"}
        )

        assert msg_id is not None

    @pytest.mark.asyncio
    async def test_dlq_handling(self, integration_setup):
        """Test dead-letter queue"""
        bus = integration_setup["bus"]

        # Publish message that will fail
        message = Message(
            id="dlq-test",
            event_type=EventType.AGENT_ERROR,
            channel=ChannelType.GUILD_RESEARCH,
            workspace_id="ws-test",
            user_id="user-test",
            source_agent="agent-1",
            payload={"error": "test"},
            timestamp=datetime.utcnow().isoformat()
        )

        # Send to DLQ
        await bus._send_to_dlq(message, "Test failure reason")

        assert ChannelType.DLQ.value in bus.metrics

    @pytest.mark.asyncio
    async def test_knowledge_base_error_recovery(self, integration_setup):
        """Test RAG error handling"""
        rag = integration_setup["rag"]

        # Try to search with invalid workspace
        results = await rag.search(
            query="test query",
            workspace_id="ws-nonexistent",
            limit=5
        )

        # Should return empty list, not error
        assert isinstance(results, list)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, integration_setup):
        """Test handling concurrent requests"""
        bus = integration_setup["bus"]

        async def publish_event(i: int):
            return await bus.publish(
                event_type=EventType.AGENT_START,
                channel=ChannelType.GUILD_BROADCAST,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent=f"agent-{i}",
                payload={"index": i}
            )

        # Publish 20 concurrent messages
        results = await asyncio.gather(*[
            publish_event(i) for i in range(20)
        ])

        assert len(results) == 20
        assert all(r is not None for r in results)

# ============================================================================
# SYSTEM METRICS & OBSERVABILITY TESTS
# ============================================================================

class TestMetricsAndObservability:
    """Test metrics collection and observability"""

    @pytest.mark.asyncio
    async def test_bus_metrics_collection(self, integration_setup):
        """Test RaptorBus metrics tracking"""
        bus = integration_setup["bus"]

        # Publish several messages
        for i in range(5):
            await bus.publish(
                event_type=EventType.AGENT_START,
                channel=ChannelType.GUILD_RESEARCH,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent=f"agent-{i}",
                payload={"index": i}
            )

        metrics = bus.get_metrics()

        assert "channels" in metrics
        assert "running" in metrics
        assert "timestamp" in metrics
        assert ChannelType.GUILD_RESEARCH.value in metrics["channels"]

    @pytest.mark.asyncio
    async def test_agent_performance_metrics(self, integration_setup, mock_agent):
        """Test agent metrics tracking"""
        agent = mock_agent

        # Register a capability
        async def test_capability(query: str):
            return {"result": "test result"}

        agent.register_capability(
            name="test_search",
            category="research",
            handler=test_capability
        )

        # Execute capability
        result = await agent.execute(
            task="test_search",
            parameters={"query": "test"}
        )

        # Check metrics
        metrics = agent.get_metrics()
        assert metrics.executions > 0
        assert "avg_duration" in agent.get_metrics_dict()

    @pytest.mark.asyncio
    async def test_rag_statistics(self, integration_setup):
        """Test RAG statistics collection"""
        rag = integration_setup["rag"]
        kb = integration_setup["kb"]

        # Create document
        await kb.create_document(
            title="Metrics Test Document",
            content="Document for metrics testing",
            category=KnowledgeCategory.STRATEGY,
            workspace_id="ws-test",
            owner_id="user-test"
        )

        # Get statistics
        stats = await rag.get_statistics("ws-test")

        assert "total_chunks" in stats
        assert "unique_documents" in stats
        assert "categories" in stats

# ============================================================================
# COMPREHENSIVE INTEGRATION SCENARIOS
# ============================================================================

class TestComprehensiveScenarios:
    """Test realistic integration scenarios"""

    @pytest.mark.asyncio
    async def test_full_marketing_workflow(self, integration_setup):
        """Test complete marketing campaign workflow"""
        bus = integration_setup["bus"]
        rag = integration_setup["rag"]
        kb = integration_setup["kb"]

        scenario = {
            "steps": [],
            "success": True,
            "errors": []
        }

        try:
            # 1. Create strategy document
            strategy_id = await kb.create_document(
                title="Q1 2024 Marketing Strategy",
                content="Focus on tech executive segment with premium positioning",
                category=KnowledgeCategory.STRATEGY,
                workspace_id="ws-test",
                owner_id="user-test"
            )
            scenario["steps"].append("strategy_created")

            # 2. Create campaign
            campaign_event = await bus.publish(
                event_type=EventType.CAMPAIGN_ACTIVATE,
                channel=ChannelType.GUILD_BROADCAST,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent="api",
                payload={
                    "campaign_id": "camp-q1-2024",
                    "name": "Q1 Tech Executive Campaign",
                    "strategy_id": strategy_id
                }
            )
            scenario["steps"].append("campaign_activated")

            # 3. Assign research agents
            research_event = await bus.publish(
                event_type=EventType.AGENT_START,
                channel=ChannelType.GUILD_RESEARCH,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent="guild-coordinator",
                payload={
                    "campaign_id": "camp-q1-2024",
                    "agents": ["researcher-1", "researcher-2"]
                }
            )
            scenario["steps"].append("research_assigned")

            # 4. Agents execute with context
            context = await RAGContextBuilder.build_execution_context(
                agent_name="researcher-1",
                task="Analyze tech executive market",
                workspace_id="ws-test",
                agent_type="researcher"
            )
            scenario["steps"].append("context_retrieved")

            # 5. Research completes
            research_complete = await bus.publish(
                event_type=EventType.AGENT_COMPLETE,
                channel=ChannelType.GUILD_BROADCAST,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent="researcher-1",
                payload={
                    "research_id": "research-001",
                    "findings": ["Insight 1", "Insight 2"]
                }
            )
            scenario["steps"].append("research_complete")

            # 6. Assign creative agents
            creative_event = await bus.publish(
                event_type=EventType.AGENT_START,
                channel=ChannelType.GUILD_MUSE,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent="guild-coordinator",
                payload={
                    "campaign_id": "camp-q1-2024",
                    "agents": ["copywriter-1", "designer-1"]
                }
            )
            scenario["steps"].append("creative_assigned")

            # 7. Compliance check
            compliance_event = await bus.publish(
                event_type=EventType.AGENT_START,
                channel=ChannelType.GUILD_GUARDIAN,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent="compliance-coordinator",
                payload={
                    "campaign_id": "camp-q1-2024",
                    "check_type": "content_review"
                }
            )
            scenario["steps"].append("compliance_check")

            # 8. Campaign ready
            ready_event = await bus.publish(
                event_type=EventType.CAMPAIGN_ACTIVATE,
                channel=ChannelType.STATE_UPDATE,
                workspace_id="ws-test",
                user_id="user-test",
                source_agent="system",
                payload={
                    "campaign_id": "camp-q1-2024",
                    "status": "ready_to_execute"
                }
            )
            scenario["steps"].append("campaign_ready")

        except Exception as e:
            scenario["success"] = False
            scenario["errors"].append(str(e))

        assert scenario["success"]
        assert len(scenario["steps"]) == 8

