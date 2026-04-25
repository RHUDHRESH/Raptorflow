import { NextRequest, NextResponse } from "next/server";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ signalId: string }> },
): Promise<NextResponse> {
  const { signalId } = await params;
  return NextResponse.json(
    { error: "migrated_to_rust_api", use: `/api/v1/intel/signals/${signalId}` },
    { status: 410 },
  );
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ signalId: string }> },
): Promise<NextResponse> {
  const { signalId } = await params;
  return NextResponse.json(
    { error: "migrated_to_rust_api", use: `/api/v1/intel/signals/${signalId}` },
    { status: 410 },
  );
}
