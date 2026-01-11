# MEMORY SYSTEMS

> Hybrid Memory: Vector + Graph + Episodic + Working

---

## 1. MEMORY ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MEMORY CONTROLLER                                 │
│                                                                             │
│  Coordinates all memory systems, handles compression, manages retrieval    │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│    VECTOR     │          │    GRAPH      │          │   EPISODIC    │
│    MEMORY     │          │    MEMORY     │          │    MEMORY     │
│               │          │               │          │               │
│ Semantic      │          │ Relationships │          │ Conversations │
│ similarity    │          │ between       │          │ and sessions  │
│ search        │          │ entities      │          │               │
│               │          │               │          │               │
│ - Foundation  │          │ - ICPs ↔      │          │ - Chat logs   │
│ - ICPs        │          │   Channels    │          │ - Move history│
│ - Moves       │          │ - Competitors │          │ - Feedback    │
│ - Research    │          │   ↔ USPs      │          │ - Preferences │
│               │          │ - Pain ↔      │          │               │
│               │          │   Solutions   │          │               │
└───────────────┘          └───────────────┘          └───────────────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────┐
                          │    WORKING        │
                          │    MEMORY         │
                          │                   │
                          │ Current session   │
                          │ context, recent   │
                          │ interactions,     │
                          │ active state      │
                          └───────────────────┘
```

---

## 2. VECTOR MEMORY (Semantic Search)

**Purpose**: Find semantically similar content across foundation, ICPs, moves, research.

**Storage**: pgvector extension in Supabase PostgreSQL

```python
# backend/memory/vector_store.py
from sentence_transformers import SentenceTransformer
from supabase import Client
import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Any

class MemoryType(Enum):
    FOUNDATION = "foundation"
    ICP = "icp"
    MOVE = "move"
    CAMPAIGN = "campaign"
    RESEARCH = "research"
    CONVERSATION = "conversation"
    FEEDBACK = "feedback"

@dataclass
class MemoryChunk:
    id: str
    workspace_id: str
    memory_type: MemoryType
    content: str
    metadata: dict[str, Any]
    embedding: np.ndarray | None = None
    score: float | None = None  # Similarity score when retrieved

class VectorMemory:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim = 384

    async def store(
        self,
        workspace_id: str,
        memory_type: MemoryType,
        content: str,
        metadata: dict[str, Any] | None = None,
        chunk_id: str | None = None
    ) -> str:
        """Store content with embedding."""
        import uuid

        # Generate embedding
        embedding = self.encoder.encode(content)

        # Store in database
        record = {
            "id": chunk_id or str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "memory_type": memory_type.value,
            "content": content,
            "metadata": metadata or {},
            "embedding": embedding.tolist()
        }

        result = self.supabase.table("memory_vectors").upsert(record).execute()
        return result.data[0]["id"]

    async def search(
        self,
        workspace_id: str,
        query: str,
        memory_types: list[MemoryType] | None = None,
        limit: int = 10,
        threshold: float = 0.5
    ) -> list[MemoryChunk]:
        """Semantic search for similar content."""

        # Generate query embedding
        query_embedding = self.encoder.encode(query)

        # Build filter
        type_filter = ""
        if memory_types:
            types = [t.value for t in memory_types]
            type_filter = f"AND memory_type IN ({','.join(repr(t) for t in types)})"

        # Vector similarity search using pgvector
        result = self.supabase.rpc(
            "match_memories",
            {
                "query_embedding": query_embedding.tolist(),
                "match_workspace_id": workspace_id,
                "match_threshold": threshold,
                "match_count": limit,
                "type_filter": memory_types[0].value if memory_types and len(memory_types) == 1 else None
            }
        ).execute()

        return [
            MemoryChunk(
                id=row["id"],
                workspace_id=row["workspace_id"],
                memory_type=MemoryType(row["memory_type"]),
                content=row["content"],
                metadata=row["metadata"],
                score=row["similarity"]
            )
            for row in result.data
        ]

    async def get_context_for_agent(
        self,
        workspace_id: str,
        query: str,
        agent_type: str
    ) -> str:
        """Get relevant context for a specific agent."""

        # Different agents need different memory types
        AGENT_MEMORY_MAP = {
            "moves_generator": [MemoryType.FOUNDATION, MemoryType.ICP, MemoryType.MOVE],
            "campaign_planner": [MemoryType.FOUNDATION, MemoryType.ICP, MemoryType.CAMPAIGN, MemoryType.MOVE],
            "muse_engine": [MemoryType.FOUNDATION, MemoryType.ICP, MemoryType.FEEDBACK],
            "blackbox_engine": [MemoryType.FOUNDATION, MemoryType.RESEARCH, MemoryType.ICP],
            "daily_wins_engine": [MemoryType.FOUNDATION, MemoryType.ICP, MemoryType.MOVE],
            "market_researcher": [MemoryType.FOUNDATION, MemoryType.RESEARCH],
            "icp_architect": [MemoryType.FOUNDATION, MemoryType.RESEARCH, MemoryType.ICP],
        }

        memory_types = AGENT_MEMORY_MAP.get(agent_type, [MemoryType.FOUNDATION])

        chunks = await self.search(
            workspace_id=workspace_id,
            query=query,
            memory_types=memory_types,
            limit=5
        )

        # Format as context string
        context_parts = []
        for chunk in chunks:
            context_parts.append(f"[{chunk.memory_type.value}] {chunk.content}")

        return "\n\n".join(context_parts)


