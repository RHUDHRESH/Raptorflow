'use client';

import { v4 as uuidv4 } from 'uuid';
import {
  Phase1Discovery,
  Phase3Data,
  JTBDForces,
  JTBDJob,
  VPCData,
  VPCPain,
  VPCGain,
  VPCReliever,
  VPCCreator,
  StrategyCanvas,
  CanvasFactor,
  ERRCGrid,
  ERRCItem,
  Claim,
  Differentiator,
  ProofStackEntry,
  PrimaryContext,
  emptyPhase3,
} from './foundation';

// ==========================================
// Phase 3 Derivation Engine
// 8-Step Pipeline: Phase1 → Phase3 Differentiation Blueprint
// ==========================================

/**
 * Step 1: Derive Primary Context
 * "You sell X to Y so they can Z"
 */
function derivePrimaryContext(phase1: Phase1Discovery): PrimaryContext {
  const offerType = phase1.offer?.primaryType || 'solution';
  const offerLabel =
    {
      saas: 'a SaaS platform',
      service: 'a professional service',
      course: 'an educational program',
      marketplace: 'a marketplace',
      app: 'an application',
      hardware: 'a hardware product',
      other: 'a solution',
    }[offerType] || 'a solution';

  const audience =
    phase1.buyerUser?.userRoles?.length > 0
      ? phase1.buyerUser.userRoles.join(', ')
      : 'business leaders';

  const outcome = phase1.success?.win90Days || 'achieve their goals';

  return {
    youSell: offerLabel,
    to: audience,
    soTheyCan: outcome,
  };
}

/**
 * Step 2: Extract JTBD Forces
 * Push/Pull/Anxiety/Habit from Phase1 inputs
 */
function extractJTBDForces(phase1: Phase1Discovery): JTBDForces {
  // Extract jobs from success metrics and origin story
  const jobs: JTBDJob[] = [];

  // Functional job from 90-day win
  if (phase1.success?.win90Days) {
    jobs.push({
      id: uuidv4(),
      type: 'functional',
      statement: phase1.success.win90Days,
      isPrimary: true,
    });
  }

  // Emotional job from origin narrative
  if (phase1.origin?.narrative) {
    const narrative = phase1.origin.narrative;
    if (narrative.length > 20) {
      jobs.push({
        id: uuidv4(),
        type: 'emotional',
        statement: `Feel confident and in control of ${phase1.offer?.primaryType || 'their work'}`,
        isPrimary: false,
      });
    }
  }

  // Extract forces from triggers and current system
  const push: string[] = [];
  const pull: string[] = [];
  const anxiety: string[] = [];
  const habit: string[] = [];

  // Push: from triggers and "what's breaking"
  phase1.triggers?.triggers?.forEach((t) => {
    if (t.type) {
      const triggerLabels: Record<string, string> = {
        hiring: 'Scaling team without systems in place',
        'revenue-drop': 'Revenue declining with no clear fix',
        'growth-plateau': 'Growth has stalled',
        'new-launch': 'New product launch pressure',
        competitor: 'Competitors moving faster',
        'budget-cycle': 'Budget cycle forcing decisions',
        compliance: 'Compliance changes requiring action',
        burnout: 'Team burnout from manual processes',
      };
      push.push(
        triggerLabels[t.type] ||
          t.freeText ||
          'Frustration with current approach'
      );
    }
  });

  // Pull: from success definition
  if (phase1.success?.win12Months) {
    pull.push(phase1.success.win12Months);
  }
  if (phase1.success?.bragMetric) {
    const metricLabels: Record<string, string> = {
      revenue: 'Significantly higher revenue',
      leads: 'More qualified leads',
      cac: 'Lower customer acquisition cost',
      roas: 'Better return on ad spend',
      activation: 'Faster user activation',
      retention: 'Higher customer retention',
      nps: 'Higher customer satisfaction',
      'hours-saved': 'More time for strategic work',
    };
    pull.push(metricLabels[phase1.success.bragMetric] || 'Better outcomes');
  }

  // Habit: from current system artifacts
  phase1.currentSystem?.artifacts?.forEach((artifact) => {
    const habitLabels: Record<string, string> = {
      sheets: 'Already comfortable with spreadsheets',
      excel: 'Excel workflows are familiar',
      notion: 'Team uses Notion for everything',
      hubspot: 'HubSpot is already set up',
      whatsapp: 'Communication happens on WhatsApp',
      slack: 'Slack is the default',
      email: 'Email workflows are established',
      trello: 'Trello boards are in place',
      'in-my-head': "Knowledge lives in founder's head",
    };
    habit.push(habitLabels[artifact] || 'Existing tools feel "good enough"');
  });

  // Anxiety: from tried before failures
  phase1.currentSystem?.triedBefore?.forEach((tried) => {
    if (tried.whatFailed) {
      anxiety.push(`Previous tool failed: "${tried.whatFailed}"`);
    }
  });

  // Default anxieties if none extracted
  if (anxiety.length === 0) {
    anxiety.push('Migration seems risky');
    anxiety.push('Team might not adopt');
  }

  // Switch triggers
  const switchTriggers =
    phase1.triggers?.triggers?.map((t) => t.type || t.freeText || '') || [];

  // Success metrics
  const successMetrics: string[] = [];
  if (phase1.success?.bragMetric) {
    successMetrics.push(phase1.success.bragMetric);
  }

  return {
    jobs,
    strugglingMoments: push.slice(0, 3),
    forces: { push, pull, anxiety, habit },
    switchTriggers: switchTriggers.filter(Boolean),
    successMetrics,
  };
}

