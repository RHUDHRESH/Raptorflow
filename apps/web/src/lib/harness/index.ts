import { cortexSearch, type CortexResult } from "@/lib/prl/cortex";
import { enrichAvatarContext, type EELContextPack } from "@/lib/eel/enrich";
import { apiFetch } from "@/lib/api";

export type SessionMode = "council" | "strategist" | "muse" | "scan" | "evaluation";

export interface HarnessInput {
  userId: string;
  mode: SessionMode;
  query: string;
  avatarKey?: string;
  includeFoundation?: boolean;
  includeCortex?: boolean;
  includeEEL?: boolean;
  cortexLimit?: number;
  token?: string;
  scanResult?: Record<string, unknown> | null;
}

export interface HarnessContextPack {
  foundationBlock: string;
  cortexBlock: string;
  eelBlock: string;
  contextPrefix: string;
  meta: {
    userId: string;
    mode: SessionMode;
    avatarKey?: string;
    cortexRippleCount: number;
    eelSessionCount?: number;
    eelAgreementRate?: number;
    assemblyMs: number;
  };
}

async function fetchFoundationSections(
  userId: string,
  token: string,
): Promise<Record<string, unknown> | null> {
  try {
    const body = await apiFetch<{ sections?: Record<string, unknown> }>("/api/v1/foundation", {
      auth: true,
      token,
    });
    return body.sections ?? null;
  } catch {
    return null;
  }
}

function formatFoundationBlock(sections: Record<string, unknown>, mode: SessionMode): string {
  const isCompact = mode === "muse";

  const ci = (sections.company_info as any) ?? {};
  const pos = (sections.positioning as any) ?? {};
  const ta = (sections.target_audience as any) ?? {};
  const goals = (sections.goals as any) ?? {};
  const comps = (sections.competitors as any) ?? {};
  const bp = (sections.brand_personality as any) ?? {};

  const companyName = ci.name ?? "the company";
  const companyStage = (sections.company_stage as string) ?? ci.stage ?? "";
  const mission = ci.mission ?? pos.mission ?? "";
  const valueProp = pos.unique_value_proposition ?? "";
  const tagline = pos.tagline ?? "";
  const uvp = pos.unique_value_proposition ?? "";
  const brandVoice =
    (sections.voice_practice as any)?.voice_fingerprint ??
    (bp.traits as string[])?.join(", ") ??
    "";
  const primaryGoal = goals.primary_goal ?? "";
  const budget = (goals.budget as any)?.monthly ?? (goals.budget as any)?.total ?? "";

  const lines = ["=== COMPANY FOUNDATION ==="];
  lines.push(`Company: ${companyName}`);
  if (companyStage) lines.push(`Stage: ${companyStage}`);
  lines.push(`Mission: ${mission || "Not set"}`);
  lines.push(`Value proposition: ${valueProp || "Not set"}`);
  if (tagline) lines.push(`Tagline: ${tagline}`);

  if (!isCompact) {
    if (ta.primary_icp) {
      const icp = ta.primary_icp as Record<string, unknown>;
      const icpName = icp.persona_name ?? icp.name ?? "Unknown";
      const role = icp.role_identity ?? "";
      const goals_list = ((icp.goals ?? icp.key_goals) as string[]) ?? [];
      lines.push(`ICP: ${icpName}${role ? ` (${role})` : ""}`);
      if (goals_list.length) lines.push(`ICP Goals: ${goals_list.slice(0, 3).join("; ")}`);
    }

    const posLines: string[] = [];
    if (pos.mission) posLines.push(`Mission: ${pos.mission}`);
    if (pos.vision) posLines.push(`Vision: ${pos.vision}`);
    if (uvp) posLines.push(`UVP: ${uvp}`);
    if (pos.statement) posLines.push(`Positioning statement: ${pos.statement}`);
    if (posLines.length) lines.push(`Positioning:\n${posLines.join("\n")}`);

    if (comps.direct?.length) {
      const direct = comps.direct.map((c: any) => c.name).join(", ") ?? "none";
      const indirect = comps.indirect?.map((c: any) => c.name).join(", ") ?? "none";
      lines.push(`Competitors: Direct: ${direct}. Indirect: ${indirect}`);
    }

    if (brandVoice) lines.push(`Brand voice: ${brandVoice}`);
    if (primaryGoal) lines.push(`Primary goal: ${primaryGoal}`);
    if (budget) lines.push(`Budget: ${budget}`);
  }

  const lastScanResult = sections._lastScanResult as Record<string, unknown> | undefined;
  if (lastScanResult) {
    lines.push(`Strategic positioning score: ${lastScanResult.positioning_score ?? "?"}/10`);
    const gaps = (lastScanResult.gaps as string[]) ?? [];
    lines.push(`Known gaps: ${gaps.length ? gaps.join(", ") : "none"}`);
  }

  lines.push("=== END FOUNDATION ===");
  return lines.join("\n");
}

