export interface SynthesisResult {
  verdict: string;
  rationale: string;
  immediate_actions: string[];
  watch_outs: string[];
  dissenting_view: string;
}

export async function synthesizeSession(_sessionId: string, _token: string): Promise<void> {
  throw new Error("migrated_to_rust_api: synthesizeSession is no longer available");
}
