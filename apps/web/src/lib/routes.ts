export const ROUTES = {
  dashboard: "/app",
  dailyWins: "/daily-wins",
  office: "/office",
  muse: "/muse",
  campaigns: "/campaigns",
  campaignNew: "/campaigns/new",
  campaignDetail: (campaignId: string) => `/campaigns/${campaignId}`,
  campaignTask: (campaignId: string, taskId: string) => `/campaigns/${campaignId}/tasks/${taskId}`,
  content: "/content",
  council: "/council",
  intel: "/intel",
  intelArtifact: (artifactId: string) => `/intel/${artifactId}`,
  nudges: "/nudges",
  foundation: "/foundation",
  uploads: "/uploads",
  billing: "/billing",
  settings: "/settings",
  ripples: "/ripples",
  debug: "/internal/debug",
} as const;

export type RouteKey = keyof typeof ROUTES;
