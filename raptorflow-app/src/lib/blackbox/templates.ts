import { BehavioralPrinciple, RiskLevel, ChannelType, GoalType } from '../blackbox-types';

export interface LeverTemplate {
    id: string;
    principle: BehavioralPrinciple;
    title_template: string;
    bet_template: string;
    why: string;
    allowed_goals?: GoalType[];
}

export interface ConstraintTemplate {
    id: string;
    description: string;
    risk_level: RiskLevel;
}

export const LEVERS: LeverTemplate[] = [
    // Friction Killers
    {
        id: 'no_link_reply',
        principle: 'friction',
        title_template: 'Reply-to-qualify instead of link',
        bet_template: 'Ask for a reply with a number or "yes" instead of sending a link.',
        why: 'Reduces friction and increases commitment via micro-yes.'
    },
    {
        id: 'one_line_signup',
        principle: 'friction',
        title_template: 'One-line signup flow',
        bet_template: 'Strip the CTA to a single sentence with zero navigation options.',
        why: 'Less choices = higher conversion rate (Hick’s Law).'
    },

    // Identity / Status
    {
        id: 'founder_identity',
        principle: 'identity',
        title_template: 'Founder identity opener',
        bet_template: 'Open with a "founders like you" identity cue to force self-selection.',
        why: 'People act in accordance with their perceived identity.',
    },
    {
        id: 'negative_persona',
        principle: 'identity',
        title_template: 'The "Not for you" framing',
        bet_template: 'Explicitly state who this is NOT for to attract the right qualified leads.',
        why: 'Exclusion signals status and scarcity.',
    },

    // Loss Aversion
    {
        id: 'leaking_money',
        principle: 'loss_aversion',
        title_template: 'You are leaking money here',
        bet_template: 'Lead with what they are losing right now, not what they will gain.',
        why: 'Loss aversion is 2x stronger than gain motivation.',
    },
    {
        id: 'fomo_deadline',
        principle: 'loss_aversion',
        title_template: 'Artificial expiry deadline',
        bet_template: 'Add a 48h expiration to the offer, even if artificial.',
        why: 'Scarcity drives immediate action.',
    },

    // Social Proof
    {
        id: 'steal_template',
        principle: 'social_proof',
        title_template: 'Steal my template',
        bet_template: 'Offer a high-value asset that "others are using" to trigger herd behavior.',
        why: 'Desire to copy success reduces perceived risk.',
    },
    {
        id: 'aggregated_proof',
        principle: 'social_proof',
        title_template: 'What 17 founders did',
        bet_template: 'Lead with aggregated data/proof from a peer group.',
        why: 'Safety in numbers reduces skepticism.',
    },

    // Pattern Interrupt
    {
        id: 'anti_design',
        principle: 'pattern_interrupt',
        title_template: 'The Anti-Design Confession',
        bet_template: 'Send a plain-text, unpolished message with one embarrassing truth.',
        why: 'Authenticity signals cut through polished noise.',
    },
    {
        id: 'ugly_ad',
        principle: 'pattern_interrupt',
        title_template: 'Ugly ad experiment',
        bet_template: 'Use deliberately low-fi creative that looks unpolished.',
        why: 'Stands out in a feed of polished corporate content.',
    },

    // Commitment
    {
        id: 'micro_yes',
        principle: 'commitment',
        title_template: 'Micro-yes ladder',
        bet_template: 'Ask a tiny, low-stakes question before the real ask.',
        why: 'Consistency principle: small yes leads to big yes.',
    },
    {
        id: 'advice_ask',
        principle: 'commitment',
        title_template: 'The Advice Trap',
        bet_template: 'Ask for advice first, then pivot to the pitch in follow-up.',
        why: 'Ben Franklin effect: asking for a favor builds rapport.',
    }
];

export const CONSTRAINTS: ConstraintTemplate[] = [
    // Safe
    { id: 'short_length', description: 'Under 100 words', risk_level: 'safe' },
    { id: 'clear_cta', description: 'Single clear CTA', risk_level: 'safe' },
    { id: 'professional_tone', description: 'Professional tone', risk_level: 'safe' },

    // Spicy
    { id: 'no_links', description: 'No hyperlinks allowed', risk_level: 'spicy' },
    { id: 'contrarian_hook', description: 'Contrarian opener', risk_level: 'spicy' },
    { id: 'visual_pattern_interrupt', description: 'Visual pattern interrupt', risk_level: 'spicy' },
    { id: 'emoji_subject', description: 'Single emoji subject line', risk_level: 'spicy' },

    // Unreasonable
    { id: 'anti_selling', description: 'Anti-selling framing', risk_level: 'unreasonable' },
    { id: 'confession', description: 'Embarrassing confession', risk_level: 'unreasonable' },
    { id: 'typo_human', description: 'Deliberate typo/lowercase', risk_level: 'unreasonable' },
    { id: 'aggressive_filter', description: 'Aggressively filter out prospects', risk_level: 'unreasonable' }
];

export const CHANNEL_DEFAULTS: Record<ChannelType, { effort: "10m" | "30m" | "2h"; time_to_signal: "24h" | "48h" | "7d" }> = {
    email: { effort: '30m', time_to_signal: '24h' },
    linkedin: { effort: '30m', time_to_signal: '24h' },
    twitter: { effort: '10m', time_to_signal: '24h' },
    whatsapp: { effort: '10m', time_to_signal: '24h' },
    youtube: { effort: '2h', time_to_signal: '7d' },
    instagram: { effort: '30m', time_to_signal: '24h' },
    other: { effort: '10m', time_to_signal: '48h' }
};