# SQL function for vector search (run once during setup)
VECTOR_SEARCH_FUNCTION = """
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding vector(384),
    match_workspace_id uuid,
    match_threshold float,
    match_count int,
    type_filter text DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    workspace_id uuid,
    memory_type text,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.workspace_id,
        m.memory_type,
        m.content,
        m.metadata,
        1 - (m.embedding <=> query_embedding) as similarity
    FROM memory_vectors m
    WHERE m.workspace_id = match_workspace_id
        AND (type_filter IS NULL OR m.memory_type = type_filter)
        AND 1 - (m.embedding <=> query_embedding) > match_threshold
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
"""
```

---

## 3. GRAPH MEMORY (Knowledge Graph)

**Purpose**: Store relationships between entities for GraphRAG.

**Storage**: PostgreSQL with adjacency list (or Neo4j for scale)

```python
# backend/memory/graph_store.py
from dataclasses import dataclass
from enum import Enum
from typing import Any
from supabase import Client

class EntityType(Enum):
    COMPANY = "company"
    ICP = "icp"
    COMPETITOR = "competitor"
    CHANNEL = "channel"
    PAIN_POINT = "pain_point"
    USP = "usp"
    FEATURE = "feature"
    MOVE = "move"
    CAMPAIGN = "campaign"
    CONTENT = "content"

class RelationType(Enum):
    # ICP relationships
    ICP_USES_CHANNEL = "uses_channel"
    ICP_HAS_PAIN = "has_pain"
    ICP_WANTS = "wants"
    ICP_FEARS = "fears"

    # Competitor relationships
    COMPETES_WITH = "competes_with"
    COMPETES_ON = "competes_on"

    # Product relationships
    SOLVES_PAIN = "solves_pain"
    HAS_USP = "has_usp"
    HAS_FEATURE = "has_feature"

    # Content relationships
    TARGETS_ICP = "targets_icp"
    USES_CHANNEL = "uses_channel"
    PART_OF_CAMPAIGN = "part_of_campaign"
    FOLLOWS_MOVE = "follows_move"

@dataclass
class Entity:
    id: str
    workspace_id: str
    entity_type: EntityType
    name: str
    properties: dict[str, Any]

@dataclass
class Relationship:
    id: str
    workspace_id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    properties: dict[str, Any]
    weight: float = 1.0

class GraphMemory:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def add_entity(
        self,
        workspace_id: str,
        entity_type: EntityType,
        name: str,
        properties: dict[str, Any] | None = None
    ) -> str:
        """Add an entity to the knowledge graph."""
        import uuid

        entity_id = str(uuid.uuid4())

        self.supabase.table("graph_entities").insert({
            "id": entity_id,
            "workspace_id": workspace_id,
            "entity_type": entity_type.value,
            "name": name,
            "properties": properties or {}
        }).execute()

        return entity_id

    async def add_relationship(
        self,
        workspace_id: str,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        properties: dict[str, Any] | None = None,
        weight: float = 1.0
    ) -> str:
        """Add a relationship between entities."""
        import uuid

        rel_id = str(uuid.uuid4())

        self.supabase.table("graph_relationships").insert({
            "id": rel_id,
            "workspace_id": workspace_id,
            "source_id": source_id,
            "target_id": target_id,
            "relation_type": relation_type.value,
            "properties": properties or {},
            "weight": weight
        }).execute()

        return rel_id

    async def get_entity_neighbors(
        self,
        workspace_id: str,
        entity_id: str,
        relation_types: list[RelationType] | None = None,
        depth: int = 1
    ) -> list[tuple[Entity, Relationship]]:
        """Get neighboring entities up to N hops."""

        # For depth=1, simple query
        query = self.supabase.table("graph_relationships").select(
            "*, source:graph_entities!source_id(*), target:graph_entities!target_id(*)"
        ).eq("workspace_id", workspace_id).or_(
            f"source_id.eq.{entity_id},target_id.eq.{entity_id}"
        )

        if relation_types:
            types = [r.value for r in relation_types]
            query = query.in_("relation_type", types)

        result = query.execute()

        neighbors = []
        for row in result.data:
            # Determine which end is the neighbor
            if row["source_id"] == entity_id:
                neighbor_data = row["target"]
            else:
                neighbor_data = row["source"]

            entity = Entity(
                id=neighbor_data["id"],
                workspace_id=neighbor_data["workspace_id"],
                entity_type=EntityType(neighbor_data["entity_type"]),
                name=neighbor_data["name"],
                properties=neighbor_data["properties"]
            )

            rel = Relationship(
                id=row["id"],
                workspace_id=row["workspace_id"],
                source_id=row["source_id"],
                target_id=row["target_id"],
                relation_type=RelationType(row["relation_type"]),
                properties=row["properties"],
                weight=row["weight"]
            )

            neighbors.append((entity, rel))

        return neighbors

    async def query_subgraph(
        self,
        workspace_id: str,
        start_entity_type: EntityType,
        start_name: str,
        path_pattern: list[RelationType]
    ) -> list[list[Entity]]:
        """Query for paths matching a pattern."""

        # Find starting entities
        start_result = self.supabase.table("graph_entities").select("*").eq(
            "workspace_id", workspace_id
        ).eq("entity_type", start_entity_type.value).ilike(
            "name", f"%{start_name}%"
        ).execute()

        if not start_result.data:
            return []

        paths = []
        for start in start_result.data:
            path = [Entity(
                id=start["id"],
                workspace_id=start["workspace_id"],
                entity_type=EntityType(start["entity_type"]),
                name=start["name"],
                properties=start["properties"]
            )]

            # Follow path pattern
            current_id = start["id"]
            for rel_type in path_pattern:
                neighbors = await self.get_entity_neighbors(
                    workspace_id, current_id, [rel_type]
                )
                if neighbors:
                    entity, _ = neighbors[0]
                    path.append(entity)
                    current_id = entity.id
                else:
                    break

            if len(path) == len(path_pattern) + 1:
                paths.append(path)

        return paths

    async def build_icp_context(self, workspace_id: str, icp_id: str) -> str:
        """Build rich context for an ICP from graph."""

        context_parts = []

        # Get ICP entity
        icp_result = self.supabase.table("graph_entities").select("*").eq(
            "id", icp_id
        ).single().execute()

        if not icp_result.data:
            return ""

        icp = icp_result.data
        context_parts.append(f"ICP: {icp['name']}")

        # Get all relationships
        neighbors = await self.get_entity_neighbors(workspace_id, icp_id)

        # Group by relationship type
        grouped = {}
        for entity, rel in neighbors:
            rel_type = rel.relation_type.value
            if rel_type not in grouped:
                grouped[rel_type] = []
            grouped[rel_type].append(entity.name)

        for rel_type, names in grouped.items():
            context_parts.append(f"{rel_type}: {', '.join(names)}")

        return "\n".join(context_parts)
```

---

## 4. EPISODIC MEMORY (Conversation History)

**Purpose**: Store conversation history, feedback, and user preferences.

```python
# backend/memory/episodic_store.py
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal
from supabase import Client

@dataclass
class Episode:
    id: str
    workspace_id: str
    session_id: str
    episode_type: Literal["conversation", "execution", "feedback"]
    content: dict[str, Any]
    timestamp: datetime
    importance: float = 1.0  # For decay calculations

