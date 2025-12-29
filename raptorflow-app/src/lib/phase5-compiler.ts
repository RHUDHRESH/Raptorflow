'use client';

import { v4 as uuidv4 } from 'uuid';
import {
  Phase4Data,
  Phase5Data,
  CandidateSegment,
  ICP,
  ICPFirmographics,
  ICPTechnographics,
  ICPJTBD,
  ICPForcesOfProgress,
  ForceItem,
  BuyingGroup,
  BuyingRole,
  BuyingJob,
  ICPPersona,
  PersonaItem,
  ICPHabitat,
  ICPFitScore,
  InterICPGraph,
  ICPGraphNode,
  ICPGraphEdge,
  emptyPhase5,
} from './foundation';

// ==========================================
// Phase 5 ICP Compiler
// 6-Step Pipeline: Phase4 → ICP Pack
// ==========================================

/**
 * Step A: Generate Candidate Segments (6-12)
 */
function generateCandidateSegments(phase4: Phase4Data): CandidateSegment[] {
  const candidates: CandidateSegment[] = [];
  const alternatives = [
    ...phase4.competitiveAlternatives.statusQuo.map((a) => ({
      name: a.name,
      type: 'statusQuo',
    })),
    ...phase4.competitiveAlternatives.direct.map((a) => ({
      name: a.name,
      type: 'direct',
    })),
    ...phase4.competitiveAlternatives.indirect.map((a) => ({
      name: a.name,
      type: 'indirect',
    })),
  ];

  // Generate segment candidates from phase4 segments
  phase4.targetSegments
    .filter((s) => !s.isExcluded)
    .forEach((segment) => {
      const dominantValue =
        phase4.differentiatedValue.find((v) => v.isDominant)?.value || '';

      alternatives.slice(0, 3).forEach((alt, i) => {
        candidates.push({
          id: uuidv4(),
          label: `${segment.name} (displacing ${alt.name})`,
          displacedAlternative: alt.name,
          dominantValue,
          fitScore: {
            valueFit: segment.scores.pain,
            switchability: 5 - (i % 3), // Varies by alternative
            reachability: segment.scores.triggers,
            dealSize: segment.scores.budget,
            confidence: segment.scores.proofFit,
            total: 0,
          },
          kept: false,
        });
      });
    });

  // Calculate totals
  candidates.forEach((c) => {
    c.fitScore.total = Math.round(
      ((c.fitScore.valueFit +
        c.fitScore.switchability +
        c.fitScore.reachability +
        c.fitScore.dealSize +
        c.fitScore.confidence) /
        5) *
        20
    );
  });

  // Sort by total score and mark top 5 as kept
  candidates.sort((a, b) => b.fitScore.total - a.fitScore.total);
  candidates.slice(0, 5).forEach((c) => (c.kept = true));

  return candidates.slice(0, 12);
}

/**
 * Step B: Score Segments (already computed in Step A)
 */
function scoreSegments(candidates: CandidateSegment[]): CandidateSegment[] {
  return candidates;
}

/**
 * Step C: Convert winners into ICPs
 */
function convertToICPs(
  candidates: CandidateSegment[],
  phase4: Phase4Data
): ICP[] {
  return candidates
    .filter((c) => c.kept)
    .slice(0, 5)
    .map((candidate, index) => {
      const baseSegment = phase4.targetSegments.find((s) =>
        candidate.label.includes(s.name)
      );

      return {
        id: uuidv4(),
        name: candidate.label.split(' (')[0],
        firmographics: buildFirmographics(baseSegment?.firmographics || {}),
        technographics: buildTechnographics(),
        jtbd: buildJTBD(phase4),
        forces: buildForces(phase4),
        triggers: extractTriggers(phase4),
        buyingGroup: buildBuyingGroup(),
        personas: [], // Built in Step D
        habitat: buildHabitat(), // Built in Step E
        objections: phase4.objectionKillshots.map((o) => o.objection),
        fitScore: candidate.fitScore,
        displacedAlternative: candidate.displacedAlternative,
        dominantValue: candidate.dominantValue,
        dataConfidence: {
          proven: [],
          inferred: ['firmographics', 'technographics'],
          assumed: ['buying_group', 'habitats'],
        },
      };
    });
}

