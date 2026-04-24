import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(_request: Request, { params }: { params: Promise<{ jobId: string }> }) {
  const { jobId } = await params;

  return NextResponse.json(
    {
      jobId,
      error: "migrated_to_rust_api",
      use: `/api/v1/foundation/scan/${jobId}`,
    },
    { status: 410 },
  );
}