/**
 * Step 3: Build Value Proposition Canvas
 */
function buildVPC(phase1: Phase1Discovery, jtbd: JTBDForces): VPCData {
  // Customer Profile: Jobs / Pains / Gains
  const customerJobs = jtbd.jobs.map((j) => j.statement);

  // Pains from push forces and struggling moments
  const pains: VPCPain[] = [...jtbd.forces.push, ...jtbd.strugglingMoments]
    .filter(Boolean)
    .slice(0, 5)
    .map((text, i) => ({
      id: uuidv4(),
      text,
      severity: 5 - i, // Descending severity
    }));

  // Gains from pull forces
  const gains: VPCGain[] = jtbd.forces.pull
    .filter(Boolean)
    .slice(0, 5)
    .map((text, i) => ({
      id: uuidv4(),
      text,
      importance: 5 - i,
    }));

  // Value Map: Pain Relievers / Gain Creators
  const unfair = phase1.offer?.unfairAdvantage;
  const productsServices = [phase1.offer?.primaryType || 'Core solution'];

  // Pain relievers linked to pains
  const painRelievers: VPCReliever[] = pains.slice(0, 3).map((pain) => ({
    id: uuidv4(),
    text: `Addresses: ${pain.text.slice(0, 50)}...`,
    painId: pain.id,
  }));

  // Gain creators linked to gains
  const gainCreators: VPCCreator[] = gains.slice(0, 3).map((gain) => ({
    id: uuidv4(),
    text: `Delivers: ${gain.text.slice(0, 50)}...`,
    gainId: gain.id,
  }));

  // Fit coverage calculation
  const addressedPains = painRelievers.length;
  const totalPains = pains.length || 1;
  const fitScore = Math.round((addressedPains / totalPains) * 100);

  const gaps = pains
    .filter((p) => !painRelievers.some((r) => r.painId === p.id))
    .map((p) => p.text);

  return {
    customerProfile: { jobs: customerJobs, pains, gains },
    valueMap: { productsServices, painRelievers, gainCreators },
    fitCoverage: { score: fitScore, gaps },
  };
}

/**
 * Step 4: Derive Competitive Factors
 */
function deriveCompetitiveFactors(
  phase1: Phase1Discovery,
  vpc: VPCData
): CanvasFactor[] {
  // Default factors for marketing/business tools
  const defaultFactors = [
    { name: 'Setup Time', targetLevel: 4 as const },
    { name: 'Strategic Guidance', targetLevel: 5 as const },
    { name: 'Execution Automation', targetLevel: 4 as const },
    { name: 'Learning Curve', targetLevel: 2 as const },
    { name: 'Price', targetLevel: 3 as const },
    { name: 'Integration Depth', targetLevel: 3 as const },
    { name: 'Proof Tracking', targetLevel: 4 as const },
    { name: 'Customization', targetLevel: 4 as const },
  ];

  // Add factors from VPC pains
  const painBasedFactors = vpc.customerProfile.pains
    .slice(0, 3)
    .map((pain) => ({
      name: pain.text.split(' ').slice(0, 3).join(' '),
      targetLevel: 4 as const,
    }));

  const allFactors = [...defaultFactors, ...painBasedFactors].slice(0, 10);

  return allFactors.map((f) => ({
    id: uuidv4(),
    name: f.name,
    mattersToUs: true,
    targetLevel: f.targetLevel,
  }));
}

