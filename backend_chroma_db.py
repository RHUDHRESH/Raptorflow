# backend/chroma_db.py
# RaptorFlow Codex - ChromaDB Vector Database & RAG System
# Week 3 Wednesday - Knowledge Base & Context Retrieval

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

# ============================================================================
# EMBEDDINGS CONFIGURATION
# ============================================================================

class EmbeddingModel:
    """Embedding model configuration and management"""

    # Default embedding model (sentence-transformers)
    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    # Alternative models
    MODELS = {
        "minilm": "sentence-transformers/all-MiniLM-L6-v2",  # Fast, 384 dims
        "mpnet": "sentence-transformers/all-mpnet-base-v2",   # Accurate, 768 dims
        "multilingual": "sentence-transformers/multilingual-MiniLM-L6-v2",  # Multilingual
    }

    # Embedding dimensions per model
    DIMENSIONS = {
        "minilm": 384,
        "mpnet": 768,
        "multilingual": 384,
    }

    @staticmethod
    def get_embedding_function(model_name: str = "minilm"):
        """Get embedding function for model"""
        model_path = EmbeddingModel.MODELS.get(model_name, EmbeddingModel.DEFAULT_MODEL)
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_path
        )

    @staticmethod
    def get_dimensions(model_name: str = "minilm") -> int:
        """Get embedding dimension for model"""
        return EmbeddingModel.DIMENSIONS.get(model_name, 384)

# ============================================================================
# DOCUMENT & CHUNK TYPES
# ============================================================================

@dataclass
class Document:
    """Knowledge base document"""
    id: str
    title: str
    content: str
    category: str  # "campaign", "strategy", "research", "template", "guideline"
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    workspace_id: str
    owner_id: str

@dataclass
class Chunk:
    """Text chunk for embedding"""
    id: str
    document_id: str
    text: str
    chunk_index: int
    metadata: Dict[str, Any]
    embedding_model: str = "minilm"

# ============================================================================
# CHROMADB RAG SYSTEM
# ============================================================================

