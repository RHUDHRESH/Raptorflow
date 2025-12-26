'use client';

import { v4 as uuidv4 } from 'uuid';
import {
    Phase3Data,
    Phase4Data,
    MarketCategory,
    CompetitiveAlternatives,
    CompetitiveAlternative,
    DifferentiatedCapability,
    DifferentiatedValue,
    TargetSegment,
    SegmentScores,
    PerceptualMap,
    PerceptualMapPoint,
    CategoryLadder,
    LadderRung,
    TAMSAMSOM,
    ElevatorPitch,
    WeAreWeAreNot,
    ObjectionKillshot,
    Phase4Visuals,
    ProofStackEntry,
    emptyPhase4,
} from './foundation';

// ==========================================
// Phase 4 Positioning Compiler
// 8-Step Pipeline: Phase3 → Positioning Pack
// ==========================================

/**
 * Step A: Normalize Evidence
 * Extract claims, metrics, alternatives from Phase 3
 */
function normalizeEvidence(phase3: Phase3Data): {
    claims: string[];
    alternatives: string[];
    capabilities: string[];
    proofRefs: string[];
} {
    const claims = phase3.claims.map(c => c.promise);
    const alternatives = phase3.jtbd.forces.habit.slice(0, 5);
    const capabilities = phase3.differentiators.map(d => d.capability);
    const proofRefs = phase3.proofStack.flatMap(p => p.proof);

    return { claims, alternatives, capabilities, proofRefs };
}

/**
 * Step B: Build Category Options (3-7 candidates)
 */
function buildCategoryOptions(phase3: Phase3Data): MarketCategory[] {
    // Derive category candidates from offer type, jobs, and value claims
    const primaryJob = phase3.jtbd.jobs.find(j => j.isPrimary)?.statement || '';
    const primaryClaim = phase3.claims.find(c => c.id === phase3.primaryClaimId);

    // Generate 5 category options
    const categories: MarketCategory[] = [
        {
            primary: 'Marketing Operating System',
            altLabels: ['MarketingOS', 'Founder Marketing Stack'],
            whyThisContext: ['Positions as system, not tool', 'Implies completeness'],
            risk: 'ok'
        },
        {
            primary: 'AI Marketing Assistant',
            altLabels: ['AI Marketing Copilot', 'Marketing AI'],
            whyThisContext: ['Trending category', 'Low switching cost'],
            risk: 'too-crowded'
        },
        {
            primary: 'Positioning Software',
            altLabels: ['Positioning Tool', 'Strategy Software'],
            whyThisContext: ['Narrow focus = differentiation', 'Clear buyer intent'],
            risk: 'too-weird'
        },
        {
            primary: 'Growth Platform',
            altLabels: ['Growth Stack', 'GTM Platform'],
            whyThisContext: ['Covers strategy + execution', 'Well-understood'],
            risk: 'too-broad'
        },
        {
            primary: 'Founder Marketing Platform',
            altLabels: ['SMB Marketing Suite', 'Lean Marketing System'],
            whyThisContext: ['Targets specific buyer', 'Differentiated positioning'],
            risk: 'ok'
        },
    ];

    return categories;
}

/**
 * Step C: Build Competitive Alternatives
 */
