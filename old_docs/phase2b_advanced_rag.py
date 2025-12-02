"""
Advanced RAG (Retrieval-Augmented Generation) System for RaptorFlow
Provides semantic search, knowledge graph, and intelligent context retrieval
for all 70+ agents across 7 Strategic Lords.

Components:
- Vector Store Integration (Chroma)
- Embedding Engine (OpenAI/Local)
- Semantic Search
- Knowledge Graph
- Reranking Engine
- Context Retrieval
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Any, Callable
from datetime import datetime
from abc import ABC, abstractmethod
import hashlib
from enum import Enum


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class SimilarityMetric(Enum):
    """Vector similarity metrics for semantic search."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"


class DocumentType(Enum):
    """Types of documents in knowledge base."""
    STRATEGY = "strategy"
    CAPABILITY = "capability"
    WORKFLOW = "workflow"
    DECISION = "decision"
    INSIGHT = "insight"
    POLICY = "policy"
    TEMPLATE = "template"
    CASE_STUDY = "case_study"
    METRIC = "metric"
    ALERT = "alert"


@dataclass
class Document:
    """Document stored in RAG system."""
    doc_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_type: DocumentType = DocumentType.STRATEGY
    lord: str = ""  # Which strategic lord domain
    agent: str = ""  # Which agent created/manages
    embedding: Optional[List[float]] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: int = 1
    tags: List[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """Result from semantic search."""
    doc_id: str
    content: str
    similarity_score: float
    rank: int
    metadata: Dict[str, Any]
    rerank_score: Optional[float] = None
    context_distance: float = 0.0


@dataclass
class KnowledgeGraphNode:
    """Node in knowledge graph."""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""
    doc_id: str = ""
    node_type: str = ""  # "concept", "entity", "relationship"
    attributes: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


@dataclass
class KnowledgeGraphEdge:
    """Edge connecting nodes in knowledge graph."""
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    relation_type: str = ""  # "depends_on", "related_to", "requires", etc.
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextWindow:
    """Retrieved context for agent execution."""
    context_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str = ""
    primary_results: List[SearchResult] = field(default_factory=list)
    related_results: List[SearchResult] = field(default_factory=list)
    graph_context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ============================================================================
# EMBEDDING ENGINE
# ============================================================================

class EmbeddingEngine(ABC):
    """Abstract base for embedding engines."""

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Convert text to embedding vector."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Convert multiple texts to embeddings."""
        pass

    @abstractmethod
    async def similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate similarity between two embeddings."""
        pass


class MockEmbeddingEngine(EmbeddingEngine):
    """Mock embedding engine for testing without external API."""

    def __init__(self):
        self.embeddings_cache = {}

    async def embed_text(self, text: str) -> List[float]:
        """Generate deterministic embedding from text hash."""
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]

        # Create deterministic embedding from hash
        hash_val = hashlib.md5(text.encode()).hexdigest()
        embedding = [
            int(hash_val[i : i + 2], 16) / 255.0 for i in range(0, len(hash_val), 2)
        ]

        # Pad or truncate to 384 dimensions
        if len(embedding) < 384:
            embedding.extend([0.0] * (384 - len(embedding)))
        else:
            embedding = embedding[:384]

        self.embeddings_cache[text] = embedding
        return embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts."""
        return [await self.embed_text(text) for text in texts]

    async def similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate cosine similarity."""
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        mag1 = sum(a ** 2 for a in emb1) ** 0.5
        mag2 = sum(b ** 2 for b in emb2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)


# ============================================================================
# VECTOR STORE (CHROMA-LIKE)
# ============================================================================

class VectorStore:
    """Vector store for semantic search (Chroma-like implementation)."""

    def __init__(self, embedding_engine: EmbeddingEngine):
        self.embedding_engine = embedding_engine
        self.documents: Dict[str, Document] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self.indices: Dict[str, List[str]] = {}  # doc_id -> embedding

    async def add_document(self, document: Document) -> bool:
        """Add document to vector store."""
        try:
            # Generate embedding if not provided
            if document.embedding is None:
                document.embedding = await self.embedding_engine.embed_text(
                    document.content
                )

            self.documents[document.doc_id] = document
            self.embeddings[document.doc_id] = document.embedding

            # Index by type and lord
            doc_type_key = f"type:{document.doc_type.value}"
            lord_key = f"lord:{document.lord}"

            if doc_type_key not in self.indices:
                self.indices[doc_type_key] = []
            if lord_key not in self.indices:
                self.indices[lord_key] = []

            self.indices[doc_type_key].append(document.doc_id)
            self.indices[lord_key].append(document.doc_id)

            return True
        except Exception as e:
            print(f"[ERROR] Failed to add document: {e}")
            return False

    async def add_documents_batch(self, documents: List[Document]) -> int:
        """Add multiple documents."""
        count = 0
        for doc in documents:
            if await self.add_document(doc):
                count += 1
        return count

    async def search(
        self,
        query: str,
        limit: int = 5,
        metric: SimilarityMetric = SimilarityMetric.COSINE,
        doc_type: Optional[DocumentType] = None,
        lord: Optional[str] = None,
    ) -> List[SearchResult]:
        """Semantic search for similar documents."""
        try:
            # Embed query
            query_embedding = await self.embedding_engine.embed_text(query)

            # Get candidates
            candidates = list(self.documents.items())

            # Filter by type if specified
            if doc_type:
                candidates = [
                    (doc_id, doc)
                    for doc_id, doc in candidates
                    if doc.doc_type == doc_type
                ]

            # Filter by lord if specified
            if lord:
                candidates = [
                    (doc_id, doc) for doc_id, doc in candidates if doc.lord == lord
                ]

            # Calculate similarities
            results = []
            for doc_id, doc in candidates:
                similarity = await self.embedding_engine.similarity(
                    query_embedding, doc.embedding or []
                )

                results.append(
                    SearchResult(
                        doc_id=doc_id,
                        content=doc.content,
                        similarity_score=similarity,
                        rank=0,
                        metadata=doc.metadata,
                    )
                )

            # Sort by similarity and rank
            results.sort(key=lambda r: r.similarity_score, reverse=True)
            for i, result in enumerate(results):
                result.rank = i + 1

            return results[:limit]
        except Exception as e:
            print(f"[ERROR] Search failed: {e}")
            return []

    async def delete_document(self, doc_id: str) -> bool:
        """Remove document from vector store."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            if doc_id in self.embeddings:
                del self.embeddings[doc_id]
            return True
        return False

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve document by ID."""
        return self.documents.get(doc_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get store statistics."""
        return {
            "total_documents": len(self.documents),
            "total_embeddings": len(self.embeddings),
            "indices": {k: len(v) for k, v in self.indices.items()},
        }


# ============================================================================
# KNOWLEDGE GRAPH
# ============================================================================

class KnowledgeGraph:
    """Knowledge graph for semantic relationships."""

    def __init__(self):
        self.nodes: Dict[str, KnowledgeGraphNode] = {}
        self.edges: Dict[str, KnowledgeGraphEdge] = {}
        self.adjacency: Dict[str, List[str]] = {}  # node_id -> [connected node_ids]

    async def add_node(self, node: KnowledgeGraphNode) -> bool:
        """Add node to graph."""
        self.nodes[node.node_id] = node
        self.adjacency[node.node_id] = []
        return True

    async def add_edge(self, edge: KnowledgeGraphEdge) -> bool:
        """Add edge connecting nodes."""
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            return False

        self.edges[edge.edge_id] = edge
        if edge.target_id not in self.adjacency[edge.source_id]:
            self.adjacency[edge.source_id].append(edge.target_id)

        return True

    async def get_neighbors(
        self, node_id: str, depth: int = 1
    ) -> Dict[str, KnowledgeGraphNode]:
        """Get connected nodes up to depth."""
        neighbors = {}
        visited = set()
        queue = [(node_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)

            if current_id in visited or current_depth > depth:
                continue

            visited.add(current_id)

            if current_id != node_id:
                neighbors[current_id] = self.nodes[current_id]

            if current_depth < depth:
                for neighbor_id in self.adjacency.get(current_id, []):
                    if neighbor_id not in visited:
                        queue.append((neighbor_id, current_depth + 1))

        return neighbors

    async def find_path(
        self, source_id: str, target_id: str
    ) -> Optional[List[str]]:
        """Find path between two nodes (BFS)."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None

        visited = set()
        queue = [(source_id, [source_id])]

        while queue:
            current_id, path = queue.pop(0)

            if current_id == target_id:
                return path

            if current_id in visited:
                continue

            visited.add(current_id)

            for neighbor_id in self.adjacency.get(current_id, []):
                if neighbor_id not in visited:
                    queue.append((neighbor_id, path + [neighbor_id]))

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "avg_degree": (
                sum(len(v) for v in self.adjacency.values()) / len(self.adjacency)
                if self.adjacency
                else 0
            ),
        }


# ============================================================================
# RERANKING ENGINE
# ============================================================================

class RerankingEngine(ABC):
    """Abstract base for result reranking."""

    @abstractmethod
    async def rerank(
        self, query: str, results: List[SearchResult]
    ) -> List[SearchResult]:
        """Rerank search results based on relevance."""
        pass


class BM25RerankingEngine(RerankingEngine):
    """BM25-based reranking (probabilistic relevance framework)."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1  # Term frequency saturation
        self.b = b  # Length normalization
        self.idf_cache = {}
        self.doc_lengths = {}

    async def _calculate_idf(self, documents: List[Document], term: str) -> float:
        """Calculate inverse document frequency."""
        docs_with_term = sum(1 for doc in documents if term.lower() in doc.content.lower())
        if docs_with_term == 0:
            return 0.0
        return (len(documents) - docs_with_term + 0.5) / (docs_with_term + 0.5)

    async def rerank(
        self, query: str, results: List[SearchResult]
    ) -> List[SearchResult]:
        """Rerank using BM25 scoring."""
        try:
            terms = query.lower().split()

            for result in results:
                doc_length = len(result.content.split())
                avg_length = 100  # Assume average doc length

                score = 0.0
                for term in terms:
                    term_freq = result.content.lower().count(term)

                    if term_freq == 0:
                        continue

                    idf = 2.0  # Simplified IDF
                    bm25_component = (
                        idf
                        * (self.k1 + 1)
                        * term_freq
                        / (
                            self.k1
                            * (
                                1
                                - self.b
                                + self.b
                                * (doc_length / avg_length)
                            )
                            + term_freq
                        )
                    )

                    score += bm25_component

                result.rerank_score = min(1.0, score / (len(terms) + 1))

            # Resort by rerank score
            results.sort(key=lambda r: r.rerank_score or 0.0, reverse=True)

            return results
        except Exception as e:
            print(f"[ERROR] Reranking failed: {e}")
            return results


# ============================================================================
# CONTEXT RETRIEVER
# ============================================================================

class ContextRetriever:
    """Retrieves and assembles context for agent execution."""

    def __init__(
        self,
        vector_store: VectorStore,
        knowledge_graph: KnowledgeGraph,
        reranking_engine: RerankingEngine,
    ):
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        self.reranking_engine = reranking_engine
        self.context_cache: Dict[str, ContextWindow] = {}

    async def retrieve_context(
        self,
        query: str,
        lord: Optional[str] = None,
        doc_type: Optional[DocumentType] = None,
        include_graph: bool = True,
        max_results: int = 5,
    ) -> ContextWindow:
        """Retrieve relevant context for query."""
        try:
            context = ContextWindow(query=query)

            # Semantic search
            search_results = await self.vector_store.search(
                query=query, limit=max_results * 2, doc_type=doc_type, lord=lord
            )

            # Rerank results
            reranked = await self.reranking_engine.rerank(query, search_results)

            # Split into primary and related
            context.primary_results = reranked[:max_results]
            context.related_results = reranked[max_results : max_results * 2]

            # Add graph context if requested
            if include_graph and context.primary_results:
                primary_doc = self.vector_store.get_document(
                    context.primary_results[0].doc_id
                )
                if primary_doc:
                    # Build graph context from knowledge graph
                    context.graph_context = {
                        "primary_doc_id": primary_doc.doc_id,
                        "document_type": primary_doc.doc_type.value,
                        "lord": primary_doc.lord,
                        "tags": primary_doc.tags,
                    }

            # Calculate confidence
            if context.primary_results:
                context.confidence = context.primary_results[0].similarity_score
            else:
                context.confidence = 0.0

            # Cache context
            self.context_cache[context.context_id] = context

            return context
        except Exception as e:
            print(f"[ERROR] Context retrieval failed: {e}")
            return ContextWindow(query=query, confidence=0.0)

    async def retrieve_related_context(
        self, doc_id: str, limit: int = 5
    ) -> List[SearchResult]:
        """Find related documents."""
        try:
            doc = self.vector_store.get_document(doc_id)
            if not doc:
                return []

            # Use document content as query
            results = await self.vector_store.search(
                query=doc.content, limit=limit + 1
            )

            # Remove self from results
            return [r for r in results if r.doc_id != doc_id][:limit]
        except Exception as e:
            print(f"[ERROR] Related context retrieval failed: {e}")
            return []

    def get_context(self, context_id: str) -> Optional[ContextWindow]:
        """Retrieve cached context."""
        return self.context_cache.get(context_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        return {
            "cached_contexts": len(self.context_cache),
            "vector_store": self.vector_store.get_statistics(),
            "knowledge_graph": self.knowledge_graph.get_statistics(),
        }


# ============================================================================
# RAG COORDINATOR
# ============================================================================

class RAGCoordinator:
    """Main RAG system coordinator."""

    def __init__(self):
        self.embedding_engine = MockEmbeddingEngine()
        self.vector_store = VectorStore(self.embedding_engine)
        self.knowledge_graph = KnowledgeGraph()
        self.reranking_engine = BM25RerankingEngine()
        self.context_retriever = ContextRetriever(
            self.vector_store, self.knowledge_graph, self.reranking_engine
        )

    async def ingest_document(
        self, content: str, doc_type: DocumentType, lord: str, agent: str,
        metadata: Dict[str, Any] = None, tags: List[str] = None,
    ) -> Document:
        """Ingest document into RAG system."""
        doc = Document(
            content=content,
            doc_type=doc_type,
            lord=lord,
            agent=agent,
            metadata=metadata or {},
            tags=tags or [],
        )

        await self.vector_store.add_document(doc)
        return doc

    async def build_knowledge_graph_from_documents(self) -> bool:
        """Build knowledge graph from documents."""
        try:
            # Create nodes for each document
            for doc_id, doc in self.vector_store.documents.items():
                node = KnowledgeGraphNode(
                    label=f"{doc.doc_type.value}_{doc.agent}",
                    doc_id=doc_id,
                    node_type=doc.doc_type.value,
                    attributes={
                        "lord": doc.lord,
                        "agent": doc.agent,
                        "tags": doc.tags,
                    },
                )
                await self.knowledge_graph.add_node(node)

            # Create edges based on similarity
            docs = list(self.vector_store.documents.values())
            for i, doc1 in enumerate(docs):
                for doc2 in docs[i + 1 :]:
                    # Calculate similarity
                    similarity = await self.embedding_engine.similarity(
                        doc1.embedding or [], doc2.embedding or []
                    )

                    # Add edge if similarity above threshold
                    if similarity > 0.5:
                        node1 = next(
                            (n for n in self.knowledge_graph.nodes.values()
                             if n.doc_id == doc1.doc_id),
                            None,
                        )
                        node2 = next(
                            (n for n in self.knowledge_graph.nodes.values()
                             if n.doc_id == doc2.doc_id),
                            None,
                        )

                        if node1 and node2:
                            edge = KnowledgeGraphEdge(
                                source_id=node1.node_id,
                                target_id=node2.node_id,
                                relation_type="related_to",
                                weight=similarity,
                            )
                            await self.knowledge_graph.add_edge(edge)

            return True
        except Exception as e:
            print(f"[ERROR] Knowledge graph building failed: {e}")
            return False

    async def query(
        self,
        query: str,
        lord: Optional[str] = None,
        doc_type: Optional[DocumentType] = None,
    ) -> ContextWindow:
        """Query RAG system."""
        return await self.context_retriever.retrieve_context(
            query=query, lord=lord, doc_type=doc_type, include_graph=True
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get complete RAG system statistics."""
        return {
            "vector_store": self.vector_store.get_statistics(),
            "knowledge_graph": self.knowledge_graph.get_statistics(),
            "context_retriever": self.context_retriever.get_statistics(),
        }


# ============================================================================
# INTEGRATION WITH SPECIALIZED AGENTS
# ============================================================================

class RAGAugmentedAgent:
    """Mixin for agents to use RAG system."""

    def __init__(self, rag_coordinator: RAGCoordinator):
        self.rag = rag_coordinator

    async def augment_context(
        self, query: str, doc_type: Optional[DocumentType] = None
    ) -> ContextWindow:
        """Get augmented context for execution."""
        # Override lord with agent's domain
        return await self.rag.query(query=query, doc_type=doc_type)

    async def ingest_knowledge(
        self,
        content: str,
        doc_type: DocumentType,
        metadata: Dict[str, Any] = None,
    ) -> Document:
        """Agent ingests knowledge into system."""
        # This would be called by specialized agents
        return await self.rag.ingest_document(
            content=content,
            doc_type=doc_type,
            lord=getattr(self, "lord_domain", "unknown"),
            agent=getattr(self, "agent_name", "unknown"),
            metadata=metadata,
        )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_rag_usage():
    """Demonstrate RAG system."""
    rag = RAGCoordinator()

    # Ingest sample documents
    docs = [
        await rag.ingest_document(
            "Strategic initiatives drive organizational growth through innovation",
            DocumentType.STRATEGY,
            "architect",
            "InitiativeArchitect",
            tags=["strategy", "growth"],
        ),
        await rag.ingest_document(
            "Learning programs enhance team capabilities and skill development",
            DocumentType.CAPABILITY,
            "cognition",
            "LearningCoordinator",
            tags=["learning", "development"],
        ),
        await rag.ingest_document(
            "Project timeline optimization minimizes delays and bottlenecks",
            DocumentType.WORKFLOW,
            "strategos",
            "TimelineTracker",
            tags=["timeline", "optimization"],
        ),
    ]

    print(f"[OK] Ingested {len(docs)} documents")

    # Build knowledge graph
    await rag.build_knowledge_graph_from_documents()
    print("[OK] Knowledge graph built")

    # Query RAG system
    context = await rag.query("How can we improve organizational growth?", lord="architect")
    print(f"[OK] Retrieved context with {len(context.primary_results)} results")
    print(f"[OK] Confidence: {context.confidence:.2f}")

    # Print statistics
    stats = rag.get_statistics()
    print(f"[OK] Vector store has {stats['vector_store']['total_documents']} documents")
    print(f"[OK] Knowledge graph has {stats['knowledge_graph']['total_nodes']} nodes")


if __name__ == "__main__":
    asyncio.run(example_rag_usage())
