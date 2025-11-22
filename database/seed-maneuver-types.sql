-- Seed Data: Maneuver Types (Templates)
-- These are the tactical playbooks that can be instantiated as Moves

-- OFFENSIVE MANEUVERS
INSERT INTO maneuver_types (id, name, category, base_duration_days, fogg_role, intensity_score, risk_profile, description, default_config) VALUES
('maneuver-authority-sprint', 'Authority Sprint', 'Offensive', 14, 'Spark', 7, 'Medium',
 'High-velocity content push to establish thought leadership. Rapid-fire publishing across channels to dominate a narrative.',
 '{"channels": ["LinkedIn", "Blog", "Email"], "content_cadence": "Daily", "typical_icps": ["Enterprise", "B2B SaaS"]}'::jsonb),

('maneuver-scarcity-flank', 'Scarcity Flank', 'Offensive', 7, 'Facilitator', 8, 'Brand_Risk',
 'Limited-time offer to drive urgency. High-intensity campaign with countdown timers and exclusive access.',
 '{"channels": ["Email", "Landing Page"], "intensity": "High", "risk_factors": ["Brand perception"]}'::jsonb),

('maneuver-viral-loop', 'Viral Loop', 'Offensive', 21, 'Spark', 9, 'Medium',
 'Engineer viral growth mechanics into product/campaign. Referral incentives and social sharing mechanisms.',
 '{"channels": ["Product", "Email", "Social"], "required_capabilities": ["Referral Engine", "Marketing Automation"]}'::jsonb),

('maneuver-trojan-horse', 'Trojan Horse', 'Offensive', 30, 'Facilitator', 6, 'Low',
 'Free tool or content that captures leads and demonstrates value. Educational content that naturally leads to product.',
 '{"channels": ["Product", "SEO", "Content"], "typical_icps": ["PLG", "Self-serve"]}'::jsonb),

('maneuver-competitive-raid', 'Competitive Raid', 'Offensive', 14, 'Signal', 7, 'Brand_Risk',
 'Direct comparison campaigns against competitors. Aggressive positioning and feature comparisons.',
 '{"channels": ["Paid Ads", "Landing Page", "SEO"], "risk_factors": ["Legal review required"]}'::jsonb),

('maneuver-blitz-campaign', 'Blitz Campaign', 'Offensive', 5, 'Spark', 10, 'Budget_Risk',
 'Short, intense multi-channel push for product launch or announcement. Maximum visibility in minimal time.',
 '{"channels": ["All channels"], "intensity": "Maximum", "budget": "High"}}'::jsonb),

-- DEFENSIVE MANEUVERS
('maneuver-garrison', 'The Garrison', 'Defensive', 30, 'Facilitator', 4, 'Low',
 'Proactive customer retention. Regular check-ins, health monitoring, and expansion plays for existing accounts.',
 '{"channels": ["Email", "In-app", "Account Management"], "focus": "Retention", "typical_icps": ["Enterprise", "High-value"]}'::jsonb),

('maneuver-community-fort', 'Community Fort', 'Defensive', 60, 'Signal', 5, 'Low',
 'Build defensible community moat. Foster user connections, peer support, and tribal identity.',
 '{"channels": ["Community", "Events", "Content"], "metrics": ["Engagement", "Retention"]}'::jsonb),

('maneuver-winback-raid', 'Win-Back Raid', 'Defensive', 14, 'Facilitator', 6, 'Medium',
 'Targeted campaign to reactivate churned customers. Personalized outreach with new value props or incentives.',
 '{"channels": ["Email", "Direct Mail", "LinkedIn"], "segments": ["Churned < 90 days"]}'::jsonb),

('maneuver-crisis-shield', 'Crisis Shield', 'Defensive', 3, 'Signal', 9, 'Brand_Risk',
 'Rapid response to brand threat or PR crisis. Coordinated messaging and stakeholder communication.',
 '{"channels": ["PR", "Social", "Email"], "activation": "Emergency", "intensity": "Maximum"}}'::jsonb),

('maneuver-price-defense', 'Price Defense', 'Defensive', 7, 'Facilitator', 7, 'Budget_Risk',
 'Counter competitive pricing pressure. Value re-framing and bundling strategies.',
 '{"channels": ["Sales", "Email", "Landing Page"], "triggers": ["Price objections"]}'::jsonb),

-- LOGISTICAL MANEUVERS
('maneuver-asset-forge', 'Asset Forge', 'Logistical', 14, 'Facilitator', 5, 'Low',
 'Systematic content/asset creation sprint. Build reusable library of marketing collateral.',
 '{"output": ["Case studies", "One-pagers", "Templates"], "typical_quantity": "10-20 assets"}}'::jsonb),

('maneuver-content-calendar', 'Content Calendar Build', 'Logistical', 7, 'Facilitator', 4, 'Low',
 'Plan and schedule content pipeline. Create editorial calendar with themes and distribution plan.',
 '{"planning_horizon": "90 days", "channels": ["Blog", "Social", "Email"]}'::jsonb),

