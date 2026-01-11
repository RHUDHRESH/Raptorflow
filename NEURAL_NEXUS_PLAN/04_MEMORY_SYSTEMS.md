# PHASE 4: MEMORY & KNOWLEDGE SYSTEMS

---

## 4.1 Foundation Store (User Context)

The Foundation is the core DNA that makes every output personalized.

```python
# backend/memory/foundation_store.py
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
import json
import logging

from core.database import async_session_maker
from core.redis_client import redis_client

logger = logging.getLogger(__name__)


class ICP(BaseModel):
    """Ideal Customer Profile."""
    id: str
    name: str
    title: str
    industry: str
    company_size: str
    pain_points: List[str]
    goals: List[str]
    objections: List[str]
    preferred_channels: List[str]
    psychographics: Dict[str, Any] = {}


class Foundation(BaseModel):
    """User's complete business Foundation."""
    user_id: str
    workspace_id: str

    # Company Info
    company_name: str
    business_description: str
    industry: str
    location: str
    website: Optional[str] = None

    # Positioning
    positioning: str
    unique_value_proposition: str
    key_differentiators: List[str] = []

    # Target Market
    icps: List[ICP] = []
    target_markets: List[str] = []

    # Brand
    brand_voice: str  # Professional, Casual, Authoritative, Friendly
    tone_keywords: List[str] = []
    messaging_pillars: List[str] = []

    # Competitors
    competitors: List[Dict[str, str]] = []  # [{name, url, notes}]

    # Products/Services
    products: List[Dict[str, Any]] = []
    pricing_info: Optional[str] = None

    # Indian Market Specific
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    regional_languages: List[str] = []  # Hindi, Tamil, Telugu, etc.

    # User Preferences (Constitution)
    constitution: Dict[str, Any] = {}  # no_emojis, formal_only, etc.

    # Subscription
    subscription_tier: str = "free"

    # Metadata
    created_at: datetime
    updated_at: datetime


class FoundationStore:
    """
    Manages user Foundation data.

    Storage:
    - PostgreSQL: Source of truth
    - Redis: Cache for fast access

    Features:
    - Lazy loading of ICP details
    - Automatic cache invalidation
    - Compressed summaries for context injection
    """

    CACHE_TTL = 3600  # 1 hour

    async def get_foundation(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's Foundation, from cache or database.
        """
        cache_key = f"foundation:{user_id}"

        # Try cache first
        cached = await redis_client.get_json(cache_key)
        if cached:
            return cached

        # Load from database
        foundation = await self._load_from_db(user_id)

        if foundation:
            # Cache it
            await redis_client.set_json(cache_key, foundation, ex=self.CACHE_TTL)

        return foundation or self._get_default_foundation(user_id)

    async def get_foundation_summary(self, user_id: str) -> str:
        """
        Get compressed Foundation summary for context injection.
        Optimized to fit in ~500 tokens.
        """
        foundation = await self.get_foundation(user_id)

        # Build compressed summary
        summary_parts = [
            f"Company: {foundation.get('company_name', 'Unknown')}",
            f"Industry: {foundation.get('industry', 'Unknown')}",
            f"Positioning: {foundation.get('positioning', '')}",
            f"UVP: {foundation.get('unique_value_proposition', '')}",
        ]

        # Add ICPs summary
        icps = foundation.get('icps', [])
        if icps:
            icp_summary = "Target ICPs: " + ", ".join([
                f"{icp.get('name')} ({icp.get('title')})"
                for icp in icps[:3]  # Limit to 3
            ])
            summary_parts.append(icp_summary)

        # Add brand voice
        summary_parts.append(f"Brand Voice: {foundation.get('brand_voice', 'Professional')}")

        # Add competitors
        competitors = foundation.get('competitors', [])
        if competitors:
            comp_names = [c.get('name') for c in competitors[:3]]
            summary_parts.append(f"Competitors: {', '.join(comp_names)}")

        return "\n".join(summary_parts)

    async def update_foundation(self, user_id: str, updates: Dict[str, Any]):
        """
        Update user's Foundation.
        """
        async with async_session_maker() as session:
            # Update database
            await session.execute(
                """
                UPDATE foundations
                SET data = data || :updates, updated_at = NOW()
                WHERE user_id = :user_id
                """,
                {"user_id": user_id, "updates": json.dumps(updates)}
            )
            await session.commit()

        # Invalidate cache
        await redis_client.delete(f"foundation:{user_id}")

        logger.info(f"Foundation updated for user {user_id}")

    async def get_icps(self, user_id: str) -> List[ICP]:
        """
        Get full ICP details for a user.
        """
        async with async_session_maker() as session:
            result = await session.execute(
                """
                SELECT * FROM icp_profiles
                WHERE user_id = :user_id
                ORDER BY created_at
                """,
                {"user_id": user_id}
            )
            rows = result.fetchall()

            return [ICP(**dict(row)) for row in rows]

    async def get_icp_by_id(self, icp_id: str) -> Optional[ICP]:
        """
        Get a specific ICP by ID.
        """
        cache_key = f"icp:{icp_id}"

        cached = await redis_client.get_json(cache_key)
        if cached:
            return ICP(**cached)

        async with async_session_maker() as session:
            result = await session.execute(
                "SELECT * FROM icp_profiles WHERE id = :icp_id",
                {"icp_id": icp_id}
            )
            row = result.fetchone()

            if row:
                icp = ICP(**dict(row))
                await redis_client.set_json(cache_key, icp.model_dump(), ex=self.CACHE_TTL)
                return icp

        return None

    async def _load_from_db(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load Foundation from PostgreSQL.
        """
        async with async_session_maker() as session:
            result = await session.execute(
                "SELECT * FROM foundations WHERE user_id = :user_id",
                {"user_id": user_id}
            )
            row = result.fetchone()

            if row:
                foundation = dict(row)

                # Load ICPs
                icps = await self.get_icps(user_id)
                foundation["icps"] = [icp.model_dump() for icp in icps]

                return foundation

        return None

    def _get_default_foundation(self, user_id: str) -> Dict[str, Any]:
        """
        Return default Foundation for new users.
        """
        return {
            "user_id": user_id,
            "company_name": "Your Company",
            "business_description": "",
            "industry": "Technology",
            "location": "India",
            "positioning": "",
            "unique_value_proposition": "",
            "brand_voice": "Professional",
            "icps": [],
            "competitors": [],
            "subscription_tier": "free",
            "constitution": {}
        }


# Singleton
foundation_store = FoundationStore()
```

