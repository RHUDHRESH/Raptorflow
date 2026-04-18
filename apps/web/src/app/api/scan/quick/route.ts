import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST() {
  return NextResponse.json(
    {
      error: "Scan routes are served by the backend API in this build.",
      mode: "quick",
    },
    { status: 501 },
  );
}