function formatCortexBlock(cortex: CortexResult, mode: SessionMode): string {
  if (!cortex.ripples.length) return "";

  const ripples = mode === "muse" ? cortex.ripples.slice(0, 3) : cortex.ripples;

  const lines = [
    "=== MEMORY CONTEXT (most relevant recent activity) ===",
    ...ripples.map(
      (r, i) =>
        `[${i + 1}] ${r.type.replace(/_/g, " ")} (${timeAgo(r.createdAt)}, relevance ${r.score.toFixed(2)}): ${r.content}`,
    ),
    "=== END MEMORY ===",
  ];

  return lines.join("\n");
}

export function formatEELBlock(eel: EELContextPack): string {
  const lines = [
    "=== AVATAR IDENTITY ===",
    `You are ${eel.avatarName}.`,
    `Sessions completed: ${eel.sessionCount}`,
    `Strategist agreement rate: ${(eel.agreementRate * 100).toFixed(0)}%`,
    "",
    "Your current behavioural profile:",
    ...eel.behaviourDescriptors.map((d) => `- ${d}`),
    "",
    eel.reflectionGate,
    "=== END AVATAR IDENTITY ===",
  ];

  return lines.join("\n");
}

function timeAgo(dateStr: string): string {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (seconds < 60) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

function withTimeout<T>(promise: Promise<T>, ms: number, label: string): Promise<T | null> {
  const timeout = new Promise<null>((resolve) =>
    setTimeout(() => {
      console.warn(`HARNESS TIMEOUT: ${label} exceeded ${ms}ms — returning null`);
      resolve(null);
    }, ms),
  );
  return Promise.race([promise, timeout]);
}

export async function assembleContext(input: HarnessInput): Promise<HarnessContextPack> {
  const startMs = Date.now();

  const {
    userId,
    mode,
    query,
    avatarKey,
    includeFoundation = true,
    includeCortex = true,
    includeEEL = true,
    cortexLimit = 5,
    token,
    scanResult,
  } = input;

  const [foundationSections, cortexResult, eelContext] = await Promise.all([
    includeFoundation && token
      ? withTimeout(fetchFoundationSections(userId, token), 1000, "foundation")
      : Promise.resolve(null),
    includeCortex
      ? withTimeout(cortexSearch({ userId, query, limit: cortexLimit }), 1500, "cortex")
      : Promise.resolve(null),
    includeEEL && avatarKey
      ? withTimeout(enrichAvatarContext(userId, avatarKey), 1000, "eel")
      : Promise.resolve(null),
  ]);

  const sectionsForFormat =
    scanResult && foundationSections
      ? { ...foundationSections, _lastScanResult: scanResult }
      : foundationSections;

  const foundationBlock = sectionsForFormat ? formatFoundationBlock(sectionsForFormat, mode) : "";
  const cortexBlock = formatCortexBlock(cortexResult ?? { ripples: [], contextBlock: "" }, mode);
  const eelBlock = eelContext ? formatEELBlock(eelContext) : "";

  const contextPrefix = [foundationBlock, cortexBlock, eelBlock].filter(Boolean).join("\n");

  const assemblyMs = Date.now() - startMs;

  console.log(
    `HARNESS [${mode}${avatarKey ? ":" + avatarKey : ""}] ` +
      `foundation:${!!foundationBlock} cortex:${cortexResult?.ripples.length ?? 0} ` +
      `eel:${!!eelBlock} assembled in ${assemblyMs}ms`,
  );

  if (assemblyMs > 2000) {
    console.warn(`HARNESS SLOW: ${assemblyMs}ms — check CORTEX query performance`);
  }

  return {
    foundationBlock,
    cortexBlock,
    eelBlock,
    contextPrefix,
    meta: {
      userId,
      mode,
      avatarKey,
      cortexRippleCount: cortexResult?.ripples.length ?? 0,
      eelSessionCount: eelContext?.sessionCount,
      eelAgreementRate: eelContext?.agreementRate,
      assemblyMs,
    },
  };
}
