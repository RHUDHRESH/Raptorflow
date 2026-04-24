export async function decayRipples(_userId: string): Promise<{
  processed: number;
  decayed: number;
  pruned: number;
}> {
  throw new Error("migrated_to_rust_api: decayRipples is no longer available");
}