class ChromaDBRAG:
    """
    ChromaDB-based Retrieval-Augmented Generation system.

    Features:
    - Vector embeddings for semantic search
    - Knowledge base management
    - Context retrieval for agents
    - Similarity search
    - Metadata filtering
    - Bulk operations
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "raptorflow_knowledge",
        embedding_model: str = "minilm"
    ):
        """Initialize ChromaDB RAG system"""
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.embedding_fn = None
        self.client = None
        self.collection = None

    async def connect(self) -> None:
        """Connect to ChromaDB"""
        try:
            # Connect to ChromaDB server
            self.client = chromadb.HttpClient(host=self.host, port=self.port)

            # Get or create collection
            self.embedding_fn = EmbeddingModel.get_embedding_function(
                self.embedding_model
            )

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"✅ ChromaDB connected: {self.collection_name}")

        except Exception as e:
            logger.error(f"❌ ChromaDB connection failed: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from ChromaDB"""
        if self.client:
            # ChromaDB HttpClient doesn't require explicit cleanup
            logger.info("✅ ChromaDB disconnected")

    async def add_document(self, document: Document) -> None:
        """
        Add document to knowledge base.

        Args:
            document: Document to add
        """
        try:
            # Split document into chunks (simple 512-char chunks)
            chunks = self._chunk_document(document)

            # Prepare data for ChromaDB
            ids = [chunk.id for chunk in chunks]
            documents = [chunk.text for chunk in chunks]
            metadatas = [
                {
                    **chunk.metadata,
                    "document_id": document.id,
                    "title": document.title,
                    "category": document.category,
                    "workspace_id": document.workspace_id,
                    "owner_id": document.owner_id,
                    "chunk_index": chunk.chunk_index
                }
                for chunk in chunks
            ]

            # Add to collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

            logger.info(
                f"📚 Document added: {document.id} "
                f"({len(chunks)} chunks, {document.category})"
            )

        except Exception as e:
            logger.error(f"❌ Add document failed: {e}")
            raise

    async def search(
        self,
        query: str,
        workspace_id: str,
        limit: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant documents.

        Args:
            query: Search query
            workspace_id: Filter by workspace
            limit: Max results
            category: Optional category filter

        Returns:
            List of relevant documents with similarity scores
        """
        try:
            # Build where filter
            where_filter = {"workspace_id": {"$eq": workspace_id}}

            if category:
                where_filter["category"] = {"$eq": category}

            # Query collection
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_filter
            )

            # Format results
            documents = []
            if results and results["ids"] and len(results["ids"]) > 0:
                for i, doc_id in enumerate(results["ids"][0]):
                    documents.append({
                        "id": doc_id,
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0,
                        "similarity": 1 - (results["distances"][0][i] if results["distances"] else 0)
                    })

            logger.info(f"🔍 Search completed: '{query}' → {len(documents)} results")
            return documents

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []

    async def get_context_for_agent(
        self,
        agent_name: str,
        workspace_id: str,
        task: str,
        context_limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get context for agent execution.

        Args:
            agent_name: Agent requesting context
            workspace_id: Workspace context
            task: Agent task description
            context_limit: Max context documents

        Returns:
            Agent context with relevant knowledge
        """
        try:
            # Search for relevant documents
            results = await self.search(
                query=task,
                workspace_id=workspace_id,
                limit=context_limit
            )

            # Format as agent context
            context = {
                "agent": agent_name,
                "task": task,
                "retrieved_knowledge": [
                    {
                        "source": doc["metadata"].get("title", "Unknown"),
                        "category": doc["metadata"].get("category", "general"),
                        "content": doc["text"],
                        "relevance": doc["similarity"],
                        "document_id": doc["metadata"].get("document_id")
                    }
                    for doc in results
                ],
                "total_knowledge_items": len(results),
                "average_relevance": (
                    sum(d["similarity"] for d in results) / len(results)
                    if results else 0
                ),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(
                f"📖 Context retrieved for {agent_name}: "
                f"{len(results)} documents (avg relevance: {context['average_relevance']:.2f})"
            )

            return context

        except Exception as e:
            logger.error(f"❌ Get context failed: {e}")
            return {
                "agent": agent_name,
                "task": task,
                "retrieved_knowledge": [],
                "error": str(e)
            }

    async def delete_document(self, document_id: str) -> None:
        """Delete document from knowledge base"""
        try:
            # Find all chunks for document
            results = self.collection.get(
                where={"document_id": {"$eq": document_id}}
            )

            if results and results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"🗑️ Document deleted: {document_id}")

        except Exception as e:
            logger.error(f"❌ Delete document failed: {e}")
            raise

    async def update_document(self, document: Document) -> None:
        """Update document in knowledge base"""
        try:
            # Delete old document
            await self.delete_document(document.id)

            # Add updated document
            await self.add_document(document)

            logger.info(f"🔄 Document updated: {document.id}")

        except Exception as e:
            logger.error(f"❌ Update document failed: {e}")
            raise

    async def get_statistics(self, workspace_id: str) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            # Count documents by category
            results = self.collection.get(
                where={"workspace_id": {"$eq": workspace_id}}
            )

            metadatas = results["metadatas"] if results and results["metadatas"] else []
            categories = {}

            for metadata in metadatas:
                category = metadata.get("category", "uncategorized")
                categories[category] = categories.get(category, 0) + 1

            return {
                "total_chunks": len(metadatas) if metadatas else 0,
                "unique_documents": len(set(
                    m.get("document_id") for m in metadatas if m
                )),
                "categories": categories,
                "embedding_model": self.embedding_model,
                "workspace_id": workspace_id
            }

        except Exception as e:
            logger.error(f"❌ Get statistics failed: {e}")
            return {}

    async def bulk_add_documents(self, documents: List[Document]) -> None:
        """Bulk add documents to knowledge base"""
        try:
            all_ids = []
            all_texts = []
            all_metadatas = []

            for document in documents:
                chunks = self._chunk_document(document)

                for chunk in chunks:
                    all_ids.append(chunk.id)
                    all_texts.append(chunk.text)
                    all_metadatas.append({
                        **chunk.metadata,
                        "document_id": document.id,
                        "title": document.title,
                        "category": document.category,
                        "workspace_id": document.workspace_id,
                        "owner_id": document.owner_id,
                        "chunk_index": chunk.chunk_index
                    })

            if all_ids:
                self.collection.add(
                    ids=all_ids,
                    documents=all_texts,
                    metadatas=all_metadatas
                )

                logger.info(
                    f"📚 Bulk add completed: {len(documents)} documents "
                    f"({len(all_ids)} chunks)"
                )

        except Exception as e:
            logger.error(f"❌ Bulk add failed: {e}")
            raise

    @staticmethod
    def _chunk_document(document: Document, chunk_size: int = 512, overlap: int = 50) -> List[Chunk]:
        """
        Split document into chunks.

        Args:
            document: Document to chunk
            chunk_size: Characters per chunk
            overlap: Overlap between chunks

        Returns:
            List of chunks
        """
        chunks = []
        content = document.content
        chunk_index = 0
        start = 0

        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_text = content[start:end].strip()

            if chunk_text:
                chunk = Chunk(
                    id=f"{document.id}_chunk_{chunk_index}",
                    document_id=document.id,
                    text=chunk_text,
                    chunk_index=chunk_index,
                    metadata={
                        "char_range": f"{start}-{end}",
                        "chunk_size": len(chunk_text)
                    }
                )
                chunks.append(chunk)

            start = end - overlap
            chunk_index += 1

        return chunks

# ============================================================================
# CHROMADB SINGLETON
# ============================================================================

_chroma_rag: Optional[ChromaDBRAG] = None

async def get_chroma_rag(
    host: str = "localhost",
    port: int = 8000,
    collection_name: str = "raptorflow_knowledge"
) -> ChromaDBRAG:
    """Get or create ChromaDB RAG singleton"""
    global _chroma_rag

    if _chroma_rag is None:
        _chroma_rag = ChromaDBRAG(
            host=host,
            port=port,
            collection_name=collection_name
        )
        await _chroma_rag.connect()

    return _chroma_rag

async def shutdown_chroma_rag() -> None:
    """Shutdown ChromaDB RAG"""
    global _chroma_rag

    if _chroma_rag:
        await _chroma_rag.disconnect()
        _chroma_rag = None

