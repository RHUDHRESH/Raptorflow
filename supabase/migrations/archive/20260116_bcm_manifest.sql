-- Business Context Manifest (BCM) table
-- Migration: 20260116_bcm_manifest.sql

CREATE TABLE IF NOT EXISTS public.business_context_manifests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    manifest JSONB NOT NULL,
    checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, version)
);

-- Index for fast lookup by workspace
CREATE INDEX IF NOT EXISTS idx_bcm_workspace ON public.business_context_manifests(workspace_id);

-- Enable Row Level Security
ALTER TABLE public.business_context_manifests ENABLE ROW LEVEL SECURITY;
