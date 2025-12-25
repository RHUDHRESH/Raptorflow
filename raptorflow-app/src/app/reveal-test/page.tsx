'use client';

import { useState } from 'react';
import { ICPRevealScreen } from '@/components/onboarding/ICPRevealScreen';
import { PositioningRevealScreen } from '@/components/onboarding/PositioningRevealScreen';
import { CompetitorsRevealScreen } from '@/components/onboarding/CompetitorsRevealScreen';
import { MessagingRevealScreen } from '@/components/onboarding/MessagingRevealScreen';
import { MarketRevealScreen } from '@/components/onboarding/MarketRevealScreen';
import { DerivedICP, DerivedPositioning, DerivedCompetitive, DerivedSoundbites, DerivedMarket } from '@/lib/foundation';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

// Mock data for testing the reveal screens
const mockICPs: DerivedICP[] = [
    {
        id: 'icp-1',
        name: 'Growth-Stage Marketing Leader',
        priority: 'primary',
        confidence: 0.87,
        description: 'Decision-makers at scaling companies who need to systematize marketing operations without hiring an agency.',
        firmographics: {
            companySize: '50-500 employees',
            industry: ['SaaS', 'B2B Tech'],
            geography: ['US', 'EU'],
            budget: '$10k-$50k annually',
        },
        painMap: {
            primary: 'Leads are inconsistent',
            secondary: ["Can't prove ROI", 'Too many disconnected tools'],
            triggers: ['Funding round', 'Hiring surge', 'Missed target'],
            urgency: 'now',
        },
        social: {
            platforms: [
                { name: 'LinkedIn', timing: 'Weekday mornings', vibe: 'Professional thought leadership' },
                { name: 'Twitter/X', timing: 'Throughout day', vibe: 'Industry hot takes' },
            ],
            authorities: ['Industry analysts', 'Peer CMOs', 'Podcast hosts'],
        },
        buying: {
            committee: [
                { role: 'Economic Buyer (CMO)', focus: 'ROI and budget impact' },
                { role: 'Technical Evaluator', focus: 'Integration and security' },
                { role: 'End User (Marketer)', focus: 'Daily usability' },
            ],
            timeline: '60-90 days',
            proofNeeded: ['Case studies', 'ROI calculator', 'Peer references'],
            blockers: ['Budget approval', 'Integration concerns'],
        },
        behavioral: {
            biases: [
                { name: 'Loss Aversion', implication: 'Fear of choosing wrong tool' },
                { name: 'Social Proof', implication: 'Validates with peer reviews' },
            ],
            deRisking: ['Free trial', 'POC with their data', 'Money-back guarantee'],
        },
    },
    {
        id: 'icp-2',
        name: 'Early-Stage Founder',
        priority: 'secondary',
        confidence: 0.72,
        description: 'Founders building their first marketing engine who need an all-in-one solution.',
        firmographics: {
            companySize: '1-20 employees',
            industry: ['Startups', 'SaaS'],
            geography: ['Global'],
            budget: '$1k-$10k annually',
        },
        painMap: {
            primary: 'Too many tools, no system',
            secondary: ['No time for marketing', 'Inconsistent messaging'],
            triggers: ['Funding round', 'Hiring first marketer'],
            urgency: 'soon',
        },
        social: {
            platforms: [
                { name: 'Twitter/X', timing: 'Evenings', vibe: 'Startup culture' },
                { name: 'Reddit', timing: 'Weekends', vibe: 'Honest peer advice' },
            ],
            authorities: ['Successful founders', 'VCs', 'Startup podcasts'],
        },
        buying: {
            committee: [{ role: 'Founder', focus: 'Speed to value' }],
            timeline: '7-14 days',
            proofNeeded: ['Demo', 'Quick wins'],
            blockers: ['Limited budget', 'Time to onboard'],
        },
        behavioral: {
            biases: [{ name: 'Optimism Bias', implication: 'Wants to move fast' }],
            deRisking: ['Free tier', 'Self-serve onboarding'],
        },
    },
];

const mockPositioning: DerivedPositioning = {
    matrix: {
        xAxis: { label: 'Ease of Use', lowEnd: 'Complex', highEnd: 'Simple' },
        yAxis: { label: 'Depth', lowEnd: 'Surface', highEnd: 'Deep' },
        positions: [
            { name: 'RaptorFlow', x: 0.85, y: 0.88, isYou: true },
            { name: 'HubSpot', x: 0.6, y: 0.5, isYou: false },
            { name: 'Spreadsheets', x: 0.3, y: 0.2, isYou: false },
            { name: 'Agencies', x: 0.4, y: 0.8, isYou: false },
        ],
    },
    ladder: [
        { rung: 1, name: 'Table Stakes', description: 'Basic functionality', score: 100, isYou: true },
        { rung: 2, name: 'Differentiation', description: 'AI-powered decision engine', score: 85, isYou: true },
        { rung: 3, name: 'Category Creation', description: 'New mental model', score: 60, isYou: false },
    ],
    statement: {
        forWhom: 'Growth-stage founders',
        company: 'RaptorFlow',
        category: 'Marketing Operating System',
        differentiator: 'turns chaos into clarity in 5 minutes',
        unlikeCompetitor: 'scattered tools and agencies',
        because: 'we make decisions, not dashboards',
    },
    oneThing: 'The only marketing OS that thinks with you',
    defensibility: 'high',
};

