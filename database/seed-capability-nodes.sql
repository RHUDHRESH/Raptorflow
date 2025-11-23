-- Seed Data: Capability Nodes for Tech Tree
-- Foundation Tier - Basic capabilities required for all operations
-- Replace 'YOUR_WORKSPACE_ID' with actual workspace UUID

INSERT INTO capability_nodes (id, name, tier, status, workspace_id, parent_node_ids, description, completion_criteria) VALUES
-- Foundation Tier
('cap-foundation-analytics', 'Analytics Core', 'Foundation', 'Unlocked', 'YOUR_WORKSPACE_ID', '{}', 
 'Basic analytics tracking and reporting', 
 '{"criteria": ["Install analytics tool", "Track key events", "Set up dashboard"]}'::jsonb),

('cap-foundation-icp', 'ICP Definition', 'Foundation', 'Unlocked', 'YOUR_WORKSPACE_ID', '{}', 
 'Define and document Ideal Customer Profiles', 
 '{"criteria": ["Create first ICP", "Document pain points", "Identify channels"]}'::jsonb),

('cap-foundation-content', 'Content Production v1', 'Foundation', 'Unlocked', 'YOUR_WORKSPACE_ID', '{}', 
 'Basic content creation workflow', 
 '{"criteria": ["Create 5 pieces of content", "Establish review process"]}'::jsonb),

('cap-foundation-email', 'Email Setup', 'Foundation', 'Unlocked', 'YOUR_WORKSPACE_ID', '{}', 
 'Email infrastructure and basic campaigns', 
 '{"criteria": ["Set up email platform", "Build first list", "Send first campaign"]}'::jsonb),

-- Traction Tier - Growth capabilities
('cap-traction-leadmagnet', 'Lead Magnet v1', 'Traction', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-foundation-content'::uuid, 'cap-foundation-email'::uuid], 
 'Create and deploy lead generation assets', 
 '{"criteria": ["Create lead magnet", "Build landing page", "Generate 50 leads"]}'::jsonb),

('cap-traction-nurture', 'Email Nurture Flow', 'Traction', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-foundation-email'::uuid, 'cap-traction-leadmagnet'::uuid], 
 'Automated email nurture sequences', 
 '{"criteria": ["Build 5-email sequence", "Segment contacts", "Achieve 25% open rate"]}'::jsonb),

('cap-traction-social', 'Social Presence', 'Traction', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-foundation-content'::uuid, 'cap-foundation-icp'::uuid], 
 'Consistent social media presence', 
 '{"criteria": ["Post 3x/week for 4 weeks", "Gain 100 followers", "Generate engagement"]}'::jsonb),

('cap-traction-seo', 'SEO Foundation', 'Traction', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-foundation-content'::uuid, 'cap-foundation-analytics'::uuid], 
 'Basic SEO optimization and organic traffic', 
 '{"criteria": ["Optimize 10 pages", "Rank for 5 keywords", "Generate organic traffic"]}'::jsonb),

('cap-traction-pipeline', 'Sales Pipeline v1', 'Traction', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-foundation-icp'::uuid, 'cap-traction-leadmagnet'::uuid], 
 'Structured sales process and CRM', 
 '{"criteria": ["Set up CRM", "Define pipeline stages", "Close 5 deals"]}'::jsonb),

-- Scale Tier - Advanced capabilities
('cap-scale-paidads', 'Paid Ads', 'Scale', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-traction-leadmagnet'::uuid, 'cap-foundation-analytics'::uuid], 
 'Paid advertising campaigns', 
 '{"criteria": ["Launch ad campaign", "Achieve target CAC", "Scale to $1k/month spend"]}'::jsonb),

('cap-scale-abtesting', 'A/B Testing', 'Scale', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-foundation-analytics'::uuid, 'cap-traction-leadmagnet'::uuid], 
 'Systematic experimentation framework', 
 '{"criteria": ["Run 5 A/B tests", "Implement testing framework", "Improve key metric by 20%"]}'::jsonb),

('cap-scale-automation', 'Marketing Automation', 'Scale', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-traction-nurture'::uuid, 'cap-traction-pipeline'::uuid], 
 'Advanced workflow automation', 
 '{"criteria": ["Build 3 automation workflows", "Score leads automatically", "Reduce manual work 50%"]}'::jsonb),

('cap-scale-partnerships', 'Partnership Channel', 'Scale', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-traction-pipeline'::uuid, 'cap-foundation-icp'::uuid], 
 'Strategic partnership development', 
 '{"criteria": ["Close 3 partnerships", "Co-marketing campaign", "Partner-sourced revenue"]}'::jsonb),

('cap-scale-community', 'Community Building', 'Scale', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-traction-social'::uuid, 'cap-foundation-content'::uuid], 
 'Engaged user community', 
 '{"criteria": ["Launch community platform", "Reach 500 members", "Weekly engagement"]}'::jsonb),

-- Dominance Tier - Market leadership capabilities
('cap-dominance-referral', 'Referral Engine', 'Dominance', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-scale-automation'::uuid, 'cap-scale-community'::uuid], 
 'Viral growth through referrals', 
 '{"criteria": ["Build referral program", "30% of users refer", "Viral coefficient > 1"]}'::jsonb),

('cap-dominance-predictive', 'Predictive Analytics', 'Dominance', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-scale-abtesting'::uuid, 'cap-foundation-analytics'::uuid], 
 'ML-powered prediction and optimization', 
 '{"criteria": ["Implement predictive model", "Forecast churn", "Predict LTV"]}'::jsonb),

('cap-dominance-brandcampaign', 'Brand Campaigns', 'Dominance', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-scale-paidads'::uuid, 'cap-scale-community'::uuid], 
 'Large-scale brand awareness initiatives', 
 '{"criteria": ["Launch brand campaign", "1M impressions", "Brand lift study"]}'::jsonb),

('cap-dominance-international', 'International Expansion', 'Dominance', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-scale-partnerships'::uuid, 'cap-foundation-icp'::uuid], 
 'Enter new geographic markets', 
 '{"criteria": ["Launch in 2 markets", "Localized content", "International revenue"]}'::jsonb),

('cap-dominance-platform', 'Platform Play', 'Dominance', 'Locked', 'YOUR_WORKSPACE_ID', 
 ARRAY['cap-scale-community'::uuid, 'cap-scale-partnerships'::uuid], 
 'Build ecosystem around your product', 
 '{"criteria": ["Launch API/SDK", "10+ integrations", "Partner marketplace"]}'::jsonb);

-- Update unlocks_maneuver_ids to link capabilities to maneuvers they unlock
-- This will be populated after maneuver_types are inserted



