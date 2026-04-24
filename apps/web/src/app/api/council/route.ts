import { NextRequest, NextResponse } from "next/server";

export async function GET(): Promise<NextResponse> {
  return NextResponse.json(
    { error: "migrated_to_rust_api", use: "/api/v1/council" },
    { status: 410 },
  );
}

export async function POST(_request: NextRequest): Promise<NextResponse> {
  return NextResponse.json(
    { error: "migrated_to_rust_api", use: "/api/v1/council" },
    { status: 410 },
  );
}