---

## 4.2 Vector Store (Semantic Memory)

```python
# backend/memory/vector_store.py
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime
import numpy as np
import logging

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MemoryChunk(BaseModel):
    """A single memory chunk with embedding."""
    id: str
    user_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = {}
    memory_type: str  # "conversation", "fact", "research", "campaign"
    source: Optional[str] = None
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    decay_weight: float = 1.0  # For memory decay


class VectorStore:
    """
    Vector storage for semantic memory retrieval.

    Features:
    - Tenant isolation (user_id namespace)
    - Memory decay (old memories fade)
    - Hybrid search (vector + metadata filters)
    - Automatic chunking
    """

    def __init__(self):
        self.embedder = None  # Will be initialized
        self._index = {}  # In-memory for dev, Pinecone/Qdrant for prod

    async def initialize(self, embedder):
        """Initialize with embedding model."""
        self.embedder = embedder

    async def add(
        self,
        user_id: str,
        content: str,
        memory_type: str,
        metadata: Dict[str, Any] = None,
        source: str = None
    ) -> str:
        """
        Add a memory chunk to the store.

        Args:
            user_id: Owner of the memory
            content: Text content to store
            memory_type: Type of memory (conversation, fact, research, campaign)
            metadata: Additional metadata for filtering
            source: Source of the memory (e.g., skill_id, url)

        Returns:
            Memory chunk ID
        """
        # Generate embedding
        embedding = await self.embedder.embed(content)

        # Create chunk
        chunk_id = f"mem_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        chunk = MemoryChunk(
            id=chunk_id,
            user_id=user_id,
            content=content,
            embedding=embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
            metadata=metadata or {},
            memory_type=memory_type,
            source=source,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow()
        )

        # Store in database
        await self._store_chunk(chunk)

        logger.debug(f"Added memory chunk {chunk_id} for user {user_id}")
        return chunk_id

    async def search(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        memory_types: List[str] = None,
        min_score: float = 0.7
    ) -> List[Tuple[MemoryChunk, float]]:
        """
        Search for relevant memories.

        Args:
            user_id: User to search memories for
            query: Search query
            top_k: Number of results to return
            memory_types: Filter by memory types
            min_score: Minimum similarity score

        Returns:
            List of (chunk, score) tuples
        """
        # Generate query embedding
        query_embedding = await self.embedder.embed(query)

        # Search with filters
        results = await self._search_vectors(
            user_id=user_id,
            query_embedding=query_embedding,
            top_k=top_k * 2,  # Fetch more to account for filtering
            memory_types=memory_types
        )

        # Filter by score and apply decay
        filtered = []
        for chunk, score in results:
            # Apply memory decay
            adjusted_score = score * chunk.decay_weight

            if adjusted_score >= min_score:
                filtered.append((chunk, adjusted_score))

                # Update access stats
                await self._update_access(chunk.id)

        # Sort by adjusted score
        filtered.sort(key=lambda x: x[1], reverse=True)

        return filtered[:top_k]

    async def delete(self, chunk_id: str):
        """Delete a memory chunk."""
        await self._delete_chunk(chunk_id)
        logger.debug(f"Deleted memory chunk {chunk_id}")

    async def apply_decay(self, user_id: str, decay_rate: float = 0.99):
        """
        Apply memory decay to reduce weight of old/unused memories.

        Called periodically (e.g., daily) to prevent memory bloat.
        """
        # Get all chunks for user
        chunks = await self._get_all_chunks(user_id)

        for chunk in chunks:
            # Calculate decay based on time since last access
            days_since_access = (datetime.utcnow() - chunk.last_accessed).days

            # Decay formula: weight = decay_rate ^ days
            new_weight = decay_rate ** days_since_access

            # Don't decay below 0.1
            chunk.decay_weight = max(0.1, new_weight)

            await self._update_chunk(chunk)

        logger.info(f"Applied memory decay for user {user_id}: {len(chunks)} chunks")

    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for a user."""
        chunks = await self._get_all_chunks(user_id)

        by_type = {}
        for chunk in chunks:
            by_type[chunk.memory_type] = by_type.get(chunk.memory_type, 0) + 1

        return {
            "total_chunks": len(chunks),
            "by_type": by_type,
            "oldest": min(c.created_at for c in chunks).isoformat() if chunks else None,
            "newest": max(c.created_at for c in chunks).isoformat() if chunks else None
        }

    # ===== Internal Methods (implement with your vector DB) =====

    async def _store_chunk(self, chunk: MemoryChunk):
        """Store chunk in vector database."""
        # Implementation depends on vector DB choice
        # Options: Pinecone, Qdrant, Weaviate, pgvector
        pass

    async def _search_vectors(
        self,
        user_id: str,
        query_embedding: List[float],
        top_k: int,
        memory_types: List[str] = None
    ) -> List[Tuple[MemoryChunk, float]]:
        """Search vectors with filters."""
        pass

    async def _update_access(self, chunk_id: str):
        """Update access stats for a chunk."""
        pass

    async def _delete_chunk(self, chunk_id: str):
        """Delete a chunk from storage."""
        pass

    async def _get_all_chunks(self, user_id: str) -> List[MemoryChunk]:
        """Get all chunks for a user."""
        pass

    async def _update_chunk(self, chunk: MemoryChunk):
        """Update a chunk in storage."""
        pass


# Singleton
vector_store = VectorStore()
```

