import { NextResponse } from "next/server";
import { prisma } from "@raptorflow/database";
import { generateNudges } from "@/lib/nudges/generateNudges";

export async function GET(request: Request): Promise<NextResponse> {
  const authHeader = request.headers.get("authorization");
  const cronSecret = process.env.CRON_SECRET?.trim();
  if (!cronSecret) {
    return NextResponse.json({ error: "cron_secret_not_configured" }, { status: 503 });
  }

  if (authHeader !== `Bearer ${cronSecret}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const activeUsers = await prisma.ripple.findMany({
    where: { createdAt: { gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) } },
    select: { userId: true },
    distinct: ["userId"],
  });

  let totalCreated = 0;
  for (const { userId } of activeUsers) {
    try {
      const nudges = await generateNudges(userId);
      totalCreated += nudges.length;
    } catch (err) {
      console.error(`Nudge generation failed for ${userId}:`, err);
    }
  }

  return NextResponse.json({ processed: activeUsers.length, totalCreated });
}
