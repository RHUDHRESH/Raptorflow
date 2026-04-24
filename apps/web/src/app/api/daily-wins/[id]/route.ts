import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id } = await params;

  const win = await prisma.dailyWin.findFirst({
    where: { id, userId },
  });

  if (!win) return NextResponse.json({ error: "not_found" }, { status: 404 });

  return NextResponse.json({ win });
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id } = await params;
  const body = await request.json().catch(() => null);

  const win = await prisma.dailyWin.findFirst({
    where: { id, userId },
  });

  if (!win) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const updated = await prisma.dailyWin.update({
    where: { id },
    data: { isRead: body.isRead ?? win.isRead },
  });

  return NextResponse.json({ win: updated });
}
