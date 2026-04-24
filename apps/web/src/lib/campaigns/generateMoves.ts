interface MoveInput {
  title: string;
  description: string;
  channel: string;
  priority: number;
  tasks: string[];
}

export async function generateMoves(_campaignId: string, _token: string): Promise<unknown[]> {
  throw new Error("migrated_to_rust_api: generateMoves is no longer available");
}
