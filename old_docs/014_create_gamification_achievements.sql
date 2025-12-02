-- Migration 014: Create Gamification & Achievements System
-- Phase: Week 2 - Codex Schema Creation
-- Purpose: Add achievements, user progress tracking, and gamification mechanics
-- New Tables: 3 (achievements, user_achievements, user_stats)
-- Scope: Expand from 48 → 51 tables

-- ============================================================================
-- TABLE 1: achievements
-- Purpose: Define achievable milestones and badges
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS achievements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

  -- Core fields
  name text NOT NULL,
  description text,
  icon_url text,

  -- Achievement configuration
  badge_type text NOT NULL, -- "milestone", "excellence", "exploration", "collaboration", "speed", "quality"
  category text, -- "campaign", "content", "engagement", "research", "innovation"
  tier text DEFAULT 'bronze', -- bronze, silver, gold, platinum

  -- Unlock conditions
  condition_type text NOT NULL, -- "count", "milestone", "combination", "time_based"
  condition_value jsonb, -- {threshold: 100, metric: "campaigns_completed", ...}
  required_previous_achievement_id uuid REFERENCES achievements(id) ON DELETE SET NULL,

  -- Rewards
  points_reward integer DEFAULT 0,
  badge_unlocks text[], -- other achievements that unlock from this
  unlock_perks text[], -- ["early_access", "premium_features", ...]

  -- Metadata
  is_active boolean DEFAULT true,
  rarity_level text DEFAULT 'common', -- common, uncommon, rare, legendary
  created_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT achievements_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT achievements_badge_type_check CHECK (badge_type IN ('milestone', 'excellence', 'exploration', 'collaboration', 'speed', 'quality')),
  CONSTRAINT achievements_tier_check CHECK (tier IN ('bronze', 'silver', 'gold', 'platinum')),
  CONSTRAINT achievements_rarity_check CHECK (rarity_level IN ('common', 'uncommon', 'rare', 'legendary'))
);

CREATE INDEX idx_achievements_workspace ON achievements(workspace_id);
CREATE INDEX idx_achievements_badge_type ON achievements(workspace_id, badge_type);
CREATE INDEX idx_achievements_category ON achievements(workspace_id, category);
CREATE INDEX idx_achievements_active ON achievements(workspace_id, is_active);

ALTER TABLE achievements ENABLE ROW LEVEL SECURITY;

CREATE POLICY achievements_workspace_isolation ON achievements
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

-- ============================================================================
-- TABLE 2: user_achievements
-- Purpose: Track which achievements individual users have unlocked
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_achievements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  achievement_id uuid NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,

  -- Progress tracking
  progress_percentage integer DEFAULT 0,
  progress_value integer DEFAULT 0,
  progress_data jsonb, -- arbitrary progress state

  -- Unlock details
  unlocked_at timestamp with time zone,
  unlocked_by_event text, -- "campaign_created", "content_published", etc.
  is_locked boolean DEFAULT true,

  -- Display
  display_on_profile boolean DEFAULT true,
  visibility text DEFAULT 'public', -- public, private, friends_only

  -- Metadata
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT user_achievements_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT user_achievements_unique UNIQUE(user_id, achievement_id),
  CONSTRAINT user_achievements_visibility_check CHECK (visibility IN ('public', 'private', 'friends_only'))
);

CREATE INDEX idx_user_achievements_workspace ON user_achievements(workspace_id);
CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_achievement ON user_achievements(achievement_id);
CREATE INDEX idx_user_achievements_unlocked ON user_achievements(workspace_id, is_locked, unlocked_at);

ALTER TABLE user_achievements ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_achievements_workspace_isolation ON user_achievements
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

CREATE POLICY user_achievements_own_access ON user_achievements
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- ============================================================================
-- TABLE 3: user_stats
-- Purpose: Aggregate user statistics and metrics
-- Workspace isolation: workspace_id + RLS policy
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_stats (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Campaign metrics
  campaigns_created integer DEFAULT 0,
  campaigns_active integer DEFAULT 0,
  campaigns_completed integer DEFAULT 0,
  total_campaign_reach bigint DEFAULT 0,

  -- Content metrics
  content_pieces_created integer DEFAULT 0,
  content_pieces_published integer DEFAULT 0,
  total_engagement_count bigint DEFAULT 0,

  -- Move metrics
  moves_created integer DEFAULT 0,
  moves_executed integer DEFAULT 0,
  moves_successful integer DEFAULT 0,
  success_rate_percentage numeric,

  -- Collaboration metrics
  collaborations_count integer DEFAULT 0,
  teams_joined integer DEFAULT 0,

  -- Gamification
  total_points integer DEFAULT 0,
  achievements_unlocked integer DEFAULT 0,
  achievements_in_progress integer DEFAULT 0,
  badges_earned text[],

  -- Engagement
  login_count integer DEFAULT 0,
  last_active_at timestamp with time zone,
  total_hours_engaged integer DEFAULT 0,

  -- Experience level
  experience_level integer DEFAULT 1,
  experience_percentage numeric DEFAULT 0,

  -- Metadata
  stats_last_updated timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  CONSTRAINT user_stats_workspace_check CHECK (workspace_id IS NOT NULL),
  CONSTRAINT user_stats_unique UNIQUE(workspace_id, user_id)
);

