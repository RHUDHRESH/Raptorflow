import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(_request: NextRequest): Promise<NextResponse> {
  return NextResponse.json(
    { error: "migrated_to_rust_api", use: "/api/v1/content" },
    { status: 410 },
  );
}