---

## 4.3 Graph Store (Knowledge Graph / GraphRAG)

```python
# backend/memory/graph_store.py
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Entity(BaseModel):
    """A node in the knowledge graph."""
    id: str
    user_id: str
    entity_type: str  # COMPANY, PERSON, PRODUCT, CONCEPT, ICP
    name: str
    properties: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None
    created_at: datetime
    updated_at: datetime


class Relationship(BaseModel):
    """An edge in the knowledge graph."""
    id: str
    user_id: str
    source_id: str
    target_id: str
    relationship_type: str  # COMPETES_WITH, TARGETS, SELLS, WORKS_AT
    properties: Dict[str, Any] = {}
    strength: float = 1.0  # 0-1, how strong is this relationship
    created_at: datetime


class GraphStore:
    """
    Knowledge Graph for structured relationship storage.

    Why GraphRAG?
    - Vector search finds "similar" content
    - Graph search finds "related" content
    - "Nike competitors" -> Graph knows Apple isn't related even if "company" is similar

    Example Relationships:
    - (Raptorflow) --[COMPETES_WITH]--> (HubSpot)
    - (ICP: Marketing Manager) --[WORKS_AT]--> (Tech Startup)
    - (Diwali Campaign) --[TARGETS]--> (ICP: Retail Owner)
    """

    def __init__(self):
        self._entities = {}  # In-memory for dev
        self._relationships = {}

    async def add_entity(
        self,
        user_id: str,
        entity_type: str,
        name: str,
        properties: Dict[str, Any] = None
    ) -> str:
        """
        Add an entity (node) to the graph.
        """
        entity_id = f"ent_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        entity = Entity(
            id=entity_id,
            user_id=user_id,
            entity_type=entity_type,
            name=name,
            properties=properties or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        await self._store_entity(entity)

        logger.debug(f"Added entity: {entity_type}:{name}")
        return entity_id

    async def add_relationship(
        self,
        user_id: str,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Dict[str, Any] = None,
        strength: float = 1.0
    ) -> str:
        """
        Add a relationship (edge) between entities.
        """
        rel_id = f"rel_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        relationship = Relationship(
            id=rel_id,
            user_id=user_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            properties=properties or {},
            strength=strength,
            created_at=datetime.utcnow()
        )

        await self._store_relationship(relationship)

        logger.debug(f"Added relationship: {source_id} --[{relationship_type}]--> {target_id}")
        return rel_id

    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        return await self._get_entity(entity_id)

    async def find_entities(
        self,
        user_id: str,
        entity_type: str = None,
        name_contains: str = None,
        limit: int = 10
    ) -> List[Entity]:
        """
        Find entities matching criteria.
        """
        return await self._find_entities(
            user_id=user_id,
            entity_type=entity_type,
            name_contains=name_contains,
            limit=limit
        )

    async def get_relationships(
        self,
        entity_id: str,
        relationship_type: str = None,
        direction: str = "both"  # "outgoing", "incoming", "both"
    ) -> List[Tuple[Relationship, Entity]]:
        """
        Get relationships for an entity.

        Returns:
            List of (relationship, connected_entity) tuples
        """
        return await self._get_relationships(
            entity_id=entity_id,
            relationship_type=relationship_type,
            direction=direction
        )

    async def traverse(
        self,
        start_entity_id: str,
        relationship_types: List[str] = None,
        max_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Traverse the graph from a starting entity.

        Returns a subgraph containing all reachable entities.
        """
        visited = set()
        subgraph = {"entities": [], "relationships": []}

        async def _traverse(entity_id: str, depth: int):
            if depth > max_depth or entity_id in visited:
                return

            visited.add(entity_id)

            entity = await self.get_entity(entity_id)
            if entity:
                subgraph["entities"].append(entity.model_dump())

            relationships = await self.get_relationships(
                entity_id=entity_id,
                relationship_type=relationship_types[0] if relationship_types else None
            )

            for rel, connected_entity in relationships:
                subgraph["relationships"].append(rel.model_dump())
                await _traverse(connected_entity.id, depth + 1)

        await _traverse(start_entity_id, 0)
        return subgraph

    async def query_path(
        self,
        start_entity_id: str,
        end_entity_id: str,
        max_depth: int = 4
    ) -> Optional[List[Tuple[Entity, Relationship]]]:
        """
        Find the shortest path between two entities.
        """
        # BFS for shortest path
        from collections import deque

        queue = deque([(start_entity_id, [])])
        visited = {start_entity_id}

        while queue:
            current_id, path = queue.popleft()

            if current_id == end_entity_id:
                return path

            if len(path) >= max_depth:
                continue

            relationships = await self.get_relationships(current_id)

            for rel, connected_entity in relationships:
                if connected_entity.id not in visited:
                    visited.add(connected_entity.id)
                    new_path = path + [(connected_entity, rel)]
                    queue.append((connected_entity.id, new_path))

        return None

    async def build_from_foundation(self, user_id: str, foundation: Dict[str, Any]):
        """
        Build initial graph from user's Foundation data.
        """
        # Add company entity
        company_id = await self.add_entity(
            user_id=user_id,
            entity_type="COMPANY",
            name=foundation.get("company_name", "Unknown"),
            properties={
                "industry": foundation.get("industry"),
                "location": foundation.get("location")
            }
        )

        # Add ICP entities
        for icp in foundation.get("icps", []):
            icp_id = await self.add_entity(
                user_id=user_id,
                entity_type="ICP",
                name=icp.get("name"),
                properties=icp
            )

            # Create relationship: Company -> TARGETS -> ICP
            await self.add_relationship(
                user_id=user_id,
                source_id=company_id,
                target_id=icp_id,
                relationship_type="TARGETS"
            )

        # Add competitor entities
        for competitor in foundation.get("competitors", []):
            comp_id = await self.add_entity(
                user_id=user_id,
                entity_type="COMPANY",
                name=competitor.get("name"),
                properties={"url": competitor.get("url")}
            )

            # Create relationship: Company -> COMPETES_WITH -> Competitor
            await self.add_relationship(
                user_id=user_id,
                source_id=company_id,
                target_id=comp_id,
                relationship_type="COMPETES_WITH"
            )

        logger.info(f"Built knowledge graph from Foundation for user {user_id}")

    # ===== Internal Methods =====

    async def _store_entity(self, entity: Entity):
        """Store entity in database."""
        pass

    async def _store_relationship(self, relationship: Relationship):
        """Store relationship in database."""
        pass

    async def _get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity from database."""
        pass

    async def _find_entities(
        self,
        user_id: str,
        entity_type: str,
        name_contains: str,
        limit: int
    ) -> List[Entity]:
        """Find entities in database."""
        pass

    async def _get_relationships(
        self,
        entity_id: str,
        relationship_type: str,
        direction: str
    ) -> List[Tuple[Relationship, Entity]]:
        """Get relationships from database."""
        pass


# Singleton
graph_store = GraphStore()
```

