'use client';

import { v4 as uuidv4 } from 'uuid';
import {
    Phase5Data,
    Phase6Data,
    MessagingBlueprint,
    MessagingPillar,
    Soundbite,
    SoundbiteType,
    SoundbiteVariants,
    RigorScores,
    RealityCheck,
    CompetitorCheck,
    ProofQualityCheck,
    ConstraintPolicy,
    AwarenessStage,
    BuyingJobType,
    ICP,
    emptyPhase6,
} from './foundation';

// ==========================================
// Phase 6 Soundbite Forge
// 5-Step Pipeline: Phase5 → Messaging Blueprint
// ==========================================

// Vague/empty adjectives to penalize
const VAGUE_WORDS = [
    'powerful', 'seamless', 'innovative', 'cutting-edge', 'best-in-class',
    'world-class', 'revolutionary', 'game-changing', 'next-generation',
    'robust', 'scalable', 'enterprise-grade', 'easy', 'simple', 'fast'
];

// Soundbite type configurations
const SOUNDBITE_CONFIGS: Record<SoundbiteType, {
    awarenessStage: AwarenessStage;
    buyingJob: BuyingJobType;
    template: string;
}> = {
    'problem-reveal': {
        awarenessStage: 'unaware',
        buyingJob: 'problem-id',
        template: "You're experiencing {pain}, and it's costing you {consequence}."
    },
    'agitate': {
        awarenessStage: 'problem',
        buyingJob: 'problem-id',
        template: "If this continues, you'll lose {stakes}."
    },
    'jtbd-progress': {
        awarenessStage: 'solution',
        buyingJob: 'solution-explore',
        template: "You're trying to make progress from {current} to {desired}, without {tradeoff}."
    },
    'mechanism': {
        awarenessStage: 'solution',
        buyingJob: 'solution-explore',
        template: "Unlike {alternative}, we {mechanism} so you get {outcome}."
    },
    'proof-punch': {
        awarenessStage: 'product',
        buyingJob: 'supplier-select',
        template: "Here's the evidence: {proof}."
    },
    'objection-kill': {
        awarenessStage: 'product',
        buyingJob: 'supplier-select',
        template: "You're worried about {objection}. Here's what happens in reality: {response}."
    },
    'action': {
        awarenessStage: 'most',
        buyingJob: 'supplier-select',
        template: "Do {action} next. It takes {time}. You'll see {result} by {timeframe}."
    }
};

/**
 * Step 1: Build Message Spine (hierarchy)
 */
function buildMessageSpine(phase5: Phase5Data): MessagingBlueprint {
    const primaryICP = phase5.icps.find(i => i.id === phase5.interICPGraph.primaryWedgeICP) || phase5.icps[0];

    // Derive controlling idea from dominant value
    const controllingIdea = primaryICP
        ? `Help ${primaryICP.name} ${primaryICP.jtbd.functional} without ${primaryICP.forces.anxiety[0]?.text || 'the usual complexity'}.`
        : 'Marketing under control, finally.';

    // Core message
    const coreMessage = primaryICP
        ? `For ${primaryICP.name}, we deliver ${primaryICP.dominantValue}.`
        : 'The founder marketing operating system.';

    // Build pillars from ICP values and capabilities
    const pillars: MessagingPillar[] = [
        {
            id: uuidv4(),
            name: 'Strategy First',
            proofIds: [],
            isProven: false,
            priority: 1
        },
        {
            id: uuidv4(),
            name: 'Execution Made Simple',
            proofIds: [],
            isProven: false,
            priority: 2
        },
        {
            id: uuidv4(),
            name: 'Evidence-Based Results',
            proofIds: [],
            isProven: false,
            priority: 3
        }
    ];

    // Find missing proof alerts
    const missingProofAlerts = pillars
        .filter(p => !p.isProven)
        .map(p => `Pillar "${p.name}" needs proof`);

    return {
        controllingIdea,
        coreMessage,
        pillars,
        missingProofAlerts
    };
}

/**
 * Step 2: Build Awareness Grid (ICP × Awareness × Buying-Job)
 */
