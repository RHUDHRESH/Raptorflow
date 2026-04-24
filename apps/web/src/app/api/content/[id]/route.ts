import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const { id } = await params;
  return NextResponse.json(
    { error: "migrated_to_rust_api", use: `/api/v1/content/${id}` },
    { status: 410 },
  );
}
