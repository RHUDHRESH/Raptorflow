-- RaptorFlow Complete Database Schema (v2.0) - Part 10: Seed Data
-- Initial data for system functionality

-- =====================================
-- 31. SYSTEM SKILLS REGISTRATION
-- =====================================

-- Register core system skills
INSERT INTO skills (name, description, instructions, type, category, is_active) VALUES
(
    'hook_generator',
    'Generates compelling hooks for marketing content',
    'Create attention-grabbing opening lines that stop the scroll and drive engagement.',
    'system',
    'hook',
    true
),
(
    'structure_optimizer',
    'Optimizes content structure for maximum impact',
    'Organize content flow for readability and persuasion.',
    'system',
    'structure',
    true
),
(
    'tone_adapter',
    'Adapts content tone to match brand voice',
    'Adjust language style to match specified brand personality.',
    'system',
    'tone',
    true
),
(
    'cta_crafter',
    'Creates compelling calls-to-action',
    'Design persuasive CTAs that drive desired user actions.',
    'system',
    'cta',
    true
),
(
    'proof_integrator',
    'Integrates social proof and credibility markers',
    'Weave in testimonials, data, and authority signals.',
    'system',
    'proof',
    true
),
(
    'edit_polish',
    'Polishes and refines content for professional quality',
    'Enhance clarity, grammar, and flow of final content.',
    'system',
    'edit_polish',
    true
) ON CONFLICT (name) DO NOTHING;

-- Register skill presets for common use cases
INSERT INTO skill_presets (name, description, intent, channel, skill_stack, is_active) VALUES
(
    'Cold Email Template',
    'Optimized skill stack for cold outreach emails',
    'leads',
    'email',
    '{
        "hook_generator": {"priority": 1, "settings": {"style": "personalized"}},
        "structure_optimizer": {"priority": 2, "settings": {"framework": "problem-solution"}},
        "tone_adapter": {"priority": 3, "settings": {"tone": "professional"}},
        "proof_integrator": {"priority": 4, "settings": {"type": "case_study"}},
        "cta_crafter": {"priority": 5, "settings": {"urgency": "medium"}},
        "edit_polish": {"priority": 6, "settings": {"formality": "business"}}
    }',
    true
),
(
    'LinkedIn Post',
    'Skill stack for engaging LinkedIn content',
    'leads',
    'linkedin',
    '{
        "hook_generator": {"priority": 1, "settings": {"style": "question"}},
        "structure_optimizer": {"priority": 2, "settings": {"framework": "storytelling"}},
        "tone_adapter": {"priority": 3, "settings": {"tone": "professional"}},
        "proof_integrator": {"priority": 4, "settings": {"type": "data"}},
        "cta_crafter": {"priority": 5, "settings": {"urgency": "low"}},
        "edit_polish": {"priority": 6, "settings": {"formality": "conversational"}}
    }',
    true
),
(
    'Sales Email',
    'Skill stack for sales-focused emails',
    'sales',
    'email',
    '{
        "hook_generator": {"priority": 1, "settings": {"style": "benefit_driven"}},
        "structure_optimizer": {"priority": 2, "settings": {"framework": "aida"}},
        "tone_adapter": {"priority": 3, "settings": {"tone": "persuasive"}},
        "proof_integrator": {"priority": 4, "settings": {"type": "testimonial"}},
        "cta_crafter": {"priority": 5, "settings": {"urgency": "high"}},
        "edit_polish": {"priority": 6, "settings": {"formality": "sales"}}
    }',
    true
) ON CONFLICT (name) DO NOTHING;

-- =====================================
-- 32. DEFAULT ASSET TYPES CONFIGURATION
-- =====================================

-- Asset type configurations are handled in application code
-- This section documents the standard asset types:
-- Text assets: email, sales-email, nurture-email, tagline, one-liner, brand-story, video-script, social-post, product-description, product-name, lead-gen-pdf, sales-talking-points
-- Visual assets: meme, social-card

-- =====================================
-- 33. BEHAVIORAL PRINCIPLES FOR EXPERIMENTS
-- =====================================

