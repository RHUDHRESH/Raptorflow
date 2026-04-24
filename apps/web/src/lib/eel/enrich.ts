export interface EELContextPack {
  avatarName: string;
  sessionCount: number;
  agreementRate: number;
  behaviourDescriptors: string[];
  reflectionGate: string;
}

export async function enrichAvatarContext(
  _userId: string,
  _avatarKey: string,
): Promise<EELContextPack> {
  throw new Error("migrated_to_rust_api: enrichAvatarContext is no longer available");
}
