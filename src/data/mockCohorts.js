export const JOURNEY_STAGES = [
    { id: 'unaware', label: 'Unaware', color: 'bg-neutral-200', description: "Don't know they have a problem" },
    { id: 'problem_aware', label: 'Problem Aware', color: 'bg-neutral-300', description: 'Know problem, not solutions' },
    { id: 'solution_aware', label: 'Solution Aware', color: 'bg-neutral-400', description: 'Know solutions exist' },
    { id: 'product_aware', label: 'Product Aware', color: 'bg-neutral-600', description: 'Know your product' },
    { id: 'most_aware', label: 'Most Aware', color: 'bg-neutral-900', description: 'Ready to buy' },
];

export const INITIAL_COHORTS = [
    {
        id: 'c1',
        name: 'Enterprise CTOs',
        description: 'Tech leaders at large companies',
        avatar: '🎯',
        health_score: 85,
        size: 1250,
        journey_distribution: {
            unaware: 0.2,
            problem_aware: 0.3,
            solution_aware: 0.25,
            product_aware: 0.15,
            most_aware: 0.1,
        },
        buying_triggers: [
            { id: 't1', trigger: 'End of quarter budget pressure', strength: 'high', timing: 'Q4', signal: 'Mentions budget deadline' },
            { id: 't2', trigger: 'Competitor raised prices', strength: 'medium', timing: 'Ongoing', signal: 'Price comparison searches' },
        ],
        decision_criteria: [
            { id: 'd1', criterion: 'ROI proven in 90 days', weight: 0.3, deal_breaker: true },
            { id: 'd2', criterion: 'Easy integration', weight: 0.25, deal_breaker: false },
            { id: 'd3', criterion: 'Social proof from peers', weight: 0.25, deal_breaker: false },
            { id: 'd4', criterion: 'Price competitiveness', weight: 0.2, deal_breaker: false },
        ],
        objection_map: [
            {
                id: 'o1',
                objection: "We don't have budget",
                frequency: 'very_common',
                stage: 'product_aware',
                root_cause: 'Perceived as nice-to-have',
                response: 'ROI calculator showing 3× return in 90 days',
                linked_assets: []
            },
            {
                id: 'o2',
                objection: "We're locked into competitor",
                frequency: 'common',
                stage: 'solution_aware',
                root_cause: 'Switching costs concern',
                response: 'Migration case study with zero downtime',
                linked_assets: []
            },
        ],
        attention_windows: {
            linkedin: {
                channel: 'LinkedIn',
                best_times: ['Tue 9am', 'Wed 2pm'],
                receptivity: 'high',
                preferred_formats: ['Carousel', 'Video', 'Article'],
                frequency_tolerance: '3×/week'
            },
            email: {
                channel: 'Email',
                best_times: ['Mon 8am'],
                receptivity: 'medium',
                preferred_formats: ['Newsletter', 'Case Study'],
                frequency_tolerance: '2×/week'
            },
        },
        competitive_frame: {
            direct_competitors: ['HubSpot', 'Marketo', 'Salesforce Marketing Cloud'],
            category_alternatives: ['Hiring agency', 'Building in-house', 'Status quo'],
            switching_triggers: ['Price increase', 'Feature gap', 'Poor support']
        },
        decision_making_unit: {
            roles: ['CTO', 'CMO', 'VP Marketing'],
            influencers: ['Marketing Director', 'Sales Ops'],
            decision_maker: 'CTO',
            approval_chain: ['CMO → CTO → CFO']
        }
    },
    {
        id: 'c2',
        name: 'Startup Founders',
        description: 'Early-stage company builders',
        avatar: '🚀',
        health_score: 72,
        size: 890,
        journey_distribution: {
            unaware: 0.4,
            problem_aware: 0.25,
            solution_aware: 0.2,
            product_aware: 0.1,
            most_aware: 0.05,
        },
        buying_triggers: [
            { id: 't3', trigger: 'Fundraising milestone', strength: 'high', timing: 'Post-raise', signal: 'Funding announcement' },
            { id: 't4', trigger: 'Team growth', strength: 'medium', timing: 'Ongoing', signal: 'Hiring posts' },
        ],
        decision_criteria: [
            { id: 'd5', criterion: 'Speed to value', weight: 0.35, deal_breaker: true },
            { id: 'd6', criterion: 'Pricing flexibility', weight: 0.3, deal_breaker: false },
            { id: 'd7', criterion: 'Modern UX', weight: 0.2, deal_breaker: false },
            { id: 'd8', criterion: 'Community support', weight: 0.15, deal_breaker: false },
        ],
        objection_map: [
            {
                id: 'o3',
                objection: 'Too expensive for our stage',
                frequency: 'common',
                stage: 'solution_aware',
                root_cause: 'Cash flow constraints',
                response: 'Startup pricing tier with deferred payment',
                linked_assets: []
            },
        ],
        attention_windows: {
            twitter: {
                channel: 'Twitter',
                best_times: ['Daily 7am', '9pm'],
                receptivity: 'high',
                preferred_formats: ['Thread', 'Meme'],
                frequency_tolerance: 'Daily'
            },
            email: {
                channel: 'Email',
                best_times: ['Sun 8pm'],
                receptivity: 'medium',
                preferred_formats: ['Weekly Digest'],
                frequency_tolerance: 'Weekly'
            },
        },
        competitive_frame: {
            direct_competitors: ['Notion', 'Airtable', 'Excel'],
            category_alternatives: ['Manual spreadsheets', 'Interns'],
            switching_triggers: ['Scaling pain', 'Data chaos']
        },
        decision_making_unit: {
            roles: ['Founder', 'Co-founder'],
            influencers: ['Advisors', 'Investors'],
            decision_maker: 'Founder',
            approval_chain: ['Founder']
        }
    },
    {
        id: 'c3',
        name: 'Marketing Directors',
        description: 'Marketing leaders at mid-market',
        avatar: '📊',
        health_score: 91,
        size: 2100,
        journey_distribution: {
            unaware: 0.15,
            problem_aware: 0.25,
            solution_aware: 0.3,
            product_aware: 0.2,
            most_aware: 0.1,
        },
        buying_triggers: [
            { id: 't5', trigger: 'Campaign performance decline', strength: 'high', timing: 'Quarterly reviews', signal: 'Job postings for growth' },
            { id: 't6', trigger: 'New executive mandate', strength: 'high', timing: 'Leadership changes', signal: 'New CMO announcement' },
        ],
        decision_criteria: [
            { id: 'd9', criterion: 'Team adoption ease', weight: 0.3, deal_breaker: true },
            { id: 'd10', criterion: 'Reporting capabilities', weight: 0.25, deal_breaker: false },
            { id: 'd11', criterion: 'Integration with stack', weight: 0.25, deal_breaker: true },
            { id: 'd12', criterion: 'Vendor reputation', weight: 0.2, deal_breaker: false },
        ],
        objection_map: [
            {
                id: 'o4',
                objection: 'Team is already overwhelmed',
                frequency: 'very_common',
                stage: 'solution_aware',
                root_cause: 'Change fatigue',
                response: 'Phased rollout plan with dedicated onboarding',
                linked_assets: []
            },
        ],
        attention_windows: {
            linkedin: {
                channel: 'LinkedIn',
                best_times: ['Wed 10am', 'Thu 3pm'],
                receptivity: 'high',
                preferred_formats: ['Case Study', 'Webinar'],
                frequency_tolerance: '2×/week'
            },
            webinars: {
                channel: 'Webinars',
                best_times: ['Thu 2pm'],
                receptivity: 'high',
                preferred_formats: ['Live Demo', 'Panel'],
                frequency_tolerance: 'Monthly'
            },
        },
        competitive_frame: {
            direct_competitors: ['Pardot', 'HubSpot Enterprise'],
            category_alternatives: ['Agencies', 'Consultants'],
            switching_triggers: ['Poor reporting', 'Lack of support']
        },
        decision_making_unit: {
            roles: ['Marketing Director', 'CMO'],
            influencers: ['Marketing Ops', 'Sales Director'],
            decision_maker: 'CMO',
            approval_chain: ['Marketing Director → CMO']
        }
    },
];
