interface DailyWinResult {
  id: string;
  userId: string;
  date: Date;
  briefing: Record<string, unknown>;
  highlights: string[];
  focusAreas: string[];
  systemActivity: Record<string, unknown>;
  isRead: boolean;
  createdAt: Date;
}

export async function generateDailyWin(
  _userId: string,
  _date: Date = new Date(),
): Promise<DailyWinResult> {
  throw new Error("migrated_to_rust_api: generateDailyWin is no longer available");
}
