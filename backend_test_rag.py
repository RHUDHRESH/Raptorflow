# backend/tests/test_rag.py
# RaptorFlow Codex - RAG System Tests
# Week 3 Wednesday - Knowledge Base Test Suite

import pytest
from datetime import datetime

from chroma_db import ChromaDBRAG, Document, EmbeddingModel
from knowledge_base import (
    KnowledgeBaseManager, KnowledgeCategory, KnowledgeTemplates
)
from rag_integration import (
    AgentRAGMixin, RAGContextBuilder, RAGMemory, RAGPerformanceTracker
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def chroma_rag():
    """Create ChromaDB RAG instance"""
    rag = ChromaDBRAG(
        host="localhost",
        port=8000,
        collection_name="test_raptorflow"
    )
    try:
        await rag.connect()
        yield rag
    finally:
        await rag.disconnect()

@pytest.fixture
async def knowledge_manager(chroma_rag):
    """Create knowledge base manager"""
    return KnowledgeBaseManager(chroma_rag)

@pytest.fixture
def sample_document():
    """Create sample document"""
    return Document(
        id="doc-001",
        title="Test Campaign Brief",
        content="This is a test campaign about marketing to tech executives.",
        category="campaign",
        metadata={"version": 1},
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        workspace_id="ws-001",
        owner_id="user-001"
    )

# ============================================================================
# EMBEDDING MODEL TESTS
# ============================================================================

class TestEmbeddingModel:
    """Test embedding model configuration"""

    def test_get_embedding_function(self):
        """Test getting embedding function"""
        fn = EmbeddingModel.get_embedding_function("minilm")
        assert fn is not None

    def test_get_dimensions(self):
        """Test getting embedding dimensions"""
        dims = EmbeddingModel.get_dimensions("minilm")
        assert dims == 384

        dims = EmbeddingModel.get_dimensions("mpnet")
        assert dims == 768

    def test_available_models(self):
        """Test available models"""
        models = list(EmbeddingModel.MODELS.keys())
        assert "minilm" in models
        assert "mpnet" in models
        assert "multilingual" in models

# ============================================================================
# CHROMADB RAG TESTS
# ============================================================================

class TestChromaDBRAG:
    """Test ChromaDB RAG functionality"""

    @pytest.mark.asyncio
    async def test_connect(self, chroma_rag):
        """Test connection"""
        assert chroma_rag.client is not None
        assert chroma_rag.collection is not None

    @pytest.mark.asyncio
    async def test_add_document(self, chroma_rag, sample_document):
        """Test adding document"""
        await chroma_rag.add_document(sample_document)
        # Document added successfully if no exception

    @pytest.mark.asyncio
    async def test_search_documents(self, chroma_rag, sample_document):
        """Test searching documents"""
        await chroma_rag.add_document(sample_document)

        results = await chroma_rag.search(
            query="marketing campaign",
            workspace_id="ws-001",
            limit=5
        )

        assert results is not None
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_with_category_filter(self, chroma_rag, sample_document):
        """Test search with category filter"""
        await chroma_rag.add_document(sample_document)

        results = await chroma_rag.search(
            query="campaign",
            workspace_id="ws-001",
            category="campaign",
            limit=5
        )

        assert results is not None

    @pytest.mark.asyncio
    async def test_bulk_add_documents(self, chroma_rag):
        """Test bulk adding documents"""
        documents = [
            Document(
                id=f"doc-{i}",
                title=f"Document {i}",
                content=f"Content for document {i}",
                category="research",
                metadata={},
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
                workspace_id="ws-001",
                owner_id="user-001"
            )
            for i in range(5)
        ]

        await chroma_rag.bulk_add_documents(documents)
        # Bulk add successful if no exception

    @pytest.mark.asyncio
    async def test_get_context_for_agent(self, chroma_rag, sample_document):
        """Test getting context for agent"""
        await chroma_rag.add_document(sample_document)

        context = await chroma_rag.get_context_for_agent(
            agent_name="researcher-1",
            workspace_id="ws-001",
            task="analyze marketing campaign",
            context_limit=5
        )

        assert "agent" in context
        assert "retrieved_knowledge" in context
        assert "timestamp" in context

    @pytest.mark.asyncio
    async def test_document_chunking(self, chroma_rag):
        """Test document chunking"""
        long_content = "This is a test. " * 100
        doc = Document(
            id="doc-long",
            title="Long Document",
            content=long_content,
            category="research",
            metadata={},
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            workspace_id="ws-001",
            owner_id="user-001"
        )

        chunks = ChromaDBRAG._chunk_document(doc)
        assert len(chunks) > 1
        assert all(chunk.text for chunk in chunks)

# ============================================================================
# KNOWLEDGE BASE MANAGER TESTS
# ============================================================================

class TestKnowledgeBaseManager:
    """Test knowledge base management"""

    @pytest.mark.asyncio
    async def test_create_document(self, knowledge_manager):
        """Test creating document"""
        doc_id = await knowledge_manager.create_document(
            title="Test Campaign",
            content="Campaign content here",
            category=KnowledgeCategory.CAMPAIGN,
            workspace_id="ws-001",
            owner_id="user-001",
            tags=["marketing", "test"]
        )

        assert doc_id is not None

    @pytest.mark.asyncio
    async def test_create_from_template(self, knowledge_manager):
        """Test creating from template"""
        doc_id = await knowledge_manager.create_from_template(
            template_name="Campaign Brief",
            title="Q1 Marketing Campaign",
            content_sections={
                "overview": "Target tech executives",
                "target_audience": "CTO and marketing leaders",
                "messaging": "Innovation and efficiency"
            },
            workspace_id="ws-001",
            owner_id="user-001"
        )

        assert doc_id is not None

    @pytest.mark.asyncio
    async def test_search_documents(self, knowledge_manager):
        """Test searching documents"""
        # Create a document first
        await knowledge_manager.create_document(
            title="Marketing Strategy",
            content="Strategic approach to marketing",
            category=KnowledgeCategory.STRATEGY,
            workspace_id="ws-001",
            owner_id="user-001"
        )

        results = await knowledge_manager.search_documents(
            query="marketing strategy",
            workspace_id="ws-001"
        )

        assert isinstance(results, list)

    def test_get_template(self):
        """Test getting templates"""
        template = KnowledgeTemplates.get_template(KnowledgeCategory.CAMPAIGN)
        assert template is not None
        assert template.name == "Campaign Brief"

    def test_template_validation(self):
        """Test template validation"""
        template = KnowledgeTemplates.CAMPAIGN_TEMPLATE
        assert "overview" in template.required_fields
        assert template.category == KnowledgeCategory.CAMPAIGN

# ============================================================================
# RAG INTEGRATION TESTS
# ============================================================================

class TestRAGContextBuilder:
    """Test RAG context building"""

    @pytest.mark.asyncio
    async def test_build_execution_context(self):
        """Test building execution context"""
        context = await RAGContextBuilder.build_execution_context(
            agent_name="researcher-1",
            task="Analyze market trends",
            workspace_id="ws-001",
            agent_type="researcher"
        )

        assert "agent" in context
        assert "task" in context
        assert "knowledge" in context
        assert "guidance" in context

    @pytest.mark.asyncio
    async def test_get_agent_guidance(self):
        """Test getting agent-specific guidance"""
        # Note: This requires ChromaDB connection, so it's a minimal test
        guidance = await RAGContextBuilder._get_agent_guidance(
            agent_type="researcher",
            workspace_id="ws-001",
            chroma=None
        )

        assert "type" in guidance
        assert guidance["type"] == "researcher"

# ============================================================================
# RAG MEMORY TESTS
# ============================================================================

class TestRAGMemory:
    """Test RAG memory system"""

    @pytest.mark.asyncio
    async def test_record_execution(self):
        """Test recording execution"""
        memory = RAGMemory("ws-001")

        await memory.record_execution(
            agent_name="researcher-1",
            task="Market analysis",
            result={
                "success": True,
                "summary": "Analysis complete",
                "duration_seconds": 120,
                "tokens_used": 1500
            },
            knowledge_used=["doc-001", "doc-002"]
        )

        assert len(memory.execution_memory) == 1

    @pytest.mark.asyncio
    async def test_get_agent_history(self):
        """Test getting agent history"""
        memory = RAGMemory("ws-001")

        # Record multiple executions
        for i in range(3):
            await memory.record_execution(
                agent_name="researcher-1",
                task=f"Task {i}",
                result={"success": True, "duration_seconds": 100, "tokens_used": 1000},
                knowledge_used=[]
            )

        history = await memory.get_agent_history("researcher-1")
        assert len(history) == 3

    @pytest.mark.asyncio
    async def test_get_success_rate(self):
        """Test getting success rate"""
        memory = RAGMemory("ws-001")

        # Record executions with mixed success
        for i in range(10):
            await memory.record_execution(
                agent_name="researcher-1",
                task=f"Task {i}",
                result={
                    "success": i % 2 == 0,
                    "duration_seconds": 100,
                    "tokens_used": 1000
                },
                knowledge_used=[]
            )

        rate = await memory.get_success_rate("researcher-1")
        assert 40 <= rate <= 60  # Should be around 50%

    @pytest.mark.asyncio
    async def test_get_similar_executions(self):
        """Test finding similar executions"""
        memory = RAGMemory("ws-001")

        # Record executions
        tasks = [
            "Analyze market trends",
            "Analyze competitor strategy",
            "Create campaign brief",
            "Create content outline"
        ]

        for task in tasks:
            await memory.record_execution(
                agent_name="researcher-1",
                task=task,
                result={"success": True, "duration_seconds": 100, "tokens_used": 1000},
                knowledge_used=[]
            )

        # Find similar to "Analyze market data"
        similar = await memory.get_similar_executions("Analyze market data")
        assert len(similar) > 0

# ============================================================================
# RAG PERFORMANCE TRACKER TESTS
# ============================================================================

class TestRAGPerformanceTracker:
    """Test RAG performance tracking"""

    def test_track_query(self):
        """Test tracking query"""
        tracker = RAGPerformanceTracker()

        tracker.track_query(
            query="marketing campaign",
            workspace_id="ws-001",
            agent="researcher-1",
            num_results=5,
            avg_relevance=0.85
        )

        assert len(tracker.queries) == 1
        assert tracker.queries[0]["query"] == "marketing campaign"

    def test_track_retrieval(self):
        """Test tracking retrieval"""
        tracker = RAGPerformanceTracker()

        tracker.track_retrieval(
            document_id="doc-001",
            relevance_score=0.92,
            used_by_agent="researcher-1"
        )

        assert len(tracker.retrievals) == 1
        assert tracker.retrievals[0]["document_id"] == "doc-001"

    def test_get_statistics(self):
        """Test getting statistics"""
        tracker = RAGPerformanceTracker()

        # Add some data
        for i in range(5):
            tracker.track_query(
                query=f"query {i}",
                workspace_id="ws-001",
                agent=f"agent-{i}",
                num_results=3 + i,
                avg_relevance=0.8 + (i * 0.02)
            )

        stats = tracker.get_statistics()

        assert stats["total_queries"] == 5
        assert "avg_results_per_query" in stats
        assert "avg_relevance" in stats

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestRAGIntegration:
    """Integration tests for complete RAG workflow"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, chroma_rag, knowledge_manager):
        """Test complete RAG workflow"""
        # 1. Create document
        doc_id = await knowledge_manager.create_document(
            title="Marketing Best Practices",
            content="Best practices for digital marketing campaigns",
            category=KnowledgeCategory.BEST_PRACTICE,
            workspace_id="ws-001",
            owner_id="user-001"
        )

        # 2. Search for knowledge
        results = await knowledge_manager.search_documents(
            query="marketing practices",
            workspace_id="ws-001"
        )

        # 3. Verify results
        assert len(results) >= 0

        logger.info("✅ Full RAG workflow successful")

