-- ============================================
-- WORKSPACE SETUP SCRIPT
-- Run this AFTER migration 004 to set up your first workspace
-- ============================================

-- Step 1: Create a default workspace
-- This will return the workspace_id - SAVE THIS!
INSERT INTO workspaces (name, slug, plan, cohorts_limit, moves_per_sprint_limit)
VALUES ('Default Workspace', 'default', 'Ascent', 3, 5)
ON CONFLICT (slug) DO UPDATE SET name = 'Default Workspace'
RETURNING id as workspace_id, name, plan;

-- Step 2: Get your user ID
-- Run this separately to find your user_id:
SELECT id as user_id, email 
FROM auth.users 
ORDER BY created_at DESC 
LIMIT 5;

-- Step 3: Assign yourself to the workspace
-- REPLACE THESE VALUES with actual IDs from steps 1 and 2:
-- INSERT INTO user_workspaces (user_id, workspace_id, role)
-- VALUES (
--   '<YOUR_USER_ID_HERE>'::uuid,
--   '<YOUR_WORKSPACE_ID_HERE>'::uuid,
--   'Owner'
-- );

-- Step 4: Verify setup
-- After running step 3, verify everything is connected:
SELECT 
  u.email,
  uw.role,
  w.name as workspace_name,
  w.plan,
  w.cohorts_limit
FROM user_workspaces uw
JOIN workspaces w ON w.id = uw.workspace_id
JOIN auth.users u ON u.id = uw.user_id
WHERE uw.user_id = auth.uid();

-- ============================================
-- OPTIONAL: Create sample data for testing
-- ============================================

-- Sample Global Strategy (requires workspace_id)
-- INSERT INTO global_strategies (
--   workspace_id,
--   business_context,
--   center_of_gravity,
--   ninety_day_goal,
--   strategy_state
-- ) VALUES (
--   '<YOUR_WORKSPACE_ID_HERE>'::uuid,
--   '{"company_name": "Acme Corp", "industry": "SaaS", "stage": "Growth", "team_size": "10-50"}'::jsonb,
--   'Product-Market Fit',
--   'Increase MRR by 25% through targeted enterprise outreach',
--   'Active'
-- );

-- Sample Cohort/ICP (requires workspace_id)
-- INSERT INTO cohorts (
--   workspace_id,
--   name,
--   executive_summary,
--   demographics,
--   psychographics,
--   tags
-- ) VALUES (
--   '<YOUR_WORKSPACE_ID_HERE>'::uuid,
--   'Enterprise SaaS Buyers',
--   'Mid-market SaaS companies looking to scale operations',
--   '{"company_size": "50-200", "industry": "Technology", "revenue": "$5M-$20M"}'::jsonb,
--   '{"motivation": 8, "ability": 7, "risk_tolerance": 6}'::jsonb,
--   ARRAY['growth_focused', 'tech_savvy', 'budget_conscious']
-- );

