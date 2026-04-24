import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(): Promise<NextResponse> {
  return NextResponse.json(
    {
      error: "migrated_to_rust_api",
      use: "GET /api/v1/council/{sessionId}/stream",
      note: "browser_frontend_uses_polling_due_to_eventsource_auth_limit",
    },
    { status: 410 },
  );
}
