import { NextResponse } from "next/server";
import { prisma } from "@raptorflow/database";

export const dynamic = "force-dynamic";

export async function GET(): Promise<NextResponse> {
  try {
    const avatars = await prisma.avatar.findMany({
      orderBy: { key: "asc" },
    });
    return NextResponse.json(avatars);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
