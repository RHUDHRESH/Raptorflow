-- Add attribution columns to Blackbox Outcomes Industrial
ALTER TABLE blackbox_outcomes_industrial
ADD COLUMN IF NOT EXISTS campaign_id UUID REFERENCES campaigns(id),
ADD COLUMN IF NOT EXISTS move_id UUID REFERENCES moves(id);

-- Create indexes for attribution lookups
CREATE INDEX IF NOT EXISTS idx_bb_outcomes_campaign_id ON blackbox_outcomes_industrial(campaign_id);
CREATE INDEX IF NOT EXISTS idx_bb_outcomes_move_id ON blackbox_outcomes_industrial(move_id);
