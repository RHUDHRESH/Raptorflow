-- Migration for enhanced Muse assets management system
-- This extends the existing muse_assets table with required fields for CRUD operations

-- Add new columns to existing muse_assets table
ALTER TABLE muse_assets
ADD COLUMN IF NOT EXISTS title text NOT NULL DEFAULT '',
ADD COLUMN IF NOT EXISTS folder text NOT NULL DEFAULT 'default',
ADD COLUMN IF NOT EXISTS prompt text,
ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1,
ADD COLUMN IF NOT EXISTS is_deleted boolean NOT NULL DEFAULT false,
ADD COLUMN IF NOT EXISTS deleted_at timestamptz,
ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Update existing records to have default values
UPDATE muse_assets SET title = COALESCE(metadata->>'title', 'Untitled Asset') WHERE title = '';
UPDATE muse_assets SET folder = COALESCE(metadata->>'folder', 'default') WHERE folder = 'default';

-- Add constraints for allowed asset types
ALTER TABLE muse_assets
ADD CONSTRAINT IF NOT EXISTS check_asset_type
CHECK (asset_type IN ('email', 'tagline', 'social-post', 'ad-copy', 'landing-page', 'blog-post', 'press-release', 'video-script', 'image-prompt', 'other'));

-- Add constraint for status values
ALTER TABLE muse_assets
ADD CONSTRAINT IF NOT EXISTS check_status
CHECK (status IN ('draft', 'ready', 'archived', 'deleted'));

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_muse_assets_workspace_folder
ON muse_assets (workspace_id, folder) WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_muse_assets_type_status
ON muse_assets (asset_type, status) WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_muse_assets_title
ON muse_assets (title) WHERE is_deleted = false;

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_muse_assets_search
ON muse_assets USING gin(search_vector) WHERE is_deleted = false;

-- Update trigger for search_vector and updated_at
CREATE OR REPLACE FUNCTION update_muse_assets_triggers()
RETURNS TRIGGER AS $$
BEGIN
    -- Update search_vector for full-text search
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.prompt, '')), 'C') ||
        setweight(to_tsvector('english', array_to_string(NEW.tags, ' ')), 'D');

    -- Update updated_at timestamp
    NEW.updated_at = now();

    -- Handle soft delete
    IF NEW.status = 'deleted' AND OLD.status != 'deleted' THEN
        NEW.is_deleted = true;
        NEW.deleted_at = now();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_update_muse_assets ON muse_assets;
CREATE TRIGGER trigger_update_muse_assets
    BEFORE INSERT OR UPDATE ON muse_assets
    FOR EACH ROW EXECUTE FUNCTION update_muse_assets_triggers();

-- Initialize search vectors for existing records
UPDATE muse_assets SET search_vector =
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(content, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(prompt, '')), 'C') ||
    setweight(to_tsvector('english', array_to_string(tags, ' ')), 'D')
WHERE search_vector IS NULL;
