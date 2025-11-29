-- Fix "Function Search Path Mutable" Security Warnings
-- These functions run with elevated privileges or are security sensitive, 
-- so we must lock down their search_path to prevent malicious schema usage.

ALTER FUNCTION public.update_quests_updated_at() SET search_path = public, pg_temp;
ALTER FUNCTION public.update_updated_at_column() SET search_path = public, pg_temp;

-- handle_new_user might not exist if auth trigger wasn't set up, but linter saw it.
-- We wrap in DO block to avoid error if it's missing, or just use straight ALTER if we trust linter.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'handle_new_user') THEN
        ALTER FUNCTION public.handle_new_user() SET search_path = public, pg_temp;
    END IF;
END
$$;

-- Update helper function with secure search_path as well
CREATE OR REPLACE FUNCTION public.is_workspace_member(_workspace_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM public.workspace_members
    WHERE workspace_id = _workspace_id
    AND user_id = auth.uid()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

-- Re-apply Policies (Ensure they exist)
-- We drop and recreate to ensure they are applied correctly.

-- 1. maneuver_types
DROP POLICY IF EXISTS "Everyone can view maneuver types" ON public.maneuver_types;
CREATE POLICY "Everyone can view maneuver types"
  ON public.maneuver_types FOR SELECT
  TO authenticated
  USING (true);

-- 2. moves
DROP POLICY IF EXISTS "Workspace members can view moves" ON public.moves;
CREATE POLICY "Workspace members can view moves"
  ON public.moves FOR SELECT
  USING (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can insert moves" ON public.moves;
CREATE POLICY "Workspace members can insert moves"
  ON public.moves FOR INSERT
  WITH CHECK (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can update moves" ON public.moves;
CREATE POLICY "Workspace members can update moves"
  ON public.moves FOR UPDATE
  USING (is_workspace_member(workspace_id))
  WITH CHECK (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can delete moves" ON public.moves;
CREATE POLICY "Workspace members can delete moves"
  ON public.moves FOR DELETE
  USING (is_workspace_member(workspace_id));

-- 3. sprints
DROP POLICY IF EXISTS "Workspace members can view sprints" ON public.sprints;
CREATE POLICY "Workspace members can view sprints"
  ON public.sprints FOR SELECT
  USING (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can insert sprints" ON public.sprints;
CREATE POLICY "Workspace members can insert sprints"
  ON public.sprints FOR INSERT
  WITH CHECK (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can update sprints" ON public.sprints;
CREATE POLICY "Workspace members can update sprints"
  ON public.sprints FOR UPDATE
  USING (is_workspace_member(workspace_id))
  WITH CHECK (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can delete sprints" ON public.sprints;
CREATE POLICY "Workspace members can delete sprints"
  ON public.sprints FOR DELETE
  USING (is_workspace_member(workspace_id));

-- 4. lines_of_operation
DROP POLICY IF EXISTS "Workspace members can view lines_of_operation" ON public.lines_of_operation;
CREATE POLICY "Workspace members can view lines_of_operation"
  ON public.lines_of_operation FOR SELECT
  USING (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can insert lines_of_operation" ON public.lines_of_operation;
CREATE POLICY "Workspace members can insert lines_of_operation"
  ON public.lines_of_operation FOR INSERT
  WITH CHECK (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can update lines_of_operation" ON public.lines_of_operation;
CREATE POLICY "Workspace members can update lines_of_operation"
  ON public.lines_of_operation FOR UPDATE
  USING (is_workspace_member(workspace_id))
  WITH CHECK (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can delete lines_of_operation" ON public.lines_of_operation;
CREATE POLICY "Workspace members can delete lines_of_operation"
  ON public.lines_of_operation FOR DELETE
  USING (is_workspace_member(workspace_id));

-- 5. move_anomalies
DROP POLICY IF EXISTS "Workspace members can view move_anomalies" ON public.move_anomalies;
CREATE POLICY "Workspace members can view move_anomalies"
  ON public.move_anomalies FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.moves
      WHERE moves.id = move_anomalies.move_id
      AND is_workspace_member(moves.workspace_id)
    )
  );

DROP POLICY IF EXISTS "Workspace members can manage move_anomalies" ON public.move_anomalies;
CREATE POLICY "Workspace members can manage move_anomalies"
  ON public.move_anomalies FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.moves
      WHERE moves.id = move_anomalies.move_id
      AND is_workspace_member(moves.workspace_id)
    )
  );

-- 6. move_logs
DROP POLICY IF EXISTS "Workspace members can view move_logs" ON public.move_logs;
CREATE POLICY "Workspace members can view move_logs"
  ON public.move_logs FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.moves
      WHERE moves.id = move_logs.move_id
      AND is_workspace_member(moves.workspace_id)
    )
  );

DROP POLICY IF EXISTS "Workspace members can manage move_logs" ON public.move_logs;
CREATE POLICY "Workspace members can manage move_logs"
  ON public.move_logs FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.moves
      WHERE moves.id = move_logs.move_id
      AND is_workspace_member(moves.workspace_id)
    )
  );

-- 7. maneuver_prerequisites
DROP POLICY IF EXISTS "Workspace members can view maneuver_prerequisites" ON public.maneuver_prerequisites;
CREATE POLICY "Workspace members can view maneuver_prerequisites"
  ON public.maneuver_prerequisites FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.capability_nodes
      WHERE capability_nodes.id = maneuver_prerequisites.required_capability_id
      AND is_workspace_member(capability_nodes.workspace_id)
    )
  );

