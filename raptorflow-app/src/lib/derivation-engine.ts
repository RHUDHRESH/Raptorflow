'use client';

import {
    FoundationData,
    DerivedICP,
    DerivedPositioning,
    DerivedCompetitive,
    DerivedSoundbites,
    DerivedMarket,
    DerivedData,
} from './foundation';

// ==========================================
// Compact Objects (Stage 1)
// ==========================================

export interface BusinessSnapshot {
    category: string;
    offerType: string;
    deliveryMode: string;
    priceAnchor: string;
    billingModel: string;
}

export interface BestCustomerSeed {
    description: string;
    whyBest: string;
    successSignals: string[];
}

export interface BuyingSystem {
    buyerRole: string;
    userRole: string;
    triggerEvents: string[];
}

export interface Alternatives {
    currentSolutions: string[];
}

export interface PainMap {
    primary: string;
    secondary: string[];
}

export interface ProofAndConstraints {
    proofArtifacts: string[];
    constraints: string[];
    gtmMotion: string;
    topChannels: string[];
    salesCycleLength: string;
}

export interface CompactObjects {
    businessSnapshot: BusinessSnapshot;
    bestCustomerSeeds: BestCustomerSeed[];
    buyingSystem: BuyingSystem;
    alternatives: Alternatives;
    painMap: PainMap;
    proofAndConstraints: ProofAndConstraints;
}

// ==========================================
// Extract Compact Objects from Foundation
// ==========================================

export function extractCompactObjects(foundation: FoundationData): CompactObjects {
    const { business, cohorts, customerInsights, messaging, proof, goals, reality } = foundation;

    return {
        businessSnapshot: {
            category: business.industry || 'Unknown',
            offerType: business.businessType || 'saas',
            deliveryMode: business.salesMotion || 'hybrid',
            priceAnchor: business.priceBand || 'unknown',
            billingModel: 'subscription', // Default for SaaS
        },
        bestCustomerSeeds: (customerInsights?.bestCustomers || []).map((desc, i) => ({
            description: desc,
            whyBest: `High-value customer ${i + 1}`,
            successSignals: ['Quick onboarding', 'High engagement', 'Referrals'],
        })),
        buyingSystem: {
            buyerRole: cohorts.buyerRole || cohorts.buyerRoleChips?.join(', ') || 'Founder',
            userRole: cohorts.buyerRole || 'End User',
            triggerEvents: customerInsights?.triggerEvents || [],
        },
        alternatives: {
            currentSolutions: customerInsights?.alternatives || [],
        },
        painMap: {
            primary: customerInsights?.painRanking?.[0] || 'Efficiency',
            secondary: customerInsights?.painRanking?.slice(1) || [],
        },
        proofAndConstraints: {
            proofArtifacts: proof?.proofTypes || [],
            constraints: goals?.constraints || [],
            gtmMotion: business.salesMotion || 'hybrid',
            topChannels: reality?.currentChannels || [],
            salesCycleLength: cohorts.salesCycle || '30-60 days',
        },
    };
}

// ==========================================
// Mock Derivation Engine
// ==========================================

export async function deriveFromFoundation(foundation: FoundationData): Promise<DerivedData> {
    const compactObjects = extractCompactObjects(foundation);

    // Simulate AI processing time
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Generate mock derived data based on compact objects
    const icps = generateMockICPs(compactObjects, foundation);
    const positioning = generateMockPositioning(compactObjects, foundation);
    const competitive = generateMockCompetitive(compactObjects, foundation);
    const soundbites = generateMockSoundbites(compactObjects, foundation);
    const market = generateMockMarket(compactObjects, foundation);

    return {
        derivedAt: new Date().toISOString(),
        icps,
        positioning,
        competitive,
        soundbites,
        market,
    };
}

// ==========================================
// Mock Data Generators
// ==========================================

