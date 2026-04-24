import { NextRequest, NextResponse } from "next/server";
import { hash } from "bcryptjs";
import { prisma } from "@raptorflow/database";

export async function POST(request: NextRequest): Promise<NextResponse> {
  const body = await request.json().catch(() => null);
  if (!body || typeof body.token !== "string" || typeof body.newPassword !== "string") {
    return NextResponse.json({ error: "invalid_body" }, { status: 400 });
  }

  const { token, newPassword } = body;

  if (newPassword.length < 8) {
    return NextResponse.json({ error: "password_too_short" }, { status: 422 });
  }

  const resetToken = await prisma.passwordResetToken.findUnique({
    where: { token },
    include: { user: true },
  });

  if (!resetToken) {
    return NextResponse.json({ error: "invalid_token" }, { status: 400 });
  }

  if (resetToken.used) {
    return NextResponse.json({ error: "token_already_used" }, { status: 400 });
  }

  if (resetToken.expiresAt < new Date()) {
    return NextResponse.json({ error: "token_expired" }, { status: 400 });
  }

  try {
    const hashedPassword = await hash(newPassword, 12);

    await prisma.$transaction([
      prisma.user.update({
        where: { clerkUserId: resetToken.userId },
        data: { password: hashedPassword },
      }),
      prisma.passwordResetToken.update({
        where: { id: resetToken.id },
        data: { used: true },
      }),
    ]);

    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json({ error: "update_failed" }, { status: 500 });
  }
}
