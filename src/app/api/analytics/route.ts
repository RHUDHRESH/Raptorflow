import { NextRequest, NextResponse } from "next/server";

// ═══════════════════════════════════════════════════════════════════════════════
// ANALYTICS API — Secure Telemetry Logging
// ═══════════════════════════════════════════════════════════════════════════════
// This route receives anonymized usage events from the client to help us
// understand how the product is used and where to improve.

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { event, payload, timestamp } = body;

    // Validate required fields
    if (!event || !timestamp) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    // Log the event (in production, this would go to your analytics provider)
    console.log("[Analytics]", {
      event,
      payload,
      timestamp,
      userAgent: request.headers.get("user-agent"),
    });

    // In production, you might send this to:
    // - Mixpanel
    // - Amplitude
    // - Segment
    // - Your own analytics database

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[Analytics Error]", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