function buildAwarenessGrid(phase5: Phase5Data): Array<{
    icpId: string;
    icpName: string;
    awarenessStage: AwarenessStage;
    buyingJob: BuyingJobType;
}> {
    const grid: Array<{ icpId: string; icpName: string; awarenessStage: AwarenessStage; buyingJob: BuyingJobType }> = [];

    phase5.icps.forEach(icp => {
        // Map each ICP to awareness stages
        const stages: AwarenessStage[] = ['unaware', 'problem', 'solution', 'product', 'most'];
        const jobs: BuyingJobType[] = ['problem-id', 'solution-explore', 'requirements', 'supplier-select'];

        stages.forEach(stage => {
            const job = stage === 'unaware' || stage === 'problem' ? 'problem-id'
                : stage === 'solution' ? 'solution-explore'
                    : 'supplier-select';

            grid.push({
                icpId: icp.id,
                icpName: icp.name,
                awarenessStage: stage,
                buyingJob: job
            });
        });
    });

    return grid;
}

/**
 * Step 3: Generate Candidates per Soundbite Type
 */
function generateCandidates(phase5: Phase5Data): Soundbite[] {
    const soundbites: Soundbite[] = [];
    const primaryICP = phase5.icps[0];

    if (!primaryICP) return soundbites;

    // Generate one soundbite per type
    const types: SoundbiteType[] = [
        'problem-reveal', 'agitate', 'jtbd-progress', 'mechanism',
        'proof-punch', 'objection-kill', 'action'
    ];

    types.forEach(type => {
        const config = SOUNDBITE_CONFIGS[type];
        let text = '';

        switch (type) {
            case 'problem-reveal':
                text = `You're spending 10+ hours a week on marketing that doesn't move the needle, and it's costing you momentum and revenue.`;
                break;
            case 'agitate':
                text = `If this continues, you'll burn through your runway before finding what works, while competitors move faster.`;
                break;
            case 'jtbd-progress':
                text = `You're trying to go from random marketing acts to systematic growth, without hiring an expensive agency or adding headcount.`;
                break;
            case 'mechanism':
                text = `Unlike HubSpot or agencies, we give you the strategy engine + execution system so you get clarity this week, not next quarter.`;
                break;
            case 'proof-punch':
                text = `Founders report saving 10+ hours/week and launching their first campaign in 3 days, not 3 months.`;
                break;
            case 'objection-kill':
                text = `You're worried about another tool that won't stick. Our guided flow means you'll have a complete strategy documented in your first session.`;
                break;
            case 'action':
                text = `Start your Foundation session now. It takes 20 minutes. You'll have your positioning locked by end of day.`;
                break;
        }

        soundbites.push({
            id: uuidv4(),
            type,
            text,
            icpId: primaryICP.id,
            awarenessStage: config.awarenessStage,
            buyingJob: config.buyingJob,
            proofIds: [],
            scores: { specificity: 0, proof: 0, differentiation: 0, awarenessFit: 0, cognitiveLoad: 0, total: 0, passing: false },
            isLocked: false,
            alternatives: []
        });
    });

    return soundbites;
}

/**
 * Step 4: Run 5 Rigor Gates
 */
function runRigorGates(soundbites: Soundbite[]): Soundbite[] {
    return soundbites.map(sb => {
        const scores = scoreRigor(sb);
        return { ...sb, scores };
    });
}

function scoreRigor(soundbite: Soundbite): RigorScores {
    const text = soundbite.text.toLowerCase();

    // Gate A: Specificity - penalize vague words
    const vagueCount = VAGUE_WORDS.filter(w => text.includes(w)).length;
    const hasNumbers = /\d+/.test(text);
    const hasTimeframe = /hour|day|week|month|minute/.test(text);
    const specificity = Math.max(1, 5 - vagueCount + (hasNumbers ? 1 : 0) + (hasTimeframe ? 1 : 0));

    // Gate B: Proof - check for proof markers
    const hasMetric = /\d+%|\d+ hour|\$\d+/.test(text);
    const hasQuote = text.includes('"') || text.includes('report');
    const proof = soundbite.proofIds.length > 0 ? 5 : hasMetric ? 4 : hasQuote ? 3 : 2;

    // Gate C: Differentiation - check for competitor contrast
    const hasContrast = text.includes('unlike') || text.includes('instead of');
    const hasSpecificAlt = /hubspot|agency|spreadsheet|notion/.test(text);
    const differentiation = hasContrast ? 4 : hasSpecificAlt ? 3 : 3;

    // Gate D: Awareness Fit - check stage-appropriate language
    const hasProductDetails = /feature|dashboard|integration|api/.test(text);
    const isUnaware = soundbite.awarenessStage === 'unaware' || soundbite.awarenessStage === 'problem';
    const awarenessFit = (isUnaware && hasProductDetails) ? 2 : 4;

    // Gate E: Cognitive Load - length and complexity
    const wordCount = text.split(' ').length;
    const cognitiveLoad = wordCount < 15 ? 5 : wordCount < 25 ? 4 : wordCount < 40 ? 3 : 2;

    const total = Math.round((specificity + proof + differentiation + awarenessFit + cognitiveLoad) / 5 * 20);
    const passing = total >= 60;

    return {
        specificity: Math.min(5, specificity),
        proof: Math.min(5, proof),
        differentiation: Math.min(5, differentiation),
        awarenessFit: Math.min(5, awarenessFit),
        cognitiveLoad: Math.min(5, cognitiveLoad),
        total,
        passing
    };
}