CREATE INDEX idx_user_stats_workspace ON user_stats(workspace_id);
CREATE INDEX idx_user_stats_user ON user_stats(user_id);
CREATE INDEX idx_user_stats_experience_level ON user_stats(workspace_id, experience_level);
CREATE INDEX idx_user_stats_points ON user_stats(workspace_id, total_points);

ALTER TABLE user_stats ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_stats_workspace_isolation ON user_stats
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid)
  WITH CHECK (workspace_id = current_setting('app.current_workspace_id')::uuid);

CREATE POLICY user_stats_own_access ON user_stats
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate success rate for moves
CREATE OR REPLACE FUNCTION calculate_move_success_rate()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE user_stats
  SET success_rate_percentage = CASE
    WHEN moves_executed > 0 THEN (moves_successful::numeric / moves_executed::numeric) * 100
    ELSE 0
  END,
  updated_at = now()
  WHERE user_id = NEW.user_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate experience level based on points
CREATE OR REPLACE FUNCTION update_experience_level()
RETURNS TRIGGER AS $$
DECLARE
  new_level integer;
BEGIN
  -- Simple level progression: every 1000 points = 1 level
  new_level := (NEW.total_points / 1000) + 1;
  NEW.experience_percentage := ((NEW.total_points % 1000)::numeric / 1000::numeric) * 100;
  NEW.experience_level := new_level;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_stats_experience_update
BEFORE UPDATE ON user_stats
FOR EACH ROW
EXECUTE FUNCTION update_experience_level();

-- ============================================================================
-- STORED PROCEDURE: Unlock Achievement
-- ============================================================================

CREATE OR REPLACE FUNCTION unlock_achievement(
  p_user_id uuid,
  p_achievement_id uuid,
  p_workspace_id uuid,
  p_event_type text DEFAULT 'manual'
)
RETURNS TABLE (
  success boolean,
  message text,
  points_awarded integer
) AS $$
DECLARE
  v_achievement achievements;
  v_user_stat user_stats;
  v_points_awarded integer;
BEGIN
  -- Get achievement details
  SELECT * INTO v_achievement
  FROM achievements
  WHERE id = p_achievement_id AND workspace_id = p_workspace_id;

  IF v_achievement IS NULL THEN
    RETURN QUERY SELECT false, 'Achievement not found', 0;
    RETURN;
  END IF;

  -- Check if already unlocked
  IF EXISTS (
    SELECT 1 FROM user_achievements
    WHERE user_id = p_user_id
    AND achievement_id = p_achievement_id
    AND is_locked = false
  ) THEN
    RETURN QUERY SELECT false, 'Achievement already unlocked', 0;
    RETURN;
  END IF;

  -- Unlock the achievement
  UPDATE user_achievements
  SET is_locked = false,
      unlocked_at = now(),
      unlocked_by_event = p_event_type
  WHERE user_id = p_user_id
  AND achievement_id = p_achievement_id;

  -- Get points reward
  v_points_awarded := v_achievement.points_reward;

  -- Update user stats
  UPDATE user_stats
  SET total_points = total_points + v_points_awarded,
      achievements_unlocked = achievements_unlocked + 1,
      achievements_in_progress = GREATEST(achievements_in_progress - 1, 0),
      updated_at = now()
  WHERE user_id = p_user_id
  AND workspace_id = p_workspace_id
  RETURNING * INTO v_user_stat;

  RETURN QUERY SELECT true, 'Achievement unlocked successfully', v_points_awarded;
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
   ('achievements', 'user_achievements', 'user_stats');
   -- Expected: 3

2. RLS policies:
   SELECT COUNT(*) FROM pg_policies
   WHERE tablename IN ('achievements', 'user_achievements', 'user_stats');
   -- Expected: 5 (achievements: 1, user_achievements: 2, user_stats: 2)

3. Indexes created:
   SELECT COUNT(*) FROM pg_indexes
   WHERE tablename IN ('achievements', 'user_achievements', 'user_stats')
   AND schemaname = 'public';
   -- Expected: 10+ indexes

4. Functions created:
   SELECT COUNT(*) FROM pg_proc
   WHERE proname IN ('calculate_move_success_rate', 'update_experience_level', 'unlock_achievement')
   AND pronamespace = 'public'::regnamespace;
   -- Expected: 3

5. Triggers:
   SELECT COUNT(*) FROM pg_trigger
   WHERE tgrelname IN ('user_stats');
   -- Expected: 1+

6. Foreign key constraints:
   SELECT COUNT(*) FROM information_schema.table_constraints
   WHERE constraint_type = 'FOREIGN KEY'
   AND table_name IN ('achievements', 'user_achievements', 'user_stats');
   -- Expected: 8+ FKs
*/