---

## 4.4 Conversation Memory

```python
# backend/memory/conversation.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import logging

from core.redis_client import redis_client
from core.database import async_session_maker

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """A single message in a conversation."""
    id: str
    role: str  # "user", "assistant", "system", "tool"
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime


class Conversation(BaseModel):
    """A conversation thread."""
    id: str
    user_id: str
    title: Optional[str] = None
    messages: List[Message] = []
    context: Dict[str, Any] = {}  # Pinned context
    created_at: datetime
    updated_at: datetime


class ConversationStore:
    """
    Manages conversation history.

    Features:
    - Rolling window (keep last N messages)
    - Pinned context (important facts that persist)
    - Automatic summarization for long conversations
    - Session resumption
    """

    MAX_MESSAGES = 50  # Maximum messages to keep in memory
    SUMMARY_THRESHOLD = 30  # Trigger summarization at this count

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        # Try Redis first
        cached = await redis_client.get_json(f"conv:{conversation_id}")
        if cached:
            return Conversation(**cached)

        # Load from database
        return await self._load_from_db(conversation_id)

    async def create_conversation(self, user_id: str, title: str = None) -> Conversation:
        """Create a new conversation."""
        conv_id = f"conv_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        conversation = Conversation(
            id=conv_id,
            user_id=user_id,
            title=title,
            messages=[],
            context={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        await self._save(conversation)
        return conversation

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> Message:
        """Add a message to a conversation."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")

        message = Message(
            id=f"msg_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            role=role,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow()
        )

        conversation.messages.append(message)
        conversation.updated_at = datetime.utcnow()

        # Check if summarization needed
        if len(conversation.messages) >= self.SUMMARY_THRESHOLD:
            await self._summarize_old_messages(conversation)

        # Enforce max messages
        if len(conversation.messages) > self.MAX_MESSAGES:
            conversation.messages = conversation.messages[-self.MAX_MESSAGES:]

        await self._save(conversation)
        return message

    async def pin_context(self, conversation_id: str, key: str, value: Any):
        """
        Pin important context that should persist across summarization.

        Example:
        - pin_context(conv_id, "user_goal", "Launch Diwali campaign")
        - pin_context(conv_id, "selected_icp", "Marketing Manager")
        """
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.context[key] = value
            await self._save(conversation)

    async def get_context_for_prompt(
        self,
        conversation_id: str,
        max_messages: int = 10
    ) -> Dict[str, Any]:
        """
        Get conversation context formatted for prompt injection.

        Returns:
        - pinned_context: Important persisted facts
        - recent_messages: Last N messages
        - summary: Summary of older messages (if any)
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return {"pinned_context": {}, "recent_messages": [], "summary": None}

        return {
            "pinned_context": conversation.context,
            "recent_messages": [
                {"role": m.role, "content": m.content}
                for m in conversation.messages[-max_messages:]
            ],
            "summary": conversation.context.get("_summary")
        }

    async def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List user's conversations."""
        async with async_session_maker() as session:
            result = await session.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations
                WHERE user_id = :user_id
                ORDER BY updated_at DESC
                LIMIT :limit OFFSET :offset
                """,
                {"user_id": user_id, "limit": limit, "offset": offset}
            )
            return [dict(row) for row in result.fetchall()]

    async def _summarize_old_messages(self, conversation: Conversation):
        """
        Summarize old messages to save context space.
        """
        # Keep last 10 messages, summarize the rest
        to_summarize = conversation.messages[:-10]

        if not to_summarize:
            return

        # Build text to summarize
        text = "\n".join([
            f"{m.role}: {m.content}"
            for m in to_summarize
        ])

        # Use cheap model for summarization
        from agents.model_client import model_client

        summary = await model_client.generate(
            model="gemini-2.0-flash-lite",
            system_prompt="Summarize this conversation, keeping key decisions and context.",
            user_prompt=text,
            max_tokens=500
        )

        # Store summary in pinned context
        conversation.context["_summary"] = summary.get("content", "")

        # Remove summarized messages
        conversation.messages = conversation.messages[-10:]

        logger.debug(f"Summarized {len(to_summarize)} messages in conversation {conversation.id}")

    async def _save(self, conversation: Conversation):
        """Save conversation to Redis and database."""
        # Redis for fast access
        await redis_client.set_json(
            f"conv:{conversation.id}",
            conversation.model_dump(),
            ex=3600  # 1 hour cache
        )

        # Database for persistence
        async with async_session_maker() as session:
            await session.execute(
                """
                INSERT INTO conversations (id, user_id, title, data, created_at, updated_at)
                VALUES (:id, :user_id, :title, :data, :created_at, :updated_at)
                ON CONFLICT (id) DO UPDATE SET
                    data = :data,
                    updated_at = :updated_at
                """,
                {
                    "id": conversation.id,
                    "user_id": conversation.user_id,
                    "title": conversation.title,
                    "data": json.dumps(conversation.model_dump()),
                    "created_at": conversation.created_at,
                    "updated_at": conversation.updated_at
                }
            )
            await session.commit()

    async def _load_from_db(self, conversation_id: str) -> Optional[Conversation]:
        """Load conversation from database."""
        async with async_session_maker() as session:
            result = await session.execute(
                "SELECT data FROM conversations WHERE id = :id",
                {"id": conversation_id}
            )
            row = result.fetchone()

            if row:
                data = json.loads(row["data"])
                return Conversation(**data)

        return None


# Singleton
conversation_store = ConversationStore()
```
