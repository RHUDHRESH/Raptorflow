import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";

export const dynamic = "force-dynamic";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { sessionId } = await params;

  const session = await prisma.councilSession.findFirst({
    where: { id: sessionId, clerkUserId: userId },
    include: {
      positions: {
        orderBy: { createdAt: "asc" },
      },
    },
  });

  if (!session) return NextResponse.json({ error: "not_found" }, { status: 404 });

  return NextResponse.json({
    session: {
      session_id: session.id,
      org_id: "",
      campaign_id: session.topic,
      session_type: "strategic_review",
      status: session.status,
      error_message: session.errorMessage ?? null,
      question: session.context ?? "",
      total_cost_usd: null,
      created_at: session.createdAt.toISOString(),
      synthesis_result: session.synthesisResult,
      synthesized_at: session.synthesizedAt?.toISOString() ?? null,
      last_scan_result: session.lastScanResult,
      positions: session.positions.map((p) => ({
        position_id: p.id,
        avatar_key: p.avatarKey,
        avatar_name: p.avatarName,
        avatar_role: p.avatarRole,
        round_number: 1,
        content: p.position,
        confidence: p.confidence,
        created_at: p.createdAt.toISOString(),
      })),
    },
  });
}
