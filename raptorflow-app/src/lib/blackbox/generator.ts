import {
  Experiment,
  GoalType,
  RiskLevel,
  ChannelType,
  ExperimentStatus,
  BehavioralPrinciple,
  SkillRef,
  AssetPlan,
} from '../blackbox-types';
import {
  LEVERS,
  CONSTRAINTS,
  CHANNEL_DEFAULTS,
  ConstraintTemplate,
} from './templates';

interface GenerationContext {
  goal: GoalType;
  risk_level: RiskLevel;
  channel: ChannelType;
  brand_voice?: string;
  banned_concepts?: string[];
  past_winners?: BehavioralPrinciple[];
}

export function generateExperiments(
  context: GenerationContext,
  count: number = 3
): Experiment[] {
  // 1. Candidate Generation
  // Pick levers that match goal (if restricted) and channel (if restricted)
  let candidates = LEVERS.filter((l) => {
    const goalMatch =
      !l.allowed_goals || l.allowed_goals.includes(context.goal);
    const channelMatch =
      !l.allowed_channels || l.allowed_channels.includes(context.channel);
    return goalMatch && channelMatch;
  });

  // If no channel-specific candidates, fall back to all levers matching goal
  if (candidates.length < count) {
    candidates = LEVERS.filter(
      (l) => !l.allowed_goals || l.allowed_goals.includes(context.goal)
    );
  }

  // 2. Ranking / Scoring (Simplified for v1)
  // Boost score for past winners, penalize past losers (not implemented yet)
  // For now, shuffle randomly
  candidates = candidates.sort(() => Math.random() - 0.5);

  // 3. Selection with Diversity Constraint
  // Must pick 'count' unique levers
  const selectedLevers = candidates.slice(0, count);

  // 4. Construction (Apply Constraints & Skills)
  return selectedLevers.map((lever, index) => {
    const constraint = selectConstraint(context.risk_level);
    const skillStack = generateSkillStack(context.channel);
    const defaults =
      CHANNEL_DEFAULTS[context.channel] || CHANNEL_DEFAULTS.other;

    return {
      id: `exp-${Date.now()}-${index}`,
      goal: context.goal,
      risk_level: context.risk_level,
      channel: context.channel,

      // Content from lever template
      title: lever.title,
      bet: lever.hypothesis,
      why: lever.why,
      principle: lever.principle,

      // NEW: Actionable experiment details
      hypothesis: lever.hypothesis,
      control: lever.control,
      variant: lever.variant,
      success_metric: lever.success_metric,
      sample_size: lever.sample_size,
      duration_days: lever.duration_days,
      action_steps: lever.action_steps,

      // Meta
      effort: defaults.effort,
      time_to_signal: defaults.time_to_signal,

      // Execution
      skill_stack: skillStack,
      asset_ids: [],
      asset_plan: generateAssetPlan(context.channel, constraint),

      status: 'draft' as ExperimentStatus,
      created_at: new Date().toISOString(),
    };
  });
}

function selectConstraint(risk: RiskLevel): ConstraintTemplate {
  // Filter constraints by exact risk match or lower (e.g. spicy can use safe)
  let potential = CONSTRAINTS.filter((c) => c.risk_level === risk);

  // Fallback logic driven by "Risk Budget":
  // Safe -> only safe
  // Spicy -> safe or spicy
  // Unreasonable -> spicy or unreasonable (avoid safe to keep it weird)
  if (risk === 'spicy') {
    potential = [
      ...potential,
      ...CONSTRAINTS.filter((c) => c.risk_level === 'safe'),
    ];
  } else if (risk === 'unreasonable') {
    potential = [
      ...potential,
      ...CONSTRAINTS.filter((c) => c.risk_level === 'spicy'),
    ];
  }

  // Pick random
  return potential[Math.floor(Math.random() * potential.length)];
}

function generateSkillStack(channel: ChannelType): SkillRef[] {
  // Basic v1 stack
  if (channel === 'email') {
    return [
      {
        skill_id: 'hook_curiosity',
        version: '1.0',
        owner: 'system',
        role: 'hook',
      },
      {
        skill_id: 'structure_pas',
        version: '1.0',
        owner: 'system',
        role: 'structure',
      },
      {
        skill_id: 'tone_founder',
        version: '1.0',
        owner: 'system',
        role: 'tone',
      },
      { skill_id: 'cta_soft', version: '1.0', owner: 'system', role: 'cta' },
      {
        skill_id: 'polish_check',
        version: '1.0',
        owner: 'system',
        role: 'edit_polish',
      },
    ];
  }
  // Minimal for others
  return [
    { skill_id: 'hook_generic', version: '1.0', owner: 'system', role: 'hook' },
    { skill_id: 'tone_generic', version: '1.0', owner: 'system', role: 'tone' },
  ];
}

function generateAssetPlan(
  channel: ChannelType,
  constraint: ConstraintTemplate
): AssetPlan {
  const typeMap: Record<ChannelType, AssetPlan['asset_type']> = {
    email: 'email',
    linkedin: 'social_post',
    twitter: 'social_post',
    instagram: 'social_post',
    tiktok: 'social_post',
    youtube: 'text', // script
    facebook: 'social_post',
    google_ads: 'text',
    website: 'text',
    blog: 'text',
    podcast: 'text',
    other: 'text',
  };

  return {
    asset_type: typeMap[channel] || 'text',
    variants: 1,
    target_length: constraint.id === 'short_length' ? 'short' : 'medium',
    notes: `Constraint: ${constraint.description}`,
  };
}
