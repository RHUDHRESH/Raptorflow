import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { generatePositions } from "@/lib/council/generatePositions";

export async function GET(): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const sessions = await prisma.councilSession.findMany({
    where: { clerkUserId: userId },
    orderBy: { createdAt: "desc" },
    include: {
      positions: {
        select: {
          id: true,
          avatarKey: true,
          avatarName: true,
          avatarRole: true,
          position: true,
          confidence: true,
          createdAt: true,
        },
      },
    },
  });

  return NextResponse.json({
    sessions: sessions.map((s) => ({
      session_id: s.id,
      org_id: "",
      campaign_id: s.topic,
      session_type: "strategic_review",
      status: s.status,
      question: s.context ?? "",
      created_at: s.createdAt.toISOString(),
    })),
  });
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const token = (await authObj.getToken({ template: "backend" })) ?? "";

  const body = await request.json().catch(() => null);
  if (!body) return NextResponse.json({ error: "invalid_body" }, { status: 400 });

  const { campaign_id, session_type, question } = body;

  const session = await prisma.councilSession.create({
    data: {
      clerkUserId: userId,
      topic: campaign_id ?? "general",
      context: question ?? "",
      status: "pending",
    },
  });

  generatePositions(session.id, token).catch((err) => {
    console.error(`[council] Position generation failed:`, err);
    prisma.councilSession
      .update({ where: { id: session.id }, data: { status: "failed" } })
      .catch(() => {});
  });

  return NextResponse.json({
    session: {
      session_id: session.id,
      org_id: "",
      campaign_id: session.topic,
      session_type: session_type ?? "strategic_review",
      status: session.status,
      question: session.context ?? "",
      created_at: session.createdAt.toISOString(),
    },
  });
}