/**
 * Step 5: Build Strategy Canvas
 */
function buildStrategyCanvas(
  factors: CanvasFactor[],
  phase1: Phase1Discovery
): StrategyCanvas {
  const n = factors.length;

  // Generate curves (1-5 scale)
  // Status quo: low on most things, high on familiarity
  const statusQuo = factors.map((_, i) => (i === n - 1 ? 2 : 3));

  // Category leader: high on everything (but expensive)
  const categoryLeader = factors.map((_, i) => (i === 4 ? 5 : 4)); // Price is high

  // You current: mid-range
  const youCurrent = factors.map(() => 3);

  // You target: matches factor.targetLevel
  const youTarget = factors.map((f) => f.targetLevel);

  return {
    factors,
    curves: { statusQuo, categoryLeader, youCurrent, youTarget },
    competitorNames: ['DIY/Manual', 'Category Leader'],
  };
}

/**
 * Step 6: Generate ERRC Grid
 */
function generateERRC(canvas: StrategyCanvas): ERRCGrid {
  const factors = canvas.factors;

  // Find factors to eliminate/reduce (where target is lower than current)
  const toReduce = factors.filter((f) => f.targetLevel <= 2);
  const toRaise = factors.filter((f) => f.targetLevel >= 4);

  return {
    eliminate:
      toReduce.length > 0
        ? [
            {
              factor: toReduce[0]?.name || 'Complexity',
              reason: 'Not core to our value proposition',
            },
          ]
        : [{ factor: 'Feature bloat', reason: 'Keep it focused' }],

    reduce: [
      {
        factor: 'Learning Curve',
        reason: 'Founders need speed, not training',
      },
    ],

    raise: toRaise.slice(0, 2).map((f) => ({
      factor: f.name,
      reason: 'Core differentiator',
    })),

    create: [
      {
        factor: 'AI-Driven Strategy',
        reason: 'No competitor offers strategic guidance with execution',
      },
    ],
  };
}

/**
 * Step 7: Generate USP/UVP Claims
 */
function generateClaims(
  jtbd: JTBDForces,
  vpc: VPCData,
  errc: ERRCGrid,
  phase1: Phase1Discovery
): Claim[] {
  const claims: Claim[] = [];

  // Claim 1: Main value proposition
  const primaryJob =
    jtbd.jobs.find((j) => j.isPrimary)?.statement || 'achieve their goals';
  const audience = phase1.buyerUser?.userRoles?.[0] || 'founders';

  claims.push({
    id: uuidv4(),
    audience,
    promise: primaryJob,
    mechanism: phase1.offer?.unfairAdvantage?.howWeWin || 'Our unique approach',
    uniqueness:
      phase1.offer?.unfairAdvantage?.whyCantCopy ||
      'First to market with this blend',
    proof: [],
    proofStrength: 'C',
    riskFlags: [],
    isSpecific: true,
    isUnique: true,
    movesBuyers: true,
  });

  // Claim 2: Speed/efficiency claim
  if (phase1.offer?.timeToValue) {
    const ttvLabels: Record<string, string> = {
      instant: 'Get value in minutes',
      'same-day': 'See results the same day',
      '1-week': 'Transform in one week',
      '2-4-weeks': 'Complete system in weeks',
    };
    claims.push({
      id: uuidv4(),
      audience,
      promise: ttvLabels[phase1.offer.timeToValue] || 'Fast time to value',
      mechanism: 'Pre-built workflows and AI assistance',
      uniqueness: 'Others require weeks of setup',
      proof: [],
      proofStrength: 'D',
      riskFlags: ['Needs demo proof'],
      isSpecific: true,
      isUnique: false,
      movesBuyers: true,
    });
  }

  // Claim 3: From ERRC "Create"
  if (errc.create.length > 0) {
    claims.push({
      id: uuidv4(),
      audience,
      promise: errc.create[0].factor,
      mechanism: errc.create[0].reason,
      uniqueness: 'Category-defining capability',
      proof: [],
      proofStrength: 'D',
      riskFlags: ['New claim - needs validation'],
      isSpecific: true,
      isUnique: true,
      movesBuyers: false,
    });
  }

  return claims;
}

/**
 * Step 8: Build Proof Stack
 */
