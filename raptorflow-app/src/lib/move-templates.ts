import { MoveGoal, ChannelType, CampaignObjective, ChecklistItem, MoveDuration } from './campaigns-types';

/**
 * Move Templates — Real actionable marketing moves with hypothesis, A/B testing, and action steps
 * Enhanced for the Moves Operator Dashboard
 */

export interface MoveTemplate {
    id: string;
    name: string;
    description: string;
    goal: MoveGoal;
    hypothesis: string;
    control: string;
    variant: string;
    success_metric: string;
    sample_size: string;
    action_steps: string[];

    // Enhanced fields for wizard
    duration: MoveDuration;
    effortPerDay: '20m' | '30m' | '45m' | '90m';
    outputs: string[];                     // e.g., ['7 posts', '1 CTA script']
    defaultChecklist: Omit<ChecklistItem, 'id'>[];  // day-by-day tasks
    cadenceDefaults?: {
        postsPerDay?: number;
        dmsPerDay?: number;
        followupsPerDay?: number;
    };

    allowed_objectives?: CampaignObjective[];
    allowed_channels?: ChannelType[];
}

export const MOVE_TEMPLATES: MoveTemplate[] = [
    // ==============================
    // ACQUISITION MOVES
    // ==============================
    {
        id: 'problem-post-sprint',
        name: 'Problem Post Sprint',
        description: '1 post/day → pain → promise → CTA. Build authority by articulating problems.',
        goal: 'leads',
        duration: 7,
        effortPerDay: '20m',
        outputs: ['7 posts', '1 CTA script'],
        hypothesis: 'If we post daily about ICP pain points, we will generate 20+ qualified leads',
        control: 'Sporadic posting without a clear theme',
        variant: '7-day sprint: 1 post/day with pain → promise → CTA structure',
        success_metric: 'Leads captured (DMs, comments, profile visits)',
        sample_size: '7 posts over 7 days',
        action_steps: [
            'Draft Post #1: Problem framing',
            'Draft Post #2: Stakes & cost of inaction',
            'Draft Post #3: Objection-killer',
            'Draft Post #4: Behind-the-scenes story',
            'Draft Post #5: Quick win / tip',
            'Draft Post #6: Social proof nugget',
            'Draft Post #7: Direct CTA post'
        ],
        cadenceDefaults: { postsPerDay: 1 },
        defaultChecklist: [
            { label: 'Draft Post #1: Problem framing', completed: false, group: 'create' },
            { label: 'Post it', completed: false, group: 'publish' },
            { label: 'Draft Post #2: Stakes & cost of inaction', completed: false, group: 'create' },
            { label: 'Post it', completed: false, group: 'publish' },
            { label: 'Draft Post #3: Objection-killer', completed: false, group: 'create' },
            { label: 'Post it', completed: false, group: 'publish' },
            { label: 'Draft Post #4: Behind-the-scenes story', completed: false, group: 'create' },
            { label: 'Post it', completed: false, group: 'publish' },
            { label: 'Draft Post #5: Quick win / tip', completed: false, group: 'create' },
            { label: 'Post it', completed: false, group: 'publish' },
            { label: 'Draft Post #6: Social proof nugget', completed: false, group: 'create' },
            { label: 'Post it', completed: false, group: 'publish' },
            { label: 'Draft Post #7: Direct CTA post', completed: false, group: 'create' },
            { label: 'Post it', completed: false, group: 'publish' },
            { label: 'Analyze engagement & note learnings', completed: false, group: 'followup' },
        ],
        allowed_objectives: ['acquire', 'launch', 'reposition'],
        allowed_channels: ['linkedin', 'twitter', 'instagram']
    },
    {
        id: 'outbound-dm-sprint',
        name: 'Outbound DM Sprint',
        description: '15 targeted DMs/day with a tight script. Start conversations.',
        goal: 'calls',
        duration: 7,
        effortPerDay: '45m',
        outputs: ['DM script', '105 conversations started'],
        hypothesis: 'If we send 15 targeted DMs per day with personalized hooks, we will book 5+ calls',
        control: 'No active DM outreach',
        variant: 'Value-first DM strategy: engage, help, then offer',
        success_metric: 'Calls booked',
        sample_size: '105 DMs over 7 days',
        action_steps: [
            'Build prospect list (50+ targets)',
            'Write DM script v1',
            'Send 15 DMs per day',
            'Follow-up on non-responders',
            'Book calls from interested replies',
            'Track: DMs sent, responses, calls booked'
        ],
        cadenceDefaults: { dmsPerDay: 15, followupsPerDay: 10 },
        defaultChecklist: [
            { label: 'Write DM script v1', completed: false, group: 'setup' },
            { label: 'Build prospect list (50+ targets)', completed: false, group: 'setup' },
            { label: 'Send 15 DMs', completed: false, group: 'publish' },
            { label: 'Log replies', completed: false, group: 'followup' },
            { label: 'Send 15 DMs', completed: false, group: 'publish' },
            { label: 'Follow-up on Day 1 non-responders', completed: false, group: 'followup' },
            { label: 'Send 15 DMs', completed: false, group: 'publish' },
            { label: 'Follow-ups', completed: false, group: 'followup' },
            { label: 'Send 15 DMs', completed: false, group: 'publish' },
            { label: 'Follow-ups', completed: false, group: 'followup' },
            { label: 'Send 15 DMs', completed: false, group: 'publish' },
            { label: 'Follow-ups', completed: false, group: 'followup' },
            { label: 'Send 15 DMs', completed: false, group: 'publish' },
            { label: 'Follow-ups', completed: false, group: 'followup' },
            { label: 'Send 15 DMs', completed: false, group: 'publish' },
            { label: 'Final follow-ups + analyze results', completed: false, group: 'followup' },
        ],
        allowed_objectives: ['acquire', 'convert'],
        allowed_channels: ['linkedin', 'instagram', 'cold_dms', 'whatsapp']
    },
    {
        id: 'case-study-sprint',
        name: 'Case Study Sprint',
        description: 'Daily social proof to build trust fast. Turn customer wins into content.',
        goal: 'proof',
        duration: 7,
        effortPerDay: '30m',
        outputs: ['7 social proof posts', '1 long-form case study'],
        hypothesis: 'If we publish daily customer success content, we will increase trust signals by 50%',
        control: 'No systematic case study content',
        variant: '7-day sprint with daily social proof posts',
        success_metric: 'Engagement rate and inbound inquiries',
        sample_size: '7 posts across 7 days',
        action_steps: [
            'Identify 3 customer stories',
            'Collect metrics & quotes',
            'Post daily social proof content',
            'Write long-form case study at end',
            'Track engagement and inbound leads'
        ],
        cadenceDefaults: { postsPerDay: 1 },
        defaultChecklist: [
            { label: 'Identify 3 customer stories', completed: false, group: 'setup' },
            { label: 'Collect metrics & quotes', completed: false, group: 'setup' },
            { label: 'Post: Customer result highlight #1', completed: false, group: 'publish' },
            { label: 'Post: Before/after transformation', completed: false, group: 'publish' },
            { label: 'Post: Customer quote + context', completed: false, group: 'publish' },
            { label: 'Post: Problem → Solution → Result', completed: false, group: 'publish' },
            { label: 'Post: Screenshot / video proof', completed: false, group: 'publish' },
            { label: 'Post: Customer result highlight #2', completed: false, group: 'publish' },
            { label: 'Post: Full case study teaser + CTA', completed: false, group: 'publish' },
            { label: 'Write long-form case study', completed: false, group: 'create' },
        ],
        allowed_objectives: ['proof', 'convert'],
        allowed_channels: ['linkedin', 'email']
    },
    {
        id: 'landing-page-sprint',
        name: 'Landing Page + CTA Sprint',
        description: 'Fix message-match + deploy CTA assets. Optimize conversion.',
        goal: 'leads',
        duration: 7,
        effortPerDay: '45m',
        outputs: ['Updated landing page', 'CTA variants', 'A/B test setup'],
        hypothesis: 'If we optimize our landing page messaging, we will increase conversion by 30%',
        control: 'Current landing page without optimization',
        variant: 'Message-match audit + hero rewrite + CTA variants',
        success_metric: 'Landing page conversion rate (%)',
        sample_size: '1000 visitors',
        action_steps: [
            'Audit current landing page',
            'Rewrite hero headline and subheadline',
            'Update social proof section',
            'Write 3 CTA button variants',
            'Implement changes and set up tracking',
            'Create A/B test'
        ],
        defaultChecklist: [
            { label: 'Audit current landing page', completed: false, group: 'setup' },
            { label: 'List top 3 message-match gaps', completed: false, group: 'setup' },
            { label: 'Rewrite hero headline', completed: false, group: 'create' },
            { label: 'Rewrite subheadline', completed: false, group: 'create' },
            { label: 'Update social proof section', completed: false, group: 'create' },
            { label: 'Add/update testimonials', completed: false, group: 'create' },
            { label: 'Write 3 CTA button variants', completed: false, group: 'create' },
            { label: 'Design CTA section', completed: false, group: 'create' },
            { label: 'Implement changes', completed: false, group: 'publish' },
            { label: 'Set up tracking', completed: false, group: 'setup' },
            { label: 'Create A/B test (if applicable)', completed: false, group: 'setup' },
            { label: 'Soft launch', completed: false, group: 'publish' },
            { label: 'Review initial metrics', completed: false, group: 'followup' },
            { label: 'Document learnings', completed: false, group: 'followup' },
        ],
        allowed_objectives: ['convert', 'acquire'],
        allowed_channels: ['email']
    },
    {
        id: 'offer-refinement-sprint',
        name: 'Offer Refinement Sprint',
        description: 'Tighten offer + objections + proof. Make your offer irresistible.',
        goal: 'sales',
        duration: 7,
        effortPerDay: '30m',
        outputs: ['Refined offer doc', 'Objection-handling scripts', 'Updated pricing'],
        hypothesis: 'If we systematically address top objections, we will increase close rate by 25%',
        control: 'Current offer without structured objection-handling',
        variant: 'Full objection audit + scripts + risk reversal',
        success_metric: 'Close rate (%)',
        sample_size: 'Next 20 sales conversations',
        action_steps: [
            'List common objections (5+)',
            'Write objection-handling scripts',
            'Create proof points for each objection',
            'Refine offer headline',
            'Add risk reversal / guarantee',
            'Test new messaging in 3 conversations'
        ],
        defaultChecklist: [
            { label: 'Audit current offer positioning', completed: false, group: 'setup' },
            { label: 'List common objections (5+)', completed: false, group: 'setup' },
            { label: 'Write objection-handling script #1-3', completed: false, group: 'create' },
            { label: 'Write objection-handling script #4-5', completed: false, group: 'create' },
            { label: 'Create proof points for each objection', completed: false, group: 'create' },
            { label: 'Refine offer headline', completed: false, group: 'create' },
            { label: 'Add risk reversal / guarantee', completed: false, group: 'create' },
            { label: 'Update pricing presentation', completed: false, group: 'create' },
            { label: 'Create comparison chart (if applicable)', completed: false, group: 'create' },
            { label: 'Test new messaging in 3 conversations', completed: false, group: 'publish' },
            { label: 'Collect feedback', completed: false, group: 'followup' },
            { label: 'Finalize offer doc', completed: false, group: 'followup' },
        ],
        allowed_objectives: ['convert', 'reposition'],
        allowed_channels: ['email', 'linkedin']
    },
    {
        id: 'workshop-webinar-sprint',
        name: 'Workshop / Webinar Sprint',
        description: 'One event + promo + follow-up. High-touch lead generation.',
        goal: 'calls',
        duration: 14,
        effortPerDay: '45m',
        outputs: ['Webinar deck', 'Promo sequence', 'Follow-up emails', 'Recording'],
        hypothesis: 'If we host a value-packed webinar, we will book 10+ calls from attendees',
        control: 'No webinar/workshop strategy',
        variant: '14-day sprint: prep + promo + deliver + follow-up',
        success_metric: 'Calls booked from attendees',
        sample_size: '50+ registrants',
        action_steps: [
            'Define topic & hook',
            'Set date & create registration page',
            'Write promo emails',
            'Create webinar slides',
            'Host the webinar',
            'Send follow-up emails',
            'Analyze results & book calls'
        ],
        cadenceDefaults: { postsPerDay: 1 },
        defaultChecklist: [
            { label: 'Define topic & hook', completed: false, group: 'setup' },
            { label: 'Set date & create registration page', completed: false, group: 'setup' },
            { label: 'Write promo email #1', completed: false, group: 'create' },
            { label: 'Send promo email #1', completed: false, group: 'publish' },
            { label: 'Post promo on LinkedIn', completed: false, group: 'publish' },
            { label: 'Write promo email #2', completed: false, group: 'create' },
            { label: 'Send promo email #2', completed: false, group: 'publish' },
            { label: 'Create webinar slides', completed: false, group: 'create' },
            { label: 'Write reminder email', completed: false, group: 'create' },
            { label: 'Send reminder email', completed: false, group: 'publish' },
            { label: 'Host the webinar', completed: false, group: 'publish' },
            { label: 'Write follow-up email for attendees', completed: false, group: 'create' },
            { label: 'Write follow-up email for no-shows', completed: false, group: 'create' },
            { label: 'Send follow-up emails', completed: false, group: 'publish' },
            { label: 'Post recording + summary', completed: false, group: 'publish' },
            { label: 'Analyze results & book calls', completed: false, group: 'followup' },
        ],
        allowed_objectives: ['acquire', 'convert', 'proof'],
        allowed_channels: ['email', 'linkedin']
    }
];

