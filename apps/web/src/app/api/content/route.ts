import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";

export const dynamic = "force-dynamic";

async function resolveOrgId(userId: string): Promise<string | null> {
  const membership = await prisma.orgMember.findFirst({
    where: { clerkUserId: userId },
    orderBy: { createdAt: "desc" },
  });

  return membership?.orgId ?? null;
}

function readUserIdFromSessionCookie(request: NextRequest): string | null {
  const sessionCookie = request.cookies.get("__session")?.value;
  if (!sessionCookie) return null;

  const parts = sessionCookie.split(".");
  if (parts.length < 2) return null;

  try {
    const payload = JSON.parse(Buffer.from(parts[1], "base64url").toString("utf8")) as {
      sub?: string;
      user_id?: string;
    };
    return payload.user_id ?? payload.sub ?? null;
  } catch {
    return null;
  }
}

export async function GET(request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const userId = authObj.userId ?? readUserIdFromSessionCookie(request);
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const orgId = await resolveOrgId(userId);
  if (!orgId) return NextResponse.json({ content: [], total: 0, status: "ok" });

  const rows = await prisma.$queryRaw<
    Array<{
      content_id: string;
      org_id: string;
      campaign_id: string | null;
      task_id: string | null;
      content_type: string;
      status: string;
      body: unknown;
      created_at: Date;
    }>
  >`
    SELECT content_id, org_id::text AS org_id, campaign_id, task_id, content_type, status, body, created_at
    FROM generated_content
    WHERE org_id = ${orgId}::uuid
    ORDER BY created_at DESC
  `;

  return NextResponse.json({
    content: rows.map((row) => ({
      content_id: row.content_id,
      org_id: row.org_id,
      campaign_id: row.campaign_id,
      task_id: row.task_id,
      content_type: row.content_type,
      status: row.status,
      body: row.body,
      created_at: row.created_at.toISOString(),
    })),
    total: rows.length,
    status: "ok",
  });
}
