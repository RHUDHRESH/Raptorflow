-- Row Level Security (RLS) Policies for Multi-Tenant Workspace Isolation
-- These policies ensure users can only access data from their own workspace

-- Enable RLS on all tables
ALTER TABLE capability_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE lines_of_operation ENABLE ROW LEVEL SECURITY;
ALTER TABLE sprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE move_anomalies ENABLE ROW LEVEL SECURITY;
ALTER TABLE move_logs ENABLE ROW LEVEL SECURITY;

-- Maneuver types are global (no workspace_id), so no RLS needed
-- They're templates available to everyone

-- Create a function to get current user's workspace_id
-- This assumes you have a workspaces table and user_workspaces junction table
CREATE OR REPLACE FUNCTION get_user_workspace_id()
RETURNS UUID AS $$
  SELECT workspace_id 
  FROM user_workspaces 
  WHERE user_id = auth.uid() 
  LIMIT 1;
$$ LANGUAGE sql SECURITY DEFINER;

-- Alternative simpler function if workspace_id is stored in user metadata
CREATE OR REPLACE FUNCTION get_user_workspace_id_from_metadata()
RETURNS UUID AS $$
  SELECT (auth.jwt() -> 'user_metadata' ->> 'workspace_id')::uuid;
$$ LANGUAGE sql SECURITY DEFINER;

-- CAPABILITY NODES POLICIES
CREATE POLICY "Users can view capability nodes in their workspace"
  ON capability_nodes FOR SELECT
  USING (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can insert capability nodes in their workspace"
  ON capability_nodes FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can update capability nodes in their workspace"
  ON capability_nodes FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can delete capability nodes in their workspace"
  ON capability_nodes FOR DELETE
  USING (workspace_id = get_user_workspace_id());

-- LINES OF OPERATION POLICIES
CREATE POLICY "Users can view LOOs in their workspace"
  ON lines_of_operation FOR SELECT
  USING (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can insert LOOs in their workspace"
  ON lines_of_operation FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can update LOOs in their workspace"
  ON lines_of_operation FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can delete LOOs in their workspace"
  ON lines_of_operation FOR DELETE
  USING (workspace_id = get_user_workspace_id());

-- SPRINTS POLICIES
CREATE POLICY "Users can view sprints in their workspace"
  ON sprints FOR SELECT
  USING (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can insert sprints in their workspace"
  ON sprints FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can update sprints in their workspace"
  ON sprints FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can delete sprints in their workspace"
  ON sprints FOR DELETE
  USING (workspace_id = get_user_workspace_id());

-- MOVES POLICIES
CREATE POLICY "Users can view moves in their workspace"
  ON moves FOR SELECT
  USING (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can insert moves in their workspace"
  ON moves FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can update moves in their workspace"
  ON moves FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Users can delete moves in their workspace"
  ON moves FOR DELETE
  USING (workspace_id = get_user_workspace_id());

-- MOVE ANOMALIES POLICIES (inherit from moves)
CREATE POLICY "Users can view anomalies for their moves"
  ON move_anomalies FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM moves 
      WHERE moves.id = move_anomalies.move_id 
      AND moves.workspace_id = get_user_workspace_id()
    )
  );

CREATE POLICY "Users can insert anomalies for their moves"
  ON move_anomalies FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM moves 
      WHERE moves.id = move_anomalies.move_id 
      AND moves.workspace_id = get_user_workspace_id()
    )
  );

CREATE POLICY "Users can update anomalies for their moves"
  ON move_anomalies FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM moves 
      WHERE moves.id = move_anomalies.move_id 
      AND moves.workspace_id = get_user_workspace_id()
    )
  );

CREATE POLICY "Users can delete anomalies for their moves"
  ON move_anomalies FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM moves 
      WHERE moves.id = move_anomalies.move_id 
      AND moves.workspace_id = get_user_workspace_id()
    )
  );

-- MOVE LOGS POLICIES (inherit from moves)
CREATE POLICY "Users can view logs for their moves"
  ON move_logs FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM moves 
      WHERE moves.id = move_logs.move_id 
      AND moves.workspace_id = get_user_workspace_id()
    )
  );

CREATE POLICY "Users can insert logs for their moves"
  ON move_logs FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM moves 
      WHERE moves.id = move_logs.move_id 
      AND moves.workspace_id = get_user_workspace_id()
    )
  );

CREATE POLICY "Users can update logs for their moves"
  ON move_logs FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM moves 
      WHERE moves.id = move_logs.move_id 
      AND moves.workspace_id = get_user_workspace_id()
    )
  );

CREATE POLICY "Users can delete logs for their moves"
  ON move_logs FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM moves 
      WHERE moves.id = move_logs.move_id 
      AND moves.workspace_id = get_user_workspace_id()
    )
  );

-- MANEUVER TYPES - Global, everyone can read
CREATE POLICY "Everyone can view maneuver types"
  ON maneuver_types FOR SELECT
  TO authenticated
  USING (true);

-- Only admins can modify maneuver types (if needed)
CREATE POLICY "Admins can modify maneuver types"
  ON maneuver_types FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE profiles.id = auth.uid() 
      AND profiles.role = 'admin'
    )
  );


