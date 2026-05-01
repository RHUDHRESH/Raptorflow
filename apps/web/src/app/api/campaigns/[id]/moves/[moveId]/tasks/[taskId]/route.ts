import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function PATCH(): Promise<NextResponse> {
  return NextResponse.json(
    {
      error: "migrated_to_rust_api",
      message: "Use PATCH /api/v1/campaigns/{id}/tasks/{id}/status on the Rust API.",
    },
    { status: 410 },
  );
}
