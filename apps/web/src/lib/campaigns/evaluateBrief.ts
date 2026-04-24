export interface EvaluationResult {
  score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  icp_fit: string;
  suggested_goal: string;
  recommended_channels: string[];
  budget_assessment: string;
}

export async function evaluateBrief(
  _campaignId: string,
  _token: string,
): Promise<EvaluationResult> {
  throw new Error("migrated_to_rust_api: evaluateBrief is no longer available");
}
