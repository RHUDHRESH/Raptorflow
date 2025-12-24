import { MoveGoal, ChannelType, CampaignObjective } from './campaigns-types';

/**
 * Move Templates — Real actionable marketing moves with hypothesis, A/B testing, and action steps
 */

export interface MoveTemplate {
    id: string;
    name: string;
    goal: MoveGoal;
    hypothesis: string;
    control: string;
    variant: string;
    success_metric: string;
    sample_size: string;
    action_steps: string[];
    allowed_objectives?: CampaignObjective[];
    allowed_channels?: ChannelType[];
}

export const MOVE_TEMPLATES: MoveTemplate[] = [
    // ==============================
    // ACQUISITION MOVES
    // ==============================
    {
        id: 'cold_email_sequence',
        name: 'Cold Email Outreach Sprint',
        goal: 'leads',
        hypothesis: 'If we send personalized cold emails with a specific pain point hook, we will get 10+ qualified replies',
        control: 'No cold email outreach running',
        variant: '5-email sequence targeting decision makers with personalized first lines',
        success_metric: 'Reply rate (%)',
        sample_size: '200 emails (40 per day for 5 days)',
        action_steps: [
            'Build list of 200 prospects matching ICP from LinkedIn Sales Navigator',
            'Research each prospect: find recent news, posts, or company updates',
            'Write email #1: Personalized hook + one pain point + soft CTA',
            'Write emails #2-5: Follow-ups with new angles and proof points',
            'Set up sequence in email tool (Apollo, Lemlist, or similar)',
            'Track: Open rate, reply rate, meetings booked'
        ],
        allowed_objectives: ['acquire'],
        allowed_channels: ['email']
    },
    {
        id: 'linkedin_connection_campaign',
        name: 'LinkedIn Connection Sprint',
        goal: 'distribution',
        hypothesis: 'If we send 25 targeted connection requests per day with a personalized note, we will grow network by 300+ relevant connections',
        control: 'Passive LinkedIn presence',
        variant: 'Active outreach with personalized connection notes',
        success_metric: 'Connection acceptance rate (%)',
        sample_size: '175 connection requests over 7 days',
        action_steps: [
            'Define exact ICP: titles, company size, industry',
            'Use LinkedIn Sales Navigator to find 200 prospects',
            'Write 3 connection note templates (personalize with name/company)',
            'Send 25 requests per day (LinkedIn limit)',
            'Track acceptance rate and immediate replies',
            'Follow up accepted connections with value-first message'
        ],
        allowed_objectives: ['acquire', 'launch'],
        allowed_channels: ['linkedin']
    },
    {
        id: 'content_value_bomb',
        name: 'Content Value Bomb Week',
        goal: 'distribution',
        hypothesis: 'If we publish 5 high-value pieces in one week, we will 3x our reach and capture 50+ new leads',
        control: 'Normal 1-2 posts per week',
        variant: '5 posts in 5 days: 1 carousel, 2 text posts, 1 video, 1 thread',
        success_metric: 'Total impressions and new followers',
        sample_size: '5 posts across 5 days',
        action_steps: [
            'Brainstorm 5 topics your ICP cares most about',
            'Create: 1 carousel (10 slides), 2 text posts (hook + story), 1 video (2 min), 1 thread',
            'Schedule posts for peak engagement times (Tue-Sat, 8-10am)',
            'Add clear CTA to each: follow, comment, or visit link',
            'Engage with every comment within first hour',
            'Track impressions, engagement rate, profile visits, new followers'
        ],
        allowed_objectives: ['acquire', 'launch', 'reposition'],
        allowed_channels: ['linkedin', 'twitter', 'instagram']
    },
    {
        id: 'dm_conversation_starter',
        name: 'DM Conversation Starter Sprint',
        goal: 'calls',
        hypothesis: 'If we start conversations in DMs without pitching, we will book 5+ calls from 50 conversations',
        control: 'No active DM outreach',
        variant: 'Value-first DM strategy: engage, help, then offer',
        success_metric: 'Conversations → Calls booked ratio',
        sample_size: '50 DM conversations over 7 days',
        action_steps: [
            'Identify 50 prospects who are actively posting about problems you solve',
            'Comment genuinely on 2-3 of their posts first (build familiarity)',
            'Send DM: Lead with value or observation, NOT a pitch',
            'If they respond, continue conversation naturally',
            'After 2-3 exchanges, offer to help with a specific problem',
            'Track: DMs sent, responses, calls booked'
        ],
        allowed_objectives: ['acquire', 'convert'],
        allowed_channels: ['linkedin', 'twitter', 'instagram', 'cold_dms']
    },

    // ==============================
    // CONVERSION MOVES
    // ==============================
    {
        id: 'warm_lead_reactivation',
        name: 'Warm Lead Reactivation Blitz',
        goal: 'sales',
        hypothesis: 'If we reach out to leads who went cold in the last 30-90 days, we will close 2-3 deals from the "dead pile"',
        control: 'Leads sitting inactive in CRM',
        variant: 'Personalized reactivation sequence with new angle',
        success_metric: 'Reply rate and deals closed',
        sample_size: '50 cold leads',
        action_steps: [
            'Export leads from CRM who: engaged but never bought, 30-90 days old',
            'Segment by original objection or reason they went cold',
            'Write 3 reactivation emails with new angle (case study, new feature, limited offer)',
            'Send email #1, wait 3 days, send #2, wait 3 days, send #3',
            'Call anyone who opens but doesn\'t reply',
            'Track: Opens, replies, calls, deals closed'
        ],
        allowed_objectives: ['convert'],
        allowed_channels: ['email']
    },
    {
        id: 'trial_conversion_push',
        name: 'Trial-to-Paid Conversion Push',
        goal: 'sales',
        hypothesis: 'If we proactively reach out to trial users on day 5 with personalized help, we will increase conversion by 20%',
        control: 'Automated trial emails only',
        variant: 'Personal outreach on day 5 with usage-based messaging',
        success_metric: 'Trial to paid conversion rate (%)',
        sample_size: '30 active trial users',
        action_steps: [
            'Identify trial users who signed up in last 7 days',
            'Check their usage: active users vs low-engagement',
            'For active users: send personalized email praising their usage + offer call',
            'For low-engagement: send helpful email asking about blockers',
            'Follow up non-responders with a 2nd email or LinkedIn message',
            'Track: Responses, calls, conversions within 14 days'
        ],
        allowed_objectives: ['convert'],
        allowed_channels: ['email', 'linkedin']
    },

    // ==============================
    // LAUNCH MOVES
    // ==============================
    {
        id: 'product_hunt_launch',
        name: 'Product Hunt Launch Prep',
        goal: 'distribution',
        hypothesis: 'If we execute a coordinated Product Hunt launch with 100 supporters, we will hit top 5 and get 500+ signups',
        control: 'Quiet launch with no coordination',
        variant: 'Coordinated launch with pre-committed supporters',
        success_metric: 'Product Hunt rank and signups',
        sample_size: '100 pre-committed supporters',
        action_steps: [
            'Set launch date 2 weeks out (Tuesday or Thursday)',
            'Build list of 100 supporters who will upvote and comment',
            'Prepare: tagline, description, 5 screenshots, maker intro video',
            'Send reminder to supporters night before + morning of',
            'Be online 6am-6pm launch day, respond to every comment',
            'Track: Upvotes, rank, signups, traffic'
        ],
        allowed_objectives: ['launch'],
        allowed_channels: ['linkedin', 'twitter', 'email']
    },
    {
        id: 'launch_announcement_sequence',
        name: 'Launch Announcement Sequence',
        goal: 'leads',
        hypothesis: 'If we build anticipation with a 5-day countdown, we will 3x launch week signups vs a sudden launch',
        control: 'Announce on launch day only',
        variant: '5-day countdown with daily teasers building to reveal',
        success_metric: 'Launch week signups',
        sample_size: '5 posts over 5 days',
        action_steps: [
            'Day -5: Post "Something big is coming" teaser',
            'Day -4: Share the problem you\'re solving (build empathy)',
            'Day -3: Hint at the solution without revealing',
            'Day -2: Behind-the-scenes / founder story',
            'Day -1: Final teaser + set expectations',
            'Day 0: Full launch announcement with clear CTA',
            'Track: Engagement each day, waitlist signups, launch conversions'
        ],
        allowed_objectives: ['launch'],
        allowed_channels: ['linkedin', 'twitter', 'email', 'instagram']
    },

    // ==============================
    // PROOF MOVES
    // ==============================
    {
        id: 'case_study_collection',
        name: 'Case Study Collection Sprint',
        goal: 'proof',
        hypothesis: 'If we systematically ask happy customers for case studies, we will collect 3-5 new proof points in 2 weeks',
        control: 'No active case study collection',
        variant: 'Structured outreach to top customers with easy-to-complete format',
        success_metric: 'Case studies collected',
        sample_size: '15 customers asked',
        action_steps: [
            'Identify 15 customers with best results or highest satisfaction',
            'Prepare simple template: 5 questions, takes 10 minutes',
            'Reach out personally (not automated) with specific ask',
            'Offer incentive: feature them, discount, swag',
            'For those who agree, schedule 15-min call to go deeper',
            'Write up case study, get their approval, publish on 3 channels'
        ],
        allowed_objectives: ['proof'],
        allowed_channels: ['email', 'linkedin']
    },
    {
        id: 'testimonial_video_blitz',
        name: 'Testimonial Video Blitz',
        goal: 'proof',
        hypothesis: 'If we collect 5 video testimonials in 1 week, we will see 25% higher conversion on landing page',
        control: 'Text testimonials only on landing page',
        variant: 'Video testimonials prominently displayed',
        success_metric: 'Videos collected + landing page conversion change',
        sample_size: '10 customers asked, 5 target videos',
        action_steps: [
            'Identify 10 enthusiastic customers (NPS 9-10 or recent praise)',
            'Send personalized request with simple instructions (Loom, Zoom, phone video)',
            'Provide specific questions to answer (keep under 60 seconds)',
            'Offer incentive: gift card, feature, extended subscription',
            'Edit videos: add captions, trim, add branding',
            'Update landing page, measure conversion before/after'
        ],
        allowed_objectives: ['proof', 'convert'],
        allowed_channels: ['email', 'linkedin']
    },

    // ==============================
    // RETENTION / ACTIVATION MOVES
    // ==============================
    {
        id: 'activation_onboarding',
        name: 'Activation Onboarding Sprint',
        goal: 'activation',
        hypothesis: 'If we personally onboard every new user in the first 48 hours, we will double Day-7 activation rate',
        control: 'Automated onboarding emails only',
        variant: 'Personal video + offer of onboarding call',
        success_metric: 'Day-7 activation rate (%)',
        sample_size: '20 new signups',
        action_steps: [
            'Set up alert for every new signup',
            'Within 4 hours: send personalized Loom intro (30-60 sec)',
            'Offer 15-min onboarding call (Calendly link)',
            'Follow up day 2 if no response: "Any questions?"',
            'Track: Loom views, calls booked, Day-7 key action completed',
            'Compare to control cohort who only got automated emails'
        ],
        allowed_objectives: ['retain', 'convert'],
        allowed_channels: ['email']
    },
    {
        id: 'churn_prevention',
        name: 'Churn Prevention Outreach',
        goal: 'activation',
        hypothesis: 'If we proactively reach out to at-risk users before they churn, we will save 30% of them',
        control: 'Wait for users to cancel, then win-back email',
        variant: 'Proactive outreach to low-engagement users',
        success_metric: 'Users saved (continued subscription)',
        sample_size: '25 at-risk users',
        action_steps: [
            'Define "at-risk": no login in 14 days, or missed key action',
            'Pull list of 25 at-risk users from analytics',
            'Send personal email: "Noticed you haven\'t been using X recently..."',
            'Offer: call to help, pause instead of cancel, or feedback request',
            'Follow up non-responders with different angle',
            'Track: Responses, calls, users who returned/stayed'
        ],
        allowed_objectives: ['retain'],
        allowed_channels: ['email']
    }
];

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