function buildProofStack(
  claims: Claim[],
  phase1: Phase1Discovery
): ProofStackEntry[] {
  const proofAssets = phase1.proofGuardrails?.proofAssets;
  const availableProof: string[] = [];

  if (proofAssets?.testimonials) availableProof.push('Testimonial');
  if (proofAssets?.caseStudies) availableProof.push('Case Study');
  if (proofAssets?.numbers) availableProof.push('Metrics');
  if (proofAssets?.logos) availableProof.push('Client Logo');
  if (proofAssets?.screenshots) availableProof.push('Screenshot');

  return claims.map((claim) => ({
    claim: claim.promise,
    proof: availableProof.length > 0 ? [availableProof[0]] : [],
    strength: claim.proofStrength,
    confidence: availableProof.length > 0 ? 0.6 : 0.3,
  }));
}

/**
 * Generate Differentiators from Phase1 and ERRC
 */
function generateDifferentiators(
  phase1: Phase1Discovery,
  errc: ERRCGrid
): Differentiator[] {
  const differentiators: Differentiator[] = [];
  const unfair = phase1.offer?.unfairAdvantage;

  if (unfair?.howWeWin) {
    differentiators.push({
      id: uuidv4(),
      capability: unfair.howWeWin,
      mechanism: unfair.whyItMatters || 'Core value driver',
      proof: [],
      status: 'unproven',
    });
  }

  // Add ERRC "Create" items as differentiators
  errc.create.forEach((item) => {
    differentiators.push({
      id: uuidv4(),
      capability: item.factor,
      mechanism: item.reason,
      proof: [],
      status: 'unproven',
    });
  });

  return differentiators;
}

// ==========================================
// Main Derivation Function
// ==========================================

export async function derivePhase3(
  phase1: Phase1Discovery
): Promise<Phase3Data> {
  // Step 1: Primary Context
  const primaryContext = derivePrimaryContext(phase1);
  const primaryContextId = uuidv4();

  // Step 2: JTBD Forces
  const jtbd = extractJTBDForces(phase1);

  // Step 3: VPC
  const vpc = buildVPC(phase1, jtbd);

  // Step 4: Competitive Factors
  const factors = deriveCompetitiveFactors(phase1, vpc);

  // Step 5: Strategy Canvas
  const strategyCanvas = buildStrategyCanvas(factors, phase1);

  // Step 6: ERRC Grid
  const errc = generateERRC(strategyCanvas);

  // Step 7: Claims
  const claims = generateClaims(jtbd, vpc, errc, phase1);

  // Step 8: Proof Stack
  const proofStack = buildProofStack(claims, phase1);

  // Differentiators
  const differentiators = generateDifferentiators(phase1, errc);

  return {
    primaryContextId,
    primaryContext,
    jtbd,
    vpc,
    differentiators,
    strategyCanvas,
    errc,
    claims,
    primaryClaimId: claims[0]?.id || '',
    proofStack,
  };
}

/**
 * Derive Phase3 from old questionnaire format (FoundationData without phase1)
 * This converts the legacy business/target/messaging structure to Phase3
 */
export async function derivePhase3FromQuestionnaire(
  data: any
): Promise<Phase3Data> {
  // Build a mock Phase1Discovery from the old format
  const phase1Mock = {
    offer: {
      primaryType: 'saas' as const,
      unfairAdvantage: {
        howWeWin: data.messaging?.elevatorPitch || 'Unique approach',
        whyItMatters: data.messaging?.problemSolved || 'Core problem addressed',
        whyCantCopy: data.messaging?.brandVoice || 'Our unique voice',
      },
      timeToValue: 'same-day' as const,
    },
    success: {
      win90Days: data.target?.goals?.[0] || 'Achieve their goals',
      win12Months: data.target?.goals?.[1] || 'Long-term success',
      bragMetric: 'revenue' as const,
    },
    buyerUser: {
      userRoles: data.target?.roles || ['Founders', 'Marketers'],
    },
    origin: {
      narrative:
        data.messaging?.problemSolved || 'Building the solution they needed.',
    },
    triggers: {
      triggers: [
        {
          type: 'growth-plateau',
          freeText: data.target?.painPoints?.[0] || 'Growth has stalled',
        },
      ],
    },
    currentSystem: {
      artifacts: ['sheets', 'in-my-head'] as any[],
      triedBefore: [],
    },
    proofGuardrails: {
      proofAssets: {
        testimonials: false,
        caseStudies: false,
        numbers: false,
        logos: false,
        screenshots: true,
      },
    },
  };

  // Use the existing derivePhase3 with the mock data
  return derivePhase3(phase1Mock as any);
}

// Re-export types
export type { Phase3Data };
