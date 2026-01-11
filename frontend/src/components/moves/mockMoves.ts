/* ══════════════════════════════════════════════════════════════════════════════
   MOVES — Mock Data & Generators
   Sample data for demonstrating the Moves UI
   ══════════════════════════════════════════════════════════════════════════════ */

import { Move, MoveCategory, MoveBriefData, ExecutionDay, MOVE_CATEGORIES } from "./types";

// --- Mock Brief Generator ---
export function generateMockBrief(category: MoveCategory, context: string): MoveBriefData {
    const categoryInfo = MOVE_CATEGORIES[category];

    // Extract keywords from context for personalization
    const words = context.toLowerCase().split(' ');
    const hasRestaurant = words.some(w => ['restaurant', 'steakhouse', 'cafe', 'bar', 'food'].includes(w));
    const hasSaas = words.some(w => ['saas', 'software', 'product', 'feature', 'launch'].includes(w));

    const names: Record<MoveCategory, string[]> = {
        ignite: ['Launch Blitz', 'The Grand Reveal', 'Ignition Sequence', 'Debut Sprint'],
        capture: ['Conversion Surge', 'Lead Magnet Sprint', 'Revenue Rally', 'Acquisition Blitz'],
        authority: ['Thought Leader Series', 'Expert Showcase', 'Authority Build', 'Trust Campaign'],
        repair: ['Reputation Reset', 'Trust Rebuild', 'Sentiment Shift', 'Crisis Response'],
        rally: ['Community Surge', 'Loyalty Sprint', 'Tribe Activation', 'VIP Campaign'],
    };

    const tones: Record<MoveCategory, string[]> = {
        ignite: ['Electric & Bold', 'Exciting & Fresh', 'Premium & Exclusive'],
        capture: ['Persuasive & Direct', 'Value-Focused', 'Urgent & Compelling'],
        authority: ['Confident & Knowledgeable', 'Thoughtful & Expert', 'Authoritative'],
        repair: ['Sincere & Humble', 'Transparent & Caring', 'Solution-Focused'],
        rally: ['Warm & Appreciative', 'Inclusive & Fun', 'Community-First'],
    };

    const strategies: Record<MoveCategory, string> = {
        ignite: 'Build anticipation with teaser content, reveal with high-impact visuals, and sustain momentum with behind-the-scenes and user reactions.',
        capture: 'Visual Feast + Direct Outreach. Pillar content on primary channels, cluster content for amplification, network actions for personal touch.',
        authority: 'Establish expertise through valuable insights, back claims with data and case studies, and engage with industry conversations.',
        repair: 'Acknowledge concerns transparently, demonstrate concrete improvements, and highlight positive testimonials from satisfied customers.',
        rally: 'Celebrate existing customers, create exclusive experiences, and encourage user-generated content and referrals.',
    };

    const metricsMap: Record<MoveCategory, string[]> = {
        ignite: ['Impressions', 'Reach', 'Shares', 'Waitlist Signups', 'PR Mentions'],
        capture: ['Leads Generated', 'Conversion Rate', 'Bookings', 'Revenue', 'CAC'],
        authority: ['Engagement Rate', 'Follower Growth', 'Mentions', 'Backlinks', 'Speaking Invites'],
        repair: ['Sentiment Score', 'Review Response Rate', 'NPS Change', 'Churn Reduction'],
        rally: ['Retention Rate', 'UGC Count', 'Referrals', 'LTV Increase', 'Community Growth'],
    };

    const randomName = names[category][Math.floor(Math.random() * names[category].length)];
    const randomTone = tones[category][Math.floor(Math.random() * tones[category].length)];

    // Generate goal based on context
    let goal = categoryInfo.goal;
    if (hasRestaurant && category === 'capture') {
        goal = '20+ bookings for the target day, increased repeat customer rate';
    } else if (hasSaas && category === 'ignite') {
        goal = '1000+ waitlist signups, 50+ demo requests, 5+ media mentions';
    }

    return {
        name: randomName,
        category,
        duration: 7,
        goal,
        tone: randomTone,
        strategy: strategies[category],
        metrics: metricsMap[category],
    };
}