function generateMockICPs(objects: CompactObjects, foundation: FoundationData): DerivedICP[] {
    const { business, cohorts } = foundation;
    const businessName = business.name || 'Your Product';

    return [
        {
            id: 'icp-1',
            name: `Growth-Stage ${cohorts.buyerRoleChips?.[0] || 'Marketing'} Leader`,
            priority: 'primary',
            confidence: 0.85,
            description: `Decision-makers at scaling companies who need ${businessName} to systematize their ${business.industry || 'operations'}.`,
            firmographics: {
                companySize: '50-500 employees',
                industry: [business.industry || 'Technology'],
                geography: cohorts.primaryRegions || ['US', 'EU'],
                budget: '$10k-$50k annually',
            },
            painMap: {
                primary: objects.painMap.primary,
                secondary: objects.painMap.secondary,
                triggers: objects.buyingSystem.triggerEvents.slice(0, 3),
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
                    { role: 'Economic Buyer', focus: 'ROI and budget impact' },
                    { role: 'Technical Evaluator', focus: 'Integration and security' },
                    { role: 'End User', focus: 'Daily usability' },
                ],
                timeline: '60-90 days',
                proofNeeded: ['Case studies', 'ROI calculator', 'Peer references'],
                blockers: ['Budget approval', 'Integration concerns', 'Change management'],
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
            name: `Early-Stage Founder`,
            priority: 'secondary',
            confidence: 0.72,
            description: `Founders building their first marketing engine who need an all-in-one solution.`,
            firmographics: {
                companySize: '1-20 employees',
                industry: [business.industry || 'Startups'],
                geography: cohorts.primaryRegions || ['Global'],
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
                committee: [
                    { role: 'Founder', focus: 'Speed to value' },
                ],
                timeline: '7-14 days',
                proofNeeded: ['Demo', 'Quick wins'],
                blockers: ['Limited budget', 'Time to onboard'],
            },
            behavioral: {
                biases: [
                    { name: 'Optimism Bias', implication: 'Wants to move fast' },
                ],
                deRisking: ['Free tier', 'Self-serve onboarding'],
            },
        },
    ];
}

function generateMockPositioning(objects: CompactObjects, foundation: FoundationData): DerivedPositioning {
    const { business, positioning } = foundation;

    return {
        matrix: {
            xAxis: { label: 'Ease of Use', lowEnd: 'Complex', highEnd: 'Simple' },
            yAxis: { label: 'Depth', lowEnd: 'Surface', highEnd: 'Deep' },
            positions: [
                { name: business.name || 'You', x: 0.8, y: 0.9, isYou: true },
                { name: 'HubSpot', x: 0.6, y: 0.5, isYou: false },
                { name: 'Spreadsheets', x: 0.3, y: 0.2, isYou: false },
                { name: 'Agencies', x: 0.4, y: 0.8, isYou: false },
            ],
        },
        ladder: [
            { rung: 1, name: 'Table Stakes', description: 'Basic functionality', score: 100, isYou: true },
            { rung: 2, name: 'Differentiation', description: positioning.ownedPosition || 'Unique approach', score: 85, isYou: true },
            { rung: 3, name: 'Category Creation', description: 'New mental model', score: 60, isYou: false },
        ],
        statement: {
            forWhom: positioning.targetAudience || 'Growth-stage founders',
            company: business.name || 'Our product',
            category: positioning.category || 'Marketing OS',
            differentiator: positioning.ownedPosition || 'AI-powered decision engine',
            unlikeCompetitor: 'Unlike scattered tools',
            because: 'Because we turn data into decisions',
        },
        oneThing: positioning.ownedPosition || 'The only marketing OS that thinks with you',
        defensibility: 'medium',
    };
}

function generateMockCompetitive(objects: CompactObjects, foundation: FoundationData): DerivedCompetitive {
    return {
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
        direct: objects.alternatives.currentSolutions.slice(0, 3).map((alt) => ({
            name: alt.charAt(0).toUpperCase() + alt.slice(1).replace(/-/g, ' '),
            positioning: 'All-in-one platform',
            weakness: 'Generic, not founder-focused',
            yourEdge: 'Built specifically for your use case',
            featureOverlap: 'medium' as const,
        })),
    };
}

function generateMockSoundbites(objects: CompactObjects, foundation: FoundationData): DerivedSoundbites {
    const { messaging, positioning, business } = foundation;

    return {
        oneLiner: messaging.promisePillar || `${business.name} helps you ${positioning.psychologicalOutcome || 'win'}.`,
        soundbites: [
            {
                type: 'problem',
                awarenessLevel: 'problem',
                text: `You're drowning in ${objects.painMap.primary.toLowerCase()}.`,
                useCase: 'Cold outreach opener',
            },
            {
                type: 'agitation',
                awarenessLevel: 'problem',
                text: `Every week you don't fix this, you're losing ground to competitors who have.`,
                useCase: 'Follow-up email',
            },
            {
                type: 'mechanism',
                awarenessLevel: 'solution',
                text: `Our ${positioning.category || 'system'} turns chaos into clarity in under 5 minutes.`,
                useCase: 'Demo intro',
            },
            {
                type: 'proof',
                awarenessLevel: 'product',
                text: messaging.proofPillar || 'Hundreds of teams already run on this.',
                useCase: 'Sales deck',
            },
            {
                type: 'urgency',
                awarenessLevel: 'most',
                text: `Q1 budget planning starts next month. Get ahead now.`,
                useCase: 'Closing email',
            },
        ],
    };
}

function generateMockMarket(objects: CompactObjects, foundation: FoundationData): DerivedMarket {
    return {
        tam: { value: 5000000000, confidence: 'low', method: 'Global market for category' },
        sam: { value: 500000000, confidence: 'med', method: 'Serviceable segment' },
        som: { value: 25000000, confidence: 'high', timeline: '3 years' },
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
}