function buildFirmographics(base: Record<string, string>): ICPFirmographics {
  return {
    industries: base.industry ? [base.industry] : ['Technology', 'SaaS'],
    excludedIndustries: [],
    companySizeMin: parseInt(base.teamSize?.split('-')[0] || '1'),
    companySizeMax: parseInt(base.teamSize?.split('-')[1] || '50'),
    revenueMin: 0,
    revenueMax: 5000000,
    geographies: ['North America', 'Europe'],
    excludedGeos: [],
  };
}

function buildTechnographics(): ICPTechnographics {
  return {
    mustHave: [],
    niceToHave: ['Slack', 'Google Workspace', 'HubSpot'],
    disqualifiers: ['Enterprise-only stack'],
    unknownStack: true,
  };
}

function buildJTBD(phase4: Phase4Data): ICPJTBD {
  const dominantValue = phase4.differentiatedValue.find((v) => v.isDominant);
  return {
    functional: dominantValue?.value || 'Get marketing under control',
    emotional: 'Feel confident about direction',
    social: 'Be seen as strategic, not chaotic',
  };
}

function buildForces(phase4: Phase4Data): ICPForcesOfProgress {
  // Infer forces from objections and alternatives
  return {
    push: [
      { text: 'Current approach is inconsistent', confidence: 'inferred' },
      { text: 'No clear marketing direction', confidence: 'inferred' },
    ],
    pull: [
      {
        text:
          phase4.differentiatedValue.find((v) => v.isDominant)?.value ||
          'Systematic approach',
        confidence: 'inferred',
      },
    ],
    anxiety: [
      { text: "Another tool that won't stick", confidence: 'assumed' },
      { text: 'Time investment might not pay off', confidence: 'assumed' },
    ],
    habit: [
      { text: 'Already have Notion/spreadsheets', confidence: 'inferred' },
    ],
  };
}

function extractTriggers(phase4: Phase4Data): string[] {
  return [
    'Funding round',
    'Hiring marketing role',
    'Launch coming up',
    'Revenue plateau',
  ];
}

function buildBuyingGroup(): BuyingGroup {
  const roles: BuyingRole[] = [
    {
      id: uuidv4(),
      role: 'Economic Buyer (Founder/CEO)',
      isActive: true,
      influence: 'high',
    },
    {
      id: uuidv4(),
      role: 'Champion (Head of Marketing)',
      isActive: true,
      influence: 'high',
    },
    {
      id: uuidv4(),
      role: 'Primary User (Marketing Manager)',
      isActive: true,
      influence: 'medium',
    },
    {
      id: uuidv4(),
      role: 'Technical Evaluator',
      isActive: false,
      influence: 'low',
    },
    {
      id: uuidv4(),
      role: 'Finance/Procurement',
      isActive: false,
      influence: 'low',
    },
    {
      id: uuidv4(),
      role: 'Blocker (Status Quo Priest)',
      isActive: true,
      influence: 'medium',
    },
  ];

  const buyingJobs: BuyingJob[] = [
    {
      job: 'problem-id',
      primaryRoleId: roles[0].id,
      supportRoleIds: [roles[1].id],
    },
    {
      job: 'solution-explore',
      primaryRoleId: roles[1].id,
      supportRoleIds: [roles[2].id],
    },
    {
      job: 'requirements',
      primaryRoleId: roles[1].id,
      supportRoleIds: [roles[0].id],
    },
    {
      job: 'supplier-select',
      primaryRoleId: roles[0].id,
      supportRoleIds: [roles[1].id],
    },
  ];

  return {
    roles,
    buyingJobs,
    consensusPath: ['Champion', 'Economic Buyer'],
    frictionLevel: 2,
  };
}

function buildHabitat(): ICPHabitat {
  return {
    platforms: ['LinkedIn', 'Twitter/X', 'Indie Hackers', 'Product Hunt'],
    communities: ['Slack communities', 'Discord servers', 'Founder meetups'],
    searchTermsProblem: [
      'how to do marketing as a founder',
      'marketing for startups',
      'marketing strategy template',
    ],
    searchTermsSolution: [
      'marketing automation',
      'positioning tool',
      'marketing OS',
    ],
    contentTypes: ['Case studies', 'Templates', 'Benchmarks', 'How-to guides'],
    triggerMoments: [
      'After funding',
      'Before launch',
      'Revenue plateau',
      'Hiring marketing',
    ],
    trustSources: ['Peer founders', 'Reviews on G2/Capterra', 'Case studies'],
  };
}

/**
 * Step D: Build Persona Stack per ICP
 */
