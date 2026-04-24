import { prisma } from "@raptorflow/database";

const CLAMP_MIN = 0.1;
const CLAMP_MAX = 0.95;
const DRIFT_RATE = 0.05;

function clamp(v: number): number {
  return Math.max(CLAMP_MIN, Math.min(CLAMP_MAX, v));
}

export async function getOrInitEgoState(
  userId: string,
  avatarKey: string,
): Promise<{
  id: string;
  authority: number;
  empathy: number;
  risk: number;
  creativity: number;
  precision: number;
  sessionCount: number;
  agreementRate: number;
}> {
  const existing = await prisma.avatarEgoState.findUnique({
    where: { userId_avatarKey: { userId, avatarKey } },
  });
  if (existing) return existing;

  const avatar = await prisma.avatar.findUnique({ where: { key: avatarKey } });
  if (!avatar) throw new Error(`Avatar ${avatarKey} not found`);

  const ev = (avatar.egoVector as Record<string, number>) ?? {};

  const state = await prisma.avatarEgoState.create({
    data: {
      userId,
      avatarKey,
      authority: clamp(ev.authority ?? 0.5),
      empathy: clamp(ev.empathy ?? 0.5),
      risk: clamp(ev.risk ?? 0.5),
      creativity: clamp(ev.creativity ?? 0.5),
      precision: clamp(ev.precision ?? 0.5),
      sessionCount: 0,
      agreementRate: 0.5,
    },
  });

  return state;
}

export async function updateEgoStateFromSession(params: {
  userId: string;
  avatarKey: string;
  strategistAgreed: boolean;
  confidence: number;
}): Promise<void> {
  const { userId, avatarKey, strategistAgreed, confidence } = params;

  const current = await prisma.avatarEgoState.findUnique({
    where: { userId_avatarKey: { userId, avatarKey } },
  });
  if (!current) return;

  const delta = strategistAgreed
    ? { risk: 0.02, authority: 0.01 }
    : { risk: -0.02, precision: 0.01 };

  const newRisk = clamp(current.risk + (delta.risk ?? 0));
  const newAuthority = clamp(current.authority + (delta.authority ?? 0));
  const newPrecision = clamp(current.precision + (delta.precision ?? 0));

  const newAgreementRate = 0.8 * current.agreementRate + 0.2 * (strategistAgreed ? 1 : 0);

  await prisma.avatarEgoState.update({
    where: { userId_avatarKey: { userId, avatarKey } },
    data: {
      risk: newRisk,
      authority: newAuthority,
      precision: newPrecision,
      sessionCount: current.sessionCount + 1,
      agreementRate: newAgreementRate,
      lastActiveAt: new Date(),
    },
  });
}

export async function decayEgoStates(userId: string): Promise<{
  processed: number;
  decayed: number;
}> {
  const states = await prisma.avatarEgoState.findMany({
    where: { userId },
  });

  const avatar = await prisma.avatar.findFirst();
  const baseEV = (avatar?.egoVector as Record<string, number>) ?? {
    authority: 0.5,
    empathy: 0.5,
    risk: 0.5,
    creativity: 0.5,
    precision: 0.5,
  };

  for (const state of states) {
    const decayed = {
      authority: state.authority * 0.95 + (baseEV.authority ?? 0.5) * 0.05,
      empathy: state.empathy * 0.95 + (baseEV.empathy ?? 0.5) * 0.05,
      risk: state.risk * 0.95 + (baseEV.risk ?? 0.5) * 0.05,
      creativity: state.creativity * 0.95 + (baseEV.creativity ?? 0.5) * 0.05,
      precision: state.precision * 0.95 + (baseEV.precision ?? 0.5) * 0.05,
    };

    await prisma.avatarEgoState.update({
      where: { id: state.id },
      data: {
        authority: clamp(decayed.authority),
        empathy: clamp(decayed.empathy),
        risk: clamp(decayed.risk),
        creativity: clamp(decayed.creativity),
        precision: clamp(decayed.precision),
      },
    });
  }

  return { processed: states.length, decayed: states.length };
}
