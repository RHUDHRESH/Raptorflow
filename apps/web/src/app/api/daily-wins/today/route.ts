import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { generateDailyWin } from "@/lib/wins/generateDailyWin";

export async function GET(): Promise<NextResponse> {
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