function buildPersonaStack(icps: ICP[]): ICP[] {
  return icps.map((icp) => ({
    ...icp,
    personas: icp.buyingGroup.roles
      .filter((r) => r.isActive)
      .map((role) => buildPersona(role, icp)),
  }));
}

function buildPersona(role: BuyingRole, icp: ICP): ICPPersona {
  const personaTemplates: Record<string, Partial<ICPPersona>> = {
    'Economic Buyer': {
      goals: [
        { text: 'Grow revenue efficiently', confidence: 'inferred' },
        { text: 'Reduce marketing chaos', confidence: 'inferred' },
      ],
      kpis: ['Revenue', 'CAC', 'Marketing ROI'],
      objections: [
        { text: 'Is this worth my time?', confidence: 'assumed' },
        { text: 'Will the team actually use it?', confidence: 'assumed' },
      ],
      proofNeeds: ['ROI calculator', 'Case studies from similar companies'],
      language: ['ROI', 'efficiency', 'system', 'control'],
    },
    Champion: {
      goals: [
        { text: 'Execute marketing effectively', confidence: 'inferred' },
        { text: 'Look strategic to leadership', confidence: 'inferred' },
      ],
      kpis: ['Campaign performance', 'Lead quality', 'Pipeline'],
      objections: [
        { text: 'Do I have time to learn this?', confidence: 'assumed' },
      ],
      proofNeeds: ['Quick start demo', 'Template library'],
      language: ['campaigns', 'leads', 'pipeline', 'content'],
    },
  };

  const template =
    Object.entries(personaTemplates).find(([key]) =>
      role.role.includes(key)
    )?.[1] || {};

  return {
    id: uuidv4(),
    role: role.role,
    goals: template.goals || [
      { text: 'Achieve their objectives', confidence: 'assumed' },
    ],
    kpis: template.kpis || [],
    objections: template.objections || [],
    proofNeeds: template.proofNeeds || [],
    language: template.language || [],
  };
}

/**
 * Step E: Build Habitats (already done in Step C)
 */
function buildHabitats(icps: ICP[]): ICP[] {
  return icps;
}

/**
 * Step F: Build Inter-ICP Relationship Graph
 */
function buildInterICPGraph(icps: ICP[]): InterICPGraph {
  const nodes: ICPGraphNode[] = [
    ...icps.map((icp) => ({
      id: icp.id,
      type: 'icp' as const,
      label: icp.name,
    })),
    // Add influencer nodes
    { id: uuidv4(), type: 'influencer', label: 'Marketing Agencies' },
    { id: uuidv4(), type: 'influencer', label: 'Startup Consultants' },
    { id: uuidv4(), type: 'influencer', label: 'VC/Accelerators' },
  ];

  const edges: ICPGraphEdge[] = [];

  // Connect influencers to ICPs
  const agencyNode = nodes.find((n) => n.label === 'Marketing Agencies');
  const consultantNode = nodes.find((n) => n.label === 'Startup Consultants');

  icps.forEach((icp, i) => {
    // Agencies influence ICPs
    if (agencyNode) {
      edges.push({
        id: uuidv4(),
        from: agencyNode.id,
        to: icp.id,
        type: 'influences',
        weight: 3,
      });
    }

    // ICPs refer each other
    if (i > 0) {
      edges.push({
        id: uuidv4(),
        from: icps[i - 1].id,
        to: icp.id,
        type: 'refers',
        weight: 2,
      });
    }
  });

  return {
    nodes,
    edges,
    primaryWedgeICP: icps[0]?.id || '',
  };
}

// ==========================================
// Main Compiler Function
// ==========================================

export async function compilePhase5(phase4: Phase4Data): Promise<Phase5Data> {
  // Step A: Generate candidates
  let candidateSegments = generateCandidateSegments(phase4);

  // Step B: Score segments
  candidateSegments = scoreSegments(candidateSegments);

  // Step C: Convert to ICPs
  let icps = convertToICPs(candidateSegments, phase4);

  // Step D: Build persona stack
  icps = buildPersonaStack(icps);

  // Step E: Build habitats (already done)
  icps = buildHabitats(icps);

  // Step F: Build inter-ICP graph
  const interICPGraph = buildInterICPGraph(icps);

  return {
    candidateSegments,
    icps,
    interICPGraph,
    version: '1.0',
  };
}

// Re-export types
export type { Phase5Data };
