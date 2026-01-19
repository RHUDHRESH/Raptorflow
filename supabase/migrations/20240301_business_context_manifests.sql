-- Migration for Business Context Manifest (BCM) system
-- Version: 1

CREATE TABLE IF NOT EXISTS public.business_context_manifests (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  version_major INTEGER NOT NULL DEFAULT 1,
  version_minor INTEGER NOT NULL DEFAULT 0,
  version_patch INTEGER NOT NULL DEFAULT 0,
  checksum TEXT NOT NULL,
  content JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT version_check CHECK (
    version_major >= 1 AND
    version_minor >= 0 AND
    version_patch >= 0
  ),
  CONSTRAINT size_check CHECK (
    octet_length(content::text) <= 4096
  )
);

-- Indexes for faster lookup
CREATE INDEX IF NOT EXISTS idx_bcm_workspace ON public.business_context_manifests(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bcm_version ON public.business_context_manifests(workspace_id, version_major, version_minor, version_patch);

-- Row Level Security
ALTER TABLE public.business_context_manifests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access their workspace's manifests" 
ON public.business_context_manifests
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.workspace_members
    WHERE workspace_members.workspace_id = business_context_manifests.workspace_id
    AND workspace_members.user_id = auth.uid()
  )
);

CREATE POLICY "Workspace admins can manage manifests" 
ON public.business_context_manifests
FOR ALL
USING (
  EXISTS (
    SELECT 1 FROM public.workspace_members
    WHERE workspace_members.workspace_id = business_context_manifests.workspace_id
    AND workspace_members.user_id = auth.uid()
    AND workspace_members.role = 'admin'
  )
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_bcm_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_bcm_timestamp
BEFORE UPDATE ON public.business_context_manifests
FOR EACH ROW
EXECUTE FUNCTION update_bcm_timestamp();
