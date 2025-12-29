-- Workspace Settings for Theme and Design Preferences
-- Migration: 20251228000001_workspace_theme_settings.sql

-- Create workspace_settings table
CREATE TABLE IF NOT EXISTS workspace_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Theme preferences
    theme_mode TEXT NOT NULL DEFAULT 'auto' CHECK (theme_mode IN ('light', 'dark', 'auto')),
    accent_color TEXT NOT NULL DEFAULT '#3b82f6', -- Default blue accent

    -- Additional design tokens for advanced customization
    design_tokens JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    -- Ensure one settings record per workspace
    UNIQUE(workspace_id)
);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_workspace_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER workspace_settings_updated_at
    BEFORE UPDATE ON workspace_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_workspace_settings_updated_at();

-- Insert default settings for existing workspaces
INSERT INTO workspace_settings (workspace_id, theme_mode, accent_color)
SELECT id, 'auto', '#3b82f6'
FROM workspaces
WHERE id NOT IN (SELECT workspace_id FROM workspace_settings);

-- Add helpful indexes
CREATE INDEX IF NOT EXISTS idx_workspace_settings_workspace_id ON workspace_settings(workspace_id);
