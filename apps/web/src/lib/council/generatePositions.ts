import { prisma } from "@raptorflow/database";
import { converseStrategist } from "@/lib/bedrock";
import { synthesizeSession } from "./synthesize";
import { assembleContext, formatEELBlock } from "@/lib/harness/index";
import { buildPrompt } from "@/lib/harness/buildPrompt";
import { enrichAvatarContext } from "@/lib/eel/enrich";
import { broadcast, channels } from "@/lib/pusher/server";

const RUST_API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080";

const COUNCIL_AVATAR_KEYS = [
  "brand-guardian",
  "growth-hacker",
  "customer-champion",
  "data-analyst",
  "creative-director",
  "contrarian",
  "market-watcher",
  "operator",
  "revenue-lead",
  "risk-officer",
  "innovator",
  "storyteller",
];

function egoVectorText(ev: Record<string, number>): string {
  return Object.entries(ev)
    .map(([k, v]) => `${k}: ${v}`)
    .join(", ");
}

function buildPositionTask(
  avatar: {
    key: string;
    name: string;
    role: string;
    systemPrompt: string;
    egoVector: Record<string, number>;
  },
  question: string,
  context?: string,
): string {
  return `You are ${avatar.name} — ${avatar.role}.

Your ego vector: ${egoVectorText(avatar.egoVector)}.

CORE DIRECTIVE:
${avatar.systemPrompt}
${context ? `\nHistorical context from memory:\n${context}\n` : ""}

STRATEGIC QUESTION:
${question}

Generate your position on the strategic question above. Be specific, opinionated, and grounded in your avatar's perspective.

Response format:
POSITION: <your detailed position (2-4 sentences)>
Confidence: <a number between 0.1 and 1.0 representing how confident you are>`;
}

function parseConfidence(text: string): number {
  const match = text.match(/Confidence:\s*(0\.\d+|1\.0)/i);
  if (match) return parseFloat(match[1]);
  const numMatch = text.match(/\b(0\.\d+|1\.0)\b/);
  return numMatch ? parseFloat(numMatch[1]) : 0.7;
}

export async function generatePositions(sessionId: string, token: string): Promise<void> {
  const session = await prisma.councilSession.findUnique({ where: { id: sessionId } });
  if (!session) throw new Error(`Session ${sessionId} not found`);

  const [avatars, foundationRes] = await Promise.all([
    prisma.avatar.findMany({ where: { key: { in: COUNCIL_AVATAR_KEYS } } }),
    fetch(`${RUST_API}/api/v1/foundation`, {
      headers: { Authorization: `Bearer ${token}` },
    }),
  ]);

  if (!foundationRes.ok) throw new Error("Failed to fetch foundation");
  const foundationData = await foundationRes.json();
  const foundation: Record<string, unknown> = foundationData.sections ?? {};
  const question = session.context ?? "What is the best strategic move for this company?";

  const ci = (foundation.company_info as any) ?? {};
  const pos = (foundation.positioning as any) ?? {};
  const REQUIRED_FIELDS = [
    { key: "companyName", value: ci.name },
    { key: "missionStatement", value: pos.mission ?? pos.unique_value_proposition },
    { key: "valueProposition", value: pos.unique_value_proposition },
    { key: "targetAudience", value: foundation.target_audience },
  ] as const;
  const missing = REQUIRED_FIELDS.filter((f) => !f.value).map((f) => f.key);
  if (missing.length > 0) {
    await prisma.councilSession.update({
      where: { id: sessionId },
      data: {
        status: "failed",
        errorMessage: `Foundation incomplete — fill in: ${missing.join(", ")} before running a Council session`,
      },
    });
    throw new Error(
      `Foundation incomplete — fill in: ${missing.join(", ")} before running a Council session`,
    );
  }

  await prisma.councilSession.update({
    where: { id: sessionId },
    data: { status: "generating" },
  });

  const sharedPack = await assembleContext({
    userId: session.clerkUserId,
    mode: "council",
    query: question,
    includeEEL: false,
    token,
  });
  console.log(
    `HARNESS [council] shared: foundation:${!!sharedPack.foundationBlock} ` +
      `cortex:${sharedPack.meta.cortexRippleCount} assembled in ${sharedPack.meta.assemblyMs}ms`,
  );

  const results = await Promise.all(
    avatars.map(async (avatar) => {
      try {
        const eelContext = await enrichAvatarContext(session.clerkUserId, avatar.key);
        const eelBlock = formatEELBlock(eelContext);
        console.log(
          `EEL: ${avatar.name} — sessions:${eelContext.sessionCount} ` +
            `agreement:${(eelContext.agreementRate * 100).toFixed(0)}%`,
        );

        const taskPrompt = buildPositionTask(
          {
            key: avatar.key,
            name: avatar.name,
            role: avatar.role,
            systemPrompt: avatar.systemPrompt,
            egoVector: avatar.egoVector as Record<string, number>,
          },
          question,
        );

        const fullPrompt = buildPrompt(sharedPack, `${eelBlock}\n\n${taskPrompt}`);

        const response = await converseStrategist(fullPrompt, 512);
        const positionMatch = response.match(/POSITION:\s*([\s\S]*?)(?=Confidence:|$)/i);
        const position = positionMatch
          ? positionMatch[1].trim()
          : response.replace(/Confidence:\s*0\.\d+/i, "").trim();
        const confidence = parseConfidence(response);
        return { avatar, position, confidence, success: true, error: null };
      } catch (err) {
        return {
          avatar,
          position: "Unable to generate position at this time.",
          confidence: 0.3,
          success: false,
          error: err instanceof Error ? err.message : "Unknown error",
        };
      }
    }),
  );

  let positionsSavedSoFar = 0;
  for (const r of results) {
    const savedPosition = await prisma.councilPosition.create({
      data: {
        sessionId,
        avatarKey: r.avatar.key,
        avatarName: r.avatar.name,
        avatarRole: r.avatar.role,
        position: r.position,
        confidence: r.confidence,
      },
    });
    positionsSavedSoFar++;

    broadcast(channels.council(sessionId), "council.position.added", savedPosition).catch(
      console.error,
    );
    broadcast(channels.user(session.clerkUserId), "council.status.changed", {
      sessionId,
      status: "generating",
      positionCount: positionsSavedSoFar,
    }).catch(console.error);
  }

  await prisma.councilSession.update({
    where: { id: sessionId },
    data: { status: "synthesizing" },
  });

  broadcast(channels.user(session.clerkUserId), "council.status.changed", {
    sessionId,
    status: "synthesizing",
    positionCount: results.length,
  }).catch(console.error);

  setTimeout(() => {
    synthesizeSession(sessionId, token).catch((err) => {
      console.error(`[generatePositions] Synthesis chained failed for ${sessionId}:`, err);
      prisma.councilSession
        .update({
          where: { id: sessionId },
          data: {
            status: "failed",
            errorMessage: err instanceof Error ? err.message : "Synthesis failed",
          },
        })
        .catch(() => {});
    });
  }, 1000);
}
