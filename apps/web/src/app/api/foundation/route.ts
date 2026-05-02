import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { ingestRipple } from "@/lib/prl/ingest";
import { broadcast, channels } from "@/lib/pusher/server";
import { getApiBaseUrl } from "@/lib/api";

const ALL_SECTION_KEYS = [
  "company_url",
  "company_info",
  "company_stage",
  "product_catalog",
  "problem_statement",
  "target_audience",
  "secondary_icps",
  "competitors",
  "differentiation",
  "positioning",
  "brand_personality",
  "voice_practice",
  "content_territories",
  "channels",
  "goals",
  "seo_keywords",
  "asset_inventory",
  "frustrations",
  "tools",
  "reference_brands",
  "strategist",
] as const;

function deepEqual(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (typeof a !== typeof b) return false;
  if (a === null || b === null) return a === b;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      if (!deepEqual(a[i], b[i])) return false;
    }
    return true;
  }
  if (typeof a === "object" && typeof b === "object") {
    const aObj = a as Record<string, unknown>;
    const bObj = b as Record<string, unknown>;
    const aKeys = Object.keys(aObj);
    const bKeys = Object.keys(bObj);
    if (aKeys.length !== bKeys.length) return false;
    for (const key of aKeys) {
      if (!bKeys.includes(key)) return false;
      if (!deepEqual(aObj[key], bObj[key])) return false;
    }
    return true;
  }
  return false;
}

async function rustFetch(path: string, token: string, options?: RequestInit): Promise<Response> {
  return fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
  });
}

async function upsertSection(section: string, data: unknown, token: string): Promise<Response> {
  return rustFetch(`/api/v1/foundation/section/${section}`, token, {
    method: "PATCH",
    body: JSON.stringify({ data }),
  });
}

async function writeFoundationVersion(
  version: number,
  changedFields: string[],
  previousValues: Record<string, unknown>,
  token: string,
): Promise<void> {
  await rustFetch("/api/v1/foundation/versions", token, {
    method: "POST",
    body: JSON.stringify({
      version,
      change_description: "User save",
      changed_fields: changedFields,
      previous_values: previousValues,
    }),
  });
}

async function getCurrentFoundation(token: string): Promise<{
  sections: Record<string, unknown>;
  version: number;
} | null> {
  const res = await rustFetch("/api/v1/foundation", token);
  if (!res.ok) return null;
  const body = await res.json();
  return {
    sections: (body.sections as Record<string, unknown>) ?? {},
    version: body.version ?? 0,
  };
}

function diffFoundation(
  incoming: Record<string, unknown>,
  currentSections: Record<string, unknown>,
): { changedFields: string[]; previousValues: Record<string, unknown> } {
  const changedFields: string[] = [];
  const previousValues: Record<string, unknown> = {};

  for (const key of ALL_SECTION_KEYS) {
    if (key in incoming) {
      const incomingValue = incoming[key];
      const currentValue = currentSections[key];
      if (!deepEqual(incomingValue, currentValue)) {
        changedFields.push(key);
        if (currentValue !== undefined) {
          previousValues[key] = currentValue;
        }
      }
    }
  }

  return { changedFields, previousValues };
}

async function handleFoundationRequest(request: NextRequest): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const token = await authObj.getToken({ template: "backend" });
  if (!token) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const incoming: Record<string, unknown> = await request.json().catch(() => null);
  if (!incoming || typeof incoming !== "object") {
    return NextResponse.json({ error: "invalid_body" }, { status: 400 });
  }

  const current = await getCurrentFoundation(token);
  const currentSections = current?.sections ?? {};
  const currentVersion = current?.version ?? 0;

  const { changedFields, previousValues } = diffFoundation(incoming, currentSections);

  for (const field of changedFields) {
    const res = await upsertSection(field, incoming[field], token);
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      return NextResponse.json(
        { error: "section_update_failed", section: field, detail },
        { status: 502 },
      );
    }
  }

  const nextVersion = currentVersion + 1;
  if (changedFields.length > 0) {
    await writeFoundationVersion(nextVersion, changedFields, previousValues, token);
  }

  const finalRes = await rustFetch("/api/v1/foundation", token);
  const finalBody = await finalRes.json();
  const sections: Record<string, unknown> = finalBody.sections ?? {};
  const ci = (sections.company_info as any) ?? {};
  const companyName = ci.name ?? "the company";
  const companyStage = (sections.company_stage as string) ?? "";

  ingestRipple({
    userId,
    type: "foundation_save",
    sourceId: userId,
    content: `Foundation updated: ${changedFields.join(", ")} — Company: ${companyName}${companyStage ? `, Stage: ${companyStage}` : ""}`,
  }).catch(console.error);

  broadcast(channels.user(userId), "foundation.saved", {
    updatedFields: changedFields,
    companyName,
  }).catch(console.error);

  return NextResponse.json(finalBody, { status: finalRes.status });
}

export async function GET(): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const token = await authObj.getToken({ template: "backend" });
  if (!token) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const res = await rustFetch("/api/v1/foundation", token);
  const body = await res.json();
  return NextResponse.json(body, { status: res.status });
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  return handleFoundationRequest(request);
}

export async function PATCH(request: NextRequest): Promise<NextResponse> {
  return handleFoundationRequest(request);
}
