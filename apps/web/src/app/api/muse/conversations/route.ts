import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";

export const dynamic = "force-dynamic";

export async function GET(): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const conversations = await prisma.museConversation.findMany({
    where: { clerkUserId: userId },
    orderBy: { updatedAt: "desc" },
    include: {
      _count: { select: { messages: true } },
      messages: {
        orderBy: { createdAt: "desc" },
        take: 1,
        select: { role: true, content: true, route: true },
      },
    },
  });

  return NextResponse.json(
    conversations.map((c) => ({
      id: c.id,
      title: c.title,
      updated_at: c.updatedAt.toISOString(),
      created_at: c.createdAt.toISOString(),
      message_count: c._count.messages,
      last_message: c.messages[0] ?? null,
    })),
  );
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const body = await request.json().catch(() => null);
  const title = body?.title ?? "New conversation";

  const conversation = await prisma.museConversation.create({
    data: {
      clerkUserId: userId,
      title,
    },
  });

  return NextResponse.json({ id: conversation.id, title: conversation.title }, { status: 201 });
}
