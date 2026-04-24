import { NextResponse } from "next/server";
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

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const orgId = await resolveOrgId(userId);
  if (!orgId) return NextResponse.json({ error: "not_found" }, { status: 404 });

  const { id } = await params;

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
    WHERE org_id = ${orgId}::uuid AND content_id = ${id}
    LIMIT 1
  `;

  const row = rows[0];
  if (!row) return NextResponse.json({ error: "not_found" }, { status: 404 });

  return NextResponse.json({
    content: {
      content_id: row.content_id,
      org_id: row.org_id,
      campaign_id: row.campaign_id,
      task_id: row.task_id,
      content_type: row.content_type,
      status: row.status,
      body: row.body,
      created_at: row.created_at.toISOString(),
    },
    status: "ok",
  });
}
