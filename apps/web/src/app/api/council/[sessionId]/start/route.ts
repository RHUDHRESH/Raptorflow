import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { generatePositions } from "@/lib/council/generatePositions";

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

  generatePositions(sessionId, token).catch((err) => {
    console.error(`[council/start] Position generation failed for ${sessionId}:`, err);
    prisma.councilSession
      .update({ where: { id: sessionId }, data: { status: "failed" } })
      .catch(() => {});
  });

  return NextResponse.json({
    status: "generating",
    session_id: sessionId,
    message: "Position generation started",
  });
}
