import { prisma } from "@raptorflow/database";
import { converseStrategist } from "@/lib/bedrock";
import { harnessPrompt } from "@/lib/harness/buildPrompt";

const RUST_API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080";

export interface EvaluationResult {
  score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  icp_fit: string;
  suggested_goal: string;
  recommended_channels: string[];
  budget_assessment: string;
}

function parseEvaluation(text: string): EvaluationResult {
  const trimmed = text.trim();
  const jsonStr = trimmed.startsWith("```")
    ? trimmed.replace(/^```json\n?/, "").replace(/\n?```$/, "")
    : trimmed;
  return JSON.parse(jsonStr) as EvaluationResult;
}

export async function evaluateBrief(campaignId: string, token: string): Promise<EvaluationResult> {
  const campaign = await prisma.campaign.findUnique({ where: { id: campaignId } });
  if (!campaign) throw new Error(`Campaign ${campaignId} not found`);

  if (!campaign.brief || campaign.brief.trim().length < 20) {
    throw new Error("Brief must be at least 20 characters");
  }

  const pendingSessions = await prisma.councilSession.findMany({
    where: { clerkUserId: campaign.clerkUserId, status: "pending" },
    select: { id: true, lastScanResult: true },
  });

  const lastScanResult =
    pendingSessions.length > 0 && pendingSessions[0].lastScanResult
      ? (pendingSessions[0].lastScanResult as Record<string, unknown>)
      : null;

  const taskPrompt = `Evaluate this campaign brief and return ONLY valid JSON with this exact structure — no markdown, no explanation:
{
  "score": <number 1-10>,
  "summary": "<2 sentences — what this campaign is trying to do and why it matters now>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>"],
  "icp_fit": "<one specific sentence directly referencing the ICP persona name and a concrete ICP detail (e.g. 'Resonates with persona X who cares about Y' or 'Does not address the Z pain point that Persona A cited')>",
  "suggested_goal": "<the single metric this campaign should optimise for, specific and measurable>",
  "recommended_channels": ["<channel 1>", "<channel 2>", "<channel 3>", "<channel 4>"],
  "budget_assessment": "<one sentence — whether the budget is realistic given the goal and channels>"
}

Campaign:
Title: ${campaign.title}
Brief: ${campaign.brief}
Goal: ${campaign.goal ?? "not specified"}
Budget: ${campaign.budget ?? "not specified"}
Timeframe: ${campaign.timeframe ?? "not specified"}`;

  const { prompt, meta } = await harnessPrompt(
    {
      userId: campaign.clerkUserId,
      mode: "evaluation",
      query: `${campaign.title} ${campaign.brief}`,
      token,
      scanResult: lastScanResult,
    },
    taskPrompt,
  );
  console.log(`Harness [evaluation] meta:`, meta);

  const response = await converseStrategist(prompt, 1024);
  const result = parseEvaluation(response);

  await prisma.campaign.update({
    where: { id: campaignId },
    data: {
      evaluationResult: result as any,
      evaluatedAt: new Date(),
      status: "active",
    },
  });

  return result;
}
