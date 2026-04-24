import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id } = await params;
  const body = await request.json().catch(() => null);

  const nudge = await prisma.nudge.findFirst({
    where: { id, userId },
  });

  if (!nudge) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const updated = await prisma.nudge.update({
    where: { id },
    data: {
      isDismissed: body.isDismissed ?? nudge.isDismissed,
      isActioned: body.isActioned ?? nudge.isActioned,
    },
  });

  return NextResponse.json({ nudge: updated });
}
