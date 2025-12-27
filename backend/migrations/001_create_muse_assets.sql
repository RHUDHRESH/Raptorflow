CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS muse_assets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id uuid NOT NULL,
    content text NOT NULL,
    asset_type text NOT NULL DEFAULT 'text',
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    embedding vector(768),
    status text NOT NULL DEFAULT 'ready',
    quality_score numeric,
    generation_prompt text,
    generation_model text,
    generation_tokens integer,
    tags text[],
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_muse_assets_workspace_id
    ON muse_assets (workspace_id);

CREATE INDEX IF NOT EXISTS idx_muse_assets_metadata_type
    ON muse_assets ((metadata->>'type'));

CREATE INDEX IF NOT EXISTS idx_muse_assets_embedding
    ON muse_assets USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
