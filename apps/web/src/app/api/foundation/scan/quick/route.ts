import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { prisma } from "@raptorflow/database";
import { converseStrategist } from "@/lib/bedrock";
import { ingestRipple } from "@/lib/prl/ingest";
import { harnessPrompt } from "@/lib/harness/buildPrompt";
import { broadcast, channels } from "@/lib/pusher/server";
import { generateNudges } from "@/lib/nudges/generateNudges";

const RUST_API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080";
const MIN_FIELDS = 5;

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

function countFilledFields(sections: Record<string, unknown>): number {
  let count = 0;
  for (const key of ALL_SECTION_KEYS) {
    const val = sections[key];
    if (
      val !== undefined &&
      val !== null &&
      val !== "" &&
      !(typeof val === "object" && Object.keys(val).length === 0)
    ) {
      count++;
    }
  }
  return count;
}

export async function POST(): Promise<NextResponse> {
  const authObj = await auth();
  const { userId } = authObj;
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const token = await authObj.getToken({ template: "backend" });
  if (!token) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  // 1. Fetch foundation from Rust backend
  const foundationRes = await fetch(`${RUST_API}/api/v1/foundation`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!foundationRes.ok) {
    return NextResponse.json(
      { error: "failed_to_fetch_foundation", detail: await foundationRes.text() },
      { status: 502 },
    );
  }

  const foundation = await foundationRes.json();
  const sections: Record<string, unknown> = foundation.sections ?? {};

  // 2. Validate minimum fields
  const filledCount = countFilledFields(sections);
  if (filledCount < MIN_FIELDS) {
    return NextResponse.json(
      {
        error: "Foundation too sparse — fill in more fields before scanning",
        filledCount,
        required: MIN_FIELDS,
      },
      { status: 400 },
    );
  }

  // 3. Build prompt and call Bedrock via Harness
  const taskPrompt = `Analyze the company foundation data above and return a JSON object with these exact keys:
- "strengths": string[] (3-5 bullet points about what's clear, well-defined, or strong)
- "gaps": string[] (3-5 things missing, vague, or weak)
- "recommendations": string[] (3-5 actionable next steps)
- "positioning_score": number (1-10, how clear their market position is)
- "summary": string (2-3 sentence executive summary)

Return only valid JSON, no markdown, no explanation.`;

  let rawResponse: string;
  try {
    const { prompt: fullPrompt, meta } = await harnessPrompt(
      {
        userId,
        mode: "scan",
        query: `strategic analysis for ${(sections.company_info as any)?.name ?? "company"} ${(sections.positioning as any)?.mission ?? ""}`,
        token,
        cortexLimit: 3,
      },
      taskPrompt,
    );
    console.log(`Harness [scan] meta:`, meta);
    rawResponse = await converseStrategist(fullPrompt, 1024);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Bedrock inference failed";
    return NextResponse.json({ error: "bedrock_error", detail: message }, { status: 502 });
  }

  // 4. Parse JSON response
  let parsed: {
    strengths?: string[];
    gaps?: string[];
    recommendations?: string[];
    positioning_score?: number;
    summary?: string;
  };

  try {
    const trimmed = rawResponse.trim();
    const jsonStr = trimmed.startsWith("```")
      ? trimmed.replace(/^```json\n?/, "").replace(/\n?```$/, "")
      : trimmed;
    parsed = JSON.parse(jsonStr);
  } catch {
    return NextResponse.json(
      { error: "failed_to_parse_scan_response", raw: rawResponse },
      { status: 502 },
    );
  }

  if (
    !parsed.strengths ||
    !parsed.gaps ||
    !parsed.recommendations ||
    parsed.positioning_score === undefined ||
    !parsed.summary
  ) {
    return NextResponse.json({ error: "invalid_scan_response_shape", parsed }, { status: 502 });
  }

  const scannedAt = new Date().toISOString();

  await prisma.councilSession
    .updateMany({
      where: { clerkUserId: userId, status: "pending" },
      data: { lastScanResult: parsed as any },
    })
    .catch(() => {});

  ingestRipple({
    userId,
    type: "foundation_save",
    sourceId: userId,
    content: `Foundation scan complete — Score: ${parsed.positioning_score}/10. Summary: ${parsed.summary}. Gaps: ${parsed.gaps.join(", ")}`,
  }).catch(console.error);

  broadcast(channels.user(userId), "foundation.scan.complete", {
    positioningScore: parsed.positioning_score,
    summary: parsed.summary,
  }).catch(console.error);

  generateNudges(userId).catch(console.error);

  return NextResponse.json({
    scan: parsed,
    scannedAt,
  });
}
