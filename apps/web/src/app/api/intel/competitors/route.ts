import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest): Promise<NextResponse> {
  return NextResponse.json(
    { error: "migrated_to_rust_api", use: "/api/v1/intel/competitors" },
    { status: 410 },
  );
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  return NextResponse.json(
    { error: "migrated_to_rust_api", use: "/api/v1/intel/competitors" },
    { status: 410 },
  );
}
