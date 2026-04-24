import { NextResponse } from "next/server";
import { prisma } from "@raptorflow/database";
import { generateIntelBrief } from "@/lib/intel/generateIntelBrief";

export async function GET(request: Request): Promise<NextResponse> {
  const authHeader = request.headers.get("authorization");
  const cronSecret = process.env.CRON_SECRET;
  if (authHeader !== `Bearer ${cronSecret}`) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const activeUsers = await prisma.ripple.findMany({
    where: { createdAt: { gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) } },
    select: { userId: true },
    distinct: ["userId"],
  });

  let processed = 0;
  for (const { userId } of activeUsers) {
    try {
      await generateIntelBrief(userId);
      processed++;
    } catch (err) {
      console.error(`Intel brief generation failed for ${userId}:`, err);
    }
  }

  return NextResponse.json({ processed, total: activeUsers.length });
}
