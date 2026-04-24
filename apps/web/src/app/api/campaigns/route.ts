import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function migrated(use: string): NextResponse {
  return NextResponse.json({ error: "migrated_to_rust_api", use }, { status: 410 });
}

export async function GET(): Promise<NextResponse> {
  return migrated("/api/v1/campaigns");
}

export async function POST(_request: NextRequest): Promise<NextResponse> {
  return migrated("/api/v1/campaigns");
}
