import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { generateNudges } from "@/lib/nudges/generateNudges";

export async function GET(request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { searchParams } = new URL(request.url);
  const type = searchParams.get("type");
  const limit = parseInt(searchParams.get("limit") ?? "50", 10);

  const nudges = await prisma.nudge.findMany({
    where: {
      userId,
      isDismissed: false,
      ...(type ? { type } : {}),
    },
    orderBy: { priority: "desc" },
    take: limit,
  });

  const totalCount = await prisma.nudge.count({
    where: { userId, isDismissed: false, ...(type ? { type } : {}) },
  });

  return NextResponse.json({ nudges, totalCount });
}

export async function POST(): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  try {
    const created = await generateNudges(userId);
    return NextResponse.json({ created });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Generation failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