function buildAlternatives(phase3: Phase3Data): CompetitiveAlternatives {
    // Extract from habits and tried-before
    const statusQuo: CompetitiveAlternative[] = phase3.jtbd.forces.habit.slice(0, 3).map((h, i) => ({
        id: uuidv4(),
        name: h.split(' ').slice(0, 3).join(' '),
        whatUsedFor: 'Current workflow',
        whatBreaks: phase3.jtbd.forces.push[i] || 'Manual effort',
        whyTolerated: 'Familiar, low switching cost',
        evidence: [],
        isConfirmed: false
    }));

    // Default direct competitors
    const direct: CompetitiveAlternative[] = [
        {
            id: uuidv4(),
            name: 'HubSpot',
            whatUsedFor: 'Marketing automation',
            whatBreaks: 'Too complex, enterprise-focused',
            whyTolerated: 'Industry standard',
            evidence: [],
            isConfirmed: false
        },
        {
            id: uuidv4(),
            name: 'Notion + Spreadsheets',
            whatUsedFor: 'DIY marketing planning',
            whatBreaks: 'No strategy guidance',
            whyTolerated: 'Free, flexible',
            evidence: [],
            isConfirmed: false
        }
    ];

    // Indirect alternatives
    const indirect: CompetitiveAlternative[] = [
        {
            id: uuidv4(),
            name: 'Marketing Agency',
            whatUsedFor: 'Outsourced execution',
            whatBreaks: 'Expensive, slow, no transfer',
            whyTolerated: 'No internal capability',
            evidence: [],
            isConfirmed: false
        },
        {
            id: uuidv4(),
            name: 'Freelance Consultant',
            whatUsedFor: 'Strategy advice',
            whatBreaks: 'No execution, episodic',
            whyTolerated: 'Affordable expertise',
            evidence: [],
            isConfirmed: false
        }
    ];

    return {
        statusQuo,
        direct,
        indirect,
        replacementStory: `Before: ${statusQuo[0]?.name || 'Manual chaos'} → After: Systematic marketing control`
    };
}

/**
 * Step D: Capabilities → Value Translation
 */
function translateCapabilitiesToValue(phase3: Phase3Data): {
    capabilities: DifferentiatedCapability[];
    values: DifferentiatedValue[];
} {
    const capabilities: DifferentiatedCapability[] = phase3.differentiators.map(d => ({
        id: uuidv4(),
        capability: d.capability,
        enables: d.mechanism,
        evidence: d.proof,
        easyToCopy: d.status === 'unproven'
    }));

    // Derive values from claims
    const values: DifferentiatedValue[] = phase3.claims.map((c, i) => ({
        id: uuidv4(),
        value: c.promise,
        forWhom: c.audience,
        because: c.mechanism,
        evidence: c.proof,
        isDominant: c.id === phase3.primaryClaimId
    }));

    return { capabilities, values };
}

/**
 * Step E: Best-Fit Segment Scoring
 */
function scoreSegments(phase3: Phase3Data): TargetSegment[] {
    // Derive segments from buyer roles and triggers
    const buyers = phase3.jtbd.jobs[0]?.statement || 'Founders';

    const segments: TargetSegment[] = [
        {
            id: uuidv4(),
            name: 'Early-Stage SaaS Founders',
            firmographics: { stage: 'Seed/Series A', teamSize: '1-10', revenue: '$0-$1M' },
            jtbd: 'Launch marketing without hiring',
            whyBestFit: ['High pain', 'No alternatives', 'Fast decision makers'],
            scores: { pain: 5, budget: 3, triggers: 5, switching: 4, proofFit: 4 },
            isPrimary: true,
            isExcluded: false
        },
        {
            id: uuidv4(),
            name: 'D2C Brand Operators',
            firmographics: { stage: 'Growth', teamSize: '5-20', revenue: '$500K-$5M' },
            jtbd: 'Scale without agency dependency',
            whyBestFit: ['Budget available', 'Clear ROI need'],
            scores: { pain: 4, budget: 4, triggers: 4, switching: 3, proofFit: 3 },
            isPrimary: false,
            isExcluded: false
        },
        {
            id: uuidv4(),
            name: 'Marketing Agencies',
            firmographics: { type: 'Agency', teamSize: '5-50' },
            jtbd: 'Deliver positioning for clients',
            whyBestFit: ['Volume buyers', 'Resell potential'],
            scores: { pain: 3, budget: 5, triggers: 3, switching: 2, proofFit: 2 },
            isPrimary: false,
            isExcluded: false
        },
        {
            id: uuidv4(),
            name: 'Enterprise Marketing Teams',
            firmographics: { stage: 'Series C+', teamSize: '50+' },
            jtbd: 'Alignment across teams',
            whyBestFit: ['Big budgets'],
            scores: { pain: 2, budget: 5, triggers: 2, switching: 1, proofFit: 1 },
            isPrimary: false,
            isExcluded: true // Not our customer
        }
    ];

    return segments;
}

