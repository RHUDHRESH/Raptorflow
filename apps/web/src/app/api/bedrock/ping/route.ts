import { convergeFast } from "@/lib/bedrock";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    const response = await convergeFast("Reply with exactly PONG", 16);
    return NextResponse.json({ response });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
