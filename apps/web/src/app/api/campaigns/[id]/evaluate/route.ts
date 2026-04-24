import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { evaluateBrief } from "@/lib/campaigns/evaluateBrief";
import { ingestRipple } from "@/lib/prl/ingest";
import { broadcast, channels } from "@/lib/pusher/server";
import { generateNudges } from "@/lib/nudges/generateNudges";

export const dynamic = "force-dynamic";

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id: campaignId } = await params;

  const campaign = await prisma.campaign.findFirst({
    where: { id: campaignId, clerkUserId: userId },
  });
  if (!campaign) return NextResponse.json({ error: "not_found" }, { status: 404 });

  await prisma.campaign.update({
    where: { id: campaignId },
    data: { status: "evaluating" },
  });

  const token = (await authObj.getToken({ template: "backend" })) ?? "";

  let evaluation: Awaited<ReturnType<typeof evaluateBrief>>;
  try {
    evaluation = await evaluateBrief(campaignId, token);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Evaluation failed";
    await prisma.campaign.update({
      where: { id: campaignId },
      data: { status: "draft" },
    });
    return NextResponse.json({ error: message }, { status: 502 });
  }

  ingestRipple({
    userId,
    type: "campaign_evaluated",
    sourceId: campaign.id,
    content: `Campaign "${campaign.title}" evaluated — Score: ${evaluation.score}/10. Strengths: ${evaluation.strengths.join(", ")}. Weaknesses: ${evaluation.weaknesses.join(", ")}. ICP fit: ${evaluation.icp_fit}`,
  }).catch(console.error);

  broadcast(channels.user(userId), "campaign.evaluated", {
    campaignId: campaign.id,
    title: campaign.title,
    score: evaluation.score,
    status: "active",
  }).catch(console.error);

  generateNudges(userId).catch(console.error);

  return NextResponse.json({
    evaluation,
    evaluatedAt: new Date().toISOString(),
  });
}
