export type RippleType =
  | "foundation_save"
  | "campaign_created"
  | "campaign_evaluated"
  | "move_generated"
  | "council_complete"
  | "muse_exchange"
  | "task_complete";

export async function ingestRipple(params: {
  userId: string;
  type: RippleType;
  sourceId: string;
  content: string;
}): Promise<void> {
  throw new Error("migrated_to_rust_api: ingestRipple is no longer available");
}
