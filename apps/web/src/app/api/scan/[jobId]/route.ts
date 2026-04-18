import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ jobId: string }> },
) {
  const { jobId } = await params;

  return NextResponse.json(
    {
      jobId,
      status: "not_available",
      error: "Scan routes are served by the backend API in this build.",
    },
    { status: 501 },
  );
}

