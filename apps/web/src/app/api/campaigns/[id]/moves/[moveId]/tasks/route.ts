import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";

export const dynamic = "force-dynamic";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string; moveId: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id: campaignId, moveId } = await params;

  const campaign = await prisma.campaign.findFirst({
    where: { id: campaignId, clerkUserId: userId },
  });
  if (!campaign) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const tasks = await prisma.task.findMany({
    where: { moveId },
    orderBy: { createdAt: "asc" },
  });

  return NextResponse.json(
    tasks.map((t) => ({
      id: t.id,
      title: t.title,
      description: t.description,
      status: t.status,
      due_date: t.dueDate?.toISOString() ?? null,
      created_at: t.createdAt.toISOString(),
    })),
  );
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; moveId: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id: campaignId, moveId } = await params;

  const campaign = await prisma.campaign.findFirst({
    where: { id: campaignId, clerkUserId: userId },
  });
  if (!campaign) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const move = await prisma.move.findFirst({ where: { id: moveId, campaignId } });
  if (!move) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const body = await request.json().catch(() => null);
  if (!body) return NextResponse.json({ error: "invalid_body" }, { status: 400 });

  const { title, description, dueDate } = body;
  if (!title) return NextResponse.json({ error: "title_required" }, { status: 400 });

  const task = await prisma.task.create({
    data: {
      moveId,
      title,
      description: description ?? null,
      dueDate: dueDate ? new Date(dueDate) : null,
      status: "pending",
    },
  });

  return NextResponse.json(
    {
      id: task.id,
      title: task.title,
      description: task.description,
      status: task.status,
      due_date: task.dueDate?.toISOString() ?? null,
      created_at: task.createdAt.toISOString(),
    },
    { status: 201 },
  );
}