// =====================================
// Template Helpers
// =====================================

/**
 * Get moves that match the given objective and channel
 */
export function getMovesForContext(
    objective: CampaignObjective,
    channels: string[],
    count: number = 3
): MoveTemplate[] {
    // Filter by objective
    let candidates = MOVE_TEMPLATES.filter(m =>
        !m.allowed_objectives || m.allowed_objectives.includes(objective)
    );

    // Prefer moves that match the channels
    const channelMatches = candidates.filter(m =>
        !m.allowed_channels || m.allowed_channels.some(ch => channels.includes(ch))
    );

    if (channelMatches.length >= count) {
        candidates = channelMatches;
    }

    // Shuffle and return
    return candidates
        .sort(() => Math.random() - 0.5)
        .slice(0, count);
}

/**
 * Get templates for a specific objective
 */
export function getTemplatesForObjective(objective: CampaignObjective): MoveTemplate[] {
    return MOVE_TEMPLATES.filter(t =>
        !t.allowed_objectives || t.allowed_objectives.includes(objective)
    );
}

/**
 * Get templates for a specific channel
 */
export function getTemplatesForChannel(channel: ChannelType): MoveTemplate[] {
    return MOVE_TEMPLATES.filter(t =>
        !t.allowed_channels || t.allowed_channels.includes(channel)
    );
}

/**
 * Get template by ID
 */
export function getTemplateById(id: string): MoveTemplate | undefined {
    return MOVE_TEMPLATES.find(t => t.id === id);
}

/**
 * Generate checklist items with unique IDs from a template
 */
export function generateChecklistFromTemplate(template: MoveTemplate): ChecklistItem[] {
    return template.defaultChecklist.map((item, idx) => ({
        ...item,
        id: `${template.id}-${idx}-${Date.now()}`
    }));
}

// =====================================
// Template Labels & Icons
// =====================================

export const EFFORT_LABELS: Record<'20m' | '30m' | '45m' | '90m', string> = {
    '20m': '20 min/day',
    '30m': '30 min/day',
    '45m': '45 min/day',
    '90m': '90 min/day'
};

export const TEMPLATE_ICONS: Record<string, string> = {
    'problem-post-sprint': '📝',
    'outbound-dm-sprint': '💬',
    'case-study-sprint': '📊',
    'landing-page-sprint': '🎯',
    'offer-refinement-sprint': '💎',
    'workshop-webinar-sprint': '🎤'
};