DROP POLICY IF EXISTS "Workspace members can manage maneuver_prerequisites" ON public.maneuver_prerequisites;
CREATE POLICY "Workspace members can manage maneuver_prerequisites"
  ON public.maneuver_prerequisites FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.capability_nodes
      WHERE capability_nodes.id = maneuver_prerequisites.required_capability_id
      AND is_workspace_member(capability_nodes.workspace_id)
    )
  );

-- 8. capability_nodes
DROP POLICY IF EXISTS "Workspace members can view capability_nodes" ON public.capability_nodes;
CREATE POLICY "Workspace members can view capability_nodes"
  ON public.capability_nodes FOR SELECT
  USING (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can manage capability_nodes" ON public.capability_nodes;
CREATE POLICY "Workspace members can manage capability_nodes"
  ON public.capability_nodes FOR ALL
  USING (is_workspace_member(workspace_id))
  WITH CHECK (is_workspace_member(workspace_id));

-- 9. assets
DROP POLICY IF EXISTS "Workspace members can view assets" ON public.assets;
CREATE POLICY "Workspace members can view assets"
  ON public.assets FOR SELECT
  USING (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can manage assets" ON public.assets;
CREATE POLICY "Workspace members can manage assets"
  ON public.assets FOR ALL
  USING (is_workspace_member(workspace_id))
  WITH CHECK (is_workspace_member(workspace_id));

-- 10. quests
DROP POLICY IF EXISTS "Workspace members can view quests" ON public.quests;
CREATE POLICY "Workspace members can view quests"
  ON public.quests FOR SELECT
  USING (is_workspace_member(workspace_id));

DROP POLICY IF EXISTS "Workspace members can manage quests" ON public.quests;
CREATE POLICY "Workspace members can manage quests"
  ON public.quests FOR ALL
  USING (is_workspace_member(workspace_id))
  WITH CHECK (is_workspace_member(workspace_id));

-- 11. quest_moves
DROP POLICY IF EXISTS "Workspace members can view quest_moves" ON public.quest_moves;
CREATE POLICY "Workspace members can view quest_moves"
  ON public.quest_moves FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.quests
      WHERE quests.id = quest_moves.quest_id
      AND is_workspace_member(quests.workspace_id)
    )
  );

DROP POLICY IF EXISTS "Workspace members can manage quest_moves" ON public.quest_moves;
CREATE POLICY "Workspace members can manage quest_moves"
  ON public.quest_moves FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.quests
      WHERE quests.id = quest_moves.quest_id
      AND is_workspace_member(quests.workspace_id)
    )
  );

-- 12. quest_milestones
DROP POLICY IF EXISTS "Workspace members can view quest_milestones" ON public.quest_milestones;
CREATE POLICY "Workspace members can view quest_milestones"
  ON public.quest_milestones FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.quests
      WHERE quests.id = quest_milestones.quest_id
      AND is_workspace_member(quests.workspace_id)
    )
  );

DROP POLICY IF EXISTS "Workspace members can manage quest_milestones" ON public.quest_milestones;
CREATE POLICY "Workspace members can manage quest_milestones"
  ON public.quest_milestones FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.quests
      WHERE quests.id = quest_milestones.quest_id
      AND is_workspace_member(quests.workspace_id)
    )
  );
