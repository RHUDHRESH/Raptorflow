import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(): Promise<NextResponse> {
  return NextResponse.json(
    {
      error: "moved_permanently",
      message: "This endpoint has moved to /api/v1/avatars",
      migration: "Use GET /api/v1/avatars via the Rust API",
    },
    { status: 410 },
  );
}
