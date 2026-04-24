export async function getOrInitEgoState(
  _userId: string,
  _avatarKey: string,
): Promise<{
  id: string;
  authority: number;
  empathy: number;
  risk: number;
  creativity: number;
  precision: number;
  sessionCount: number;
  agreementRate: number;
}> {
  throw new Error("migrated_to_rust_api: getOrInitEgoState is no longer available");
}

export async function updateEgoStateFromSession(_params: {
  userId: string;
  avatarKey: string;
  strategistAgreed: boolean;
  confidence: number;
}): Promise<void> {
  throw new Error("migrated_to_rust_api: updateEgoStateFromSession is no longer available");
}

export async function decayEgoStates(_userId: string): Promise<{
  processed: number;
  decayed: number;
}> {
  throw new Error("migrated_to_rust_api: decayEgoStates is no longer available");
}
