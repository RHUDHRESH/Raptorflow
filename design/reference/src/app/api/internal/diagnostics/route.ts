import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(): Promise<NextResponse> {
  // Internal diagnostics are authenticated twice: middleware at the edge and a route-level check here.
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  // Keep the payload intentionally minimal so diagnostics do not become an env dump.
  return NextResponse.json({
    ok: true,
    route: "internal.diagnostics",
    authenticated: true,
    timestamp: new Date().toISOString()
  });
}
