-- Migration 015: Create Agent Registry System
-- Phase: Week 2 - Codex Schema Creation
-- Purpose: Add comprehensive agent management and registry
-- New Tables: 4 (agent_registry, agent_capabilities, agent_assignments, agent_performance)
-- Scope: Expand from 51 → 55 tables

-- ============================================================================
-- TABLE 1: agent_registry
-- Purpose: Master registry of all agents in the system (70+ agents)
-- Global scope: No workspace_id (agents are global, but assignments are per workspace)
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_registry (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Agent identification
  agent_name text NOT NULL UNIQUE,
  agent_type text NOT NULL, -- "lord", "researcher", "creative", "intelligence", "guardian"
  guild_name text, -- "Council of Lords", "Research Guild", "Muse", "Matrix", "Guardians"

  -- Description and purpose
  description text,
  purpose text,
  domain_expertise text[],

  -- Agent configuration
  model_config jsonb, -- {model: "claude-sonnet", temperature: 0.7, max_tokens: 2000, ...}
  system_prompt text,
  personality_traits text[], -- [confident, analytical, creative, cautious, ...]

  -- Capabilities
  supported_inputs text[], -- [text, image, url, file, ...]
  supported_outputs text[], -- [text, json, html, image, video, ...]
  tool_access text[], -- [search, research, analyze, create, publish, ...]

  -- Performance baseline
  avg_execution_time_seconds integer,
  success_rate_percentage numeric,
  error_rate_percentage numeric,
  cost_per_execution numeric,

  -- Status
  is_active boolean DEFAULT true,
  version text DEFAULT '1.0',
  release_date date,
  deprecated_date date,

  -- Metadata
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT agent_registry_type_check CHECK (agent_type IN ('lord', 'researcher', 'creative', 'intelligence', 'guardian'))
);

CREATE INDEX idx_agent_registry_type ON agent_registry(agent_type);
CREATE INDEX idx_agent_registry_guild ON agent_registry(guild_name);
CREATE INDEX idx_agent_registry_active ON agent_registry(is_active);
CREATE INDEX idx_agent_registry_name ON agent_registry(agent_name);

-- ============================================================================
-- TABLE 2: agent_capabilities
-- Purpose: Detailed breakdown of what each agent can do
-- Reference to agent_registry (global scope)
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_capabilities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id uuid NOT NULL REFERENCES agent_registry(id) ON DELETE CASCADE,

  -- Capability definition
  capability_name text NOT NULL,
  description text,
  category text NOT NULL, -- "research", "analysis", "creation", "optimization", "monitoring"
  subcategory text,

  -- Capability scope
  input_types text[],
  output_types text[],
  external_apis text[], -- APIs this capability uses
  required_permissions text[],

  -- Performance metrics
  typical_execution_time_seconds integer,
  typical_token_usage integer,
  typical_cost numeric,
  success_rate_percentage numeric,

  -- Configuration
  is_enabled boolean DEFAULT true,
  configuration jsonb, -- capability-specific config
  parameter_schema jsonb, -- JSON schema for input parameters

  -- Metadata
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT agent_capabilities_unique UNIQUE(agent_id, capability_name),
  CONSTRAINT agent_capabilities_category_check CHECK (category IN ('research', 'analysis', 'creation', 'optimization', 'monitoring'))
);

CREATE INDEX idx_agent_capabilities_agent ON agent_capabilities(agent_id);
CREATE INDEX idx_agent_capabilities_category ON agent_capabilities(category);
CREATE INDEX idx_agent_capabilities_enabled ON agent_capabilities(agent_id, is_enabled);

-- ============================================================================
-- TABLE 3: agent_assignments
-- Purpose: Track which agents are assigned to workspaces and campaigns
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_assignments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  agent_id uuid NOT NULL REFERENCES agent_registry(id) ON DELETE CASCADE,

  -- Assignment context
  assigned_to_campaign_id uuid REFERENCES campaigns(id) ON DELETE CASCADE,
  assigned_to_guild_operation_id uuid, -- can reference guild operations when created

  -- Assignment details
  assignment_status text NOT NULL DEFAULT 'active',
  -- active, paused, completed, failed, archived
  priority_level text DEFAULT 'normal', -- low, normal, high, critical
  assigned_date timestamp with time zone DEFAULT now(),

  -- Configuration for this assignment
  assignment_config jsonb, -- workspace/campaign-specific agent config
  task_queue jsonb, -- pending tasks for this agent
  execution_constraints jsonb, -- rate limits, budget limits, etc.

  -- Performance tracking
  tasks_assigned integer DEFAULT 0,
  tasks_completed integer DEFAULT 0,
  tasks_failed integer DEFAULT 0,
  total_tokens_used integer DEFAULT 0,
  total_cost_incurred numeric DEFAULT 0,

  -- Metadata
  assigned_by uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT agent_assignments_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT agent_assignments_unique UNIQUE(workspace_id, agent_id, assigned_to_campaign_id),
  CONSTRAINT agent_assignments_status_check CHECK (assignment_status IN ('active', 'paused', 'completed', 'failed', 'archived')),
  CONSTRAINT agent_assignments_priority_check CHECK (priority_level IN ('low', 'normal', 'high', 'critical'))
);

CREATE INDEX idx_agent_assignments_workspace ON agent_assignments(workspace_id);
CREATE INDEX idx_agent_assignments_agent ON agent_assignments(agent_id);
CREATE INDEX idx_agent_assignments_campaign ON agent_assignments(assigned_to_campaign_id);
CREATE INDEX idx_agent_assignments_status ON agent_assignments(workspace_id, assignment_status);

