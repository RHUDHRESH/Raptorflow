import { NextResponse } from "next/server";
import { prisma } from "@raptorflow/database";
import { decayRipples } from "@/lib/prl/decay";
import { decayEgoStates } from "@/lib/eel/egoState";

export async function GET(request: Request): Promise<NextResponse> {
  const authHeader = request.headers.get("authorization");
  const cronSecret = process.env.CRON_SECRET?.trim();
  if (!cronSecret) {
    return NextResponse.json({ error: "cron_secret_not_configured" }, { status: 503 });
  }

  if (authHeader !== `Bearer ${cronSecret}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const userIds = await prisma.ripple.findMany({
    distinct: ["userId"],
    select: { userId: true },
  });

  let totalRippleProcessed = 0;
  let totalRippleDecayed = 0;
  let totalRipplePruned = 0;
  let totalEgoProcessed = 0;

  for (const { userId } of userIds) {
    try {
      const rippleStats = await decayRipples(userId);
      totalRippleProcessed += rippleStats.processed;
      totalRippleDecayed += rippleStats.decayed;
      totalRipplePruned += rippleStats.pruned;
    } catch (err) {
      console.error(`[decay:cron] Ripple decay failed for user ${userId}:`, err);
    }

    try {
      const egoStats = await decayEgoStates(userId);
      totalEgoProcessed += egoStats.processed;
    } catch (err) {
      console.error(`[decay:cron] Ego decay failed for user ${userId}:`, err);
    }
  }

  return NextResponse.json({
    ripples: {
      processed: totalRippleProcessed,
      decayed: totalRippleDecayed,
      pruned: totalRipplePruned,
    },
    ego: { processed: totalEgoProcessed },
  });
}
