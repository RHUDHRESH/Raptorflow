import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { createIntelSignal } from "@/lib/intel/analyzeCompetitor";

export async function GET(request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { searchParams } = new URL(request.url);
  const type = searchParams.get("type");
  const unreadOnly = searchParams.get("unread") === "true";

  const signals = await prisma.intelSignal.findMany({
    where: {
      userId,
      ...(type ? { type } : {}),
      ...(unreadOnly ? { isArchived: false, isRead: false } : {}),
    },
    orderBy: { createdAt: "desc" },
    take: 50,
  });

  return NextResponse.json({ signals });
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const body = await request.json().catch(() => null);
  if (!body) return NextResponse.json({ error: "invalid_body" }, { status: 400 });

  const signal = await createIntelSignal({
    userId,
    type: body.type ?? "opportunity",
    source: body.source ?? "manual",
    title: body.title,
    summary: body.summary,
    detail: body.detail,
    severity: body.severity ?? "medium",
    relatedTo: body.relatedTo,
  });

  return NextResponse.json({ signal }, { status: 201 });
}
