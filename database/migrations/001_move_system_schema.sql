-- KOA Move System - Database Schema
-- Supabase/PostgreSQL Migration

-- Table: maneuver_types (Static template definitions)
CREATE TABLE IF NOT EXISTS maneuver_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  category VARCHAR(20) NOT NULL CHECK (category IN ('Offensive', 'Defensive', 'Logistical', 'Recon')),
  base_duration_days INTEGER DEFAULT 14,
  fogg_role VARCHAR(20) CHECK (fogg_role IN ('Spark', 'Facilitator', 'Signal')),
  intensity_score INTEGER CHECK (intensity_score BETWEEN 1 AND 10),
  risk_profile VARCHAR(20) CHECK (risk_profile IN ('Low', 'Medium', 'Brand_Risk', 'Budget_Risk')),
  description TEXT,
  default_config JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table: capability_nodes (Tech Tree)
CREATE TABLE IF NOT EXISTS capability_nodes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  tier VARCHAR(20) NOT NULL CHECK (tier IN ('Foundation', 'Traction', 'Scale', 'Dominance')),
  status VARCHAR(20) DEFAULT 'Locked' CHECK (status IN ('Locked', 'In_Progress', 'Unlocked')),
  workspace_id UUID NOT NULL,
  parent_node_ids UUID[] DEFAULT '{}',
  unlocks_maneuver_ids UUID[] DEFAULT '{}',
  description TEXT,
  completion_criteria JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  unlocked_at TIMESTAMP
);

-- Table: lines_of_operation (Strategic groupings)
CREATE TABLE IF NOT EXISTS lines_of_operation (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  name VARCHAR(150) NOT NULL,
  strategic_objective TEXT,
  seasonality_tag VARCHAR(20) CHECK (seasonality_tag IN ('Harvest', 'Planting', 'Agnostic')),
  center_of_gravity VARCHAR(100),
  status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Paused', 'Complete')),
  start_date DATE,
  target_date DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table: sprints (Time-boxed execution windows)
CREATE TABLE IF NOT EXISTS sprints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  name VARCHAR(100),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  theme VARCHAR(200),
  capacity_budget INTEGER DEFAULT 100,
  current_load INTEGER DEFAULT 0,
  season_type VARCHAR(20) CHECK (season_type IN ('High_Season', 'Low_Season', 'Shoulder')),
  status VARCHAR(20) DEFAULT 'Planning' CHECK (status IN ('Planning', 'Active', 'Review', 'Complete')),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table: moves (Actual executing instances)
CREATE TABLE IF NOT EXISTS moves (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  maneuver_type_id UUID REFERENCES maneuver_types(id),
  sprint_id UUID REFERENCES sprints(id),
  line_of_operation_id UUID REFERENCES lines_of_operation(id),
  name VARCHAR(200) NOT NULL,
  primary_icp_id UUID NOT NULL,
  secondary_icp_ids UUID[] DEFAULT '{}',
  
  -- OODA Configuration
  status VARCHAR(30) DEFAULT 'Planning' CHECK (status IN ('Planning', 'OODA_Observe', 'OODA_Orient', 'OODA_Decide', 'OODA_Act', 'Complete', 'Killed')),
  ooda_config JSONB DEFAULT '{}',
  
  -- Fogg Behavior Model
  fogg_config JSONB DEFAULT '{}',
  
  -- Execution details
  goal TEXT,
  channels VARCHAR(50)[] DEFAULT '{}',
  content_frequency VARCHAR(100),
  action_types VARCHAR(50)[] DEFAULT '{}',
  key_metrics JSONB DEFAULT '{}',
  decision_checkpoints JSONB DEFAULT '[]',
  
  -- Tracking
  start_date DATE,
  end_date DATE,
  progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),
  owner_id UUID,
  health_status VARCHAR(10) DEFAULT 'green' CHECK (health_status IN ('green', 'amber', 'red')),
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Table: move_anomalies (AI-detected issues)
CREATE TABLE IF NOT EXISTS move_anomalies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  move_id UUID REFERENCES moves(id) ON DELETE CASCADE,
  type VARCHAR(30) CHECK (type IN ('Tone_Clash', 'Fatigue', 'Drift', 'Rule_Violation', 'Capacity_Overload')),
  severity INTEGER CHECK (severity BETWEEN 1 AND 5),
  description TEXT,
  detected_at TIMESTAMP DEFAULT NOW(),
  resolution TEXT,
  resolved_at TIMESTAMP,
  status VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open', 'Acknowledged', 'Resolved', 'Ignored'))
);

-- Table: move_logs (Daily execution tracking)
CREATE TABLE IF NOT EXISTS move_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  move_id UUID REFERENCES moves(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  actions_completed INTEGER DEFAULT 0,
  notes TEXT,
  metrics_snapshot JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Junction table: maneuver_prerequisites (Tech Tree dependencies)
CREATE TABLE IF NOT EXISTS maneuver_prerequisites (
  maneuver_type_id UUID REFERENCES maneuver_types(id) ON DELETE CASCADE,
  required_capability_id UUID REFERENCES capability_nodes(id) ON DELETE CASCADE,
  PRIMARY KEY (maneuver_type_id, required_capability_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_moves_workspace ON moves(workspace_id);
CREATE INDEX IF NOT EXISTS idx_moves_sprint ON moves(sprint_id);
CREATE INDEX IF NOT EXISTS idx_moves_status ON moves(status);
CREATE INDEX IF NOT EXISTS idx_moves_icp ON moves(primary_icp_id);
CREATE INDEX IF NOT EXISTS idx_capability_nodes_workspace ON capability_nodes(workspace_id);
CREATE INDEX IF NOT EXISTS idx_capability_nodes_status ON capability_nodes(status);
CREATE INDEX IF NOT EXISTS idx_sprints_workspace ON sprints(workspace_id);
CREATE INDEX IF NOT EXISTS idx_sprints_status ON sprints(status);
CREATE INDEX IF NOT EXISTS idx_anomalies_move ON move_anomalies(move_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_status ON move_anomalies(status);
CREATE INDEX IF NOT EXISTS idx_logs_move ON move_logs(move_id);
CREATE INDEX IF NOT EXISTS idx_logs_date ON move_logs(date);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for moves table
CREATE TRIGGER update_moves_updated_at
  BEFORE UPDATE ON moves
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();