class EpisodicMemory:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.decay_factor = 0.95  # Memory importance decays over time

    async def add_episode(
        self,
        workspace_id: str,
        session_id: str,
        episode_type: str,
        content: dict[str, Any],
        importance: float = 1.0
    ) -> str:
        """Add a new episode."""
        import uuid

        episode_id = str(uuid.uuid4())

        self.supabase.table("episodic_memory").insert({
            "id": episode_id,
            "workspace_id": workspace_id,
            "session_id": session_id,
            "episode_type": episode_type,
            "content": content,
            "importance": importance,
            "created_at": "now()"
        }).execute()

        return episode_id

    async def get_recent_episodes(
        self,
        workspace_id: str,
        episode_types: list[str] | None = None,
        limit: int = 20,
        session_id: str | None = None
    ) -> list[Episode]:
        """Get recent episodes with decay applied."""

        query = self.supabase.table("episodic_memory").select("*").eq(
            "workspace_id", workspace_id
        ).order("created_at", desc=True).limit(limit)

        if episode_types:
            query = query.in_("episode_type", episode_types)

        if session_id:
            query = query.eq("session_id", session_id)

        result = query.execute()

        episodes = []
        now = datetime.now()

        for row in result.data:
            created = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            age_hours = (now - created.replace(tzinfo=None)).total_seconds() / 3600

            # Apply decay
            decayed_importance = row["importance"] * (self.decay_factor ** (age_hours / 24))

            episodes.append(Episode(
                id=row["id"],
                workspace_id=row["workspace_id"],
                session_id=row["session_id"],
                episode_type=row["episode_type"],
                content=row["content"],
                timestamp=created,
                importance=decayed_importance
            ))

        return episodes

    async def get_conversation_context(
        self,
        workspace_id: str,
        session_id: str,
        max_messages: int = 10
    ) -> list[dict]:
        """Get conversation history for context."""

        episodes = await self.get_recent_episodes(
            workspace_id=workspace_id,
            session_id=session_id,
            episode_types=["conversation"],
            limit=max_messages
        )

        # Sort by timestamp ascending (oldest first)
        episodes.sort(key=lambda e: e.timestamp)

        return [e.content for e in episodes]

    async def get_user_preferences(
        self,
        workspace_id: str
    ) -> dict[str, Any]:
        """Extract user preferences from feedback episodes."""

        episodes = await self.get_recent_episodes(
            workspace_id=workspace_id,
            episode_types=["feedback"],
            limit=50
        )

        preferences = {
            "tone_preferences": [],
            "channel_preferences": [],
            "time_preferences": [],
            "content_likes": [],
            "content_dislikes": []
        }

        for episode in episodes:
            content = episode.content
            if content.get("type") == "tone_feedback":
                preferences["tone_preferences"].append(content.get("preferred_tone"))
            elif content.get("type") == "content_feedback":
                if content.get("liked"):
                    preferences["content_likes"].append(content.get("content_type"))
                else:
                    preferences["content_dislikes"].append(content.get("content_type"))

        return preferences

    async def summarize_session(
        self,
        workspace_id: str,
        session_id: str
    ) -> str:
        """Summarize a session for long-term storage."""
        from langchain_google_vertexai import ChatVertexAI

        episodes = await self.get_recent_episodes(
            workspace_id=workspace_id,
            session_id=session_id,
            limit=100
        )

        if not episodes:
            return ""

        # Format episodes
        episode_text = "\n".join([
            f"[{e.episode_type}] {e.content}"
            for e in episodes
        ])

        # Use LLM to summarize
        llm = ChatVertexAI(model_name="gemini-2.0-flash-lite", max_tokens=500)

        summary = await llm.ainvoke(
            f"Summarize this session into key points:\n\n{episode_text}"
        )

        return summary.content
```

---

## 5. WORKING MEMORY (Current Session)

**Purpose**: Fast access to current session state, recent context.

**Storage**: Redis (Upstash) for speed

```python
# backend/memory/working_memory.py
from upstash_redis import Redis
from dataclasses import dataclass
from typing import Any
import json

@dataclass
class WorkingMemoryState:
    session_id: str
    workspace_id: str
    user_id: str

    # Current context
    current_agent: str | None
    current_task: str | None

    # Recent messages (last 5)
    recent_messages: list[dict]

    # Loaded context
    foundation_summary: str | None
    active_icps: list[dict]

    # Execution state
    pending_approvals: list[dict]
    last_output: dict | None

