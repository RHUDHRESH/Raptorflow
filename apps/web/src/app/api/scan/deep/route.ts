import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST() {
  return NextResponse.json(
    {
      error: "migrated_to_rust_api",
      use: "/api/v1/foundation/scan/deep",
    },
    { status: 410 },
  );
}
