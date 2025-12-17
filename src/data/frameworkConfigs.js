/**
 * RaptorFlow Framework Configurations
 * 
 * Each marketing framework is defined by 6 slots:
 * 1. Inputs - What you start with
 * 2. Rules - Constraints you can't break
 * 3. Daily Actions - What you do each day
 * 4. Outputs - What you make
 * 5. Channels - Where you put it
 * 6. Metrics - How you know it worked
 */

// ═══════════════════════════════════════════════════════════════════════════════
// PROBLEM TYPES (8 Core Jobs)
// ═══════════════════════════════════════════════════════════════════════════════

export const PROBLEM_TYPES = {
    awareness: {
        id: 'awareness',
        statement: "No one knows I exist",
        goal: 'Awareness + Trust',
        defaultKpi: 'Inbound leads',
        defaultDuration: 14,
        description: 'New to market, zero brand awareness, cold audience',
        deliverables: ['Hero article', 'Visual proof asset', '5 distribution posts'],
        icon: 'target'
    },
    conversion: {
        id: 'conversion',
        statement: "People know me but won't buy",
        goal: 'Conversion',
        defaultKpi: 'Booked calls',
        defaultDuration: 7,
        description: 'Warm audience, good engagement, but no conversions',
        deliverables: ['Landing page', 'Email sequence', 'Sales script'],
        icon: 'results'
    },
    cac: {
        id: 'cac',
        statement: "CAC is too high",
        goal: 'Efficient Growth',
        defaultKpi: 'CAC reduction',
        defaultDuration: 30,
        description: 'High acquisition costs, paid channels burning cash',
        deliverables: ['Referral mechanism', 'Viral content', 'Organic playbook'],
        icon: 'growth'
    },
    focus: {
        id: 'focus',
        statement: "I'm spreading too thin",
        goal: 'Focus + Efficiency',
        defaultKpi: 'Channel ROI',
        defaultDuration: 14,
        description: 'Posting everywhere, nothing working, exhausted',
        deliverables: ['Channel audit', 'Master playbook', '20+ focused posts'],
        icon: 'target'
    },
    clarity: {
        id: 'clarity',
        statement: "I don't know what's working",
        goal: 'Clarity + Control',
        defaultKpi: 'Attribution clarity',
        defaultDuration: 14,
        description: 'Running campaigns but no idea what drives results',
        deliverables: ['Hypothesis doc', 'A/B test setup', 'Segment analysis'],
        icon: 'testing'
    },
    launch: {
        id: 'launch',
        statement: "I need to launch something",
        goal: 'Launch Impact',
        defaultKpi: 'Launch signups',
        defaultDuration: 7,
        description: 'New product, feature, or market entry',
        deliverables: ['Launch page', 'Email burst', 'Social campaign'],
        icon: 'launch'
    },
    revenue: {
        id: 'revenue',
        statement: "I'm stuck at current revenue",
        goal: 'Revenue Expansion',
        defaultKpi: 'LTV increase',
        defaultDuration: 30,
        description: 'Customer base stagnant, hit a plateau',
        deliverables: ['Value ladder', 'Upsell sequence', 'Case studies'],
        icon: 'growth'
    },
    positioning: {
        id: 'positioning',
        statement: "I'm not standing out",
        goal: 'Positioning + Differentiation',
        defaultKpi: 'Brand recall',
        defaultDuration: 14,
        description: 'Look like everyone else, generic positioning',
        deliverables: ['Manifesto', 'POV content', 'Shareable asset'],
        icon: 'magic'
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// FRAMEWORK CONFIGURATIONS (12 Frameworks)
// ═══════════════════════════════════════════════════════════════════════════════

export const FRAMEWORK_CONFIGS = {
    // ─────────────────────────────────────────────────────────────────────────────
    // 1. RESEARCH-DRIVEN AUTHORITY (Ogilvy)
    // ─────────────────────────────────────────────────────────────────────────────
    ogilvy: {
        id: 'ogilvy',
        name: 'Research-Driven Authority',
        expert: 'Ogilvy',
        subtitle: 'Build credibility through depth',
        problemTypes: ['awareness', 'positioning'],
        defaultDuration: 14,

        // Slot 1: Inputs
        inputs: {
            fields: [
                { id: 'research_topic', label: 'Research Topic', type: 'text', required: true, placeholder: 'What will you research deeply?' },
                { id: 'big_idea', label: 'One Big Idea', type: 'text', required: true, placeholder: 'The ONE promise you will make' },
                { id: 'proof_points', label: 'Proof Points (3+)', type: 'textarea', required: true, placeholder: 'List 3+ sources/data points' },
                { id: 'visual_evidence', label: 'Visual Evidence', type: 'file', required: false, placeholder: 'Chart, graph, or visual proof' }
            ]
        },

        // Slot 2: Rules
        rules: {
            required: [
                { id: 'research_first', label: 'Research before creating', locked: true },
                { id: 'one_promise', label: 'Only ONE promise per move', locked: true },
                { id: 'cite_sources', label: 'Must cite 3+ sources', locked: true },
                { id: 'visual_required', label: 'Visual evidence required', locked: true }
            ],
            optional: [
                { id: 'no_message_change', label: "Can't change message mid-move", default: true }
            ]
        },

        // Slot 3: Daily Actions
        dailyActions: {
            templates: [
                { day: 1, task: 'Deep customer research - interviews or data analysis', duration: 120 },
                { day: 2, task: 'Define your ONE big idea from research', duration: 60 },
                { day: 3, task: 'Gather 3+ proof points with citations', duration: 90 },
                { day: 4, task: 'Create visual proof asset (chart/graph)', duration: 60 },
                { day: 5, task: 'Write hero article (2000+ words)', duration: 180 },
                { day: 6, task: 'Create repetition piece #1', duration: 45 },
                { day: 7, task: 'Create repetition piece #2', duration: 45 },
                { day: 8, task: 'Publish hero article', duration: 30 },
                { day: 9, task: 'Create repetition piece #3', duration: 45 },
                { day: 10, task: 'Create repetition piece #4', duration: 45 },
                { day: 11, task: 'Create repetition piece #5', duration: 45 },
                { day: 12, task: 'Engage with audience responses', duration: 60 },
                { day: 13, task: 'Analyze performance data', duration: 45 },
                { day: 14, task: 'Document learnings for playbook', duration: 45 }
            ]
        },

        // Slot 4: Outputs
        outputs: {
            deliverables: [
                { id: 'research_report', name: 'Research Report', type: 'document', required: true },
                { id: 'big_idea_doc', name: 'Big Idea Document', type: 'document', required: true },
                { id: 'hero_article', name: 'Hero Article (2000+ words)', type: 'article', required: true },
                { id: 'visual_proof', name: 'Visual Proof Asset', type: 'image', required: true },
                { id: 'repetitions', name: '5 Repetition Pieces', type: 'posts', required: true }
            ]
        },

        // Slot 5: Channels
        channels: {
            recommended: ['linkedin', 'blog'],
            optional: ['email', 'twitter'],
            notRecommended: ['instagram', 'tiktok']
        },

        // Slot 6: Metrics
        metrics: {
            primary: { name: 'Brand Recall', target: '80% understand your promise', type: 'percentage' },
            leading: [
                { name: 'Article Depth', target: '2000+ words' },
                { name: 'Proof Citations', target: '3+' },
                { name: 'Inbound Leads', target: '50-70' }
            ]
        },

        // Fit Criteria
        fitCriteria: {
            hasTime: 0.3,
            canWrite: 0.25,
            hasData: 0.2,
            wantsTrust: 0.25
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 2. DIRECT RESPONSE CONVERSION (Kennedy)
    // ─────────────────────────────────────────────────────────────────────────────
    kennedy: {
        id: 'kennedy',
        name: 'Offer Blitz',
        expert: 'Kennedy',
        subtitle: 'Direct Response Conversion',
        problemTypes: ['conversion', 'launch'],
        defaultDuration: 7,

        inputs: {
            fields: [
                { id: 'godfather_offer', label: 'Godfather Offer', type: 'textarea', required: true, placeholder: 'An offer so good they can\'t refuse' },
                { id: 'risk_reversal', label: 'Risk Reversal', type: 'select', required: true, options: ['Money-back guarantee', 'Free trial', 'Pay after results', 'No questions asked refund'] },
                { id: 'urgency_mechanism', label: 'Urgency Mechanism', type: 'select', required: true, options: ['Countdown timer', 'Limited spots', 'Price increase', 'Bonus deadline'] },
                { id: 'direct_cta', label: 'Direct CTA', type: 'text', required: true, placeholder: 'Clear command action (Book now, Get started, etc.)' }
            ]
        },

        rules: {
            required: [
                { id: 'must_have_urgency', label: 'Must have urgency mechanism', locked: true },
                { id: 'must_remove_risk', label: 'Must remove risk completely', locked: true },
                { id: 'direct_cta', label: 'CTA must be direct command', locked: true },
                { id: 'max_duration', label: 'Max 7 days', locked: true },
                { id: 'track_daily', label: 'Track everything daily', locked: true }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Design godfather offer with risk reversal', duration: 90 },
                { day: 2, task: 'Set up urgency mechanism', duration: 45 },
                { day: 3, task: 'Create landing page with offer', duration: 120 },
                { day: 4, task: 'Write 5-email sequence', duration: 180 },
                { day: 5, task: 'Launch sequence + start outreach', duration: 60 },
                { day: 6, task: 'Track hourly, follow up with warm leads', duration: 120 },
                { day: 7, task: 'Final push + close deals', duration: 180 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'landing_page', name: 'Landing Page with Offer', type: 'page', required: true },
                { id: 'email_sequence', name: '5-7 Email Sequence', type: 'emails', required: true },
                { id: 'sales_script', name: 'Sales Script', type: 'document', required: true },
                { id: 'countdown', name: 'Countdown Timer', type: 'component', required: true }
            ]
        },

        channels: {
            recommended: ['email', 'landing_page', 'dms'],
            optional: ['linkedin', 'whatsapp'],
            notRecommended: ['blog', 'youtube']
        },

        metrics: {
            primary: { name: 'Conversion Rate', target: '3%+', type: 'percentage' },
            leading: [
                { name: 'Response Rate', target: '10%+' },
                { name: 'CAC', target: 'Track' },
                { name: 'Time-to-Convert', target: '<7 days' }
            ]
        },

        fitCriteria: {
            needsFastResults: 0.35,
            hasWarmAudience: 0.25,
            hasSalesMotion: 0.2,
            canBeAggressive: 0.2
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 3. HYPER-NICHE DOMINANCE (Godin)
    // ─────────────────────────────────────────────────────────────────────────────
    godin: {
        id: 'godin',
        name: 'Niche Takeover',
        expert: 'Godin',
        subtitle: 'Hyper-Niche Dominance',
        problemTypes: ['positioning', 'awareness', 'cac'],
        defaultDuration: 14,

        inputs: {
            fields: [
                { id: 'tiny_niche', label: 'Smallest Viable Niche', type: 'text', required: true, placeholder: 'The smallest group you can dominate' },
                { id: 'remarkable_element', label: 'Remarkable Element', type: 'textarea', required: true, placeholder: 'What makes you worth talking about?' },
                { id: 'sneezers', label: '10 Sneezers/Influencers', type: 'textarea', required: true, placeholder: 'List 10 people who can spread your idea' }
            ]
        },

        rules: {
            required: [
                { id: 'hyper_specific', label: 'Must be hyper-specific niche', locked: true },
                { id: 'single_niche', label: 'Single niche only', locked: true },
                { id: 'must_be_remarkable', label: 'Must be remarkable enough to spread', locked: true },
                { id: 'no_broad_positioning', label: 'No broad positioning allowed', locked: true }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Define your tiny niche precisely', duration: 60 },
                { day: 2, task: 'Identify 10 sneezers in your niche', duration: 90 },
                { day: 3, task: 'Write your niche manifesto', duration: 120 },
                { day: 4, task: 'Create shareable asset (meme/data/hot take)', duration: 90 },
                { day: 5, task: 'Craft 10 custom pitches for sneezers', duration: 120 },
                { day: 6, task: 'Seed sneezer #1-3', duration: 60 },
                { day: 7, task: 'Seed sneezer #4-6', duration: 60 },
                { day: 8, task: 'Seed sneezer #7-10', duration: 60 },
                { day: 9, task: 'Monitor spread and engage', duration: 60 },
                { day: 10, task: 'Create second wave content', duration: 90 },
                { day: 11, task: 'Amplify with engaged sneezers', duration: 60 },
                { day: 12, task: 'Engage in niche communities', duration: 60 },
                { day: 13, task: 'Measure niche penetration', duration: 45 },
                { day: 14, task: 'Document learnings', duration: 45 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'manifesto', name: 'Niche Manifesto', type: 'document', required: true },
                { id: 'shareable_asset', name: 'Shareable Asset', type: 'content', required: true },
                { id: 'custom_pitches', name: '10 Custom Pitches', type: 'messages', required: true }
            ]
        },

        channels: {
            recommended: ['word_of_mouth', 'communities', 'linkedin'],
            optional: ['twitter', 'email'],
            notRecommended: ['paid_ads', 'mass_outreach']
        },

        metrics: {
            primary: { name: 'Niche Penetration', target: '50%', type: 'percentage' },
            leading: [
                { name: 'Organic Referral Rate', target: '30%' },
                { name: 'Sneezer Amplification', target: 'Each refers 5' }
            ]
        },

        fitCriteria: {
            canGoSpecific: 0.35,
            hasRemarkableAngle: 0.25,
            canIdentifySneezers: 0.2,
            patienceForOrganic: 0.2
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 4. BEHAVIORAL FRICTION REMOVAL (Sutherland)
    // ─────────────────────────────────────────────────────────────────────────────
    sutherland: {
        id: 'sutherland',
        name: 'Friction Fix',
        expert: 'Sutherland',
        subtitle: 'Behavioral Friction Removal',
        problemTypes: ['conversion', 'clarity'],
        defaultDuration: 14,

        inputs: {
            fields: [
                { id: 'friction_point', label: 'ONE Friction Point', type: 'text', required: true, placeholder: 'The single biggest blocker to conversion' },
                { id: 'lateral_solutions', label: 'How Other Industries Solved It', type: 'textarea', required: true, placeholder: 'Research 3 lateral examples' },
                { id: 'psychological_blocker', label: 'Psychological Blocker', type: 'select', required: true, options: ['Fear', 'Confusion', 'Overwhelm', 'Trust', 'Effort', 'Time'] }
            ]
        },

        rules: {
            required: [
                { id: 'fix_one_thing', label: 'Fix ONE thing only', locked: true },
                { id: 'test_before_after', label: 'Must test before/after', locked: true },
                { id: 'no_big_redesigns', label: 'No big redesigns allowed', locked: true },
                { id: 'focus_psychology', label: 'Focus on psychology, not features', locked: true }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Identify the friction point', duration: 60 },
                { day: 2, task: 'Research how other industries solved it', duration: 90 },
                { day: 3, task: 'Design tiny nudge hypothesis', duration: 60 },
                { day: 4, task: 'Set up A/B test baseline', duration: 90 },
                { day: 5, task: 'Implement the nudge', duration: 120 },
                { day: 6, task: 'Launch A/B test', duration: 30 },
                { day: 7, task: 'Monitor day 1 results', duration: 30 },
                { day: 8, task: 'Monitor day 2 results', duration: 30 },
                { day: 9, task: 'Monitor day 3 results', duration: 30 },
                { day: 10, task: 'Midpoint analysis', duration: 60 },
                { day: 11, task: 'Monitor day 5 results', duration: 30 },
                { day: 12, task: 'Monitor day 6 results', duration: 30 },
                { day: 13, task: 'Final analysis and results', duration: 90 },
                { day: 14, task: 'Document and apply winner', duration: 60 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'friction_audit', name: 'Friction Audit', type: 'document', required: true },
                { id: 'nudge_hypothesis', name: 'Nudge Hypothesis', type: 'document', required: true },
                { id: 'ab_test_setup', name: 'A/B Test Setup', type: 'test', required: true },
                { id: 'results_analysis', name: 'Results Analysis', type: 'document', required: true }
            ]
        },

        channels: {
            recommended: ['existing_funnel'],
            optional: [],
            notRecommended: ['new_channels']
        },

        metrics: {
            primary: { name: 'Conversion Lift', target: '15%+', type: 'percentage' },
            leading: [
                { name: 'Friction Removal Score', target: 'Reduced' },
                { name: 'Psychological Blocker Solved', target: 'Yes/No' }
            ]
        },

        fitCriteria: {
            hasExistingFunnel: 0.35,
            canRunTests: 0.25,
            wantsQuickWins: 0.2,
            hasTrafficForTest: 0.2
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 5. MULTI-TIER VALUE LADDER (Brunson)
    // ─────────────────────────────────────────────────────────────────────────────
    brunson: {
        id: 'brunson',
        name: 'Value Ladder',
        expert: 'Brunson',
        subtitle: 'Multi-Tier Revenue',
        problemTypes: ['revenue', 'conversion'],
        defaultDuration: 30,

        inputs: {
            fields: [
                { id: 'lead_magnet', label: 'Free Lead Magnet', type: 'text', required: true, placeholder: 'High-value free offer' },
                { id: 'entry_offer', label: 'Entry Offer (₹500-2000)', type: 'text', required: true, placeholder: 'Low-risk first purchase' },
                { id: 'core_offer', label: 'Core Offer (₹5k-20k)', type: 'text', required: true, placeholder: 'Main product/service' },
                { id: 'premium_offer', label: 'Premium Offer (₹50k+)', type: 'text', required: true, placeholder: 'High-ticket transformation' }
            ]
        },

        rules: {
            required: [
                { id: 'value_each_tier', label: 'Create value at each tier', locked: true },
                { id: 'automate_transitions', label: 'Automate tier transitions', locked: true },
                { id: 'easy_yes_first', label: 'Start with easy yes', locked: true },
                { id: 'solve_real_problem', label: 'Each tier solves real problem', locked: true }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Design lead magnet', duration: 90 },
                { day: 2, task: 'Create lead magnet content', duration: 180 },
                { day: 3, task: 'Design entry offer', duration: 90 },
                { day: 4, task: 'Create entry offer page', duration: 120 },
                { day: 5, task: 'Design core offer', duration: 90 },
                { day: 6, task: 'Create core offer page', duration: 120 },
                { day: 7, task: 'Design premium offer', duration: 90 },
                { day: 8, task: 'Create premium offer page', duration: 120 },
                { day: 9, task: 'Write free-to-entry email sequence', duration: 120 },
                { day: 10, task: 'Write entry-to-core email sequence', duration: 120 },
                { day: 11, task: 'Write core-to-premium email sequence', duration: 120 },
                { day: 12, task: 'Set up automation flows', duration: 180 },
                { day: 13, task: 'Test entire ladder flow', duration: 90 },
                { day: 14, task: 'Launch lead magnet', duration: 60 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'lead_magnet', name: 'Lead Magnet', type: 'content', required: true },
                { id: 'tier_offers', name: '3-4 Tier Offers', type: 'pages', required: true },
                { id: 'email_sequences', name: 'Email Automation Sequences', type: 'emails', required: true },
                { id: 'upsell_flows', name: 'Upsell/Downsell Flows', type: 'automation', required: true }
            ]
        },

        channels: {
            recommended: ['email', 'landing_pages', 'funnel_automation'],
            optional: ['linkedin', 'webinars'],
            notRecommended: ['organic_social']
        },

        metrics: {
            primary: { name: 'LTV', target: 'Increase', type: 'currency' },
            leading: [
                { name: 'Free-to-Paid', target: '30%+' },
                { name: 'Tier Ascension', target: '10%' },
                { name: 'CAC Payback Time', target: '<30 days' }
            ]
        },

        fitCriteria: {
            hasMultipleOffers: 0.3,
            canAutomate: 0.25,
            hasTraffic: 0.25,
            wantsLTV: 0.2
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 6. SOCIAL PROOF AMPLIFICATION (Cialdini)
    // ─────────────────────────────────────────────────────────────────────────────
    cialdini: {
        id: 'cialdini',
        name: 'Proof Blitz',
        expert: 'Cialdini',
        subtitle: 'Social Proof Amplification',
        problemTypes: ['conversion', 'revenue'],
        defaultDuration: 14,

        inputs: {
            fields: [
                { id: 'customer_results', label: 'Customer Results (3-5)', type: 'textarea', required: true, placeholder: 'List specific customer outcomes with numbers' },
                { id: 'specific_numbers', label: 'Specific Numbers', type: 'textarea', required: true, placeholder: 'Exact metrics (%, $, time saved)' },
                { id: 'real_people', label: 'Real People (with permission)', type: 'textarea', required: true, placeholder: 'Names, companies, photos' }
            ]
        },

        rules: {
            required: [
                { id: 'must_be_real', label: 'Must be real (no fake testimonials)', locked: true },
                { id: 'show_numbers', label: 'Must show specific numbers', locked: true },
                { id: 'address_objections', label: 'Must address objections', locked: true },
                { id: 'video_over_text', label: 'Video > Text', locked: false }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Identify 5 best customer results', duration: 60 },
                { day: 2, task: 'Reach out for case study interviews', duration: 60 },
                { day: 3, task: 'Interview customer #1', duration: 90 },
                { day: 4, task: 'Interview customer #2', duration: 90 },
                { day: 5, task: 'Interview customer #3', duration: 90 },
                { day: 6, task: 'Create before/after comparisons', duration: 120 },
                { day: 7, task: 'Write case study #1', duration: 120 },
                { day: 8, task: 'Write case study #2', duration: 120 },
                { day: 9, task: 'Create video testimonials', duration: 180 },
                { day: 10, task: 'Build ROI calculator', duration: 120 },
                { day: 11, task: 'Compile proof wall on website', duration: 90 },
                { day: 12, task: 'Add proof to sales pages', duration: 60 },
                { day: 13, task: 'Add proof to email sequences', duration: 60 },
                { day: 14, task: 'Measure conversion lift', duration: 45 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'case_studies', name: '3-5 Detailed Case Studies', type: 'documents', required: true },
                { id: 'testimonials', name: 'Video Testimonials', type: 'videos', required: false },
                { id: 'before_after', name: 'Before/After Comparisons', type: 'content', required: true },
                { id: 'roi_calc', name: 'ROI Calculator', type: 'tool', required: false },
                { id: 'proof_wall', name: 'Results Wall', type: 'page', required: true }
            ]
        },

        channels: {
            recommended: ['landing_page', 'linkedin', 'email', 'sales_calls'],
            optional: ['twitter', 'youtube'],
            notRecommended: []
        },

        metrics: {
            primary: { name: 'Trust Score Increase', target: 'Measurable lift', type: 'score' },
            leading: [
                { name: 'Objection Removal Rate', target: 'Track' },
                { name: 'Fence-Sitter Conversion', target: '+20%' }
            ]
        },

        fitCriteria: {
            hasHappyCustomers: 0.4,
            canGetTestimonials: 0.3,
            needsTrustBuilding: 0.15,
            warmAudience: 0.15
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 7. OBJECTION DEMOLITION
    // ─────────────────────────────────────────────────────────────────────────────
    objection: {
        id: 'objection',
        name: 'Objection Killer',
        expert: 'Sales Psychology',
        subtitle: 'Demolish Buying Objections',
        problemTypes: ['conversion', 'revenue'],
        defaultDuration: 14,

        inputs: {
            fields: [
                { id: 'top_objections', label: 'Top 5-10 Customer Objections', type: 'textarea', required: true, placeholder: 'List real objections you hear' },
                { id: 'real_responses', label: 'Your Best Responses', type: 'textarea', required: true, placeholder: 'What actually works when you address these' },
                { id: 'proof_per_objection', label: 'Proof for Each', type: 'textarea', required: true, placeholder: 'Evidence to back up each response' }
            ]
        },

        rules: {
            required: [
                { id: 'real_objections', label: 'Must address REAL objections', locked: true },
                { id: 'be_honest', label: 'Must be honest', locked: true },
                { id: 'qa_format', label: 'Direct Q&A format', locked: true },
                { id: 'proof_required', label: 'Proof required per objection', locked: true }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Map all objections from sales calls', duration: 90 },
                { day: 2, task: 'Research best responses', duration: 90 },
                { day: 3, task: 'Gather proof for top 3 objections', duration: 90 },
                { day: 4, task: 'Create FAQ asset', duration: 120 },
                { day: 5, task: 'Create comparison guide', duration: 120 },
                { day: 6, task: 'Create objection rebuttal article #1', duration: 90 },
                { day: 7, task: 'Create objection rebuttal article #2', duration: 90 },
                { day: 8, task: 'Create objection rebuttal video', duration: 120 },
                { day: 9, task: 'Add to sales scripts', duration: 60 },
                { day: 10, task: 'Add to website FAQs', duration: 60 },
                { day: 11, task: 'Add to email sequences', duration: 60 },
                { day: 12, task: 'Test in live sales calls', duration: 120 },
                { day: 13, task: 'Refine based on feedback', duration: 60 },
                { day: 14, task: 'Measure win rate improvement', duration: 45 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'objection_map', name: 'Objection Map', type: 'document', required: true },
                { id: 'faq_asset', name: 'FAQ Asset', type: 'page', required: true },
                { id: 'comparison_guide', name: 'Comparison Guide', type: 'document', required: true },
                { id: 'rebuttal_content', name: 'Rebuttal Articles/Videos', type: 'content', required: true }
            ]
        },

        channels: {
            recommended: ['website', 'sales_scripts', 'email', 'linkedin'],
            optional: ['youtube'],
            notRecommended: []
        },

        metrics: {
            primary: { name: 'Win Rate Increase', target: 'Measurable', type: 'percentage' },
            leading: [
                { name: 'Objection Conversion Rate', target: 'Track' },
                { name: 'Time-to-Close Reduction', target: 'Track' }
            ]
        },

        fitCriteria: {
            knowsObjections: 0.35,
            hasSalesProcess: 0.25,
            warmLeadsExist: 0.2,
            canCreateContent: 0.2
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 8. VIRAL CONTAGION DESIGN (Berger)
    // ─────────────────────────────────────────────────────────────────────────────
    berger: {
        id: 'berger',
        name: 'Viral Engine',
        expert: 'Berger',
        subtitle: 'Viral Contagion Design',
        problemTypes: ['awareness', 'cac', 'launch'],
        defaultDuration: 14,

        inputs: {
            fields: [
                { id: 'social_currency', label: 'Social Currency Hook', type: 'textarea', required: true, placeholder: 'What makes people look good sharing this?' },
                { id: 'emotional_trigger', label: 'Emotional Trigger', type: 'select', required: true, options: ['Surprise', 'Anger', 'Joy', 'Fear', 'Awe', 'Anxiety'] },
                { id: 'identity_signal', label: 'Identity Signal', type: 'text', required: true, placeholder: 'What does sharing say about them?' }
            ]
        },

        rules: {
            required: [
                { id: 'social_currency', label: 'Must provide social currency', locked: true },
                { id: 'emotion', label: 'Must tap emotion', locked: true },
                { id: 'identity', label: 'Must be identity signal', locked: true },
                { id: 'no_hard_sell', label: 'No hard sell allowed', locked: true }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Identify social currency hook', duration: 60 },
                { day: 2, task: 'Design emotional trigger', duration: 60 },
                { day: 3, task: 'Create contagious content piece #1', duration: 120 },
                { day: 4, task: 'Create contagious content piece #2', duration: 120 },
                { day: 5, task: 'Identify 10 micro-influencers', duration: 90 },
                { day: 6, task: 'Seed with micro-influencers', duration: 60 },
                { day: 7, task: 'Track shares and spread', duration: 30 },
                { day: 8, task: 'Amplify winners', duration: 60 },
                { day: 9, task: 'Create second wave content', duration: 90 },
                { day: 10, task: 'Seed second wave', duration: 60 },
                { day: 11, task: 'Track viral coefficient', duration: 30 },
                { day: 12, task: 'Double down on winners', duration: 60 },
                { day: 13, task: 'Measure reach vs effort', duration: 45 },
                { day: 14, task: 'Document playbook', duration: 45 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'viral_content', name: 'High-Shareability Content', type: 'content', required: true },
                { id: 'seeding_strategy', name: 'Seeding Strategy', type: 'document', required: true },
                { id: 'amplification', name: 'Amplification Mechanics', type: 'process', required: true }
            ]
        },

        channels: {
            recommended: ['twitter', 'linkedin', 'instagram', 'tiktok'],
            optional: [],
            notRecommended: ['email', 'blog']
        },

        metrics: {
            primary: { name: 'Share Rate vs Likes', target: 'Shares > Likes', type: 'ratio' },
            leading: [
                { name: 'Organic vs Paid Reach', target: '10x ratio' },
                { name: 'Viral Coefficient', target: '>1' }
            ]
        },

        fitCriteria: {
            hasRemarkableAngle: 0.35,
            understandsAudience: 0.25,
            canSeedInfluencers: 0.2,
            noHardSellNeeded: 0.2
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 9. DEEP CHANNEL MASTERY (Patel)
    // ─────────────────────────────────────────────────────────────────────────────
    patel: {
        id: 'patel',
        name: 'Channel Domination',
        expert: 'Patel',
        subtitle: 'Deep Channel Mastery',
        problemTypes: ['focus', 'clarity'],
        defaultDuration: 14,

        inputs: {
            fields: [
                { id: 'chosen_channel', label: 'ONE Channel to Master', type: 'select', required: true, options: ['LinkedIn', 'Twitter', 'Instagram', 'YouTube', 'Email', 'TikTok'] },
                { id: 'content_pieces', label: '20+ Content Pieces Planned', type: 'textarea', required: true, placeholder: 'List your 20 content ideas' },
                { id: 'test_variables', label: '5 Test Variables', type: 'textarea', required: true, placeholder: 'Time, format, hook, CTA, length' }
            ]
        },

        rules: {
            required: [
                { id: 'one_channel', label: 'ONE channel only', locked: true },
                { id: '3x_volume', label: '3x normal posting volume', locked: true },
                { id: '5_tests', label: 'Test 5+ variables', locked: true },
                { id: 'document_all', label: 'Document everything', locked: true }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Audit current channel performance', duration: 60 },
                { day: 2, task: 'Plan 20+ content pieces', duration: 90 },
                { day: 3, task: 'Create content batch #1 (5 pieces)', duration: 180 },
                { day: 4, task: 'Post 3x, test timing variable', duration: 60 },
                { day: 5, task: 'Create content batch #2 (5 pieces)', duration: 180 },
                { day: 6, task: 'Post 3x, test format variable', duration: 60 },
                { day: 7, task: 'Analyze week 1, kill losers', duration: 90 },
                { day: 8, task: 'Create content batch #3 (5 pieces)', duration: 180 },
                { day: 9, task: 'Post 3x, test hook variable', duration: 60 },
                { day: 10, task: 'Create content batch #4 (5 pieces)', duration: 180 },
                { day: 11, task: 'Post 3x, test CTA variable', duration: 60 },
                { day: 12, task: 'Post 3x, test length variable', duration: 60 },
                { day: 13, task: 'Final analysis', duration: 90 },
                { day: 14, task: 'Create channel playbook', duration: 90 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'content_pieces', name: '20+ Channel-Specific Content', type: 'content', required: true },
                { id: 'experiments', name: 'Optimization Experiments', type: 'tests', required: true },
                { id: 'playbook', name: 'Channel Playbook Document', type: 'document', required: true }
            ]
        },

        channels: {
            recommended: ['chosen_channel_only'],
            optional: [],
            notRecommended: ['all_others']
        },

        metrics: {
            primary: { name: 'Channel ROI', target: '3x vs baseline', type: 'multiplier' },
            leading: [
                { name: 'Format Winner', target: 'Identified' },
                { name: 'Best Timing', target: 'Identified' }
            ]
        },

        fitCriteria: {
            canFocus: 0.35,
            hasCapacity: 0.25,
            wantsClarity: 0.2,
            canCreateVolume: 0.2
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 10. DATA-DRIVEN OPTIMIZATION
    // ─────────────────────────────────────────────────────────────────────────────
    datadriven: {
        id: 'datadriven',
        name: 'Test & Learn',
        expert: 'Analytics',
        subtitle: 'Data-Driven Optimization',
        problemTypes: ['clarity', 'focus'],
        defaultDuration: 14,

        inputs: {
            fields: [
                { id: 'hypothesis', label: 'Clear Hypothesis', type: 'textarea', required: true, placeholder: 'If X, then Y will increase by Z%' },
                { id: 'baseline_data', label: 'Baseline Data', type: 'textarea', required: true, placeholder: 'Current metrics to beat' },
                { id: 'segment', label: 'Segment Definition', type: 'text', required: true, placeholder: 'Which audience segment to test' }
            ]
        },

        rules: {
            required: [
                { id: 'hypothesis_required', label: 'Hypothesis required', locked: true },
                { id: 'proper_ab', label: 'Proper A/B test setup', locked: true },
                { id: 'segment_first', label: 'Segment before generalizing', locked: true },
                { id: 'causation', label: 'Causation not correlation', locked: true }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Define clear hypothesis', duration: 60 },
                { day: 2, task: 'Gather baseline data', duration: 90 },
                { day: 3, task: 'Define segments', duration: 60 },
                { day: 4, task: 'Set up test infrastructure', duration: 120 },
                { day: 5, task: 'Launch test', duration: 30 },
                { day: 6, task: 'Monitor day 1', duration: 30 },
                { day: 7, task: 'Monitor day 2', duration: 30 },
                { day: 8, task: 'Monitor day 3', duration: 30 },
                { day: 9, task: 'Midpoint check', duration: 60 },
                { day: 10, task: 'Monitor day 5', duration: 30 },
                { day: 11, task: 'Monitor day 6', duration: 30 },
                { day: 12, task: 'Analyze by segment', duration: 90 },
                { day: 13, task: 'Create segment playbooks', duration: 90 },
                { day: 14, task: 'Document learnings', duration: 60 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'hypothesis_doc', name: 'Hypothesis Document', type: 'document', required: true },
                { id: 'ab_setup', name: 'A/B Test Setup', type: 'test', required: true },
                { id: 'segment_analysis', name: 'Segment Analysis', type: 'document', required: true },
                { id: 'playbooks', name: 'Cohort-Specific Playbooks', type: 'documents', required: true }
            ]
        },

        channels: {
            recommended: ['existing_channels'],
            optional: [],
            notRecommended: ['new_channels']
        },

        metrics: {
            primary: { name: 'Hypothesis Validated', target: 'Yes/No', type: 'boolean' },
            leading: [
                { name: 'Lift per Segment', target: 'Measured' },
                { name: 'CAC by Cohort', target: '-40%' }
            ]
        },

        fitCriteria: {
            hasData: 0.35,
            canRunTests: 0.25,
            wantsCausation: 0.2,
            hasTraffic: 0.2
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 11. REFERRAL MECHANISM
    // ─────────────────────────────────────────────────────────────────────────────
    referral: {
        id: 'referral',
        name: 'Referral Engine',
        expert: 'Viral Loops',
        subtitle: 'Built-in Referral Mechanism',
        problemTypes: ['cac', 'revenue'],
        defaultDuration: 14,

        inputs: {
            fields: [
                { id: 'referral_trigger', label: 'Referral Trigger in Product', type: 'textarea', required: true, placeholder: 'When/where will users refer?' },
                { id: 'incentive', label: 'Incentive Structure', type: 'textarea', required: true, placeholder: 'What do both parties get?' },
                { id: 'k_factor_target', label: 'K-Factor Target', type: 'number', required: true, placeholder: 'Target viral coefficient (e.g., 1.2)' }
            ]
        },

        rules: {
            required: [
                { id: 'in_product', label: 'Built into product mechanics', locked: true },
                { id: 'valuable_incentive', label: 'Incentive must be valuable', locked: true },
                { id: 'k_greater_1', label: 'K-factor > 1 required for growth', locked: true },
                { id: 'automate', label: 'Automate everything', locked: true }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Design referral trigger moment', duration: 60 },
                { day: 2, task: 'Design incentive structure', duration: 60 },
                { day: 3, task: 'Create referral landing page', duration: 120 },
                { day: 4, task: 'Set up tracking system', duration: 120 },
                { day: 5, task: 'Implement referral UI in product', duration: 180 },
                { day: 6, task: 'Set up automated rewards', duration: 120 },
                { day: 7, task: 'Test full referral flow', duration: 90 },
                { day: 8, task: 'Launch to small segment', duration: 30 },
                { day: 9, task: 'Monitor K-factor', duration: 30 },
                { day: 10, task: 'Iterate on friction points', duration: 90 },
                { day: 11, task: 'Expand to larger segment', duration: 30 },
                { day: 12, task: 'Monitor viral cycle', duration: 30 },
                { day: 13, task: 'Optimize for K>1', duration: 90 },
                { day: 14, task: 'Document and scale', duration: 60 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'trigger', name: 'Referral Trigger Mechanism', type: 'feature', required: true },
                { id: 'incentive', name: 'Incentive Offer', type: 'offer', required: true },
                { id: 'tracking', name: 'Tracking System', type: 'system', required: true },
                { id: 'rewards', name: 'Automated Rewards', type: 'automation', required: true }
            ]
        },

        channels: {
            recommended: ['in_product'],
            optional: [],
            notRecommended: ['external_marketing']
        },

        metrics: {
            primary: { name: 'K-Factor', target: '>1', type: 'ratio' },
            leading: [
                { name: 'Referral CAC', target: '5-10x cheaper' },
                { name: 'Viral Cycle Time', target: 'Track' }
            ]
        },

        fitCriteria: {
            hasProduct: 0.35,
            canBuildFeature: 0.25,
            wantsOrganicGrowth: 0.2,
            hasHappyUsers: 0.2
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // 12. CONTENT VELOCITY (GaryVee)
    // ─────────────────────────────────────────────────────────────────────────────
    garyvee: {
        id: 'garyvee',
        name: 'Content Blitz',
        expert: 'GaryVee',
        subtitle: 'Content Velocity',
        problemTypes: ['awareness', 'focus', 'launch'],
        defaultDuration: 7,

        inputs: {
            fields: [
                { id: 'pillar_asset', label: 'ONE Pillar Asset', type: 'text', required: true, placeholder: 'Keynote, podcast, long video, article' },
                { id: 'channels_to_test', label: '3 Channel Formats', type: 'textarea', required: true, placeholder: 'Which 3 channels/formats to test' },
                { id: 'kill_criteria', label: '48-Hour Kill Criteria', type: 'text', required: true, placeholder: 'What makes you kill a format?' }
            ]
        },

        rules: {
            required: [
                { id: 'pillar_first', label: 'Pillar content first', locked: true },
                { id: 'chop_10', label: 'Chop into 10+ micro-pieces', locked: true },
                { id: 'test_3', label: 'Test 3+ channels simultaneously', locked: true },
                { id: 'kill_day_3', label: 'Kill bottom performers Day 3', locked: true }
            ],
            optional: []
        },

        dailyActions: {
            templates: [
                { day: 1, task: 'Create pillar asset', duration: 240 },
                { day: 2, task: 'Chop into 10+ micro-pieces', duration: 180 },
                { day: 3, task: 'Launch on all 3 channels', duration: 60 },
                { day: 4, task: '48h check - kill losers', duration: 60 },
                { day: 5, task: 'Double winner channel', duration: 90 },
                { day: 6, task: 'Create more content for winner', duration: 120 },
                { day: 7, task: 'Lock winning format for 30 days', duration: 60 }
            ]
        },

        outputs: {
            deliverables: [
                { id: 'pillar', name: '1 Pillar Asset', type: 'content', required: true },
                { id: 'micro_pieces', name: '10+ Micro-Pieces', type: 'content', required: true },
                { id: 'channel_tests', name: '3 Channel Format Tests', type: 'tests', required: true }
            ]
        },

        channels: {
            recommended: ['linkedin', 'instagram', 'twitter'],
            optional: ['tiktok', 'youtube'],
            notRecommended: []
        },

        metrics: {
            primary: { name: 'Engagement by Format', target: 'First 48h', type: 'score' },
            leading: [
                { name: 'Channel ROI', target: 'Winner identified' },
                { name: 'Content Velocity', target: '10+ from 1' }
            ]
        },

        fitCriteria: {
            hasContentCapacity: 0.35,
            canMoveFast: 0.25,
            wantsVolume: 0.2,
            canKillLosers: 0.2
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Get frameworks that solve a specific problem type
 */
export const getFrameworksForProblem = (problemType) => {
    return Object.values(FRAMEWORK_CONFIGS).filter(
        config => config.problemTypes.includes(problemType)
    )
}

/**
 * Calculate framework fit score based on situation
 * @param {Object} framework - The framework config
 * @param {Object} situation - User's situation answers
 * @returns {number} - Fit score 0-100
 */
export const calculateFrameworkFit = (framework, situation) => {
    let score = 0
    const weights = framework.fitCriteria

    // Map situation answers to fit criteria
    const mappings = {
        // Speed/time
        needsFastResults: situation.speedNeeded === '7',
        hasTime: situation.timeBudget === '15h',
        canMoveFast: situation.speedNeeded === '7',

        // Assets and proof
        hasProof: situation.customerResults === 'strong',
        hasHappyCustomers: situation.customerResults !== 'none',
        canGetTestimonials: situation.customerResults !== 'none',
        hasData: situation.customerResults !== 'none',

        // Audience
        hasWarmAudience: situation.trafficLevel !== 'low',
        warmAudience: situation.trafficLevel !== 'low',
        warmLeadsExist: situation.trafficLevel !== 'low',
        hasTraffic: situation.trafficLevel !== 'low',
        hasTrafficForTest: situation.trafficLevel !== 'low',

        // Offer
        hasClearOffer: situation.clearOffer === 'sharp',
        hasMultipleOffers: situation.clearOffer !== 'messy',

        // Capabilities
        canWrite: true, // Assume yes
        canCreateContent: true,
        canCreateVolume: situation.timeBudget !== '4h',
        hasCapacity: situation.timeBudget !== '4h',
        hasSalesMotion: situation.salesMotion !== 'checkout',
        hasSalesProcess: situation.salesMotion === 'calls',
        canBeAggressive: true,
        canAutomate: true,
        canFocus: true,
        canGoSpecific: true,
        hasRemarkableAngle: true,
        canIdentifySneezers: true,
        patienceForOrganic: situation.speedNeeded !== '7',
        hasExistingFunnel: situation.trafficLevel !== 'low',
        canRunTests: situation.trafficLevel !== 'low',
        wantsQuickWins: situation.speedNeeded === '7',
        canSeedInfluencers: true,
        noHardSellNeeded: true,
        wantsCausation: true,
        wantsClarity: true,
        wantsTrust: true,
        wantsLTV: true,
        needsTrustBuilding: true,
        knowsObjections: true,
        understandsAudience: true,
        hasProduct: true,
        canBuildFeature: true,
        wantsOrganicGrowth: true,
        hasHappyUsers: situation.customerResults !== 'none',
        hasContentCapacity: situation.timeBudget !== '4h',
        wantsVolume: true,
        canKillLosers: true
    }

    // Calculate weighted score
    Object.entries(weights).forEach(([criterion, weight]) => {
        if (mappings[criterion]) {
            score += weight * 100
        }
    })

    return Math.round(score)
}

/**
 * Get ranked framework recommendations for a problem + situation
 */
export const getFrameworkRecommendations = (problemType, situation, maxResults = 4) => {
    const frameworks = getFrameworksForProblem(problemType)

    const scored = frameworks.map(framework => ({
        ...framework,
        fitScore: calculateFrameworkFit(framework, situation)
    }))

    // Sort by fit score descending
    scored.sort((a, b) => b.fitScore - a.fitScore)

    return scored.slice(0, maxResults)
}

/**
 * Generate tasks from framework template for a specific duration
 */
export const generateTasksFromFramework = (framework, startDate) => {
    const start = new Date(startDate)

    return framework.dailyActions.templates.map(template => ({
        id: `task_${template.day}_${Date.now()}`,
        text: template.task,
        day: template.day,
        duration: template.duration,
        status: 'todo',
        scheduledDate: new Date(start.getTime() + (template.day - 1) * 24 * 60 * 60 * 1000).toISOString()
    }))
}

export default FRAMEWORK_CONFIGS
