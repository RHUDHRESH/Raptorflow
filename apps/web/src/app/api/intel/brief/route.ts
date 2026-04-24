import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { generateIntelBrief } from "@/lib/intel/generateIntelBrief";

export async function POST(_request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  try {
    const brief = await generateIntelBrief(userId);
    return NextResponse.json({ brief });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Brief generation failed";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
