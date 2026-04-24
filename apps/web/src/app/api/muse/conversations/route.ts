import { NextRequest, NextResponse } from "next/server";

function migrated(use: string): NextResponse {
  return NextResponse.json({ error: "migrated_to_rust_api", use }, { status: 410 });
}

export async function GET(): Promise<NextResponse> {
  return migrated("/api/v1/muse");
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  return migrated("/api/v1/muse");
}
