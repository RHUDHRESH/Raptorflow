-- Quests: Gamified sequences of moves with goals and rewards
-- Quests wrap multiple moves into a cohesive campaign with progression

CREATE TABLE IF NOT EXISTS quests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  goal TEXT NOT NULL,
  difficulty TEXT CHECK (difficulty IN ('Beginner', 'Intermediate', 'Advanced')) DEFAULT 'Beginner',
  status TEXT CHECK (status IN ('Not_Started', 'In_Progress', 'Completed', 'Failed')) DEFAULT 'Not_Started',
  
  -- Quest metadata
  estimated_duration_weeks INTEGER DEFAULT 4,
  xp_reward INTEGER DEFAULT 100,
  
  -- Progress tracking
  progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
  
  -- Dates
  start_date DATE,
  target_completion_date DATE,
  actual_completion_date DATE,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quest Moves: Many-to-many relationship between quests and moves
CREATE TABLE IF NOT EXISTS quest_moves (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quest_id UUID NOT NULL REFERENCES quests(id) ON DELETE CASCADE,
  move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE,
  sequence_order INTEGER NOT NULL, -- Order in which moves should be completed
  is_required BOOLEAN DEFAULT true, -- Required or optional
  status TEXT CHECK (status IN ('Pending', 'In_Progress', 'Completed', 'Skipped')) DEFAULT 'Pending',
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(quest_id, move_id),
  UNIQUE(quest_id, sequence_order)
);

-- Quest Milestones: Key checkpoints within a quest
CREATE TABLE IF NOT EXISTS quest_milestones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quest_id UUID NOT NULL REFERENCES quests(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  order_index INTEGER NOT NULL,
  is_completed BOOLEAN DEFAULT false,
  completed_at TIMESTAMPTZ,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(quest_id, order_index)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_quests_workspace ON quests(workspace_id);
CREATE INDEX IF NOT EXISTS idx_quests_status ON quests(status);
CREATE INDEX IF NOT EXISTS idx_quest_moves_quest ON quest_moves(quest_id);
CREATE INDEX IF NOT EXISTS idx_quest_moves_move ON quest_moves(move_id);
CREATE INDEX IF NOT EXISTS idx_quest_milestones_quest ON quest_milestones(quest_id);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_quests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_quests_updated_at
  BEFORE UPDATE ON quests
  FOR EACH ROW
  EXECUTE FUNCTION update_quests_updated_at();

CREATE TRIGGER trigger_update_quest_moves_updated_at
  BEFORE UPDATE ON quest_moves
  FOR EACH ROW
  EXECUTE FUNCTION update_quests_updated_at();

CREATE TRIGGER trigger_update_quest_milestones_updated_at
  BEFORE UPDATE ON quest_milestones
  FOR EACH ROW
  EXECUTE FUNCTION update_quests_updated_at();

-- Enable RLS
ALTER TABLE quests ENABLE ROW LEVEL SECURITY;
ALTER TABLE quest_moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE quest_milestones ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own quests"
  ON quests FOR SELECT
  USING (auth.uid() = workspace_id);

CREATE POLICY "Users can create their own quests"
  ON quests FOR INSERT
  WITH CHECK (auth.uid() = workspace_id);

CREATE POLICY "Users can update their own quests"
  ON quests FOR UPDATE
  USING (auth.uid() = workspace_id);

CREATE POLICY "Users can delete their own quests"
  ON quests FOR DELETE
  USING (auth.uid() = workspace_id);

-- Quest moves policies (inherit from quest)
CREATE POLICY "Users can view quest moves for their quests"
  ON quest_moves FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM quests
    WHERE quests.id = quest_moves.quest_id
    AND quests.workspace_id = auth.uid()
  ));

CREATE POLICY "Users can manage quest moves for their quests"
  ON quest_moves FOR ALL
  USING (EXISTS (
    SELECT 1 FROM quests
    WHERE quests.id = quest_moves.quest_id
    AND quests.workspace_id = auth.uid()
  ));

-- Quest milestones policies (inherit from quest)
CREATE POLICY "Users can view quest milestones for their quests"
  ON quest_milestones FOR SELECT
  USING (EXISTS (
    SELECT 1 FROM quests
    WHERE quests.id = quest_milestones.quest_id
    AND quests.workspace_id = auth.uid()
  ));

CREATE POLICY "Users can manage quest milestones for their quests"
  ON quest_milestones FOR ALL
  USING (EXISTS (
    SELECT 1 FROM quests
    WHERE quests.id = quest_milestones.quest_id
    AND quests.workspace_id = auth.uid()
  ));





