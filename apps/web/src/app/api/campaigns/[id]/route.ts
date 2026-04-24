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

  const { id } = await params;

  const campaign = await prisma.campaign.findFirst({
    where: { id, clerkUserId: userId },
    include: {
      moves: {
        orderBy: { priority: "asc" },
        include: {
          tasks: { orderBy: { createdAt: "asc" } },
        },
      },
    },
  });

  if (!campaign) return NextResponse.json({ error: "not_found" }, { status: 404 });

  return NextResponse.json({
    id: campaign.id,
    title: campaign.title,
    brief: campaign.brief,
    status: campaign.status,
    goal: campaign.goal,
    budget: campaign.budget,
    timeframe: campaign.timeframe,
    evaluation_result: campaign.evaluationResult,
    evaluated_at: campaign.evaluatedAt?.toISOString() ?? null,
    created_at: campaign.createdAt.toISOString(),
    updated_at: campaign.updatedAt.toISOString(),
    moves: campaign.moves.map((m) => ({
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
        created_at: t.createdAt.toISOString(),
      })),
    })),
  });
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id } = await params;

  const existing = await prisma.campaign.findFirst({
    where: { id, clerkUserId: userId },
  });
  if (!existing) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const body = await request.json().catch(() => null);
  if (!body) return NextResponse.json({ error: "invalid_body" }, { status: 400 });

  const { title, brief, status, goal, budget, timeframe } = body;

  const updated = await prisma.campaign.update({
    where: { id },
    data: {
      ...(title !== undefined && { title }),
      ...(brief !== undefined && { brief }),
      ...(status !== undefined && { status }),
      ...(goal !== undefined && { goal }),
      ...(budget !== undefined && { budget }),
      ...(timeframe !== undefined && { timeframe }),
    },
  });

  return NextResponse.json({
    id: updated.id,
    title: updated.title,
    brief: updated.brief,
    status: updated.status,
    goal: updated.goal,
    budget: updated.budget,
    timeframe: updated.timeframe,
    updated_at: updated.updatedAt.toISOString(),
  });
}

export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id } = await params;

  const existing = await prisma.campaign.findFirst({
    where: { id, clerkUserId: userId },
  });
  if (!existing) return NextResponse.json({ error: "not_found" }, { status: 404 });

  await prisma.campaign.delete({ where: { id } });

  return NextResponse.json({ success: true });
}