const mockCompetitive: DerivedCompetitive = {
    statusQuo: {
        name: 'Manual Processes',
        description: 'Spreadsheets, docs, and tribal knowledge',
        manualPatches: ['Weekly meetings', 'Slack threads', 'Ad-hoc reports'],
        toleratedPain: 'Slow, error-prone, but familiar',
        yourWedge: 'Automate the mundane, amplify the strategic',
    },
    indirect: [
        {
            name: 'Freelancers / Agencies',
            mechanism: 'Outsourced expertise',
            priceRange: '$2k-$20k/month',
            weakness: 'Expensive, slow, hard to scale',
            yourEdge: 'In-house control at fraction of cost',
        },
        {
            name: 'Point Solutions',
            mechanism: 'Best-of-breed tools stitched together',
            priceRange: '$500-$5k/month total',
            weakness: 'No unified view, integration hell',
            yourEdge: 'One system, one source of truth',
        },
    ],
    direct: [
        {
            name: 'HubSpot',
            positioning: 'All-in-one CRM platform',
            weakness: 'Generic, overwhelming for small teams',
            yourEdge: 'Built specifically for founders',
            featureOverlap: 'medium',
        },
    ],
};

const mockSoundbites: DerivedSoundbites = {
    oneLiner: 'RaptorFlow turns marketing chaos into a system that actually works.',
    soundbites: [
        {
            type: 'problem',
            awarenessLevel: 'problem',
            text: "You're drowning in marketing tools but still guessing what to do next.",
            useCase: 'Cold outreach opener',
        },
        {
            type: 'agitation',
            awarenessLevel: 'problem',
            text: 'Every week you spend in chaos, your competitors with systems pull further ahead.',
            useCase: 'Follow-up email',
        },
        {
            type: 'mechanism',
            awarenessLevel: 'solution',
            text: 'Our marketing OS turns your context into a 90-day action plan in under 10 minutes.',
            useCase: 'Demo intro',
        },
        {
            type: 'proof',
            awarenessLevel: 'product',
            text: '200+ teams run their entire marketing operation on RaptorFlow.',
            useCase: 'Sales deck',
        },
        {
            type: 'urgency',
            awarenessLevel: 'most',
            text: 'Q1 budget planning starts next month. Get your system ready now.',
            useCase: 'Closing email',
        },
    ],
};

const mockMarket: DerivedMarket = {
    tam: { value: 50_000_000_000, confidence: 'low', method: 'Global marketing software market' },
    sam: { value: 5_000_000_000, confidence: 'med', method: 'SMB marketing automation segment' },
    som: { value: 25_000_000, confidence: 'high', timeline: '3 years' },
    assumptions: [
        { factor: 'Target accounts', value: '50,000', confidence: 'med' },
        { factor: 'Average contract value', value: '$5,000/year', confidence: 'high' },
        { factor: 'Win rate', value: '15%', confidence: 'med' },
    ],
    pathToSom: {
        customersNeeded: 5000,
        leadsPerMonth: 500,
        winRate: 0.15,
        channelMix: [
            { channel: 'LinkedIn', percentage: 40 },
            { channel: 'Content/SEO', percentage: 30 },
            { channel: 'Referrals', percentage: 20 },
            { channel: 'Paid', percentage: 10 },
        ],
    },
    sliderDefaults: {
        targetAccounts: 50000,
        reachablePercent: 20,
        qualifiedPercent: 10,
        adoptionPercent: 15,
        arpa: 5000,
    },
};

export default function RevealTestPage() {
    const router = useRouter();
    const [stage, setStage] = useState<'icps' | 'positioning' | 'competitors' | 'messaging' | 'market'>('icps');

    const handleContinue = () => {
        switch (stage) {
            case 'icps': setStage('positioning'); break;
            case 'positioning': setStage('competitors'); break;
            case 'competitors': setStage('messaging'); break;
            case 'messaging': setStage('market'); break;
            case 'market':
                toast.success('Foundation Complete!', { description: 'Reveal flow finished.' });
                router.push('/dashboard');
                break;
        }
    };

    switch (stage) {
        case 'icps':
            return <ICPRevealScreen icps={mockICPs} onContinue={handleContinue} />;
        case 'positioning':
            return <PositioningRevealScreen positioning={mockPositioning} onContinue={handleContinue} />;
        case 'competitors':
            return <CompetitorsRevealScreen competitive={mockCompetitive} onContinue={handleContinue} />;
        case 'messaging':
            return <MessagingRevealScreen soundbites={mockSoundbites} onContinue={handleContinue} />;
        case 'market':
            return <MarketRevealScreen market={mockMarket} onComplete={handleContinue} />;
    }
}
