import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { generateDailyWin } from "@/lib/wins/generateDailyWin";

export async function GET(): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const wins = await prisma.dailyWin.findMany({
    where: { userId },
    orderBy: { date: "desc" },
    take: 30,
  });

  const today = new Date();
  today.setUTCHours(0, 0, 0, 0);
  const todayWin =
    wins.find((w) => {
      const d = new Date(w.date);
      d.setUTCHours(0, 0, 0, 0);
      return d.getTime() === today.getTime();
    }) ?? null;

  return NextResponse.json({ wins, todayWin });
}

export async function POST(): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  try {
    const win = await generateDailyWin(userId);
    return NextResponse.json({ win });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Generation failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
