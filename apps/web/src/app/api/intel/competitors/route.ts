import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { analyzeCompetitor } from "@/lib/intel/analyzeCompetitor";

export async function GET(request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const snapshots = await prisma.competitorSnapshot.findMany({
    where: { userId },
    orderBy: { lastAnalyzedAt: "desc" },
  });

  return NextResponse.json({ snapshots });
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const body = await request.json().catch(() => null);
  if (!body || !body.competitorName) {
    return NextResponse.json({ error: "competitorName is required" }, { status: 400 });
  }

  const analysis = await analyzeCompetitor(userId, body.competitorName, body.website ?? null);

  return NextResponse.json({ analysis }, { status: 201 });
}
