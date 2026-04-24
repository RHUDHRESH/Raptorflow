import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { generateMoves } from "@/lib/campaigns/generateMoves";
import { ingestRipple } from "@/lib/prl/ingest";
import { broadcast, channels } from "@/lib/pusher/server";

export const dynamic = "force-dynamic";

export async function POST(
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

  const token = (await authObj.getToken({ template: "backend" })) ?? "";

  let moves: unknown[];
  try {
    moves = await generateMoves(campaignId, token);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Move generation failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }

  ingestRipple({
    userId,
    type: "move_generated",
    sourceId: campaign.id,
    content: `Move ladder generated for "${campaign.title}": ${(moves as Array<{ title: string }>).map((m) => m.title).join(" → ")}`,
  }).catch(console.error);

  broadcast(channels.user(userId), "moves.generated", {
    campaignId,
    moveCount: (moves as Array<{ id: string; title: string; channel: string; priority: number }>)
      .length,
    moves: moves as Array<{ id: string; title: string; channel: string; priority: number }>,
  }).catch(console.error);

  return NextResponse.json({ moves });
}
