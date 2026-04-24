import { NextRequest, NextResponse } from "next/server";
import { apiFetch } from "@/lib/api";

export const dynamic = "force-dynamic";

interface PositioningDraftRequest {
  foundationId: string;
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const body = (await req.json()) as PositioningDraftRequest;

    if (!body.foundationId) {
      return NextResponse.json({ error: "foundationId is required" }, { status: 400 });
    }

    const draft = await apiFetch("/api/v1/foundation/positioning/draft", {
      method: "POST",
      auth: true,
      body,
    });

    return NextResponse.json(draft);
  } catch (error) {
    console.error("Positioning draft proxy error:", error);
    return NextResponse.json(
      {
        error: "Failed to generate positioning draft",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}
