import hashlib
import logging

import httpx
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.crawl_cache import CrawlCache
from db import get_db_connection
from inference import InferenceProvider


class IngestionService:
    """
    Industrial pipeline for turning documents into surgical RAG chunks.
    Target: agent_memory_semantic table (768 dimensions).
    """

    def __init__(self):
        self.embedder = InferenceProvider.get_embeddings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800, chunk_overlap=150, separators=["\n\n", "\n", ".", " ", ""]
        )
        self.logger = logging.getLogger("raptorflow.ingestion")

    def _generate_id(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    async def ingest_text(self, tenant_id: str, content: str, metadata: dict):
        """Processes raw text into embedded chunks for semantic memory."""
        chunks = self.splitter.split_text(content)
        self.logger.info(f"Splitting content into {len(chunks)} chunks")

        # Batch Embeddings (Economy & Speed)
        embeddings = await self.embedder.aembed_documents(chunks)

        async with get_db_connection() as conn:
            cursor = await conn.cursor()
            async with cursor as cur:
                for chunk, emb in zip(chunks, embeddings):
                    chunk_id = self._generate_id(chunk)
                    await cur.execute(
                        """
                        INSERT INTO agent_memory_semantic (id, tenant_id, fact, embedding, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (chunk_id, tenant_id, chunk, emb, metadata),
                    )
                await conn.commit()

        return len(chunks)

    async def fetch_url(self, url: str) -> str:
        """Extracts text content from a given URL."""
        cache = CrawlCache()
        cached = cache.get(url)
        if cached.entry and cached.is_fresh:
            return cached.entry.get("content", "")

        async with httpx.AsyncClient() as client:
            headers = {}
            if cached.entry:
                headers = cache.build_revalidation_headers(cached.entry)
            response = await client.get(url, headers=headers or None)
            if response.status_code == httpx.codes.NOT_MODIFIED and cached.entry:
                cache.touch(cached.entry)
                return cached.entry.get("content", "")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            content = soup.get_text(separator=" ", strip=True)
            cache.set(
                url,
                content,
                etag=response.headers.get("ETag"),
                last_modified=response.headers.get("Last-Modified"),
            )
            return content

    async def ingest_url(self, tenant_id: str, url: str):
        """Fetches and ingests content from a URL."""
        content = await self.fetch_url(url)
        return await self.ingest_text(
            tenant_id, content, {"source": url, "type": "url"}
        )
