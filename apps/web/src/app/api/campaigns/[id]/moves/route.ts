import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function migrated(use: string): NextResponse {
  return NextResponse.json({ error: "migrated_to_rust_api", use }, { status: 410 });
}

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const { id } = await params;
  return migrated(`/api/v1/campaigns/${id}/moves`);
}

export async function POST(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const { id } = await params;
  return migrated(`/api/v1/campaigns/${id}/moves`);
}
