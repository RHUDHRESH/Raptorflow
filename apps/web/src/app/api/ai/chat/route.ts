import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const GROQ_BASE_URL = process.env.GROQ_API_BASE_URL ?? "https://api.groq.com/openai/v1";
const GROQ_API_KEY = process.env.GROQ_API_KEY;

export async function POST(req: NextRequest): Promise<NextResponse> {
  if (!GROQ_API_KEY) {
    return NextResponse.json(
      { error: "GROQ_API_KEY is not configured on the server." },
      { status: 503 },
    );
  }

  const body = await req.json();

  const upstream = await fetch(`${GROQ_BASE_URL}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${GROQ_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!upstream.ok) {
    const text = await upstream.text().catch(() => "(no body)");
    return NextResponse.json(
      { error: `Groq error ${upstream.status}: ${text}` },
      { status: upstream.status },
    );
  }

  if (body.stream) {
    return new NextResponse(upstream.body, {
      status: upstream.status,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  }

  const data = await upstream.json();
  return NextResponse.json(data);
}
