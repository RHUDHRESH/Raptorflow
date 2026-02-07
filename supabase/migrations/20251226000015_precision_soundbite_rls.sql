-- RaptorFlow Migration: RLS Policies for Precision Soundbite Framework 3.0

-- Enable RLS on all new tables
ALTER TABLE foundation_jtbd ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_message_hierarchy ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_awareness_matrix ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_proof_vault ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_precision_soundbites ENABLE ROW LEVEL SECURITY;

-- 1. foundation_jtbd Policies
CREATE POLICY "Foundation JTBD: Workspace members can view" ON foundation_jtbd
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Foundation JTBD: Owners and admins can manage" ON foundation_jtbd
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = foundation_jtbd.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- 2. foundation_message_hierarchy Policies
CREATE POLICY "Foundation Message Hierarchy: Workspace members can view" ON foundation_message_hierarchy
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Foundation Message Hierarchy: Owners and admins can manage" ON foundation_message_hierarchy
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = foundation_message_hierarchy.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- 3. foundation_awareness_matrix Policies
CREATE POLICY "Foundation Awareness Matrix: Workspace members can view" ON foundation_awareness_matrix
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Foundation Awareness Matrix: Owners and admins can manage" ON foundation_awareness_matrix
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = foundation_awareness_matrix.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- 4. foundation_proof_vault Policies
CREATE POLICY "Foundation Proof Vault: Workspace members can view" ON foundation_proof_vault
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Foundation Proof Vault: Owners and admins can manage" ON foundation_proof_vault
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = foundation_proof_vault.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- 5. foundation_precision_soundbites Policies
CREATE POLICY "Foundation Precision Soundbites: Workspace members can view" ON foundation_precision_soundbites
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Foundation Precision Soundbites: Owners and admins can manage" ON foundation_precision_soundbites
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.workspace_id = foundation_precision_soundbites.workspace_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );
