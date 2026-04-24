import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { classifyRoute, type MuseRoute } from "@/lib/muse/classifyRoute";
import { routeHandler } from "@/lib/muse/handlers";
import { ingestRipple } from "@/lib/prl/ingest";

export const dynamic = "force-dynamic";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id: conversationId } = await params;

  const conversation = await prisma.museConversation.findFirst({
    where: { id: conversationId, clerkUserId: userId },
  });
  if (!conversation) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const body = await request.json().catch(() => null);
  if (!body || !body.message)
    return NextResponse.json({ error: "message_required" }, { status: 400 });

  const { message: userMessage } = body;

  const [, titleUpdate] = await Promise.all([
    prisma.museMessage.create({
      data: {
        conversationId,
        role: "user",
        content: userMessage,
      },
    }),
    conversation.title === "New conversation"
      ? prisma.museConversation.update({
          where: { id: conversationId },
          data: { title: userMessage.slice(0, 50) },
        })
      : Promise.resolve(null),
  ]);

  const recentMessages = await prisma.museMessage.findMany({
    where: { conversationId },
    orderBy: { createdAt: "desc" },
    take: 10,
  });
  const history = recentMessages.reverse().map((m) => ({ role: m.role, content: m.content }));

  const route: MuseRoute = await classifyRoute(userMessage);

  const { response, sessionId } = await routeHandler(route, {
    userMessage,
    conversationHistory: history,
    clerkUserId: userId,
  });

  const assistantMsg = await prisma.museMessage.create({
    data: {
      conversationId,
      role: "assistant",
      content: response,
      route,
    },
  });

  await prisma.museConversation.update({
    where: { id: conversationId },
    data: { updatedAt: new Date() },
  });

  ingestRipple({
    userId,
    type: "muse_exchange",
    sourceId: conversationId,
    content: `Muse exchange (${route}): User asked "${userMessage.slice(0, 100)}". Response: "${response.slice(0, 200)}"`,
  }).catch(console.error);

  return NextResponse.json({
    response,
    route,
    conversationId,
    messageId: assistantMsg.id,
    ...(sessionId ? { sessionId } : {}),
  });
}
