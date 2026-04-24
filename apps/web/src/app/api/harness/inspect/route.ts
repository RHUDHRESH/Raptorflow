import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { assembleContext } from "@/lib/harness/index";

export async function POST(request: Request): Promise<NextResponse> {
  if (process.env.NODE_ENV === "production") {
    return NextResponse.json({ error: "Not available in production" }, { status: 403 });
  }

  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const token = (await authObj.getToken({ template: "backend" })) ?? undefined;

  const body = await request.json().catch(() => null);
  if (!body || !body.query || !body.mode)
    return NextResponse.json({ error: "query and mode required" }, { status: 400 });

  const pack = await assembleContext({
    userId,
    mode: body.mode,
    query: body.query,
    avatarKey: body.avatarKey,
    token,
  });

  return NextResponse.json({
    contextPrefix: pack.contextPrefix,
    foundationBlock: pack.foundationBlock,
    cortexBlock: pack.cortexBlock,
    eelBlock: pack.eelBlock,
    meta: pack.meta,
  });
}
