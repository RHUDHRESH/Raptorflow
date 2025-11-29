-- Fix RLS Security for all tables reported by linter
-- This migration enables RLS and applies workspace-scoped policies

-- Helper function to check workspace membership
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
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 1. maneuver_types
ALTER TABLE public.maneuver_types ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Everyone can view maneuver types" ON public.maneuver_types;
CREATE POLICY "Everyone can view maneuver types"
  ON public.maneuver_types FOR SELECT
  TO authenticated
  USING (true);

-- 2. moves
ALTER TABLE public.moves ENABLE ROW LEVEL SECURITY;

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
ALTER TABLE public.sprints ENABLE ROW LEVEL SECURITY;

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
ALTER TABLE public.lines_of_operation ENABLE ROW LEVEL SECURITY;

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
ALTER TABLE public.move_anomalies ENABLE ROW LEVEL SECURITY;

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
ALTER TABLE public.move_logs ENABLE ROW LEVEL SECURITY;

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
ALTER TABLE public.maneuver_prerequisites ENABLE ROW LEVEL SECURITY;

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
ALTER TABLE public.capability_nodes ENABLE ROW LEVEL SECURITY;

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
ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;

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
ALTER TABLE public.quests ENABLE ROW LEVEL SECURITY;

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
ALTER TABLE public.quest_moves ENABLE ROW LEVEL SECURITY;

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
ALTER TABLE public.quest_milestones ENABLE ROW LEVEL SECURITY;

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