/**
 * Step 5: Generate Variants
 */
function generateVariants(soundbites: Soundbite[]): SoundbiteVariants[] {
    return soundbites.map(sb => {
        const baseText = sb.text;
        const shortVersion = baseText.split('.')[0] + '.';

        return {
            soundbiteId: sb.id,
            landingHero: baseText,
            subhead: shortVersion,
            adHooks: [
                `🎯 ${shortVersion}`,
                `Stop. ${shortVersion}`,
                shortVersion
            ],
            emailSubjects: [
                shortVersion.slice(0, 50),
                `Quick question: ${shortVersion.slice(0, 40)}`,
                `[New] ${shortVersion.slice(0, 45)}`
            ],
            salesOpener: `I noticed something about your marketing. ${shortVersion}`,
            linkedInOpener: `Talked to 50 founders this month. ${shortVersion}`
        };
    });
}

/**
 * Build Reality Check
 */
function buildRealityCheck(soundbites: Soundbite[]): RealityCheck {
    const competitorChecks: CompetitorCheck[] = soundbites.map(sb => ({
        soundbiteId: sb.id,
        couldSay: sb.scores.differentiation < 4,
        competitor: 'HubSpot',
        reason: sb.scores.differentiation < 4 ? 'Too generic, could be any marketing tool' : 'Specific to our approach'
    }));

    const proofQuality: ProofQualityCheck[] = soundbites.map(sb => ({
        soundbiteId: sb.id,
        quality: sb.scores.proof >= 4 ? 'strong' : sb.scores.proof >= 3 ? 'medium' : 'weak',
        reason: sb.proofIds.length > 0 ? 'Has attached proof' : 'Needs supporting evidence'
    }));

    const awarenessMismatches = soundbites
        .filter(sb => sb.scores.awarenessFit < 3)
        .map(sb => `Soundbite "${sb.type}" may have awareness stage mismatch`);

    const claimsAtRisk = soundbites
        .filter(sb => sb.scores.proof < 3 && sb.type === 'proof-punch')
        .map(sb => `Proof Punch needs actual evidence`);

    return {
        competitorChecks,
        proofQuality,
        awarenessMismatches,
        claimsAtRisk
    };
}

// ==========================================
// Main Forge Function
// ==========================================

export async function forgePhase6(phase5: Phase5Data): Promise<Phase6Data> {
    // Step 1: Build message spine
    const blueprint = buildMessageSpine(phase5);

    // Step 2: Build awareness grid (used internally)
    const awarenessGrid = buildAwarenessGrid(phase5);

    // Step 3: Generate candidates
    let soundbites = generateCandidates(phase5);

    // Step 4: Run rigor gates
    soundbites = runRigorGates(soundbites);

    // Step 5: Generate variants
    const variants = generateVariants(soundbites);

    // Build reality check
    const realityCheck = buildRealityCheck(soundbites);

    // Default constraints
    const constraints: ConstraintPolicy = {
        bannedClaims: [],
        bannedWords: [],
        regulatedFlags: [],
        tonePreference: 'direct'
    };

    return {
        blueprint,
        soundbites,
        variants,
        realityCheck,
        constraints,
        version: '1.0'
    };
}

// Helper for regenerating single soundbite
export function regenerateSoundbite(soundbite: Soundbite, phase5: Phase5Data): Soundbite {
    // Generate new text based on type
    const config = SOUNDBITE_CONFIGS[soundbite.type];
    const primaryICP = phase5.icps[0];

    let newText = soundbite.text + ' (regenerated)';

    const scored: Soundbite = {
        ...soundbite,
        text: newText,
        scores: scoreRigor({ ...soundbite, text: newText })
    };

    return scored;
}

// Re-export types
export type { Phase6Data };
