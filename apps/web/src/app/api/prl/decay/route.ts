import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { decayRipples } from "@/lib/prl/decay";
import { decayEgoStates } from "@/lib/eel/egoState";

export async function POST(): Promise<NextResponse> {
  if (process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Use cron route for production" }, { status: 403 });
  }

  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const rippleStats = await decayRipples(userId);
  const egoStats = await decayEgoStates(userId);

  return NextResponse.json({ ripples: rippleStats, ego: egoStats });
}
