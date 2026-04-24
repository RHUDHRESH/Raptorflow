import { prisma } from "@raptorflow/database";
import { converseStrategist } from "@/lib/bedrock";
import { ingestRipple } from "@/lib/prl/ingest";
import { updateEgoStateFromSession } from "@/lib/eel/egoState";
import { harnessPrompt } from "@/lib/harness/buildPrompt";
import { broadcast, channels } from "@/lib/pusher/server";
import { generateNudges } from "@/lib/nudges/generateNudges";

export interface SynthesisResult {
  verdict: string;
  rationale: string;
  immediate_actions: string[];
  watch_outs: string[];
  dissenting_view: string;
}

function parseSynthesis(text: string): SynthesisResult {
  const trimmed = text.trim();
  const jsonStr = trimmed.startsWith("```")
    ? trimmed.replace(/^```json\n?/, "").replace(/\n?```$/, "")
    : trimmed;
  return JSON.parse(jsonStr) as SynthesisResult;
}

export async function synthesizeSession(sessionId: string, token: string): Promise<void> {
  const session = await prisma.councilSession.findUnique({
    where: { id: sessionId },
    include: { positions: { orderBy: { createdAt: "asc" } } },
  });
  if (!session) throw new Error(`Session ${sessionId} not found`);

  const question = session.context ?? "What is the best strategic move for this company?";

  const positionsText = session.positions
    .sort((a, b) => b.confidence - a.confidence)
    .map(
      (p) =>
        `--- ${p.avatarName} (${p.avatarRole}) [confidence: ${p.confidence.toFixed(2)}]\n${p.position}`,
    )
    .join("\n\n");

  const taskPrompt = `Topic debated: ${question}

COUNCIL POSITIONS:
${positionsText}

Synthesize into a JSON object with:
"verdict", "rationale", "immediate_actions", "watch_outs", "dissenting_view"
Return only valid JSON.`;

  const { prompt, meta } = await harnessPrompt(
    {
      userId: session.clerkUserId,
      mode: "strategist",
      query: `${question} strategy recommendation`,
      token,
      scanResult: (session.lastScanResult as Record<string, unknown>) ?? null,
    },
    taskPrompt,
  );
  console.log(`Harness [strategist] meta:`, meta);

  const response = await converseStrategist(prompt, 1024);
  const result = parseSynthesis(response);

  await prisma.councilSession.update({
    where: { id: sessionId },
    data: {
      status: "complete",
      synthesisResult: result as any,
      synthesizedAt: new Date(),
    },
  });

  ingestRipple({
    userId: session.clerkUserId,
    type: "council_complete",
    sourceId: sessionId,
    content: `Council session on "${session.topic}" complete — Verdict: ${result.verdict}. Watch-outs: ${result.watch_outs.join(", ")}`,
  }).catch(console.error);

  broadcast(channels.council(sessionId), "council.complete", {
    sessionId,
    synthesisResult: result,
    synthesizedAt: new Date().toISOString(),
  }).catch(console.error);

  broadcast(channels.user(session.clerkUserId), "council.status.changed", {
    sessionId,
    status: "complete",
  }).catch(console.error);

  for (const position of session.positions) {
    const agreed = (result.rationale ?? "")
      .toLowerCase()
      .includes(position.avatarName.toLowerCase());
    updateEgoStateFromSession({
      userId: session.clerkUserId,
      avatarKey: position.avatarKey,
      strategistAgreed: agreed,
      confidence: position.confidence,
    }).catch(console.error);
  }

  generateNudges(session.clerkUserId).catch(console.error);
}
