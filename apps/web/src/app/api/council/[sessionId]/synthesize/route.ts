import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(): Promise<NextResponse> {
  return NextResponse.json(
    {
      error: "migrated_to_rust_api",
      use: "POST /api/v1/council/{sessionId}/synthesize",
    },
    { status: 410 },
  );
}
