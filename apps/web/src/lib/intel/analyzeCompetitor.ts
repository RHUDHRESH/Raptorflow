export interface CompetitorAnalysis {
  competitorName: string;
  website: string | null;
  strengths: string[];
  weaknesses: string[];
  messagingThemes: string[];
  targetAudience: string[];
  positioning: string;
  threats: string[];
  opportunities: string[];
}

export async function analyzeCompetitor(
  _userId: string,
  competitorName: string,
  _website: string | null,
): Promise<CompetitorAnalysis> {
  throw new Error(
    `migrated_to_rust_api: analyzeCompetitor for ${competitorName} is no longer available`,
  );
}

export async function createIntelSignal(params: {
  userId: string;
  type: string;
  source: string;
  title: string;
  summary: string;
  detail?: string;
  severity?: string;
  relatedTo?: string;
}): Promise<void> {
  throw new Error("migrated_to_rust_api: createIntelSignal is no longer available");
}
