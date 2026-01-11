-- Muse Assets table (product-specific)
-- Migration: 20240107_muse_assets.sql
-- Description: Content assets for creative inspiration and management with workspace isolation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Muse Assets table
CREATE TABLE IF NOT EXISTS public.muse_assets (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Workspace isolation
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Asset metadata
    title TEXT NOT NULL,
    description TEXT,
    asset_type TEXT NOT NULL, -- e.g., 'image', 'video', 'audio', 'text', 'document', 'infographic', 'template'
    category TEXT NOT NULL, -- e.g., 'inspiration', 'reference', 'template', 'generated', 'uploaded'
    status TEXT DEFAULT 'draft', -- draft, processing, ready, published, archived, deleted
    priority INTEGER DEFAULT 3, -- 1=High, 2=Medium, 3=Low, 4=Background

    -- Content and media
    content TEXT,
    content_type TEXT, -- e.g., 'text/plain', 'text/markdown', 'image/jpeg', 'video/mp4', 'audio/mp3'
    content_size INTEGER DEFAULT 0, -- Size in bytes
    content_url TEXT, -- URL to stored content (GCS, S3, etc.)
    content_hash TEXT, -- Hash for deduplication

    -- File information
    file_name TEXT,
    file_extension TEXT,
    mime_type TEXT,
    dimensions JSONB DEFAULT '{}', -- For images: {width, height}, for videos: {duration, fps}

    -- AI generation metadata
    ai_generated BOOLEAN DEFAULT FALSE,
    ai_model TEXT, -- Model used for generation
    ai_prompt TEXT, -- Original prompt used
    ai_parameters JSONB DEFAULT '{}', -- Generation parameters
    ai_confidence DECIMAL(3,2) DEFAULT 0.00,
    ai_processing_time INTEGER, -- Processing time in milliseconds
    ai_generated_at TIMESTAMPTZ,

    -- Creative inspiration data
    inspiration_source TEXT, -- e.g., 'user_input', 'foundation', 'icp', 'campaign', 'move'
    inspiration_context JSONB DEFAULT '{}', -- Context that inspired this asset
    creative_brief TEXT, -- Brief description of creative intent
    style_preferences JSONB DEFAULT '{}', -- Style preferences and guidelines

    -- Asset relationships
    foundation_id UUID REFERENCES foundations(id) ON DELETE SET NULL,
    icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    move_id UUID REFERENCES moves(id) ON DELETE SET NULL,
    parent_asset_id UUID REFERENCES muse_assets(id) ON DELETE SET NULL, -- For variations or derivatives

    -- Usage and performance
    usage_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2) DEFAULT 0.00,

    -- Quality and moderation
    quality_score DECIMAL(3,2) DEFAULT 0.00, -- 0.00 to 1.00
    moderation_status TEXT DEFAULT 'pending', -- pending, approved, rejected, flagged
    moderation_notes TEXT,
    moderated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    moderated_at TIMESTAMPTZ,

    -- Tags and metadata
    tags JSONB DEFAULT '[]', -- Array of tags for categorization
    keywords JSONB DEFAULT '[]', -- SEO keywords
    attributes JSONB DEFAULT '{}', -- Custom attributes
    metadata JSONB DEFAULT '{}', -- Additional metadata

    -- Versioning
    version INTEGER DEFAULT 1,
    is_latest BOOLEAN DEFAULT TRUE,
    version_notes TEXT,

    -- Ownership and tracking
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ,

    -- Constraints
    CHECK (priority >= 1 AND priority <= 4),
    CHECK (content_size >= 0),
    CHECK (usage_count >= 0),
    CHECK (download_count >= 0),
    CHECK (share_count >= 0),
    CHECK (view_count >= 0),
    CHECK (like_count >= 0),
    CHECK (conversion_rate >= 0 AND conversion_rate <= 100),
    CHECK (quality_score >= 0 AND quality_score <= 1),
    CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    CHECK (version >= 1)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_muse_assets_workspace_id ON public.muse_assets(workspace_id);
CREATE INDEX IF NOT EXISTS idx_muse_assets_asset_type ON public.muse_assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_muse_assets_category ON public.muse_assets(category);
CREATE INDEX IF NOT EXISTS idx_muse_assets_status ON public.muse_assets(status);
CREATE INDEX IF NOT EXISTS idx_muse_assets_priority ON public.muse_assets(priority);
CREATE INDEX IF NOT EXISTS idx_muse_assets_ai_generated ON public.muse_assets(ai_generated);
CREATE INDEX IF NOT EXISTS idx_muse_assets_content_hash ON public.muse_assets(content_hash);
CREATE INDEX IF NOT EXISTS idx_muse_assets_created_at ON public.muse_assets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_muse_assets_created_by ON public.muse_assets(created_by);
CREATE INDEX IF NOT EXISTS idx_muse_assets_published_at ON public.muse_assets(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_muse_assets_usage_count ON public.muse_assets(usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_muse_assets_quality_score ON public.muse_assets(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_muse_assets_foundation_id ON public.muse_assets(foundation_id);
CREATE INDEX IF NOT EXISTS idx_muse_assets_icp_profile_id ON public.muse_assets(icp_profile_id);
CREATE INDEX IF NOT EXISTS idx_muse_assets_campaign_id ON public.muse_assets(campaign_id);
CREATE INDEX IF NOT EXISTS idx_muse_assets_move_id ON public.muse_assets(move_id);
CREATE INDEX IF NOT EXISTS idx_muse_assets_parent_asset_id ON public.muse_assets(parent_asset_id);
CREATE INDEX IF NOT EXISTS idx_muse_assets_is_latest ON public.muse_assets(is_latest);
CREATE INDEX IF NOT EXISTS idx_muse_assets_tags ON public.muse_assets USING GIN (tags) WITH (jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_muse_assets_keywords ON public.muse_assets USING GIN (keywords) WITH (jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_muse_assets_attributes ON public.muse_assets USING GIN (attributes) WITH (jsonb_path_ops);

-- Vector index for semantic search
CREATE INDEX IF NOT EXISTS idx_muse_assets_content_embedding
    ON public.muse_assets USING ivfflat (content_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Unique constraint on content hash per workspace
CREATE UNIQUE INDEX IF NOT EXISTS idx_muse_assets_unique_content_hash
    ON public.muse_assets(workspace_id, content_hash) WHERE content_hash IS NOT NULL;

-- Unique constraint on title per workspace (for non-draft assets)
CREATE UNIQUE INDEX IF NOT EXISTS idx_muse_assets_unique_title
    ON public.muse_assets(workspace_id, title) WHERE status != 'draft';

-- Trigger for updated_at
CREATE TRIGGER muse_assets_updated_at
    BEFORE UPDATE ON public.muse_assets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE public.muse_assets ENABLE ROW LEVEL SECURITY;
