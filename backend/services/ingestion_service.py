import asyncio
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from inference import InferenceProvider
from db import get_db_connection
import hashlib
import logging

class IngestionService:
    """
    Industrial pipeline for turning documents into surgical RAG chunks.
    """
    
    def __init__(self):
        self.embedder = InferenceProvider.get_embeddings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        self.logger = logging.getLogger("raptorflow.ingestion")

    def _generate_id(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    async def ingest_text(self, workspace_id: str, content: str, source_metadata: dict):
        """Processes raw text into embedded chunks."""
        chunks = self.splitter.split_text(content)
        self.logger.info(f"Splitting content into {len(chunks)} chunks")
        
        # Batch Embeddings (Economy)
        embeddings = await self.embedder.aembed_documents(chunks)
        
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                for chunk, emb in zip(chunks, embeddings):
                    chunk_id = self._generate_id(chunk)
                    await cur.execute(
                        """
                        INSERT INTO muse_assets (id, workspace_id, content, embedding, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (chunk_id, workspace_id, chunk, emb, source_metadata)
                    )
                await conn.commit()
        
        return len(chunks)

    async def ingest_pdf(self, workspace_id: str, file_path: str):
        """Placeholder for OCR / PDF extraction logic..."""
        pass