ALTER TABLE agent_assignments ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_assignments_workspace_isolation ON agent_assignments
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- TABLE 4: agent_performance
-- Purpose: Track agent execution metrics and performance over time
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_performance (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  agent_id uuid NOT NULL REFERENCES agent_registry(id) ON DELETE CASCADE,

  -- Time period
  measurement_date date NOT NULL,
  measurement_hour integer,

  -- Execution metrics
  execution_count integer DEFAULT 0,
  success_count integer DEFAULT 0,
  failure_count integer DEFAULT 0,
  error_count integer DEFAULT 0,

  -- Performance metrics
  avg_execution_time_seconds numeric,
  min_execution_time_seconds numeric,
  max_execution_time_seconds numeric,
  p50_execution_time_seconds numeric,
  p95_execution_time_seconds numeric,
  p99_execution_time_seconds numeric,

  -- Token usage
  total_input_tokens integer DEFAULT 0,
  total_output_tokens integer DEFAULT 0,
  avg_input_tokens_per_execution numeric,
  avg_output_tokens_per_execution numeric,

  -- Cost
  total_cost_incurred numeric DEFAULT 0,
  avg_cost_per_execution numeric,

  -- Quality metrics
  success_rate_percentage numeric,
  error_rate_percentage numeric,
  quality_score numeric, -- 0-100

  -- Metadata
  created_at timestamp with time zone DEFAULT now(),

  CONSTRAINT agent_performance_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT agent_performance_unique UNIQUE(workspace_id, agent_id, measurement_date, measurement_hour)
);

CREATE INDEX idx_agent_performance_workspace ON agent_performance(workspace_id);
CREATE INDEX idx_agent_performance_agent ON agent_performance(agent_id);
CREATE INDEX idx_agent_performance_date ON agent_performance(workspace_id, measurement_date);
CREATE INDEX idx_agent_performance_agent_date ON agent_performance(agent_id, measurement_date);

ALTER TABLE agent_performance ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_performance_workspace_isolation ON agent_performance
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to record agent execution
CREATE OR REPLACE FUNCTION record_agent_execution(
  p_workspace_id uuid,
  p_agent_id uuid,
  p_execution_time_seconds numeric,
  p_input_tokens integer,
  p_output_tokens integer,
  p_cost numeric,
  p_success boolean
)
RETURNS void AS $$
DECLARE
  v_today date := CURRENT_DATE;
  v_hour integer := EXTRACT(HOUR FROM now())::integer;
BEGIN
  -- Update or create performance record
  INSERT INTO agent_performance (
    workspace_id, agent_id, measurement_date, measurement_hour,
    execution_count, success_count, failure_count,
    total_input_tokens, total_output_tokens, total_cost_incurred
  ) VALUES (
    p_workspace_id, p_agent_id, v_today, v_hour,
    1, CASE WHEN p_success THEN 1 ELSE 0 END, CASE WHEN p_success THEN 0 ELSE 1 END,
    p_input_tokens, p_output_tokens, p_cost
  )
  ON CONFLICT (workspace_id, agent_id, measurement_date, measurement_hour) DO UPDATE SET
    execution_count = agent_performance.execution_count + 1,
    success_count = agent_performance.success_count + CASE WHEN p_success THEN 1 ELSE 0 END,
    failure_count = agent_performance.failure_count + CASE WHEN p_success THEN 0 ELSE 1 END,
    total_input_tokens = agent_performance.total_input_tokens + p_input_tokens,
    total_output_tokens = agent_performance.total_output_tokens + p_output_tokens,
    total_cost_incurred = agent_performance.total_cost_incurred + p_cost;

  -- Update assignment stats
  UPDATE agent_assignments
  SET
    tasks_completed = tasks_completed + CASE WHEN p_success THEN 1 ELSE 0 END,
    tasks_failed = tasks_failed + CASE WHEN p_success THEN 0 ELSE 1 END,
    total_tokens_used = total_tokens_used + p_input_tokens + p_output_tokens,
    total_cost_incurred = total_cost_incurred + p_cost
  WHERE workspace_id = p_workspace_id
  AND agent_id = p_agent_id
  AND assignment_status = 'active';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- MIGRATION VERIFICATION BLOCK
-- ============================================================================

/*
POST-MIGRATION VERIFICATION:

1. Table creation:
   SELECT COUNT(*) FROM information_schema.tables
   WHERE table_schema = 'public' AND table_name IN
   ('agent_registry', 'agent_capabilities', 'agent_assignments', 'agent_performance');
   -- Expected: 4

2. RLS policies:
   SELECT COUNT(*) FROM pg_policies
   WHERE tablename IN ('agent_assignments', 'agent_performance');
   -- Expected: 4 (2 per table)

3. Indexes created:
   SELECT COUNT(*) FROM pg_indexes
   WHERE tablename IN ('agent_registry', 'agent_capabilities', 'agent_assignments', 'agent_performance')
   AND schemaname = 'public';
   -- Expected: 15+ indexes

4. Functions created:
   SELECT COUNT(*) FROM pg_proc
   WHERE proname = 'record_agent_execution'
   AND pronamespace = 'public'::regnamespace;
   -- Expected: 1

5. Foreign key constraints:
   SELECT COUNT(*) FROM information_schema.table_constraints
   WHERE constraint_type = 'FOREIGN KEY'
   AND table_name IN ('agent_registry', 'agent_capabilities', 'agent_assignments', 'agent_performance');
   -- Expected: 7+ FKs
*/