// --- Mock Execution Generator ---
export function generateMockExecution(brief: MoveBriefData): ExecutionDay[] {
    const phases = ['Tease', 'Reveal', 'Proof', 'Urgency', 'Close', 'Sustain', 'Review'];

    const pillarTasks: Record<MoveCategory, string[]> = {
        capture: [
            'Create high-contrast hero image of offer',
            'Publish carousel: "The Value Breakdown"',
            'Share customer testimonial video',
            'Post scarcity graphic: "Only X spots left"',
            'Final push: Time-limited bonus offer',
            'Thank you post + customer highlights',
            'Results recap + lessons learned',
        ],
        ignite: [
            'Teaser visual: "Something big is coming"',
            'Full reveal post + announcement video',
            'Behind-the-scenes content',
            'Early adopter spotlight',
            'Feature deep-dive carousel',
            'User reactions compilation',
            'Launch week recap',
        ],
        authority: [
            'Share contrarian industry insight',
            'Publish data-backed thought piece',
            'Expert Q&A or hot takes thread',
            'Case study breakdown',
            'Industry trend analysis',
            'Lessons from experience post',
            'Week summary + engagement wins',
        ],
        repair: [
            'Public acknowledgment post',
            'Detailed action plan reveal',
            'Progress update with proof',
            'Customer success story',
            'Team/process improvement share',
            'Positive feedback compilation',
            'Forward-looking commitment',
        ],
        rally: [
            'Customer appreciation post',
            'Exclusive offer for community',
            'UGC contest announcement',
            'Community spotlight feature',
            'Referral program push',
            'VIP experience preview',
            'Community wins celebration',
        ],
    };

    const clusterActions: string[][] = [
        ['Story poll: Gauge interest', 'Tweet teaser with countdown'],
        ['Repost to all channels', 'Email blast to subscribers'],
        ['Story: Share testimonials', 'LinkedIn article embed'],
        ['Countdown sticker story', 'Reminder email send'],
        ['Limited time story push', 'SMS to VIP list'],
        ['Share customer reactions', 'Community thank you'],
        ['Story highlights save', 'Newsletter recap'],
    ];

    const networkActions: Array<{ title: string; channel: string }> = [
        { title: 'DM 5 warm prospects', channel: 'DM' },
        { title: 'Email 10 newsletter leads', channel: 'Email' },
        { title: 'Comment on 5 industry posts', channel: 'Comment' },
        { title: 'Call 3 hot prospects', channel: 'Call' },
        { title: 'Follow up with interested leads', channel: 'DM' },
        { title: 'Thank engaged customers', channel: 'DM' },
        { title: 'Schedule debrief calls', channel: 'Call' },
    ];

    return Array.from({ length: brief.duration }, (_, i) => ({
        day: i + 1,
        phase: phases[i] || 'Sustain',
        pillarTask: {
            id: `pillar-${i + 1}`,
            title: pillarTasks[brief.category][i] || 'Continue momentum',
            description: 'Primary content piece for the day',
            status: 'pending', // All tasks start as pending
            channel: 'Multi-channel',
        },
        clusterActions: (clusterActions[i] || ['Support post', 'Engagement boost']).map((action, j) => ({
            id: `cluster-${i + 1}-${j + 1}`,
            title: action,
            description: '',
            status: 'pending', // All tasks start as pending
            channel: j === 0 ? 'Stories' : 'Social',
        })),
        networkAction: {
            id: `network-${i + 1}`,
            title: networkActions[i]?.title || 'Engage with audience',
            description: 'Personal outreach action',
            status: 'pending', // All tasks start as pending
            channel: networkActions[i]?.channel || 'DM',
        },
    }));
}

// Helper to get dates relative to today
function getRelativeDate(daysOffset: number): string {
    const date = new Date();
    date.setDate(date.getDate() + daysOffset);
    return date.toISOString();
}

// --- Sample Moves for List ---
export const SAMPLE_MOVES: Move[] = [
    {
        id: 'mov-001',
        name: 'Tomahawk Tuesday Takeover',
        category: 'capture',
        status: 'active',
        duration: 7,
        goal: '20 bookings for next Tuesday',
        tone: 'Premium & Exclusive',
        context: 'I own a steakhouse. Tuesdays are dead. I want to fill tables on Tuesday nights.',
        createdAt: getRelativeDate(-2),
        startDate: getRelativeDate(-1), // Started yesterday, so Day 2 tasks show today
        progress: 14,
        execution: generateMockExecution({
            name: 'Tomahawk Tuesday Takeover',
            category: 'capture',
            duration: 7,
            goal: '20 bookings for next Tuesday',
            tone: 'Premium & Exclusive',
            strategy: 'Visual Feast + Direct Outreach',
            metrics: ['Bookings', 'Revenue', 'Table Turnover'],
        }),
    },
    {
        id: 'mov-002',
        name: 'Founder Insights Series',
        category: 'authority',
        status: 'completed',
        duration: 7,
        goal: 'Establish thought leadership in B2B marketing',
        tone: 'Confident & Knowledgeable',
        context: 'Position myself as an expert in B2B marketing for SaaS founders.',
        createdAt: getRelativeDate(-15),
        startDate: getRelativeDate(-14),
        endDate: getRelativeDate(-7),
        progress: 100,
        execution: [],
    },
    {
        id: 'mov-003',
        name: 'New Year Strategy Launch',
        category: 'ignite',
        status: 'draft',
        duration: 7,
        goal: 'Generate buzz for 2026 product roadmap',
        tone: 'Electric & Bold',
        context: 'Announce our 2026 product vision and upcoming features.',
        createdAt: getRelativeDate(-1),
        progress: 0,
        execution: generateMockExecution({
            name: 'New Year Strategy Launch',
            category: 'ignite',
            duration: 7,
            goal: 'Generate buzz for product launch',
            tone: 'Electric & Bold',
            strategy: 'Build anticipation → Reveal → Sustain',
            metrics: ['Impressions', 'Signups', 'Shares'],
        }),
    },
];
