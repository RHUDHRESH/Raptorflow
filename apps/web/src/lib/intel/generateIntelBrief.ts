import { prisma } from "@raptorflow/database";
import { harnessPrompt } from "@/lib/harness/buildPrompt";
import { converseStrategist } from "@/lib/bedrock";
import { createIntelSignal } from "./analyzeCompetitor";

const RUST_API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080";

interface IntelBrief {
  signals: Array<{
    type: string;
    source: string;
    title: string;
    summary: string;
    severity: string;
  }>;
  competitorThreats: string[];
  marketOpportunities: string[];
  recommendedActions: string[];
}

export async function generateIntelBrief(userId: string): Promise<IntelBrief> {
  const [recentSignals, competitorSnapshots, recentRipples] = await Promise.all([
    prisma.intelSignal.findMany({
      where: { userId, createdAt: { gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) } },
      orderBy: { createdAt: "desc" },
      take: 20,
    }),
    prisma.competitorSnapshot.findMany({
      where: { userId },
      orderBy: { lastAnalyzedAt: "desc" },
      take: 5,
    }),
    prisma.ripple.findMany({
      where: { userId, createdAt: { gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) } },
      orderBy: { createdAt: "desc" },
      take: 10,
    }),
  ]);

  const competitorNames =
    competitorSnapshots.map((c: { competitorName: string }) => c.competitorName).join(", ") ||
    "none tracked";

  const activityTypes =
    [...new Set(recentRipples.map((r: { type: string }) => r.type))].join(", ") || "limited";

  const { prompt } = await harnessPrompt(
    { userId, mode: "scan", query: "intel brief competitive analysis market intelligence" },
    `Generate a weekly intel briefing for this company.

Recent activity: ${activityTypes}
Tracked competitors: ${competitorNames}
Recent intel signals: ${recentSignals.length > 0 ? recentSignals.map((s: { title: string }) => s.title).join(", ") : "none"}

Return a JSON object with:
- "signals": array of {type, source, title, summary, severity} — key signals from the last 7 days
- "competitorThreats": string[] (2-3 threats based on competitor analysis)
- "marketOpportunities": string[] (2-3 opportunities identified)
- "recommendedActions": string[] (2-3 specific actions to take this week)

Return only valid JSON.`,
  );

  const response = await converseStrategist(prompt, 1024);

  let brief: IntelBrief;
  try {
    const trimmed = response.trim();
    const jsonStr = trimmed.startsWith("```")
      ? trimmed.replace(/^```json\n?/, "").replace(/\n?```$/, "")
      : trimmed;
    brief = JSON.parse(jsonStr);
  } catch {
    brief = {
      signals: [],
      competitorThreats: ["Monitor competitor activity for market shifts"],
      marketOpportunities: ["Explore underserved segments identified in recent activity"],
      recommendedActions: ["Review competitor snapshots", "Update strategic positioning if needed"],
    };
  }

  for (const signal of brief.signals ?? []) {
    await createIntelSignal({
      userId,
      type: signal.type,
      source: signal.source,
      title: signal.title,
      summary: signal.summary,
      severity: signal.severity,
    });
  }

  return brief;
}
