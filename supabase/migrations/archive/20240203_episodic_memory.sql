-- Episodic memory tables for conversation and session tracking
-- Stores conversation episodes and their metadata

CREATE TABLE IF NOT EXISTS conversation_episodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Session identification
    session_id UUID NOT NULL,

    -- Episode classification
    episode_type TEXT NOT NULL CHECK (episode_type IN (
        'conversation', 'task', 'approval', 'feedback', 'decision', 'research'
    )),

    -- Episode content
    title TEXT,
    summary TEXT,
    content TEXT NOT NULL,

    -- Structured data
    key_decisions JSONB DEFAULT '[]',
    entities_mentioned JSONB DEFAULT '[]',
    action_items JSONB DEFAULT '[]',

    -- Metadata
    metadata JSONB DEFAULT '{}',
    importance DECIMAL(3,2) DEFAULT 1.0 CHECK (importance >= 0.0 AND importance <= 10.0),
    tags TEXT[] DEFAULT '{}',

    -- Timing information
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN ended_at IS NOT NULL THEN
                EXTRACT(EPOCH FROM (ended_at - started_at))::INTEGER
            ELSE NULL
        END
    ) STORED,

    -- Token usage tracking
    token_count INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,

    -- Search and indexing
    embedding vector(384),

    -- Constraints
    CONSTRAINT valid_episode_timing CHECK (ended_at IS NULL OR ended_at >= started_at)
);

-- Indexes for performance
CREATE INDEX idx_conversation_episodes_workspace_id ON conversation_episodes(workspace_id);
CREATE INDEX idx_conversation_episodes_session_id ON conversation_episodes(session_id);
CREATE INDEX idx_conversation_episodes_type ON conversation_episodes(episode_type);
CREATE INDEX idx_conversation_episodes_workspace_session ON conversation_episodes(workspace_id, session_id);
CREATE INDEX idx_conversation_episodes_started_at ON conversation_episodes(started_at);
CREATE INDEX idx_conversation_episodes_importance ON conversation_episodes(importance);
CREATE INDEX idx_conversation_episodes_tags ON conversation_episodes USING GIN(tags);

-- Vector index for semantic search
CREATE INDEX idx_conversation_episodes_embedding ON conversation_episodes
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Full-text search index
CREATE INDEX idx_conversation_episodes_content_fts ON conversation_episodes
USING GIN(to_tsvector('english', content || ' ' || COALESCE(summary, '') || ' ' || COALESCE(title, '')));

-- Function to get session episodes with pagination
CREATE OR REPLACE FUNCTION get_session_episodes(
    p_workspace_id UUID,
    p_session_id UUID,
    p_limit INTEGER DEFAULT 50,
    p_offset INTEGER DEFAULT 0,
    p_episode_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    episode_id UUID,
    episode_type TEXT,
    title TEXT,
    summary TEXT,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    message_count INTEGER,
    importance DECIMAL(3,2),
    tags TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.episode_type,
        e.title,
        e.summary,
        e.started_at,
        e.ended_at,
        e.duration_seconds,
        e.message_count,
        e.importance,
        e.tags
    FROM conversation_episodes e
    WHERE e.workspace_id = p_workspace_id
    AND e.session_id = p_session_id
    AND (p_episode_type IS NULL OR e.episode_type = p_episode_type)
    ORDER BY e.started_at DESC
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- Function to search episodes by content
CREATE OR REPLACE FUNCTION search_episodes(
    p_workspace_id UUID,
    p_query TEXT,
    p_limit INTEGER DEFAULT 10,
    p_episode_types TEXT[] DEFAULT NULL
)
RETURNS TABLE (
    episode_id UUID,
    episode_type TEXT,
    title TEXT,
    summary TEXT,
    started_at TIMESTAMPTZ,
    relevance_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.episode_type,
        e.title,
        e.summary,
        e.started_at,
        ts_rank(
            to_tsvector('english', e.content || ' ' || COALESCE(e.summary, '') || ' ' || COALESCE(e.title, '')),
            plainto_tsquery('english', p_query)
        )::REAL as relevance_score
    FROM conversation_episodes e
    WHERE e.workspace_id = p_workspace_id
    AND to_tsvector('english', e.content || ' ' || COALESCE(e.summary, '') || ' ' || COALESCE(e.title, ''))
        @@ plainto_tsquery('english', p_query)
    AND (p_episode_types IS NULL OR e.episode_type = ANY(p_episode_types))
    ORDER BY relevance_score DESC, e.started_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE conversation_episodes IS 'Episodic memory for storing conversation episodes and sessions';
COMMENT ON COLUMN conversation_episodes.session_id IS 'Unique identifier for a conversation session';
COMMENT ON COLUMN conversation_episodes.episode_type IS 'Type of episode (conversation, task, approval, etc.)';
COMMENT ON COLUMN conversation_episodes.key_decisions IS 'Array of important decisions made during the episode';
COMMENT ON COLUMN conversation_episodes.entities_mentioned IS 'Array of entities mentioned during the episode';
COMMENT ON COLUMN conversation_episodes.action_items IS 'Array of action items identified during the episode';
COMMENT ON COLUMN conversation_episodes.importance IS 'Importance score of the episode (0.0-10.0)';
COMMENT ON COLUMN conversation_episodes.embedding IS 'Vector embedding for semantic similarity search';
COMMENT ON FUNCTION get_session_episodes IS 'Get paginated episodes for a session';
COMMENT ON FUNCTION search_episodes IS 'Search episodes by content with relevance scoring';
