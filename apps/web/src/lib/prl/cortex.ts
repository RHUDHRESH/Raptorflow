export interface CortexResult {
  ripples: Array<{
    content: string;
    type: string;
    salience: number;
    score: number;
    createdAt: string;
  }>;
  contextBlock: string;
}

export async function cortexSearch(params: {
  userId: string;
  query: string;
  limit?: number;
  minSalience?: number;
}): Promise<CortexResult> {
  throw new Error("migrated_to_rust_api: cortexSearch is no longer available");
}
