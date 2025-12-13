-- Enable pgvector extension for vector storage and similarity search
-- This enables RaptorFlow's memory and learning capabilities

-- Enable the extension (requires superuser privileges in production)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create memory tables for the v2 agentic system

-- =====================================================
-- VECTOR MEMORY TABLES
-- =====================================================

-- Embeddings storage for RAG and semantic search
CREATE TABLE IF NOT EXISTS memory_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL, -- 'market_research', 'brand_memory', 'user_preference', etc.
    content_id VARCHAR(255), -- Reference to original content
    content TEXT NOT NULL, -- Original text content
    embedding vector(768), -- OpenAI ada-002 dimension (adjust based on your model)
    metadata JSONB DEFAULT '{}', -- Additional metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector search index for performance
CREATE INDEX IF NOT EXISTS memory_embeddings_embedding_idx
ON memory_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100); -- Adjust based on data size

-- Content type index for filtering
CREATE INDEX IF NOT EXISTS memory_embeddings_content_type_idx
ON memory_embeddings(content_type);

-- User index for partitioning
CREATE INDEX IF NOT EXISTS memory_embeddings_user_idx
ON memory_embeddings(user_id);

-- =====================================================
-- BRAND MEMORY TABLES
-- =====================================================

-- Brand voice and style guidelines
CREATE TABLE IF NOT EXISTS brand_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    brand_name VARCHAR(255),
    voice_tone JSONB DEFAULT '{}', -- {'formal': 0.8, 'conversational': 0.6, etc.}
    style_guidelines JSONB DEFAULT '{}', -- Writing style preferences
    brand_colors JSONB DEFAULT '[]', -- Color palette
    brand_values TEXT[], -- Core brand values
    competitor_mentions JSONB DEFAULT '[]', -- How to handle competitors
    taboo_topics TEXT[], -- Topics to avoid
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- USER PREFERENCE TABLES
-- =====================================================

-- Learned user preferences from interactions
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    preference_type VARCHAR(100) NOT NULL, -- 'tone', 'length', 'complexity', 'channels', etc.
    preference_value JSONB NOT NULL, -- Flexible preference data
    confidence_score DECIMAL(3,2) DEFAULT 0.5, -- How confident we are in this preference
    sample_size INTEGER DEFAULT 1, -- Number of interactions this is based on
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Preference learning events
CREATE TABLE IF NOT EXISTS preference_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- 'thumbs_up', 'thumbs_down', 'edit', 'regenerate'
    original_output TEXT,
    modified_output TEXT,
    feedback_text TEXT,
    metadata JSONB DEFAULT '{}', -- Additional context
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- TEMPLATE WEIGHTING TABLES
-- =====================================================

-- Success rates and performance of different templates/assets
CREATE TABLE IF NOT EXISTS template_weights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    template_type VARCHAR(100) NOT NULL, -- 'email', 'landing_page', 'ad_copy', etc.
    template_id VARCHAR(255) NOT NULL,
    template_name VARCHAR(255),
    total_uses INTEGER DEFAULT 0,
    successful_uses INTEGER DEFAULT 0,
    success_rate DECIMAL(5,4) DEFAULT 0,
    avg_performance_score DECIMAL(3,2), -- 0-1 scale
    last_used TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- RAW SOURCE MATERIAL TABLES
-- =====================================================

-- Store crawled/scraped content before embedding
CREATE TABLE IF NOT EXISTS raw_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(50) NOT NULL, -- 'rss', 'twitter', 'reddit', 'news', 'web'
    source_url TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    author VARCHAR(255),
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    relevance_score DECIMAL(3,2), -- AI-determined relevance
    topics TEXT[], -- Extracted topics
    sentiment DECIMAL(3,2), -- -1 to 1 scale
    metadata JSONB DEFAULT '{}',
    processed BOOLEAN DEFAULT FALSE
);

-- =====================================================
-- BEHAVIOR TRACKING TABLES
-- =====================================================

-- User behavior patterns for addiction loop optimization
CREATE TABLE IF NOT EXISTS user_behavior_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL, -- 'workflow_started', 'agent_output_viewed', 'feedback_given', etc.
    event_data JSONB DEFAULT '{}',
    session_id VARCHAR(255), -- For session tracking
    user_agent TEXT, -- Browser/client info
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Addiction metrics (ethical tracking only)
CREATE TABLE IF NOT NULL EXISTS addiction_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
    daily_active_sessions INTEGER DEFAULT 0,
    total_session_duration INTEGER DEFAULT 0, -- minutes
    workflows_completed INTEGER DEFAULT 0,
    feedback_given INTEGER DEFAULT 0,
    feature_adoption_rate DECIMAL(5,4), -- Features used / total available
    engagement_score DECIMAL(3,2), -- Calculated engagement metric
    UNIQUE(user_id, metric_date)
);

-- =====================================================
-- RLS POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE memory_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE preference_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_weights ENABLE ROW LEVEL SECURITY;
ALTER TABLE raw_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_behavior_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE addiction_metrics ENABLE ROW LEVEL SECURITY;

