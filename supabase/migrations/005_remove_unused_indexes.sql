-- Remove Unused Indexes (Performance Cleanup)
-- We are selectively dropping indexes reported as unused, while PRESERVING those critical for RLS and Foreign Keys.

-- billing_history
DROP INDEX IF EXISTS idx_billing_history_user;
DROP INDEX IF EXISTS idx_billing_history_workspace;
DROP INDEX IF EXISTS idx_billing_history_merchant_txn;
DROP INDEX IF EXISTS idx_billing_history_status;
DROP INDEX IF EXISTS idx_billing_history_created;
DROP INDEX IF EXISTS idx_billing_history_plan;

-- autopay_subscriptions
DROP INDEX IF EXISTS idx_autopay_subs_merchant_id;
DROP INDEX IF EXISTS idx_autopay_subs_status;
DROP INDEX IF EXISTS idx_autopay_subs_user;
DROP INDEX IF EXISTS idx_autopay_subs_workspace;
DROP INDEX IF EXISTS idx_autopay_subs_plan;
DROP INDEX IF EXISTS idx_autopay_subs_next_billing;
DROP INDEX IF EXISTS idx_autopay_subs_created;

-- autopay_payments
DROP INDEX IF EXISTS idx_autopay_payments_subscription;
DROP INDEX IF EXISTS idx_autopay_payments_user;
DROP INDEX IF EXISTS idx_autopay_payments_payment_id;
DROP INDEX IF EXISTS idx_autopay_payments_status;
DROP INDEX IF EXISTS idx_autopay_payments_date;
DROP INDEX IF EXISTS idx_autopay_payments_created;

-- assets
DROP INDEX IF EXISTS idx_assets_workspace;
DROP INDEX IF EXISTS idx_assets_move;
DROP INDEX IF EXISTS idx_assets_icp;
DROP INDEX IF EXISTS idx_assets_type;
DROP INDEX IF EXISTS idx_assets_status;
DROP INDEX IF EXISTS idx_assets_tags;

-- quests / gamification
DROP INDEX IF EXISTS idx_quests_workspace;
DROP INDEX IF EXISTS idx_quests_status;
DROP INDEX IF EXISTS idx_quest_moves_quest;
DROP INDEX IF EXISTS idx_quest_moves_move;
DROP INDEX IF EXISTS idx_quest_milestones_quest;

-- moves / sprints (Legacy/Unused)
DROP INDEX IF EXISTS idx_moves_workspace;
DROP INDEX IF EXISTS idx_moves_sprint;
DROP INDEX IF EXISTS idx_moves_status;
DROP INDEX IF EXISTS idx_moves_icp;
DROP INDEX IF EXISTS idx_sprints_workspace;
DROP INDEX IF EXISTS idx_sprints_status;

-- other modules
DROP INDEX IF EXISTS idx_capability_nodes_workspace;
DROP INDEX IF EXISTS idx_capability_nodes_status;
DROP INDEX IF EXISTS idx_anomalies_move;
DROP INDEX IF EXISTS idx_anomalies_status;
DROP INDEX IF EXISTS idx_logs_move;
DROP INDEX IF EXISTS idx_logs_date;
DROP INDEX IF EXISTS idx_subscriptions_user_id;
DROP INDEX IF EXISTS idx_subscriptions_status;
DROP INDEX IF EXISTS idx_workspaces_owner_id;
DROP INDEX IF EXISTS idx_profiles_plan;
DROP INDEX IF EXISTS idx_payments_user_id;
DROP INDEX IF EXISTS idx_payments_status;
DROP INDEX IF EXISTS idx_payments_phonepe_txn;

-- agent_executions
DROP INDEX IF EXISTS idx_agent_executions_status;
-- Keeping idx_agent_executions_intake_id as it supports RLS join

-- shared_links
DROP INDEX IF EXISTS idx_shared_links_token;
-- Keeping idx_shared_links_intake_id as it supports RLS join

-- user_profiles
DROP INDEX IF EXISTS idx_user_profiles_onboarding;

-- NOTE: We are explicitly KEEPING the following despite linter warnings, as they support RLS or recent Foreign Keys:
-- idx_onboarding_intake_user_id
-- idx_onboarding_intake_sales_rep
-- idx_onboarding_intake_share_token (Useful for token lookups)
-- idx_shared_links_sales_rep
-- idx_onboarding_analyses_user
-- idx_projects_user
-- idx_plans_project
-- idx_positioning_blueprints_analysis
-- idx_positioning_blueprints_user
-- idx_moves_line_of_op
-- idx_moves_maneuver_type
-- idx_maneuver_prereq_required_cap
