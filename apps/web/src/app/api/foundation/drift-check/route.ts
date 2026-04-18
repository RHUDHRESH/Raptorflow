import { NextRequest, NextResponse } from "next/server";
import { apiFetch } from "@/lib/api";

export const dynamic = "force-dynamic";

interface DriftItem {
  field: string;
  currentValue: any;
  suggestedValue: string;
  reason: string;
}

interface DriftCheckRequest {
  conversationText: string;
  foundationId?: string;
}

interface DriftCheckResponse {
  driftDetected: boolean;
  driftItems: DriftItem[];
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const { conversationText }: DriftCheckRequest = await req.json();

    if (!conversationText) {
      return NextResponse.json({ error: "conversationText is required" }, { status: 400 });
    }

    const foundation = await apiFetch<{ sections: any }>("/api/v1/foundation/snapshot", {
      auth: true,
    });
    const sections = foundation?.sections || {};
    const conversation = conversationText.toLowerCase();

    const driftItems: DriftItem[] = [];

    const competitors = sections.competitors;
    if (competitors) {
      const knownCompetitors: string[] = [];
      if (competitors.direct) {
        competitors.direct.forEach((c: any) => {
          if (c.name) knownCompetitors.push(c.name.toLowerCase());
          if (c.competitor_url) knownCompetitors.push(c.competitor_url.toLowerCase());
        });
      }
      if (competitors.indirect) {
        competitors.indirect.forEach((c: any) => {
          if (c.name) knownCompetitors.push(c.name.toLowerCase());
          if (c.competitor_url) knownCompetitors.push(c.competitor_url.toLowerCase());
        });
      }

      const competitorMentions =
        conversationText.match(/(?:www\.)?([a-zA-Z0-9-]+\.(?:com|io|net|org|co))/gi) || [];
      for (const mention of competitorMentions) {
        const normalizedMention = mention.toLowerCase();
        const cleanMention = normalizedMention.replace(/^https?:\/\/(www\.)?/, "").split("/")[0];
        const isKnown = knownCompetitors.some(
          (kc) => cleanMention.includes(kc) || kc.includes(cleanMention),
        );
        if (!isKnown && normalizedMention.length > 3) {
          const existingCompetitors = [
            ...(competitors.direct || []),
            ...(competitors.indirect || []),
          ].map((c: any) => c.name);
          driftItems.push({
            field: "competitors",
            currentValue: existingCompetitors,
            suggestedValue: mention,
            reason: `User mentioned ${mention} in conversation but it's not in your competitor list`,
          });
        }
      }
    }

    const productCatalog = sections.product_catalog;
    if (productCatalog && productCatalog.products) {
      const knownProducts = productCatalog.products
        .map((p: any) => p.name?.toLowerCase())
        .filter(Boolean);
      const productKeywords = [
        "launch",
        "new product",
        "introducing",
        "releasing",
        "new feature",
        "new offering",
      ];
      for (const keyword of productKeywords) {
        if (conversation.includes(keyword)) {
          const extractMatch = conversationText.match(new RegExp(`${keyword}\\s+([^,\\.]+)`, "i"));
          if (extractMatch && extractMatch[1]) {
            const mentionedProduct = extractMatch[1].trim();
            if (!knownProducts.some((kp: string) => mentionedProduct.toLowerCase().includes(kp))) {
              driftItems.push({
                field: "product_catalog",
                currentValue: knownProducts,
                suggestedValue: mentionedProduct,
                reason: `User mentioned a new product "${mentionedProduct}" in conversation`,
              });
              break;
            }
          }
        }
      }
    }

    const targetAudience = sections.target_audience;
    if (targetAudience && targetAudience.segments) {
      const industryKeywords = [
        "enterprise",
        "smb",
        "startup",
        "mid-market",
        "b2b",
        "b2c",
        "saas",
        "fintech",
        "healthcare",
        "retail",
      ];
      for (const keyword of industryKeywords) {
        if (conversation.includes(keyword)) {
          const currentIndustry =
            targetAudience.segments[0]?.demographics?.industry ||
            targetAudience.segments[0]?.demographics?.company_size;
          if (currentIndustry && !currentIndustry.toString().toLowerCase().includes(keyword)) {
            driftItems.push({
              field: "target_audience",
              currentValue: currentIndustry,
              suggestedValue: keyword,
              reason: `User mentioned "${keyword}" in conversation which differs from your ICP`,
            });
            break;
          }
        }
      }
    }

    return NextResponse.json({
      driftDetected: driftItems.length > 0,
      driftItems,
    });
  } catch (error) {
    console.error("Drift check error:", error);
    return NextResponse.json(
      {
        error: "Failed to check for drift",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}
