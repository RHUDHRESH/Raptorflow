import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { broadcast, channels } from "@/lib/pusher/server";

export const dynamic = "force-dynamic";

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; moveId: string; taskId: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id: campaignId, moveId, taskId } = await params;

  const campaign = await prisma.campaign.findFirst({
    where: { id: campaignId, clerkUserId: userId },
  });
  if (!campaign) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const task = await prisma.task.findFirst({
    where: { id: taskId, moveId },
  });
  if (!task) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const body = await request.json().catch(() => null);
  if (!body) return NextResponse.json({ error: "invalid_body" }, { status: 400 });

  const { status, title, description, dueDate } = body;

  const updated = await prisma.task.update({
    where: { id: taskId },
    data: {
      ...(status !== undefined && { status }),
      ...(title !== undefined && { title }),
      ...(description !== undefined && { description }),
      ...(dueDate !== undefined && { dueDate: dueDate ? new Date(dueDate) : null }),
    },
  });

  const allTasksInMove: Array<{ status: string }> = await prisma.task.findMany({ where: { moveId } });
  broadcast(channels.campaign(campaignId), "task.updated", {
    taskId,
    moveId,
    campaignId,
    status: updated.status,
    moveStats: {
      totalTasks: allTasksInMove.length,
      completedTasks: allTasksInMove.filter((t) => t.status === "complete").length,
    },
  }).catch(console.error);

  return NextResponse.json({
    id: updated.id,
    title: updated.title,
    description: updated.description,
    status: updated.status,
    due_date: updated.dueDate?.toISOString() ?? null,
    updated_at: updated.updatedAt.toISOString(),
  });
}