class WorkingMemory:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.ttl = 3600  # 1 hour TTL

    def _key(self, session_id: str) -> str:
        return f"working_memory:{session_id}"

    async def initialize(
        self,
        session_id: str,
        workspace_id: str,
        user_id: str
    ) -> WorkingMemoryState:
        """Initialize working memory for a new session."""

        state = WorkingMemoryState(
            session_id=session_id,
            workspace_id=workspace_id,
            user_id=user_id,
            current_agent=None,
            current_task=None,
            recent_messages=[],
            foundation_summary=None,
            active_icps=[],
            pending_approvals=[],
            last_output=None
        )

        await self.save(state)
        return state

    async def get(self, session_id: str) -> WorkingMemoryState | None:
        """Get current working memory state."""

        data = self.redis.get(self._key(session_id))
        if not data:
            return None

        parsed = json.loads(data)
        return WorkingMemoryState(**parsed)

    async def save(self, state: WorkingMemoryState):
        """Save working memory state."""

        data = {
            "session_id": state.session_id,
            "workspace_id": state.workspace_id,
            "user_id": state.user_id,
            "current_agent": state.current_agent,
            "current_task": state.current_task,
            "recent_messages": state.recent_messages[-5:],  # Keep last 5
            "foundation_summary": state.foundation_summary,
            "active_icps": state.active_icps,
            "pending_approvals": state.pending_approvals,
            "last_output": state.last_output
        }

        self.redis.setex(
            self._key(state.session_id),
            self.ttl,
            json.dumps(data)
        )

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """Add a message to working memory."""

        state = await self.get(session_id)
        if not state:
            return

        state.recent_messages.append({
            "role": role,
            "content": content
        })

        await self.save(state)

    async def load_context(
        self,
        session_id: str,
        vector_memory: 'VectorMemory',
        graph_memory: 'GraphMemory'
    ):
        """Load relevant context into working memory."""

        state = await self.get(session_id)
        if not state:
            return

        # Load foundation summary
        from supabase import create_client
        supabase = create_client(...)  # Get client

        foundation = supabase.table("foundations").select(
            "summary"
        ).eq("workspace_id", state.workspace_id).single().execute()

        if foundation.data:
            state.foundation_summary = foundation.data["summary"]

        # Load active ICPs
        icps = supabase.table("icp_profiles").select("*").eq(
            "workspace_id", state.workspace_id
        ).eq("is_primary", True).execute()

        state.active_icps = icps.data or []

        await self.save(state)
```

---

## 6. MEMORY CONTROLLER (Unified Access)

```python
# backend/memory/controller.py
from .vector_store import VectorMemory, MemoryType
from .graph_store import GraphMemory, EntityType
from .episodic_store import EpisodicMemory
from .working_memory import WorkingMemory
from dataclasses import dataclass

@dataclass
class UnifiedContext:
    """Combined context from all memory systems."""
    foundation_summary: str
    relevant_memories: list[str]  # From vector search
    graph_context: str  # From graph traversal
    recent_conversation: list[dict]  # From episodic
    user_preferences: dict  # From feedback
    working_state: dict  # Current session

