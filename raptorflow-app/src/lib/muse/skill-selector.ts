import { IcpMemory } from '@/types/icp-types';

export interface Skill {
  id: string;
  name: string;
  owner: 'system' | 'user';
  intent: 'cold_outreach' | 'nurture' | 'sales' | 'announcement';

  compatiblePains: string[];
  compatibleUrgency: string[];
  compatibleTone: string[];
  compatibleCta: string[];
  incompatibleTraits: string[];

  minIcpConfidence: number;
  baseQualityScore: number;
}

export interface MuseContext {
  intent: string; // 'email', 'social', etc.
  subIntent?: string; // 'cold', 'nurture'
  icp: IcpMemory;
  userSkillInventory?: Skill[];
  systemSkillInventory?: Skill[];
}

export function selectSkill(
  context: MuseContext,
  systemSkills: Skill[]
): Skill {
  // 1. Filter by intent
  const eligibleSkills = systemSkills.filter(
    (s) => s.intent === context.intent
  );

  // If no fit, fallback to a generic safe skill (mocked here as first available or placeholder)
  const safeSkill = eligibleSkills[0] || systemSkills[0];

  if (!context.icp) return safeSkill;

  // 2. Score Skills
  const scored = eligibleSkills.map((skill) => {
    let score = skill.baseQualityScore;

    // Pain Match (+0.15 / -0.20)
    const painMatch = context.icp.pains.primary.some((p) =>
      skill.compatiblePains.includes(p)
    );
    if (painMatch) score += 0.15;
    else if (skill.compatiblePains.length > 0) score -= 0.2; // Penalize if skill targets specific pains but ICP doesn't have them

    // Tone Match (+0.10 / -0.10)
    const toneMatch = context.icp.language.tone.some((t) =>
      skill.compatibleTone.includes(t)
    );
    if (toneMatch) score += 0.1;
    else if (skill.compatibleTone.length > 0) score -= 0.1;

    // Urgency Match (+0.10 / -0.15)
    if (
      context.icp.targeting.urgency &&
      skill.compatibleUrgency.includes(context.icp.targeting.urgency)
    ) {
      score += 0.1;
    } else if (
      skill.compatibleUrgency.includes('now') &&
      context.icp.targeting.urgency === 'someday'
    ) {
      score -= 0.15; // Mismatch
    }

    // CTA Alignment (+0.05 / -0.10)
    const ctaMatch = context.icp.language.ctaStyle.some((c) =>
      skill.compatibleCta.includes(c)
    );
    if (ctaMatch) score += 0.05;

    // Incompatibility Penalty (-0.30)
    // Flatten disqualifiers
    const allDisqualifiers = [...context.icp.targeting.whoNot];
    const conflict = allDisqualifiers.some((d) =>
      skill.incompatibleTraits.includes(d)
    );
    if (conflict) score -= 0.3;

    // Confidence Penalty (-0.25)
    if (context.icp.confidence < skill.minIcpConfidence) {
      score -= 0.25;
    }

    return { skill, score };
  });

  // 3. Sort & Select
  scored.sort((a, b) => b.score - a.score);

  // Debug Log (Development only)
  console.log('--- Skill Selection Logic ---');
  scored.forEach((s) =>
    console.log(`[${s.skill.name}]: ${s.score.toFixed(2)}`)
  );

  // Threshold Check
  const best = scored[0];
  if (best && best.score >= 0.4) {
    return best.skill;
  }

  // Fallback if no skill meets threshold
  return safeSkill;
}