-- Create a reference table for behavioral principles
CREATE TABLE IF NOT EXISTS behavioral_principles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    example_usage TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO behavioral_principles (name, description, example_usage) VALUES
(
    'friction',
    'Reduce barriers to action to increase conversion rates',
    'Remove form fields, simplify checkout process, eliminate unnecessary steps'
),
(
    'identity',
    'Leverage self-concept and social identity to drive behavior',
    'Appeal to aspirational identity, reinforce group membership, use social identity cues'
),
(
    'loss_aversion',
    'Frame choices around potential losses rather than gains',
    'Highlight what users will lose by not acting, use scarcity, emphasize missed opportunities'
),
(
    'social_proof',
    'Use social validation to influence decision making',
    'Show testimonials, display user counts, highlight popular choices, use authority signals'
),
(
    'pattern_interrupt',
    'Break expected patterns to capture attention',
    'Use unexpected visuals, surprising statements, unconventional formats'
),
(
    'commitment',
    'Leverage consistency principle to maintain engagement',
    'Get small commitments first, use public commitments, create investment loops'
),
(
    'pricing_psych',
    'Apply psychological pricing principles',
    'Use anchoring, decoy pricing, charm pricing, bundle pricing strategies'
) ON CONFLICT (name) DO NOTHING;

-- =====================================
-- 34. DEFAULT WORKSPACE SETTINGS
-- =====================================

-- Create default workspace settings template
CREATE TABLE IF NOT EXISTS default_workspace_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key TEXT UNIQUE NOT NULL,
    setting_value JSONB,
    description TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO default_workspace_settings (setting_key, setting_value, description) VALUES
(
    'features_enabled',
    '{
        "campaigns": true,
        "moves": true,
        "blackbox": true,
        "muse": true,
        "radar": true,
        "icp": true,
        "foundation": true,
        "matrix": true
    }',
    'Default enabled features for new workspaces'
),
(
    'limits',
    '{
        "campaigns_per_month": 50,
        "moves_per_month": 200,
        "experiments_per_month": 100,
        "assets_per_month": 500,
        "storage_mb": 1024,
        "team_members": 10
    }',
    'Default limits for starter plan workspaces'
),
(
    'notifications',
    '{
        "email_notifications": true,
        "push_notifications": true,
        "campaign_updates": true,
        "experiment_results": true,
        "team_activity": true,
        "system_updates": false
    }',
    'Default notification preferences'
),
(
    'ui_preferences',
    '{
        "theme": "light",
        "language": "en",
        "timezone": "UTC",
        "date_format": "MM/DD/YYYY",
        "time_format": "12h"
    }',
    'Default UI preferences'
) ON CONFLICT (setting_key) DO NOTHING;

-- =====================================
-- 35. SYSTEM CONFIGURATION
-- =====================================

-- System-wide configuration
CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key TEXT UNIQUE NOT NULL,
    config_value JSONB,
    description TEXT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO system_config (config_key, config_value, description) VALUES
(
    'app_version',
    '"2.0.0"',
    'Current application version'
),
(
    'supported_languages',
    '["en", "es", "fr", "de", "it", "pt", "ja", "zh"]',
    'Supported application languages'
),
(
    'default_currency',
    '"USD"',
    'Default currency for billing'
),
(
    'max_file_size_mb',
    '50',
    'Maximum file upload size in MB'
),
(
    'vector_embedding_dimension',
    '768',
    'Dimension for vector embeddings'
),
(
    'similarity_threshold',
    '0.8',
    'Default threshold for vector similarity searches'
),
(
    'cleanup_retention_days',
    '90',
    'Days to retain deleted data before permanent cleanup'
) ON CONFLICT (config_key) DO NOTHING;

-- =====================================
-- 36. SAMPLE TEMPLATES
-- =====================================

-- Sample campaign templates
CREATE TABLE IF NOT EXISTS campaign_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    objective TEXT,
    duration_days INTEGER DEFAULT 30,

    template_data JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO campaign_templates (name, description, objective, duration_days, template_data) VALUES
