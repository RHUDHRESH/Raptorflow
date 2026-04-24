import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";

export const dynamic = "force-dynamic";

export async function GET(
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

  const moves = await prisma.move.findMany({
    where: { campaignId },
    orderBy: { priority: "asc" },
    include: { tasks: { orderBy: { createdAt: "asc" } } },
  });

  return NextResponse.json(
    moves.map((m) => ({
      id: m.id,
      title: m.title,
      description: m.description,
      channel: m.channel,
      priority: m.priority,
      status: m.status,
      tasks: m.tasks.map((t) => ({
        id: t.id,
        title: t.title,
        description: t.description,
        status: t.status,
        due_date: t.dueDate?.toISOString() ?? null,
      })),
    })),
  );
}

export async function POST(
  request: NextRequest,
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

  const body = await request.json().catch(() => null);
  if (!body) return NextResponse.json({ error: "invalid_body" }, { status: 400 });

  const { title, description, channel, priority } = body;
  if (!title || !channel || priority === undefined) {
    return NextResponse.json({ error: "title_channel_priority_required" }, { status: 400 });
  }

  const move = await prisma.move.create({
    data: {
      campaignId,
      title,
      description: description ?? "",
      channel,
      priority,
      status: "pending",
    },
  });

  return NextResponse.json(
    {
      id: move.id,
      title: move.title,
      description: move.description,
      channel: move.channel,
      priority: move.priority,
      status: move.status,
      tasks: [],
    },
    { status: 201 },
  );
}