('maneuver-tech-stack-upgrade', 'Tech Stack Upgrade', 'Logistical', 30, 'Facilitator', 6, 'Budget_Risk',
 'Implement or migrate marketing technology. Tool evaluation, setup, and team training.',
 '{"phases": ["Evaluation", "Implementation", "Migration", "Training"]}'::jsonb),

('maneuver-process-hardening', 'Process Hardening', 'Logistical', 14, 'Facilitator', 4, 'Low',
 'Systematize and document workflows. Create SOPs and automate repetitive tasks.',
 '{"output": ["SOPs", "Templates", "Automation workflows"]}'::jsonb),

('maneuver-team-sprint', 'Team Sprint Training', 'Logistical', 5, 'Facilitator', 3, 'Low',
 'Intensive team training or skill development. Workshops and capability building.',
 '{"topics": ["Skills", "Tools", "Strategy"], "format": "Workshops"}}'::jsonb),

-- RECON MANEUVERS
('maneuver-intel-sweep', 'Intel Sweep', 'Recon', 7, 'Signal', 4, 'Low',
 'Systematic market and competitor research. Deep-dive analysis and insight gathering.',
 '{"output": ["Research report", "Competitive analysis", "Market insights"]}'::jsonb),

('maneuver-customer-interviews', 'Customer Interview Blitz', 'Recon', 14, 'Signal', 5, 'Low',
 'Structured customer discovery. Interview campaigns to validate assumptions and find insights.',
 '{"target": "20-30 interviews", "output": ["Insights report", "ICP refinement"]}'::jsonb),

('maneuver-data-mining', 'Data Mining', 'Recon', 10, 'Signal', 5, 'Low',
 'Extract insights from existing data. Analytics deep-dive to find hidden patterns and opportunities.',
 '{"sources": ["Product analytics", "CRM", "Support tickets"], "output": ["Insights dashboard"]}'::jsonb),

('maneuver-ab-test-battery', 'A/B Test Battery', 'Recon', 21, 'Signal', 6, 'Low',
 'Run multiple experiments to find winning tactics. Systematic testing of hypotheses.',
 '{"test_count": "5-10 tests", "metrics": ["Conversion", "Engagement", "Retention"]}'::jsonb),

('maneuver-market-probe', 'Market Probe', 'Recon', 14, 'Signal', 6, 'Budget_Risk',
 'Test new market or segment with low-risk campaign. Validate demand before full commitment.',
 '{"approach": "Lean campaign", "budget": "Limited", "decision_criteria": ["Response rate", "CAC"]}'::jsonb);

-- Link maneuvers to required capabilities via junction table
INSERT INTO maneuver_prerequisites (maneuver_type_id, required_capability_id) VALUES
-- Foundation maneuvers (no prerequisites - everyone starts here)

-- Authority Sprint requires content + social
('maneuver-authority-sprint', 'cap-foundation-content'),
('maneuver-authority-sprint', 'cap-traction-social'),

-- Scarcity Flank requires email + lead magnet
('maneuver-scarcity-flank', 'cap-traction-leadmagnet'),
('maneuver-scarcity-flank', 'cap-traction-nurture'),

-- Viral Loop requires advanced capabilities
('maneuver-viral-loop', 'cap-dominance-referral'),
('maneuver-viral-loop', 'cap-scale-automation'),

-- Trojan Horse requires content + SEO
('maneuver-trojan-horse', 'cap-foundation-content'),
('maneuver-trojan-horse', 'cap-traction-seo'),

-- Competitive Raid requires paid ads
('maneuver-competitive-raid', 'cap-scale-paidads'),
('maneuver-competitive-raid', 'cap-traction-leadmagnet'),

-- Blitz Campaign requires all scale capabilities
('maneuver-blitz-campaign', 'cap-scale-paidads'),
('maneuver-blitz-campaign', 'cap-scale-automation'),
('maneuver-blitz-campaign', 'cap-traction-social'),

-- Garrison requires pipeline + nurture
('maneuver-garrison', 'cap-traction-pipeline'),
('maneuver-garrison', 'cap-traction-nurture'),

-- Community Fort requires community building
('maneuver-community-fort', 'cap-scale-community'),

-- Win-Back requires nurture
('maneuver-winback-raid', 'cap-traction-nurture'),

-- Asset Forge requires just content foundation
('maneuver-asset-forge', 'cap-foundation-content'),

-- Intel Sweep requires analytics
('maneuver-intel-sweep', 'cap-foundation-analytics'),

-- Customer Interviews requires ICP
('maneuver-customer-interviews', 'cap-foundation-icp'),

-- Data Mining requires analytics
('maneuver-data-mining', 'cap-foundation-analytics'),

-- A/B Test Battery requires testing capability
('maneuver-ab-test-battery', 'cap-scale-abtesting'),

-- Market Probe requires paid ads
('maneuver-market-probe', 'cap-scale-paidads');

-- Note: Update capability_nodes.unlocks_maneuver_ids after this runs
-- This creates the reverse relationship for the Tech Tree UI