(
    'Product Launch Campaign',
    'Complete campaign template for new product launches',
    'launch',
    30,
    '{
        "phases": [
            {"name": "Pre-Launch Teaser", "duration": 7, "moves": ["social_announcement", "email_teaser"]},
            {"name": "Launch Day", "duration": 1, "moves": ["product_announcement", "launch_email"]},
            {"name": "Launch Week", "duration": 7, "moves": ["demo_webinar", "early_bird_offer"]},
            {"name": "Post-Launch", "duration": 15, "moves": ["testimonial_collection", "follow_up_sequence"]}
        ],
        "kpis": ["signups", "demo_requests", "early_sales"],
        "channels": ["email", "linkedin", "twitter"],
        "assets_required": ["landing_page", "email_templates", "social_posts"]
    }'
),
(
    'Lead Generation Campaign',
    'Campaign focused on generating qualified leads',
    'acquire',
    21,
    '{
        "phases": [
            {"name": "Awareness", "duration": 7, "moves": ["content_marketing", "social_engagement"]},
            {"name": "Consideration", "duration": 7, "moves": ["case_study_promotion", "webinar"]},
            {"name": "Conversion", "duration": 7, "moves": ["free_trial_offer", "consultation_booking"]}
        ],
        "kpis": ["leads", "mqls", "sqls"],
        "channels": ["linkedin", "email", "content"],
        "assets_required": ["lead_magnet", "landing_pages", "email_sequence"]
    }'
),
(
    'Re-engagement Campaign',
    'Campaign to re-engage dormant customers',
    'retain',
    14,
    '{
        "phases": [
            {"name": "Segmentation", "duration": 2, "moves": ["data_analysis", "audience_segmentation"]},
            {"name": "Personalized Outreach", "duration": 7, "moves": ["personalized_emails", "special_offers"]},
            {"name": "Follow-up", "duration": 5, "moves": ["phone_calls", "final_offer"]}
        ],
        "kpis": ["re_engagement_rate", "conversion_rate", "revenue"],
        "channels": ["email", "phone", "personalized_outreach"],
        "assets_required": ["email_templates", "offer_assets", "follow_up_scripts"]
    }'
) ON CONFLICT (name) DO NOTHING;

-- Sample move templates
CREATE TABLE IF NOT EXISTS move_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    goal TEXT,
    channel TEXT,
    duration_days INTEGER DEFAULT 7,

    template_data JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO move_templates (name, description, goal, channel, duration_days, template_data) VALUES
(
    'Cold Email Sequence',
    'Multi-touch cold email outreach sequence',
    'leads',
    'email',
    7,
    '{
        "steps": [
            {"day": 1, "type": "initial_outreach", "subject": "Quick question"},
            {"day": 3, "type": "follow_up", "subject": "Re: Quick question"},
            {"day": 7, "type": "breakup", "subject": "Closing the loop"}
        ],
        "assets_required": ["email_templates", "prospect_list"],
        "success_metrics": ["reply_rate", "meeting_booked"]
    }'
),
(
    'LinkedIn Content Series',
    'Series of LinkedIn posts to build authority',
    'leads',
    'linkedin',
    5,
    '{
        "posts": [
            {"day": 1, "type": "insight", "format": "text_with_image"},
            {"day": 2, "type": "story", "format": "carousel"},
            {"day": 3, "type": "how_to", "format": "video"},
            {"day": 4, "type": "case_study", "format": "document"},
            {"day": 5, "type": "question", "format": "poll"}
        ],
        "assets_required": ["content_calendar", "visual_assets"],
        "success_metrics": ["engagement_rate", "profile_views", "connection_requests"]
    }'
),
(
    'A/B Test Experiment',
    'Structured A/B test for optimization',
    'proof',
    'email',
    14,
    '{
        "hypothesis": "Subject line B will outperform subject line A",
        "variants": [
            {"name": "Control", "subject": "Traditional approach"},
            {"name": "Variant", "subject": "New approach"}
        ],
        "sample_size": "1000_contacts",
        "success_metric": "open_rate",
        "assets_required": ["email_variants", "tracking_setup"],
        "success_metrics": ["statistical_significance", "lift_percentage"]
    }'
) ON CONFLICT (name) DO NOTHING;

-- =====================================
-- 37. FINAL VALIDATION
-- =====================================

-- Create a function to validate the database setup
CREATE OR REPLACE FUNCTION validate_database_setup()
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    table_count INTEGER;
    index_count INTEGER;
    policy_count INTEGER;
    function_count INTEGER;
    trigger_count INTEGER;
BEGIN
    -- Count database objects
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE';

    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'public';

    SELECT COUNT(*) INTO policy_count
    FROM pg_policies
    WHERE schemaname = 'public';

    SELECT COUNT(*) INTO function_count
    FROM information_schema.routines
    WHERE routine_schema = 'public'
    AND routine_type = 'FUNCTION';

    SELECT COUNT(*) INTO trigger_count
    FROM information_schema.triggers
    WHERE trigger_schema = 'public';

    result := jsonb_build_object(
        'validation_timestamp', now(),
        'tables_count', table_count,
        'indexes_count', index_count,
        'rls_policies_count', policy_count,
        'functions_count', function_count,
        'triggers_count', trigger_count,
        'status', 'completed',
        'version', '2.0.0'
    );

    RETURN result;
END;
$$ language 'plpgsql';

-- Run validation and store result
INSERT INTO system_config (config_key, config_value, description) VALUES
(
    'database_validation',
    validate_database_setup(),
    'Database setup validation results'
) ON CONFLICT (config_key) DO UPDATE SET
    config_value = validate_database_setup(),
    updated_at = now();
