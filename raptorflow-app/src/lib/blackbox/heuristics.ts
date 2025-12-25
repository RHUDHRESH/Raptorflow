import { BehavioralPrinciple, GoalType, ChannelType } from '../blackbox-types';

export interface HeuristicTemplate {
    id: string;
    title: string;
    description: string;
    principle: BehavioralPrinciple;
    hypothesis_template: string;
    control_placeholder: string;
    variant_placeholder: string;
    success_metric: string;
    sample_size_recommendation: string;
    duration_days: number;
    allowed_goals?: GoalType[];
    allowed_channels?: ChannelType[];
    impact_score: number; // 1-10
    risk_score: number; // 1-10
}

export const HEURISTICS_LIBRARY: HeuristicTemplate[] = [
    {
        id: 'subject_line_question',
        title: 'The Question Hook',
        description: 'Replacing a statement with a curiosity-driven question in subject lines.',
        principle: 'pattern_interrupt',
        hypothesis_template: 'If we replace the standard subject line with a question that targets a core pain point, then open rates will increase by 15% because curiosity triggers an immediate dopamine response.',
        control_placeholder: 'How to scale your SaaS marketing',
        variant_placeholder: 'Why is your SaaS marketing stuck at $10k MRR?',
        success_metric: 'Open Rate',
        sample_size_recommendation: '500 contacts',
        duration_days: 3,
        allowed_channels: ['email'],
        allowed_goals: ['replies', 'clicks'],
        impact_score: 7,
        risk_score: 2
    },
    {
        id: 'social_proof_count',
        title: 'Quantified Social Proof',
        description: 'Adding specific numbers to social proof instead of generic claims.',
        principle: 'social_proof',
        hypothesis_template: 'If we add the specific number of founders using RaptorFlow to the landing page hero, then conversion rate will increase by 10% due to the bandwagon effect.',
        control_placeholder: 'Join hundreds of founders using RaptorFlow.',
        variant_placeholder: 'Join 1,243 founders who automated their 90-day plan this week.',
        success_metric: 'Conversion Rate',
        sample_size_recommendation: '1000 visitors',
        duration_days: 7,
        allowed_channels: ['website', 'google_ads', 'facebook'],
        allowed_goals: ['sales', 'leads', 'clicks'],
        impact_score: 8,
        risk_score: 1
    },
    {
        id: 'loss_aversion_countdown',
        title: 'The Regret Trigger',
        description: 'Using a countdown timer to emphasize what they lose by waiting.',
        principle: 'loss_aversion',
        hypothesis_template: 'If we include a 24-hour countdown timer for the early-bird offer, then sales will increase by 20% because humans are 2x more motivated to avoid loss than achieve gain.',
        control_placeholder: 'Offer ends soon.',
        variant_placeholder: 'Offer expires in 23:59:59. Save $200 now or lose it forever.',
        success_metric: 'Sales Volume',
        sample_size_recommendation: '2000 impressions',
        duration_days: 1,
        allowed_channels: ['email', 'website', 'instagram'],
        allowed_goals: ['sales', 'clicks'],
        impact_score: 9,
        risk_score: 5
    },
    {
        id: 'friction_one_click',
        title: 'The Zero-Friction CTA',
        description: 'Removing all unnecessary steps from the primary action.',
        principle: 'friction',
        hypothesis_template: 'If we replace the multi-field signup form with a one-click Google Auth button, then signup completion will increase by 30% by eliminating cognitive load.',
        control_placeholder: 'Fill out name, email, and company to start.',
        variant_placeholder: 'Continue with Google (1-click).',
        success_metric: 'Signup Completion Rate',
        sample_size_recommendation: '500 sessions',
        duration_days: 5,
        allowed_channels: ['website'],
        allowed_goals: ['leads', 'sales'],
        impact_score: 10,
        risk_score: 3
    }
];