-- RLS Policies (users can only access their own data)
CREATE POLICY "Users can access their own embeddings" ON memory_embeddings
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access their own brand memory" ON brand_memory
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access their own preferences" ON user_preferences
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access their own preference events" ON preference_events
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access their own template weights" ON template_weights
    FOR ALL USING (auth.uid() = user_id);

-- Raw sources are generally accessible (for market research)
CREATE POLICY "Users can read raw sources" ON raw_sources
    FOR SELECT USING (true);

-- Admin-only for raw sources writes
CREATE POLICY "Admins can manage raw sources" ON raw_sources
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM auth.users
            WHERE id = auth.uid()
            AND raw_user_meta_data->>'role' = 'admin'
        )
    );

CREATE POLICY "Users can access their own behavior events" ON user_behavior_events
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access their own addiction metrics" ON addiction_metrics
    FOR ALL USING (auth.uid() = user_id);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Vector search performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS memory_embeddings_vector_idx
ON memory_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- User-specific indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS brand_memory_user_idx ON brand_memory(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS user_preferences_user_type_idx ON user_preferences(user_id, preference_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS template_weights_user_type_idx ON template_weights(user_id, template_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS user_behavior_events_user_type_idx ON user_behavior_events(user_id, event_type);

-- Time-based indexes for analytics
CREATE INDEX CONCURRENTLY IF NOT EXISTS preference_events_created_idx ON preference_events(created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS user_behavior_events_created_idx ON user_behavior_events(created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS addiction_metrics_date_idx ON addiction_metrics(metric_date DESC);

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding vector(768),
    match_threshold float DEFAULT 0.8,
    match_count int DEFAULT 10,
    user_filter uuid DEFAULT NULL,
    content_type_filter text DEFAULT NULL
)
RETURNS TABLE(
    id uuid,
    user_id uuid,
    content_type text,
    content_id text,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        me.id,
        me.user_id,
        me.content_type,
        me.content_id,
        me.content,
        me.metadata,
        1 - (me.embedding <=> query_embedding) AS similarity
    FROM memory_embeddings me
    WHERE (user_filter IS NULL OR me.user_id = user_filter)
      AND (content_type_filter IS NULL OR me.content_type = content_type_filter)
      AND 1 - (me.embedding <=> query_embedding) > match_threshold
    ORDER BY me.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to update template weights
CREATE OR REPLACE FUNCTION update_template_weight(
    p_user_id uuid,
    p_template_type text,
    p_template_id text,
    p_success boolean,
    p_performance_score decimal DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO template_weights (
        user_id, template_type, template_id, total_uses, successful_uses,
        success_rate, avg_performance_score, last_used
    ) VALUES (
        p_user_id, p_template_type, p_template_id, 1,
        CASE WHEN p_success THEN 1 ELSE 0 END,
        CASE WHEN p_success THEN 1.0 ELSE 0.0 END,
        p_performance_score, NOW()
    )
    ON CONFLICT (user_id, template_type, template_id)
    DO UPDATE SET
        total_uses = template_weights.total_uses + 1,
        successful_uses = template_weights.successful_uses + CASE WHEN p_success THEN 1 ELSE 0 END,
        success_rate = ROUND(
            (template_weights.successful_uses + CASE WHEN p_success THEN 1 ELSE 0 END)::decimal /
            (template_weights.total_uses + 1), 4
        ),
        avg_performance_score = CASE
            WHEN p_performance_score IS NOT NULL AND template_weights.avg_performance_score IS NOT NULL THEN
                ROUND((template_weights.avg_performance_score + p_performance_score) / 2, 2)
            WHEN p_performance_score IS NOT NULL THEN p_performance_score
            ELSE template_weights.avg_performance_score
        END,
        last_used = NOW();
END;
$$;

-- =====================================================
-- INITIAL SEED DATA
-- =====================================================

-- Insert default brand memory template
INSERT INTO brand_memory (user_id, brand_name, voice_tone, style_guidelines)
SELECT
    id as user_id,
    'Your Brand' as brand_name,
    '{"professional": 0.7, "conversational": 0.6, "authoritative": 0.8}'::jsonb as voice_tone,
    '{"brevity": "prefer_concise", "formality": "business_casual", "humor": "subtle"}'::jsonb as style_guidelines
FROM auth.users
WHERE id NOT IN (SELECT DISTINCT user_id FROM brand_memory)
ON CONFLICT DO NOTHING;

-- Insert default user preferences
INSERT INTO user_preferences (user_id, preference_type, preference_value, confidence_score)
SELECT
    u.id as user_id,
    'tone' as preference_type,
    '"professional"' as preference_value,
    0.5 as confidence_score
FROM auth.users u
WHERE u.id NOT IN (
    SELECT DISTINCT user_id FROM user_preferences WHERE preference_type = 'tone'
)
UNION ALL
SELECT
    u.id as user_id,
    'length' as preference_type,
    '"medium"' as preference_value,
    0.5 as confidence_score
FROM auth.users u
WHERE u.id NOT IN (
    SELECT DISTINCT user_id FROM user_preferences WHERE preference_type = 'length'
)
ON CONFLICT DO NOTHING;


