import { prisma } from "@raptorflow/database";
import { broadcast, channels } from "@/lib/pusher/server";

export interface CompetitorAnalysis {
  competitorName: string;
  website: string | null;
  strengths: string[];
  weaknesses: string[];
  messagingThemes: string[];
  targetAudience: string[];
  positioning: string;
  threats: string[];
  opportunities: string[];
}

export async function analyzeCompetitor(
  userId: string,
  competitorName: string,
  website: string | null,
): Promise<CompetitorAnalysis> {
  const analysis: CompetitorAnalysis = {
    competitorName,
    website,
    strengths: [`Clear brand identity for ${competitorName}`],
    weaknesses: [`Potential gap in ${competitorName}'s offering`],
    messagingThemes: ["Product-led growth", "Value proposition focus"],
    targetAudience: ["Mid-market B2B companies"],
    positioning: `Direct competitor in the same market segment`,
    threats: [`${competitorName} is gaining market share`],
    opportunities: [`Differentiation opportunity in underserved segments`],
  };

  const snapshot = await prisma.competitorSnapshot.upsert({
    where: { userId_competitorName: { userId, competitorName } },
    update: {
      snapshot: analysis as any,
      lastAnalyzedAt: new Date(),
    },
    create: {
      userId,
      competitorName,
      website,
      snapshot: analysis as any,
    },
  });

  await prisma.intelSignal.create({
    data: {
      userId,
      type: "competitor_move",
      source: "ai_analysis",
      title: `New competitor analysis: ${competitorName}`,
      summary: `Analyzed ${competitorName} — ${analysis.opportunities[0]}`,
      severity: "medium",
    },
  });

  broadcast(channels.user(userId), "intel.signal", {
    signalId: snapshot.id,
    type: "competitor_move",
    title: `Competitor analysis: ${competitorName}`,
  }).catch(console.error);

  return analysis;
}

export async function createIntelSignal(params: {
  userId: string;
  type: string;
  source: string;
  title: string;
  summary: string;
  detail?: string;
  severity?: string;
  relatedTo?: string;
}): Promise<void> {
  const signal = await prisma.intelSignal.create({
    data: {
      userId: params.userId,
      type: params.type,
      source: params.source,
      title: params.title,
      summary: params.summary,
      detail: params.detail,
      severity: params.severity ?? "medium",
      relatedTo: params.relatedTo,
    },
  });

  broadcast(channels.user(params.userId), "intel.signal", {
    signalId: signal.id,
    type: signal.type,
    title: signal.title,
  }).catch(console.error);
}
