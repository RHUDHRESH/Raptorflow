import { NextRequest, NextResponse } from "next/server";
import { apiFetch } from "@/lib/api";

export const dynamic = "force-dynamic";

interface PositioningDraftRequest {
  foundationId: string;
}

interface PositioningDraftResponse {
  statement: string;
  templateComponents: {
    forWho: string;
    whoProblem: string;
    brand: string;
    category: string;
    differentiation: string;
    because: string;
  };
  qualityScore: number;
  qualityFeedback: string;
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const { foundationId }: PositioningDraftRequest = await req.json();

    if (!foundationId) {
      return NextResponse.json({ error: "foundationId is required" }, { status: 400 });
    }

    // Get foundation data
    const foundation = await apiFetch<any>("/api/v1/foundation", { auth: true });

    if (!foundation) {
      return NextResponse.json({ error: "Foundation not found" }, { status: 404 });
    }

    // Extract relevant data for positioning
    const icp = foundation.target_audience?.primary_icp;
    const competitors = foundation.competitors;
    const differentiation = foundation.differentiation || [];
    const product = foundation.product_catalog?.primary_product;
    const problem = foundation.problem_statement;

    // Get company info
    const companyInfo = foundation.company_info;
    const brand = companyInfo?.name || "your brand";

    // Generate positioning draft using AI
    const draft = await generatePositioningDraft({
      icp,
      competitors,
      differentiation,
      product,
      problem,
      brand,
      companyInfo,
    });

    return NextResponse.json(draft);
  } catch (error) {
    console.error("Positioning draft error:", error);
    return NextResponse.json(
      {
        error: "Failed to generate positioning draft",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}

async function generatePositioningDraft(data: any): Promise<PositioningDraftResponse> {
  const { icp, competitors, differentiation, product, problem, brand, companyInfo } = data;

  // Extract ICP info
  let icpName = "your ideal customers";
  let icpProblem = problem || "face significant challenges";

  if (icp) {
    if (icp.B2B) {
      icpName = icp.B2B.persona_name || icp.B2B.name || "B2B customers";
      icpProblem = icp.B2B.pain_points?.[0] || problem || "face complex business challenges";
    } else if (icp.B2C) {
      icpName = icp.B2C.persona_name || icp.B2C.name || "consumers";
      icpProblem = icp.B2C.pain_points?.[0] || problem || "face everyday challenges";
    }
  }

  // Extract competitor and differentiation info
  const competitorNames = competitors?.direct?.map((c: any) => c.name).join(", ") || "competitors";
  const diffPoints = differentiation.slice(0, 2).join(" and ") || "unique value";

  // Category based on company info
  const category = companyInfo?.industry || "technology solutions";

  // Construct template components
  const templateComponents = {
    forWho: icpName,
    whoProblem: icpProblem,
    brand: brand,
    category: category,
    differentiation: diffPoints,
    because: `unlike ${competitorNames}, we deliver ${product || "proven results"}`,
  };

  // Generate full statement
  const statement = `For ${templateComponents.forWho} who ${templateComponents.whoProblem}, ${templateComponents.brand} is a ${templateComponents.category} that ${templateComponents.differentiation}, because ${templateComponents.because}.`;

  // For now, return mock quality score and feedback
  // In real implementation, this would call AI to evaluate
  const qualityScore = 0.75;
  const qualityFeedback =
    "Strong foundation with clear value proposition. Consider quantifying differentiation with specific metrics.";

  return {
    statement,
    templateComponents,
    qualityScore,
    qualityFeedback,
  };
}
