import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ signalId: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { signalId } = await params;

  const signal = await prisma.intelSignal.findFirst({
    where: { id: signalId, userId },
  });

  if (!signal) return NextResponse.json({ error: "not_found" }, { status: 404 });

  return NextResponse.json({ signal });
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ signalId: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { signalId } = await params;
  const body = await request.json().catch(() => null);

  const signal = await prisma.intelSignal.findFirst({
    where: { id: signalId, userId },
  });

  if (!signal) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const updated = await prisma.intelSignal.update({
    where: { id: signalId },
    data: {
      isRead: body.isRead ?? signal.isRead,
      isArchived: body.isArchived ?? signal.isArchived,
    },
  });

  return NextResponse.json({ signal: updated });
}