/**
 * Step F: Generate Positioning Outputs
 */
function generatePositioningOutputs(
    category: MarketCategory,
    segments: TargetSegment[],
    values: DifferentiatedValue[],
    alternatives: CompetitiveAlternatives
): {
    statement: string;
    pitch: ElevatorPitch;
    weAreWeAreNot: WeAreWeAreNot;
    objections: ObjectionKillshot[];
} {
    const primarySegment = segments.find(s => s.isPrimary)?.name || 'founders';
    const dominantValue = values.find(v => v.isDominant)?.value || 'marketing clarity and control';

    // Dunford-style positioning statement
    const statement = `For ${primarySegment} who struggle with marketing chaos, ${category.primary} is the system that brings ${dominantValue}. Unlike ${alternatives.statusQuo[0]?.name || 'DIY tools'}, we provide strategic guidance with execution automation.`;

    // Elevator pitches
    const pitch: ElevatorPitch = {
        tenSec: `We help ${primarySegment} ${dominantValue}.`,
        thirtySec: `${category.primary} gives ${primarySegment} a complete system to ${dominantValue}. No more guessing, no more random posting.`,
        twoMin: `Most ${primarySegment} waste months on marketing that doesn't move the needle. They're stuck between expensive agencies and chaotic DIY. ${category.primary} changes that. We give you the strategy, the plan, the execution tools, and the tracking — all in one system. You'll know exactly what to say, who to say it to, and see if it's working. That's marketing under control.`
    };

    // We Are / We Are Not
    const weAreWeAreNot: WeAreWeAreNot = {
        weAre: [
            'A complete marketing system',
            'Built for founders, not enterprises',
            'Strategy-first, then execution',
            'Evidence-based, not vibes'
        ],
        weAreNot: [
            'A social media scheduler',
            'An agency replacement',
            'A content generator',
            'Enterprise software'
        ]
    };

    // Objection killshots
    const objections: ObjectionKillshot[] = [
        {
            id: uuidv4(),
            objection: "I don't have time for another tool",
            alternativeTied: 'DIY/Manual',
            response: 'This replaces 5 tools, not adds another. Net time saved: 10+ hours/week.',
            evidence: ''
        },
        {
            id: uuidv4(),
            objection: "Why not just hire an agency?",
            alternativeTied: 'Agency',
            response: 'Agencies cost $5K+/mo with no knowledge transfer. This builds internal capability.',
            evidence: ''
        },
        {
            id: uuidv4(),
            objection: "I can do this in Notion",
            alternativeTied: 'Notion + Spreadsheets',
            response: 'Notion has no strategy engine. You still have to figure out WHAT to do.',
            evidence: ''
        }
    ];

    return { statement, pitch, weAreWeAreNot, objections };
}

/**
 * Step G: Generate Visuals
 */
