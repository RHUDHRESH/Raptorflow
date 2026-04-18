import { NextRequest, NextResponse } from "next/server";
import { apiFetch } from "@/lib/api";

export const dynamic = "force-dynamic";

interface PositioningLockRequest {
  foundationId: string;
  positioning: {
    statement: string;
    templateComponents: any;
    qualityScore: number;
    qualityFeedback: string;
  };
}

interface DownstreamImpact {
  campaignId: string;
  campaignName: string;
  impactDescription: string;
}

interface PositioningLockResponse {
  success: boolean;
  downstreamImpact: DownstreamImpact[];
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const { foundationId, positioning }: PositioningLockRequest = await req.json();

    if (!foundationId || !positioning) {
      return NextResponse.json(
        { error: "foundationId and positioning are required" },
        { status: 400 },
      );
    }

    // Get active campaigns
    const campaigns = await apiFetch<any[]>("/api/v1/campaigns", { auth: true });

    // Assess downstream impact
    const downstreamImpact: DownstreamImpact[] = [];
    for (const campaign of campaigns || []) {
      if (campaign.status === "active") {
        const impact = assessCampaignImpact(campaign, positioning);
        if (impact) {
          downstreamImpact.push({
            campaignId: campaign.id,
            campaignName: campaign.name,
            impactDescription: impact,
          });
        }
      }
    }

    // Update foundation with locked positioning
    const lockedPositioning = {
      ...positioning,
      isLocked: true,
      lockedAt: new Date().toISOString(),
    };

    await apiFetch("/api/v1/foundation/section/positioning", {
      method: "PATCH",
      body: { data: lockedPositioning },
      auth: true,
    });

    return NextResponse.json({
      success: true,
      downstreamImpact,
    });
  } catch (error) {
    console.error("Positioning lock error:", error);
    return NextResponse.json(
      {
        error: "Failed to lock positioning",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}

function assessCampaignImpact(campaign: any, newPositioning: any): string | null {
  // Simple impact assessment logic
  // In real implementation, this would be more sophisticated

  const campaignBrief = campaign.brief || "";
  const campaignName = campaign.name || "";

  // Check if campaign references positioning keywords
  const positioningKeywords = [
    "positioning",
    "brand",
    "differentiation",
    "unique",
    "value proposition",
  ];

  const hasPositioningReference = positioningKeywords.some(
    (keyword) =>
      campaignBrief.toLowerCase().includes(keyword) || campaignName.toLowerCase().includes(keyword),
  );

  if (hasPositioningReference) {
    return `Campaign "${campaignName}" references positioning concepts that may need updating to align with the new positioning statement.`;
  }

  // Check if campaign targets same ICP
  // This would require more complex logic to compare ICP data

  // For now, return impact for any active campaign as a conservative approach
  return `Campaign "${campaignName}" may benefit from messaging alignment with the new positioning. Consider reviewing campaign copy and creative assets.`;
}
