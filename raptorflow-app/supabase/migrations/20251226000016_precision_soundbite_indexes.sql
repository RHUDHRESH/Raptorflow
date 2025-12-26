-- RaptorFlow Migration: Performance Indexes for Precision Soundbite Framework 3.0

CREATE INDEX IF NOT EXISTS idx_foundation_jtbd_workspace_id ON foundation_jtbd(workspace_id);
CREATE INDEX IF NOT EXISTS idx_foundation_message_hierarchy_workspace_id ON foundation_message_hierarchy(workspace_id);
CREATE INDEX IF NOT EXISTS idx_foundation_awareness_matrix_workspace_id ON foundation_awareness_matrix(workspace_id);
CREATE INDEX IF NOT EXISTS idx_foundation_proof_vault_workspace_id ON foundation_proof_vault(workspace_id);
CREATE INDEX IF NOT EXISTS idx_foundation_precision_soundbites_workspace_id ON foundation_precision_soundbites(workspace_id);
CREATE INDEX IF NOT EXISTS idx_foundation_precision_soundbites_type ON foundation_precision_soundbites(type);
CREATE INDEX IF NOT EXISTS idx_foundation_precision_soundbites_status ON foundation_precision_soundbites(status);