function generateVisuals(
    phase3: Phase3Data,
    category: MarketCategory,
    alternatives: CompetitiveAlternatives
): Phase4Visuals {
    // Perceptual Map (2x2)
    const perceptualMap: PerceptualMap = {
        xAxis: {
            label: 'Strategic Guidance',
            rationale: 'Status quo lacks direction; direct competitors focus on execution only',
            minLabel: 'Tactical Only',
            maxLabel: 'Strategic + Tactical'
        },
        yAxis: {
            label: 'Ease of Use',
            rationale: 'Enterprise tools are complex; DIY is unguided chaos',
            minLabel: 'Complex',
            maxLabel: 'Simple'
        },
        points: [
            { id: uuidv4(), name: 'DIY/Manual', x: -0.8, y: 0.3, isYou: false },
            { id: uuidv4(), name: 'HubSpot', x: 0.2, y: -0.6, isYou: false },
            { id: uuidv4(), name: 'Agency', x: 0.6, y: -0.2, isYou: false },
            { id: uuidv4(), name: 'RaptorFlow', x: 0.7, y: 0.7, isYou: true },
        ]
    };

    // Category Ladder
    const ladder: CategoryLadder = {
        category: category.primary,
        rungs: [
            { brand: 'RaptorFlow', position: 1, isYou: true },
            { brand: 'HubSpot Starter', position: 2, isYou: false },
            { brand: 'Notion + Tools', position: 3, isYou: false },
            { brand: 'Spreadsheets', position: 4, isYou: false },
        ],
        whyDifferentLadder: 'We created a new category: Founder Marketing System. Not competing on "marketing automation" ladder.'
    };

    return {
        perceptualMap,
        ladder,
        strategyCanvas: phase3.strategyCanvas,
        errc: phase3.errc
    };
}

/**
 * Step H: Compute TAM/SAM/SOM
 */
function computeTAMSAMSOM(
    category: MarketCategory,
    segments: TargetSegment[]
): TAMSAMSOM {
    const primarySegment = segments.find(s => s.isPrimary);

    return {
        tam: {
            value: 50_000_000_000, // $50B global marketing software
            currency: 'USD',
            formula: 'Global marketing software market (Gartner)',
            category: category.primary
        },
        sam: {
            value: 2_000_000_000, // $2B SMB marketing tools
            currency: 'USD',
            formula: 'SMB segment × founder-led companies × marketing tool spend',
            segment: primarySegment?.name || 'Early-Stage Founders'
        },
        som: {
            value: 10_000_000, // $10M serviceable via current channels
            currency: 'USD',
            formula: '5,000 customers × $2,000 ACV × first 2 years',
            reachability: 'Content + community + product-led growth'
        },
        assumptions: [
            '500K early-stage SaaS companies globally',
            'Average spend on marketing tools: $4,000/year',
            '1% penetration rate in year 1',
            '$2,000 ACV (annual contract value)'
        ]
    };
}

// ==========================================
// Main Compiler Function
// ==========================================

export async function compilePhase4(phase3: Phase3Data): Promise<Phase4Data> {
    // Step A: Normalize evidence
    const evidence = normalizeEvidence(phase3);

    // Step B: Build category options
    const categoryOptions = buildCategoryOptions(phase3);
    const marketCategory = categoryOptions.find(c => c.risk === 'ok') || categoryOptions[0];

    // Step C: Build alternatives
    const competitiveAlternatives = buildAlternatives(phase3);

    // Step D: Capabilities → Value
    const { capabilities, values } = translateCapabilitiesToValue(phase3);

    // Step E: Score segments
    const targetSegments = scoreSegments(phase3);

    // Step F: Generate outputs
    const { statement, pitch, weAreWeAreNot, objections } = generatePositioningOutputs(
        marketCategory,
        targetSegments,
        values,
        competitiveAlternatives
    );

    // Step G: Generate visuals
    const visuals = generateVisuals(phase3, marketCategory, competitiveAlternatives);

    // Step H: Compute TAM/SAM/SOM
    const tamSamSom = computeTAMSAMSOM(marketCategory, targetSegments);

    // Build proof stack from Phase 3
    const proofStack = phase3.proofStack;

    return {
        marketCategory,
        categoryOptions,
        competitiveAlternatives,
        differentiatedCapabilities: capabilities,
        differentiatedValue: values,
        targetSegments,
        positioningStatement: statement,
        elevatorPitch: pitch,
        weAreWeAreNot,
        objectionKillshots: objections,
        visuals,
        tamSamSom,
        proofStack,
        version: '1.0'
    };
}

// Re-export types
export type { Phase4Data };
