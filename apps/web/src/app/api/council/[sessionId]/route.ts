import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> },
): Promise<NextResponse> {
  const { sessionId } = await params;
  return NextResponse.json(
    { error: "migrated_to_rust_api", use: `/api/v1/council/${sessionId}` },
    { status: 410 },
  );
}

export async function PATCH(
  _request: NextRequest,
  { params }: { params: Promise<{ sessionId: string }> },
): Promise<NextResponse> {
  const { sessionId } = await params;
  return NextResponse.json(
    { error: "migrated_to_rust_api", use: `/api/v1/council/${sessionId}` },
    { status: 410 },
  );
}
