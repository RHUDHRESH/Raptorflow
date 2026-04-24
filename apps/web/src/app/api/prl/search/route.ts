import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { cortexSearch } from "@/lib/prl/cortex";

export async function POST(request: NextRequest): Promise<NextResponse> {
  if (process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Not available in production" }, { status: 403 });
  }

  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const body = await request.json().catch(() => null);
  if (!body || !body.query) return NextResponse.json({ error: "query_required" }, { status: 400 });

  const result = await cortexSearch({
    userId,
    query: body.query,
    limit: body.limit ?? 5,
    minSalience: body.minSalience ?? 0.2,
  });

  return NextResponse.json(result);
}
