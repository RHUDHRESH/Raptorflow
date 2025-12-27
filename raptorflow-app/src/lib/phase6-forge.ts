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
    // SIGNAL-7 types
    VoCPhrase,
    SB7Spine,
    AwarenessStageContent,
    Signal7Soundbite,
    Signal7Type,
    ProofSlot,
    VoiceSpec,
    ObjectionKiller,
    WebsiteHeroPack,
    AdAngle,
    ChannelAsset,
    QAReport,
    ToneRisk,
} from './foundation';

// ==========================================
// Phase 6 SIGNAL-7 Messaging Factory
// Complete implementation of the SIGNAL-7 algorithm
// ==========================================

// Vague/fluffy words to flag
const FLUFFY_WORDS = [
    'powerful', 'seamless', 'innovative', 'cutting-edge', 'best-in-class',
    'world-class', 'revolutionary', 'game-changing', 'next-generation',
    'robust', 'scalable', 'enterprise-grade', 'easy', 'simple', 'fast',
    'AI-powered', 'leverage', 'synergy', 'holistic', 'end-to-end',
    'state-of-the-art', 'comprehensive', 'mission-critical', 'optimize'
];

// VoC extraction patterns
const VOC_PATTERNS = [
    { regex: /i(?:'m| am) tired of/gi, category: 'tired-of' as const },
    { regex: /we lose time because/gi, category: 'lose-time' as const },
    { regex: /i don(?:'t| not) trust/gi, category: 'dont-trust' as const },
    { regex: /we need/gi, category: 'need' as const },
    { regex: /our customers? (?:always )?say/gi, category: 'general' as const },
];

// SIGNAL-7 soundbite configurations
const SIGNAL7_CONFIGS: Record<Signal7Type, {
    awarenessStage: AwarenessStage;
    purpose: string;
    template: string;
}> = {
    'status-quo-enemy': {
        awarenessStage: 'unaware',
        purpose: 'Show what they\'re currently trapped in',
        template: 'You\'re {status_quo}, and it\'s costing you {consequence}.'
    },
    'problem-agitate': {
        awarenessStage: 'problem',
        purpose: 'PAS: Problem + Agitation',
        template: '{problem}. Every {time}, this means {agitation}. If this continues, {stakes}.'
    },
    'outcome': {
        awarenessStage: 'solution',
        purpose: 'Tangible + time-bound result',
        template: 'Go from {before} to {after} in {timeframe}.'
    },
    'mechanism': {
        awarenessStage: 'solution',
        purpose: 'Your unique way (not "AI-powered" fluff)',
        template: 'Unlike {alternative}, we {mechanism} so you get {benefit}.'
    },
    'objection-kill': {
        awarenessStage: 'product',
        purpose: 'Top objection → Rebuttal',
        template: 'Worried about {objection}? Here\'s what actually happens: {response}.'
    },
    'proof': {
        awarenessStage: 'product',
        purpose: 'Credibility stack',
        template: '{metric}. {testimonial_hint}. {guarantee}.'
    },
    'cta': {
        awarenessStage: 'most',
        purpose: 'One clean action',
        template: '{action} now. {time}. {result}.'
    }
};

// ==========================================
// Step 1: VoC Mining
// ==========================================

function extractVoCPhrases(phase5: Phase5Data): VoCPhrase[] {
    const phrases: VoCPhrase[] = [];
    const primaryICP = phase5.icps[0];
    if (!primaryICP) return phrases;

    // Extract from persona language
    primaryICP.personas.forEach(persona => {
        persona.language.forEach(lang => {
            phrases.push({
                id: uuidv4(),
                text: lang,
                source: 'extracted',
                category: 'general',
                isLocked: false
            });
        });
    });

    // Extract from push forces (pains)
    primaryICP.forces.push.forEach(force => {
        phrases.push({
            id: uuidv4(),
            text: `I'm tired of ${force.text.toLowerCase()}`,
            source: 'extracted',
            category: 'tired-of',
            isLocked: false
        });
    });

    // Extract from anxiety forces
    primaryICP.forces.anxiety.forEach(force => {
        phrases.push({
            id: uuidv4(),
            text: `I don't trust ${force.text.toLowerCase()}`,
            source: 'extracted',
            category: 'dont-trust',
            isLocked: false
        });
    });

    // Dedupe and limit to top 12
    const seen = new Set<string>();
    return phrases.filter(p => {
        const normalized = p.text.toLowerCase().trim();
        if (seen.has(normalized)) return false;
        seen.add(normalized);
        return true;
    }).slice(0, 12);
}

// ==========================================
// Step 2: SB7 Narrative Spine Builder
// ==========================================

function buildSB7Spine(phase5: Phase5Data): SB7Spine {
    const primaryICP = phase5.icps[0];
    if (!primaryICP) {
        return {
            character: 'Founders and marketing leaders',
            wants: 'systematic marketing growth',
            problemExternal: 'Marketing scattered across tools and channels',
            problemInternal: 'Feeling overwhelmed and unsure what actually works',
            problemPhilosophical: 'You shouldn\'t need an agency to market your own business',
            guide: 'RaptorFlow',
            guideVibe: 'operator',
            plan: ['Complete Foundation', 'Get your Messaging Kit', 'Execute with Moves'],
            ctaDirect: 'Start your Foundation now',
            ctaTransitional: 'See how it works',
            success: 'Marketing finally under control, with proof it works',
            failure: 'More wasted time and budget on random marketing acts',
            narrativeVariant: 'escape-chaos'
        };
    }

    return {
        character: primaryICP.name,
        wants: primaryICP.jtbd.functional,
        problemExternal: primaryICP.forces.push[0]?.text || 'Current tools are fragmented',
        problemInternal: primaryICP.jtbd.emotional,
        problemPhilosophical: `You shouldn\'t need ${primaryICP.displacedAlternative || 'expensive agencies'} to ${primaryICP.jtbd.functional.toLowerCase()}`,
        guide: 'RaptorFlow',
        guideVibe: 'operator',
        plan: ['Complete Foundation', 'Get your Messaging Kit', 'Execute with Moves'],
        ctaDirect: 'Start your Foundation now',
        ctaTransitional: 'See how it works',
        success: primaryICP.dominantValue || 'Marketing under control',
        failure: `More ${primaryICP.forces.push[0]?.text.toLowerCase() || 'wasted time'}`,
        narrativeVariant: 'escape-chaos'
    };
}

// ==========================================
// Step 3: Awareness Ladder Generator
// ==========================================

function buildAwarenessLadder(phase5: Phase5Data): AwarenessStageContent[] {
    const primaryICP = phase5.icps[0];
    const stages: AwarenessStage[] = ['unaware', 'problem', 'solution', 'product', 'most'];

    const stageContent: Record<AwarenessStage, {
        whatTheyThinking: string;
        whatToSay: string;
        whatNotToSay: string;
        sampleLine: string;
    }> = {
        'unaware': {
            whatTheyThinking: 'I\'m busy. Marketing is fine, I think.',
            whatToSay: 'Question the status quo. Reveal hidden costs.',
            whatNotToSay: 'Don\'t pitch features. Don\'t mention your product yet.',
            sampleLine: 'Most founders spend 10+ hours/week on marketing that doesn\'t move the needle.'
        },
        'problem': {
            whatTheyThinking: 'Something is wrong, but I don\'t know what to do.',
            whatToSay: 'Name the problem. Agitate the pain. Show stakes.',
            whatNotToSay: 'Don\'t jump to solutions. Don\'t overwhelm with options.',
            sampleLine: `${primaryICP?.forces.push[0]?.text || 'Marketing chaos'} costs you more than time—it costs momentum.`
        },
        'solution': {
            whatTheyThinking: 'There must be a better way.',
            whatToSay: 'Introduce the category. Explain your mechanism.',
            whatNotToSay: 'Don\'t get into features yet. Focus on approach.',
            sampleLine: 'You need a marketing operating system, not another tool.'
        },
        'product': {
            whatTheyThinking: 'Is this the right one for me?',
            whatToSay: 'Differentiate. Proof. Handle objections.',
            whatNotToSay: 'Don\'t be generic. Every claim needs proof.',
            sampleLine: 'Unlike agencies or point tools, RaptorFlow gives you strategy + execution in one system.'
        },
        'most': {
            whatTheyThinking: 'I\'m ready. What do I do next?',
            whatToSay: 'Clear CTA. Remove friction. Reinforce value.',
            whatNotToSay: 'Don\'t over-explain. They\'re convinced, just close.',
            sampleLine: 'Start your Foundation now. 20 minutes. Positioning locked by end of day.'
        }
    };

    return stages.map((stage, index) => ({
        stage,
        ...stageContent[stage],
        isFocused: stage === 'problem' || stage === 'solution' // Default focus
    }));
}

// ==========================================
// Step 4: SIGNAL-7 Soundbite Generator
// ==========================================

function generateSignal7Soundbites(phase5: Phase5Data, vocPhrases: VoCPhrase[]): Signal7Soundbite[] {
    const primaryICP = phase5.icps[0];
    const soundbites: Signal7Soundbite[] = [];
    const types: Signal7Type[] = [
        'status-quo-enemy', 'problem-agitate', 'outcome', 'mechanism',
        'objection-kill', 'proof', 'cta'
    ];

    types.forEach((type, index) => {
        const config = SIGNAL7_CONFIGS[type];
        let text = '';
        let proofNeeded = '';
        const vocAnchors: string[] = [];

        // Include VoC phrase if available
        if (vocPhrases.length > 0 && index < vocPhrases.length) {
            vocAnchors.push(vocPhrases[index].id);
        }

        switch (type) {
            case 'status-quo-enemy':
                text = primaryICP
                    ? `You're ${primaryICP.forces.habit[0]?.text.toLowerCase() || 'piecing together spreadsheets and tools'}, and it's costing you 10+ hours a week with nothing to show for it.`
                    : 'You\'re spending 10+ hours a week on marketing that doesn\'t move the needle, and it\'s costing you momentum and revenue.';
                proofNeeded = 'Time study or founder survey';
                break;

            case 'problem-agitate':
                text = primaryICP
                    ? `${primaryICP.forces.push[0]?.text || 'Random marketing acts'}. Every week, this means more wasted budget and lost opportunities. If this continues, you'll burn through your runway before finding what actually works.`
                    : 'Marketing chaos costs more than time. Every month of scattered efforts means lost revenue and burned credibility. If this continues, competitors moving systematically will leave you behind.';
                proofNeeded = 'Case story or metric';
                break;

            case 'outcome':
                text = primaryICP
                    ? `Go from guessing what to post to having a complete marketing system—in one week, not one quarter.`
                    : 'Go from marketing chaos to complete clarity in 7 days, not 90.';
                proofNeeded = 'Implementation timeline proof';
                break;

            case 'mechanism':
                text = primaryICP
                    ? `Unlike ${primaryICP.displacedAlternative || 'agencies or point tools'}, we give you the strategy engine + execution system so you get clarity this week, not next quarter.`
                    : 'Unlike HubSpot or agencies, we give you positioning + messaging + execution in one guided flow—so you get clarity this week, not next quarter.';
                proofNeeded = 'Mechanism demo or explainer';
                break;

            case 'objection-kill':
                text = primaryICP
                    ? `Worried about ${primaryICP.objections[0]?.toLowerCase() || 'another tool that won\'t stick'}? Our guided flow means you'll have a complete strategy documented in your first session.`
                    : 'Worried about another tool that won\'t stick? Our guided flow means you\'ll have a complete strategy documented in your first 20-minute session.';
                proofNeeded = 'Completion rate or time-to-value metric';
                break;

            case 'proof':
                text = 'Founders report saving 10+ hours/week. First campaign live in 3 days, not 3 months. If it doesn\'t work, we\'ll refund your first month.';
                proofNeeded = 'Testimonial, metric, guarantee';
                break;

            case 'cta':
                text = 'Start your Foundation session now. It takes 20 minutes. You\'ll have your positioning locked by end of day.';
                proofNeeded = 'None required';
                break;
        }

        const scores = scoreRigor(text, type, vocAnchors.length > 0);

        soundbites.push({
            id: uuidv4(),
            type,
            text,
            purpose: config.purpose,
            awarenessStage: config.awarenessStage,
            proofNeeded,
            evidenceUsed: [],
            vocAnchors,
            punchLevel: 3, // Default: balanced
            scores,
            isLocked: false
        });
    });

    return soundbites;
}

// ==========================================
// Step 5: Rigor Gate Scoring
// ==========================================

function scoreRigor(text: string, type: Signal7Type, hasVoC: boolean): RigorScores {
    const lowerText = text.toLowerCase();

    // Gate A: Specificity - penalize vague words, reward numbers/timeframes
    const fluffCount = FLUFFY_WORDS.filter(w => lowerText.includes(w)).length;
    const hasNumbers = /\d+/.test(text);
    const hasTimeframe = /hour|day|week|month|minute|quarter/.test(lowerText);
    const hasConcreteNoun = /founder|marketer|ceo|tool|spreadsheet|agency|hubspot/.test(lowerText);
    let specificity = Math.min(5, Math.max(1, 4 - fluffCount + (hasNumbers ? 1 : 0) + (hasTimeframe ? 1 : 0)));

    // Gate B: Proof
    const hasMetric = /\d+%|\d+ hour|\$\d+|\d+x/.test(text);
    const hasTestimonial = /report|say|told/.test(lowerText);
    const hasGuarantee = /refund|guarantee|money back|free/.test(lowerText);
    const proof = hasMetric && hasGuarantee ? 5 : hasMetric ? 4 : hasTestimonial ? 3 : 2;

    // Gate C: Differentiation
    const hasContrast = /unlike|instead of|not like|different from/.test(lowerText);
    const hasSpecificAlt = /hubspot|agency|spreadsheet|notion|mailchimp|hootsuite/.test(lowerText);
    const differentiation = hasContrast && hasSpecificAlt ? 5 : hasContrast ? 4 : hasSpecificAlt ? 3 : 2;

    // Gate D: Awareness Fit (based on type)
    const earlyStageTypes: Signal7Type[] = ['status-quo-enemy', 'problem-agitate'];
    const hasProductDetails = /feature|dashboard|integration|api|click|button/.test(lowerText);
    const isEarlyStage = earlyStageTypes.includes(type);
    const awarenessFit = (isEarlyStage && hasProductDetails) ? 2 : 4;

    // Gate E: Cognitive Load
    const wordCount = text.split(' ').length;
    const cognitiveLoad = wordCount < 15 ? 5 : wordCount < 25 ? 4 : wordCount < 40 ? 3 : 2;

    // Bonus for VoC anchoring
    if (hasVoC) {
        specificity = Math.min(5, specificity + 1);
    }

    const total = Math.round(((specificity + proof + differentiation + awarenessFit + cognitiveLoad) / 25) * 100);
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

// ==========================================
// Step 6: Proof Slots Generator
// ==========================================

function buildProofSlots(soundbites: Signal7Soundbite[]): ProofSlot[] {
    return soundbites.map(sb => {
        const hasAnyProof = sb.evidenceUsed.length > 0;
        return {
            soundbiteId: sb.id,
            metricProof: undefined,
            socialProof: undefined,
            mechanismProof: undefined,
            riskReversal: sb.type === 'proof' ? { type: 'guarantee' as const, details: 'Money-back guarantee if not satisfied' } : undefined,
            status: hasAnyProof ? 'green' : sb.scores.proof >= 4 ? 'yellow' : 'red'
        };
    });
}

// ==========================================
// Step 7: Objection Killers
// ==========================================

function buildObjectionKillers(phase5: Phase5Data): ObjectionKiller[] {
    const primaryICP = phase5.icps[0];
    const objections = primaryICP?.objections.slice(0, 3) || [
        'Another tool that won\'t stick',
        'Takes too long to see results',
        'Too expensive for our stage'
    ];

    const rebuttals = [
        'Our guided flow means you\'ll have a complete strategy documented in your first 20-minute session.',
        'You\'ll have your first campaign live in 3 days, not 3 months.',
        'Costs less than one month of a freelancer. ROI visible in week one.'
    ];

    return objections.map((obj, i) => ({
        id: uuidv4(),
        objection: obj,
        rebuttal: rebuttals[i] || 'We address this in your onboarding call.',
        proofAttached: undefined
    }));
}

// ==========================================
// Step 8: Voice Spec Builder
// ==========================================

function buildVoiceSpec(): VoiceSpec {
    return {
        toneDial: 'confident',
        alwaysUse: ['founders', 'clarity', 'momentum', 'system', 'proof'],
        neverUse: ['leverage', 'synergy', 'revolutionary', 'AI-powered', 'seamless'],
        cadenceStyle: 'punchy',
        brandVoiceExamples: [
            'Marketing. Finally under control.',
            'Stop guessing. Start executing.',
            'From chaos to clarity in one week.'
        ]
    };
}

// ==========================================
// Step 9: Asset Packaging
// ==========================================

function buildWebsiteHero(soundbites: Signal7Soundbite[], blueprint: MessagingBlueprint): WebsiteHeroPack {
    const outcomeSoundbite = soundbites.find(s => s.type === 'outcome');
    const mechanismSoundbite = soundbites.find(s => s.type === 'mechanism');
    const ctaSoundbite = soundbites.find(s => s.type === 'cta');

    return {
        headline: blueprint.controllingIdea || 'Marketing. Finally under control.',
        subhead: outcomeSoundbite?.text.split('.')[0] || 'From chaos to clarity in one week.',
        bullets: [
            'Complete positioning in 20 minutes',
            'Messaging kit ready same day',
            'First campaign live in 3 days'
        ],
        cta: 'Start Your Foundation',
        trustLine: 'Trusted by 500+ founders'
    };
}

function buildAdAngles(soundbites: Signal7Soundbite[]): AdAngle[] {
    const angleTypes: Array<{ angle: AdAngle['angle']; soundbiteType: Signal7Type }> = [
        { angle: 'pain', soundbiteType: 'problem-agitate' },
        { angle: 'status-quo-enemy', soundbiteType: 'status-quo-enemy' },
        { angle: 'mechanism', soundbiteType: 'mechanism' },
        { angle: 'outcome', soundbiteType: 'outcome' },
        { angle: 'proof', soundbiteType: 'proof' },
        { angle: 'urgency', soundbiteType: 'cta' }
    ];

    return angleTypes.map(({ angle, soundbiteType }) => {
        const sb = soundbites.find(s => s.type === soundbiteType);
        const text = sb?.text || '';
        const firstSentence = text.split('.')[0] + '.';

        return {
            angle,
            headline: firstSentence,
            body: text
        };
    });
}

function buildChannelAssets(soundbites: Signal7Soundbite[], blueprint: MessagingBlueprint): ChannelAsset[] {
    const outcomeSb = soundbites.find(s => s.type === 'outcome');
    const mechanismSb = soundbites.find(s => s.type === 'mechanism');
    const proofSb = soundbites.find(s => s.type === 'proof');

    return [
        {
            channel: 'linkedin',
            variants: [
                {
                    id: uuidv4(),
                    label: 'Thought Leadership',
                    content: {
                        openingHook: outcomeSb?.text.split('.')[0] + '.' || 'Most founders waste 10+ hours/week on marketing.',
                        body: `${mechanismSb?.text || ''}\n\n${proofSb?.text || ''}`,
                        cta: 'Comment "SYSTEM" and I\'ll send you the framework.'
                    },
                    soundbiteIds: [outcomeSb?.id, mechanismSb?.id, proofSb?.id].filter(Boolean) as string[],
                    awarenessStage: 'solution'
                },
                {
                    id: uuidv4(),
                    label: 'Direct Pitch',
                    content: {
                        openingHook: blueprint.controllingIdea || 'Marketing. Finally under control.',
                        body: 'We built something for founders tired of random marketing acts.',
                        cta: 'Link in comments.'
                    },
                    soundbiteIds: [],
                    awarenessStage: 'product'
                }
            ]
        },
        {
            channel: 'email',
            variants: [
                {
                    id: uuidv4(),
                    label: 'Cold Intro',
                    content: {
                        subject: 'Quick question about your marketing',
                        body: `I noticed you're [observation]. Most founders in your position are spending 10+ hours/week on marketing that doesn't move revenue.\n\nWe built something that fixes this in one week.\n\nWorth a quick look?`,
                        cta: 'Reply "yes" and I\'ll send details'
                    },
                    soundbiteIds: [],
                    awarenessStage: 'unaware'
                },
                {
                    id: uuidv4(),
                    label: 'Follow-up 1',
                    content: {
                        subject: 'Re: marketing question',
                        body: 'Bumping this up. The offer stands: complete marketing system in one week instead of one quarter.\n\nNo agency fees. No 6-month contracts.',
                        cta: 'Interested?'
                    },
                    soundbiteIds: [],
                    awarenessStage: 'problem'
                },
                {
                    id: uuidv4(),
                    label: 'Follow-up 2 (Break-up)',
                    content: {
                        subject: 'Closing the loop',
                        body: 'Haven\'t heard back, so I\'ll assume timing isn\'t right.\n\nIf that changes, the offer stands. We\'ve helped 500+ founders get their marketing under control.',
                        cta: 'Good luck either way.'
                    },
                    soundbiteIds: [],
                    awarenessStage: 'problem'
                }
            ]
        },
        {
            channel: 'deck',
            variants: [
                {
                    id: uuidv4(),
                    label: 'One-liner',
                    content: {
                        headline: blueprint.controllingIdea || 'Marketing. Finally under control.',
                        subhead: 'The founder marketing operating system.'
                    },
                    soundbiteIds: [],
                    awarenessStage: 'product'
                }
            ]
        }
    ];
}

// ==========================================
// Step 10: QA Report Builder
// ==========================================

function buildQAReport(soundbites: Signal7Soundbite[]): QAReport {
    const allText = soundbites.map(s => s.text).join(' ').toLowerCase();

    // Fluff detection
    const fluffyWords = FLUFFY_WORDS
        .filter(word => allText.includes(word))
        .map(word => ({
            word,
            location: soundbites.find(s => s.text.toLowerCase().includes(word))?.type || 'unknown'
        }));

    // Differentiation score (average)
    const diffScores = soundbites.map(s => s.scores.differentiation);
    const avgDiff = diffScores.reduce((a, b) => a + b, 0) / diffScores.length;

    // Claims at risk
    const claimsAtRisk = soundbites
        .filter(s => s.scores.proof < 3 && s.type !== 'cta')
        .map(s => `${s.type}: needs proof`);

    return {
        sevenSecondTestPass: soundbites.filter(s => s.scores.cognitiveLoad >= 4).length >= 4,
        differentiationScore: Math.round(avgDiff * 20),
        fluffyWords,
        claimsAtRisk,
        competitorSimilarity: [] // Would require embeddings for real implementation
    };
}

// ==========================================
// Legacy Builders (for backward compatibility)
// ==========================================

function buildMessageSpine(phase5: Phase5Data): MessagingBlueprint {
    const primaryICP = phase5.icps.find(i => i.id === phase5.interICPGraph.primaryWedgeICP) || phase5.icps[0];

    const controllingIdea = primaryICP
        ? `Help ${primaryICP.name} ${primaryICP.jtbd.functional} without ${primaryICP.forces.anxiety[0]?.text || 'the usual complexity'}.`
        : 'Marketing under control, finally.';

    const coreMessage = primaryICP
        ? `For ${primaryICP.name}, we deliver ${primaryICP.dominantValue}.`
        : 'The founder marketing operating system.';

    const pillars: MessagingPillar[] = [
        { id: uuidv4(), name: 'Strategy First', proofIds: [], isProven: false, priority: 1 },
        { id: uuidv4(), name: 'Execution Made Simple', proofIds: [], isProven: false, priority: 2 },
        { id: uuidv4(), name: 'Evidence-Based Results', proofIds: [], isProven: false, priority: 3 }
    ];

    return {
        controllingIdea,
        coreMessage,
        pillars,
        missingProofAlerts: pillars.filter(p => !p.isProven).map(p => `Pillar "${p.name}" needs proof`)
    };
}

function convertToLegacySoundbites(signal7: Signal7Soundbite[]): Soundbite[] {
    return signal7.map(sb => ({
        id: sb.id,
        type: sb.type.replace(/-/g, '_') as SoundbiteType,
        text: sb.text,
        icpId: '',
        awarenessStage: sb.awarenessStage,
        buyingJob: 'problem-id' as BuyingJobType,
        proofIds: [],
        scores: sb.scores,
        isLocked: sb.isLocked,
        alternatives: []
    }));
}

function generateVariants(soundbites: Soundbite[]): SoundbiteVariants[] {
    return soundbites.map(sb => {
        const shortVersion = sb.text.split('.')[0] + '.';
        return {
            soundbiteId: sb.id,
            landingHero: sb.text,
            subhead: shortVersion,
            adHooks: [`🎯 ${shortVersion}`, `Stop. ${shortVersion}`, shortVersion],
            emailSubjects: [shortVersion.slice(0, 50), `Quick question: ${shortVersion.slice(0, 40)}`],
            salesOpener: `I noticed something about your marketing. ${shortVersion}`,
            linkedInOpener: `Talked to 50 founders this month. ${shortVersion}`
        };
    });
}

function buildRealityCheck(soundbites: Soundbite[]): RealityCheck {
    return {
        competitorChecks: soundbites.map(sb => ({
            soundbiteId: sb.id,
            couldSay: sb.scores.differentiation < 4,
            competitor: 'HubSpot',
            reason: sb.scores.differentiation < 4 ? 'Too generic' : 'Specific to our approach'
        })),
        proofQuality: soundbites.map(sb => ({
            soundbiteId: sb.id,
            quality: sb.scores.proof >= 4 ? 'strong' : sb.scores.proof >= 3 ? 'medium' : 'weak',
            reason: sb.proofIds.length > 0 ? 'Has attached proof' : 'Needs evidence'
        })),
        awarenessMismatches: [],
        claimsAtRisk: []
    };
}

// ==========================================
// Main Forge Function
// ==========================================

export async function forgePhase6(phase5: Phase5Data, toneRisk: ToneRisk = 'balanced'): Promise<Phase6Data> {
    // Step 1: VoC Mining
    const vocPhrases = extractVoCPhrases(phase5);

    // Step 2: SB7 Spine
    const sb7Spine = buildSB7Spine(phase5);

    // Step 3: Awareness Ladder
    const awarenessLadder = buildAwarenessLadder(phase5);

    // Step 4: SIGNAL-7 Soundbites
    const signal7Soundbites = generateSignal7Soundbites(phase5, vocPhrases);

    // Step 5: Proof Slots
    const proofSlots = buildProofSlots(signal7Soundbites);

    // Step 6: Objection Killers
    const objectionKillers = buildObjectionKillers(phase5);

    // Step 7: Voice Spec
    const voiceSpec = buildVoiceSpec();

    // Step 8: Legacy blueprint (for backward compat)
    const blueprint = buildMessageSpine(phase5);

    // Step 9: Assets
    const websiteHero = buildWebsiteHero(signal7Soundbites, blueprint);
    const adAngles = buildAdAngles(signal7Soundbites);
    const channelAssets = buildChannelAssets(signal7Soundbites, blueprint);

    // Step 10: QA Report
    const qaReport = buildQAReport(signal7Soundbites);

    // Legacy soundbites
    const soundbites = convertToLegacySoundbites(signal7Soundbites);
    const variants = generateVariants(soundbites);
    const realityCheck = buildRealityCheck(soundbites);

    const constraints: ConstraintPolicy = {
        bannedClaims: [],
        bannedWords: voiceSpec.neverUse,
        regulatedFlags: [],
        tonePreference: toneRisk === 'aggressive' ? 'aggressive' : toneRisk === 'conservative' ? 'warm' : 'direct'
    };

    return {
        // SIGNAL-7 fields
        snapshotId: uuidv4(),
        toneRisk,
        vocPhrases,
        sb7Spine,
        awarenessLadder,
        signal7Soundbites,
        proofSlots,
        voiceSpec,
        objectionKillers,
        websiteHero,
        adAngles,
        channelAssets,
        qaReport,

        // Legacy fields
        blueprint,
        soundbites,
        variants,
        realityCheck,
        constraints,
        version: '2.0'
    };
}

// Helper for regenerating single soundbite
export function regenerateSoundbite(soundbite: Soundbite, phase5: Phase5Data): Soundbite {
    const newText = soundbite.text + ' (regenerated)';
    return {
        ...soundbite,
        text: newText,
        scores: scoreRigor(newText, 'outcome', false)
    };
}

// Helper for regenerating SIGNAL-7 soundbite
export function regenerateSignal7Soundbite(
    soundbite: Signal7Soundbite,
    phase5: Phase5Data,
    punchLevel: number = 3
): Signal7Soundbite {
    // In a real implementation, this would use AI or more sophisticated templates
    let newText = soundbite.text;

    if (punchLevel > 3) {
        // More punchy: shorter, more direct
        newText = soundbite.text.split('.')[0] + '. Period.';
    } else if (punchLevel < 3) {
        // More precise: add specificity
        newText = soundbite.text.replace(/\d+/g, (match) => String(parseInt(match) * 1.2));
    }

    return {
        ...soundbite,
        text: newText,
        punchLevel,
        scores: scoreRigor(newText, soundbite.type, soundbite.vocAnchors.length > 0)
    };
}

// Re-export types
export type { Phase6Data };
