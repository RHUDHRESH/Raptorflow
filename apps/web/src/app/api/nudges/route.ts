import { NextRequest, NextResponse } from "next/server";

function migrated(use: string): NextResponse {
  return NextResponse.json({ error: "migrated_to_rust_api", use }, { status: 410 });
}

export async function GET(request: NextRequest): Promise<NextResponse> {
  return migrated("/api/v1/nudges");
}

export async function POST(): Promise<NextResponse> {
  return migrated("/api/v1/nudges");
}
