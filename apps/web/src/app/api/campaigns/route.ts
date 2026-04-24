import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { ingestRipple } from "@/lib/prl/ingest";
import { broadcast, channels } from "@/lib/pusher/server";

export const dynamic = "force-dynamic";

export async function GET(): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const campaigns = await prisma.campaign.findMany({
    where: { clerkUserId: userId },
    orderBy: { createdAt: "desc" },
    include: {
      _count: { select: { moves: true } },
    },
  });

  return NextResponse.json(
    campaigns.map((c) => ({
      id: c.id,
      title: c.title,
      brief: c.brief,
      status: c.status,
      goal: c.goal,
      budget: c.budget,
      timeframe: c.timeframe,
      evaluation_result: c.evaluationResult,
      evaluated_at: c.evaluatedAt?.toISOString() ?? null,
      move_count: c._count.moves,
      created_at: c.createdAt.toISOString(),
      updated_at: c.updatedAt.toISOString(),
    })),
  );
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const body = await request.json().catch(() => null);
  if (!body) return NextResponse.json({ error: "invalid_body" }, { status: 400 });

  const { title, brief, goal, budget, timeframe } = body;

  if (!title || typeof title !== "string" || title.trim().length === 0) {
    return NextResponse.json({ error: "title_required" }, { status: 400 });
  }
  if (!brief || typeof brief !== "string" || brief.trim().length < 20) {
    return NextResponse.json({ error: "brief_min_20_chars" }, { status: 400 });
  }

  const campaign = await prisma.campaign.create({
    data: {
      clerkUserId: userId,
      title: title.trim(),
      brief: brief.trim(),
      goal: goal ?? null,
      budget: budget ?? null,
      timeframe: timeframe ?? null,
      status: "draft",
    },
  });

  ingestRipple({
    userId,
    type: "campaign_created",
    sourceId: campaign.id,
    content: `New campaign created: "${campaign.title}" — Goal: ${campaign.goal ?? "not specified"}. Brief: ${campaign.brief}`,
  }).catch(console.error);

  broadcast(channels.user(userId), "campaign.evaluated", {
    campaignId: campaign.id,
    title: campaign.title,
    status: "draft",
  }).catch(console.error);

  return NextResponse.json(
    {
      id: campaign.id,
      title: campaign.title,
      brief: campaign.brief,
      status: campaign.status,
      goal: campaign.goal,
      budget: campaign.budget,
      timeframe: campaign.timeframe,
      move_count: 0,
      created_at: campaign.createdAt.toISOString(),
    },
    { status: 201 },
  );
}
