import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { synthesizeSession } from "@/lib/council/synthesize";

export const dynamic = "force-dynamic";

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { sessionId } = await params;

  const session = await prisma.councilSession.findFirst({
    where: { id: sessionId, clerkUserId: userId },
  });
  if (!session) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const token = (await authObj.getToken({ template: "backend" })) ?? "";

  synthesizeSession(sessionId, token).catch((err) => {
    console.error(`[council/synthesize] Synthesis failed for ${sessionId}:`, err);
    prisma.councilSession
      .update({ where: { id: sessionId }, data: { status: "failed" } })
      .catch(() => {});
  });

  return NextResponse.json({
    status: "synthesizing",
    session_id: sessionId,
    message: "Synthesis started",
  });
}
