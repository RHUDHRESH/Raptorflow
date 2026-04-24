import { prisma } from "@raptorflow/database";
import { getOrInitEgoState } from "./egoState";

export interface EELContextPack {
  avatarName: string;
  sessionCount: number;
  agreementRate: number;
  behaviourDescriptors: string[];
  reflectionGate: string;
}

function describeDimension(
  label: string,
  value: number,
  highLabel: string,
  lowLabel: string,
): string {
  if (value > 0.7) return `${highLabel}`;
  if (value < 0.3) return `${lowLabel}`;
  return `balanced ${label}`;
}

function buildBehaviourDescriptors(state: {
  authority: number;
  empathy: number;
  risk: number;
  creativity: number;
  precision: number;
}): string[] {
  const desc: string[] = [];
  desc.push(
    describeDimension(
      "authority",
      state.authority,
      "Decisive and commanding",
      "Collaborative and deferential",
    ),
  );
  desc.push(
    describeDimension(
      "empathy",
      state.empathy,
      "Highly empathetic to customer pain",
      "Analytical and detached",
    ),
  );
  desc.push(
    describeDimension("risk", state.risk, "Aggressive risk-taker", "Risk-averse and cautious"),
  );
  desc.push(
    describeDimension(
      "creativity",
      state.creativity,
      "Highly creative and unconventional",
      "Conventional and practical",
    ),
  );
  desc.push(
    describeDimension(
      "precision",
      state.precision,
      "Precise and detail-oriented",
      "Big-picture and loose",
    ),
  );
  return desc.filter(Boolean);
}

function buildReflectionGate(
  avatarName: string,
  sessionCount: number,
  agreementRate: number,
): string {
  if (sessionCount === 0) return `This is your first session — stay true to your core perspective.`;
  const pct = (agreementRate * 100).toFixed(0);
  if (agreementRate > 0.7) {
    return `You have been cited positively in ${pct}% of past sessions. The Strategist often agrees with you. Be confident but watch for groupthink.`;
  }
  if (agreementRate > 0.4) {
    return `You've been cited in ${pct}% of past sessions. The Strategist sometimes agrees with you. Your perspective has been both accepted and challenged.`;
  }
  return `You have been cited in only ${pct}% of past sessions. The Strategist often disagrees with you. Double-check your assumptions before going against the grain.`;
}

export async function enrichAvatarContext(
  userId: string,
  avatarKey: string,
): Promise<EELContextPack> {
  const avatar = await prisma.avatar.findUnique({ where: { key: avatarKey } });
  if (!avatar) throw new Error(`Avatar ${avatarKey} not found`);

  const state = await getOrInitEgoState(userId, avatarKey);

  const behaviourDescriptors = buildBehaviourDescriptors({
    authority: state.authority,
    empathy: state.empathy,
    risk: state.risk,
    creativity: state.creativity,
    precision: state.precision,
  });

  const reflectionGate = buildReflectionGate(avatar.name, state.sessionCount, state.agreementRate);

  return {
    avatarName: avatar.name,
    sessionCount: state.sessionCount,
    agreementRate: state.agreementRate,
    behaviourDescriptors,
    reflectionGate,
  };
}
