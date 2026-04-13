export const routeCachePolicy = {
  api: "force-dynamic",
  marketing: "default",
  diagnostics: "force-dynamic"
} as const;

export const queryFreshness = {
  campaigns: 30_000,
  foundation: 60_000,
  intel: 15_000,
  dailyWins: 300_000
} as const;
