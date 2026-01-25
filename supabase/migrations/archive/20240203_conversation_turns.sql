-- Conversation turns table for detailed message tracking
-- Stores individual messages within conversation episodes

CREATE TABLE IF NOT EXISTS conversation_turns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Episode association
    episode_id UUID NOT NULL REFERENCES conversation_episodes(id) ON DELETE CASCADE,

    -- Turn information
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,

    -- Tool call information
    tool_calls JSONB DEFAULT '[]',
    tool_results JSONB DEFAULT '[]',

    -- Turn ordering and timing
    turn_index INTEGER NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}',
    token_count INTEGER DEFAULT 0,

    -- Processing information
    processing_time_ms INTEGER,
    model_used TEXT,
    temperature DECIMAL(3,2),

    -- Constraints
    CONSTRAINT unique_turn_order UNIQUE (episode_id, turn_index),
    CONSTRAINT valid_turn_index CHECK (turn_index >= 0)
);

-- Indexes for performance
CREATE INDEX idx_conversation_turns_episode_id ON conversation_turns(episode_id);
CREATE INDEX idx_conversation_turns_role ON conversation_turns(role);
CREATE INDEX idx_conversation_turns_timestamp ON conversation_turns(timestamp);
CREATE INDEX idx_conversation_turns_episode_order ON conversation_turns(episode_id, turn_index);
CREATE INDEX idx_conversation_turns_metadata ON conversation_turns USING GIN(metadata);

-- Function to get conversation turns for an episode
CREATE OR REPLACE FUNCTION get_conversation_turns(
    p_episode_id UUID,
    p_limit INTEGER DEFAULT 100,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    turn_id UUID,
    role TEXT,
    content TEXT,
    tool_calls JSONB,
    tool_results JSONB,
    turn_index INTEGER,
    timestamp TIMESTAMPTZ,
    token_count INTEGER,
    processing_time_ms INTEGER,
    model_used TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        t.role,
        t.content,
        t.tool_calls,
        t.tool_results,
        t.turn_index,
        t.timestamp,
        t.token_count,
        t.processing_time_ms,
        t.model_used
    FROM conversation_turns t
    WHERE t.episode_id = p_episode_id
    ORDER BY t.turn_index ASC
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- Function to get conversation statistics for an episode
CREATE OR REPLACE FUNCTION get_conversation_stats(p_episode_id UUID)
RETURNS TABLE (
    total_turns INTEGER,
    user_turns INTEGER,
    assistant_turns INTEGER,
    tool_turns INTEGER,
    total_tokens INTEGER,
    avg_tokens_per_turn DECIMAL(10,2),
    total_processing_time_ms INTEGER,
    conversation_duration_seconds INTEGER
) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
BEGIN
    -- Get episode timing
    SELECT started_at, ended_at INTO start_time, end_time
    FROM conversation_episodes
    WHERE id = p_episode_id;

    RETURN QUERY
    SELECT
        COUNT(*)::INTEGER as total_turns,
        COUNT(*) FILTER (WHERE role = 'user')::INTEGER as user_turns,
        COUNT(*) FILTER (WHERE role = 'assistant')::INTEGER as assistant_turns,
        COUNT(*) FILTER (WHERE role = 'tool')::INTEGER as tool_turns,
        COALESCE(SUM(token_count), 0)::INTEGER as total_tokens,
        CASE
            WHEN COUNT(*) > 0 THEN
                ROUND(AVG(token_count)::DECIMAL, 2)
            ELSE 0
        END as avg_tokens_per_turn,
        COALESCE(SUM(processing_time_ms), 0)::INTEGER as total_processing_time_ms,
        CASE
            WHEN start_time IS NOT NULL AND end_time IS NOT NULL THEN
                EXTRACT(EPOCH FROM (end_time - start_time))::INTEGER
            ELSE NULL
        END as conversation_duration_seconds
    FROM conversation_turns
    WHERE episode_id = p_episode_id;
END;
$$ LANGUAGE plpgsql;

-- Function to search within conversation turns
CREATE OR REPLACE FUNCTION search_conversation_turns(
    p_workspace_id UUID,
    p_query TEXT,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    turn_id UUID,
    episode_id UUID,
    episode_type TEXT,
    role TEXT,
    content TEXT,
    timestamp TIMESTAMPTZ,
    relevance_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        t.episode_id,
        e.episode_type,
        t.role,
        t.content,
        t.timestamp,
        ts_rank(
            to_tsvector('english', t.content),
            plainto_tsquery('english', p_query)
        )::REAL as relevance_score
    FROM conversation_turns t
    JOIN conversation_episodes e ON t.episode_id = e.id
    WHERE e.workspace_id = p_workspace_id
    AND to_tsvector('english', t.content) @@ plainto_tsquery('english', p_query)
    ORDER BY relevance_score DESC, t.timestamp DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update episode message count when turns are added/removed
CREATE OR REPLACE FUNCTION update_episode_message_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE conversation_episodes
        SET message_count = (
            SELECT COUNT(*) FROM conversation_turns
            WHERE episode_id = NEW.episode_id
        ),
        token_count = (
            SELECT COALESCE(SUM(token_count), 0) FROM conversation_turns
            WHERE episode_id = NEW.episode_id
        )
        WHERE id = NEW.episode_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE conversation_episodes
        SET message_count = (
            SELECT COUNT(*) FROM conversation_turns
            WHERE episode_id = OLD.episode_id
        ),
        token_count = (
            SELECT COALESCE(SUM(token_count), 0) FROM conversation_turns
            WHERE episode_id = OLD.episode_id
        )
        WHERE id = OLD.episode_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_episode_message_count
    AFTER INSERT OR UPDATE OR DELETE ON conversation_turns
    FOR EACH ROW
    EXECUTE FUNCTION update_episode_message_count();

-- Comments for documentation
COMMENT ON TABLE conversation_turns IS 'Individual conversation turns within episodes';
COMMENT ON COLUMN conversation_turns.episode_id IS 'Reference to the parent episode';
COMMENT ON COLUMN conversation_turns.role IS 'Role of the message sender (user, assistant, system, tool)';
COMMENT ON COLUMN conversation_turns.tool_calls IS 'Array of tool calls made in this turn';
COMMENT ON COLUMN conversation_turns.tool_results IS 'Array of tool call results';
COMMENT ON COLUMN conversation_turns.turn_index IS 'Sequential order of the turn within the episode';
COMMENT ON COLUMN conversation_turns.processing_time_ms IS 'Time taken to process this turn in milliseconds';
COMMENT ON COLUMN conversation_turns.model_used IS 'AI model used for generating this turn';
COMMENT ON FUNCTION get_conversation_turns IS 'Get all turns for a specific episode';
COMMENT ON FUNCTION get_conversation_stats IS 'Get conversation statistics for an episode';
COMMENT ON FUNCTION search_conversation_turns IS 'Search within conversation turns across episodes';
COMMENT ON TRIGGER trigger_update_episode_message_count IS 'Update episode statistics when turns change';
