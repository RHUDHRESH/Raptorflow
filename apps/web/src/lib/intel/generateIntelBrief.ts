interface IntelBrief {
  signals: Array<{
    type: string;
    source: string;
    title: string;
    summary: string;
    severity: string;
  }>;
  competitorThreats: string[];
  marketOpportunities: string[];
  recommendedActions: string[];
}

export async function generateIntelBrief(_userId: string): Promise<IntelBrief> {
  throw new Error("migrated_to_rust_api: generateIntelBrief is no longer available");
}
