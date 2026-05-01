import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(): Promise<NextResponse> {
  return NextResponse.json(
    {
      error: "migrated_to_rust_api",
      message: "Use POST /api/v1/campaigns/{id}/moves/generate on the Rust API.",
    },
    { status: 410 },
  );
}