class MemoryController:
    def __init__(
        self,
        vector_memory: VectorMemory,
        graph_memory: GraphMemory,
        episodic_memory: EpisodicMemory,
        working_memory: WorkingMemory
    ):
        self.vector = vector_memory
        self.graph = graph_memory
        self.episodic = episodic_memory
        self.working = working_memory

    async def get_unified_context(
        self,
        workspace_id: str,
        session_id: str,
        query: str,
        agent_type: str
    ) -> UnifiedContext:
        """Get unified context from all memory systems."""

        # 1. Get working memory state
        working_state = await self.working.get(session_id)

        # 2. Vector search for relevant memories
        vector_context = await self.vector.get_context_for_agent(
            workspace_id=workspace_id,
            query=query,
            agent_type=agent_type
        )

        # 3. Graph context for ICPs
        graph_context = ""
        if working_state and working_state.active_icps:
            for icp in working_state.active_icps[:2]:  # Top 2 ICPs
                icp_context = await self.graph.build_icp_context(
                    workspace_id, icp["id"]
                )
                graph_context += f"\n{icp_context}"

        # 4. Recent conversation
        conversation = await self.episodic.get_conversation_context(
            workspace_id=workspace_id,
            session_id=session_id,
            max_messages=5
        )

        # 5. User preferences
        preferences = await self.episodic.get_user_preferences(workspace_id)

        return UnifiedContext(
            foundation_summary=working_state.foundation_summary if working_state else "",
            relevant_memories=vector_context.split("\n\n") if vector_context else [],
            graph_context=graph_context,
            recent_conversation=conversation,
            user_preferences=preferences,
            working_state=working_state.__dict__ if working_state else {}
        )

    async def vectorize_onboarding(
        self,
        workspace_id: str,
        onboarding_data: dict
    ):
        """Vectorize complete onboarding for fast retrieval."""

        # Store foundation summary
        if onboarding_data.get("foundation_summary"):
            await self.vector.store(
                workspace_id=workspace_id,
                memory_type=MemoryType.FOUNDATION,
                content=onboarding_data["foundation_summary"],
                metadata={"source": "onboarding", "step": "final"}
            )

        # Store each ICP
        for icp in onboarding_data.get("icps", []):
            icp_text = f"""
            ICP: {icp['name']}
            Tagline: {icp['tagline']}
            Demographics: {icp['demographics']}
            Psychographics: {icp['psychographics']}
            Behaviors: {icp['behaviors']}
            """

            await self.vector.store(
                workspace_id=workspace_id,
                memory_type=MemoryType.ICP,
                content=icp_text,
                metadata={"icp_id": icp["id"], "name": icp["name"]},
                chunk_id=f"icp-{icp['id']}"
            )

        # Store research findings
        for finding in onboarding_data.get("research", []):
            await self.vector.store(
                workspace_id=workspace_id,
                memory_type=MemoryType.RESEARCH,
                content=finding["content"],
                metadata=finding.get("metadata", {})
            )

        # Build knowledge graph
        await self._build_onboarding_graph(workspace_id, onboarding_data)

    async def _build_onboarding_graph(
        self,
        workspace_id: str,
        data: dict
    ):
        """Build knowledge graph from onboarding data."""

        # Add company entity
        company_id = await self.graph.add_entity(
            workspace_id=workspace_id,
            entity_type=EntityType.COMPANY,
            name=data.get("company_name", "Company"),
            properties={"industry": data.get("industry")}
        )

        # Add ICPs and relationships
        for icp in data.get("icps", []):
            icp_entity_id = await self.graph.add_entity(
                workspace_id=workspace_id,
                entity_type=EntityType.ICP,
                name=icp["name"],
                properties=icp
            )

            # Add pain points
            for pain in icp.get("psychographics", {}).get("fears", []):
                pain_id = await self.graph.add_entity(
                    workspace_id=workspace_id,
                    entity_type=EntityType.PAIN_POINT,
                    name=pain,
                    properties={}
                )
                await self.graph.add_relationship(
                    workspace_id=workspace_id,
                    source_id=icp_entity_id,
                    target_id=pain_id,
                    relation_type=RelationType.ICP_HAS_PAIN
                )

            # Add channels
            for channel in icp.get("behaviors", {}).get("hangouts", []):
                channel_id = await self.graph.add_entity(
                    workspace_id=workspace_id,
                    entity_type=EntityType.CHANNEL,
                    name=channel,
                    properties={}
                )
                await self.graph.add_relationship(
                    workspace_id=workspace_id,
                    source_id=icp_entity_id,
                    target_id=channel_id,
                    relation_type=RelationType.ICP_USES_CHANNEL
                )
```

---

## 7. CONTEXT COMPRESSION

**Purpose**: Compress large contexts to fit LLM context windows efficiently.

```python
# backend/memory/compression.py
from langchain_google_vertexai import ChatVertexAI

class ContextCompressor:
    def __init__(self):
        self.llm = ChatVertexAI(
            model_name="gemini-2.0-flash-lite",
            max_tokens=1000
        )
        self.max_context_tokens = 4000

    async def compress(
        self,
        context: UnifiedContext,
        query: str,
        target_tokens: int = 2000
    ) -> str:
        """Compress context to target token count."""

        # Build full context
        full_context = f"""
FOUNDATION:
{context.foundation_summary}

RELEVANT MEMORIES:
{chr(10).join(context.relevant_memories)}

KNOWLEDGE GRAPH:
{context.graph_context}

RECENT CONVERSATION:
{chr(10).join([f"{m['role']}: {m['content']}" for m in context.recent_conversation])}

USER PREFERENCES:
{context.user_preferences}
"""

        # Estimate tokens (rough: 4 chars per token)
        estimated_tokens = len(full_context) // 4

        if estimated_tokens <= target_tokens:
            return full_context

        # Compress using LLM
        compressed = await self.llm.ainvoke(f"""
Compress this context to the essential information needed to answer: "{query}"

Keep:
- Key facts about the business
- Relevant ICP details
- Recent conversation context
- User preferences that matter

Remove:
- Redundant information
- Details not relevant to the query
- Verbose descriptions

CONTEXT:
{full_context}

COMPRESSED (under {target_tokens} tokens):
""")

        return compressed.content
```
