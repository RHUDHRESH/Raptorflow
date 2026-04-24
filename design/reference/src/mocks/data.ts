import type {
  FoundationResponse,
  Campaign,
  CouncilSession,
  MuseConversation,
  Ripple,
  Essence,
  BillingStatus,
  FoundationSnapshot,
} from "@/lib/api";

const ORG_ID = "00000000-0000-0000-0000-000000000000";

export const mockFoundation: FoundationResponse = {
  orgId: ORG_ID,
  version: 3,
  sections: {
    url: "https://example.com",
    identityConfirmation: { confirmed: true },
    businessStageAndTeam: {
      stage: "growth",
      teamSize: "11-50",
      department: "marketing",
    },
    whatYouActuallySell: {
      primaryOffering: "Marketing automation software",
      secondaryOfferings: ["Consulting", "Training"],
    },
    theProblemYouSolve: {
      primaryProblem: "Campaign execution is slow and siloed",
      secondaryProblems: ["Limited visibility into performance", "Content bottlenecks"],
    },
    primaryIcp: {
      industries: ["SaaS", "E-commerce"],
      companySize: "50-500 employees",
      roles: ["VP Marketing", "CMO", "Marketing Director"],
    },
    secondaryIcps: [],
    competitiveLandscape: [
      { name: "HubSpot", differentiation: "All-in-one but expensive" },
      { name: "Marketo", differentiation: "Enterprise but complex" },
    ],
    competitiveDifferentiation: "AI-native with council deliberation",
    positioningStatement:
      "For growth-stage B2B SaaS companies who need marketing execution at speed, RaptorFlow is an AI-powered marketing OS that delivers campaigns faster than traditional agencies because your AI council works 24/7.",
    brandPersonality: {
      voice: "Confident but not arrogant",
      tone: "Professional with personality",
      values: ["Speed", "Clarity", "Memory"],
    },
    voiceInPractice: "We speak like a smart friend who knows marketing inside out.",
    contentTerritories: ["Campaign strategy", "Content production", "Performance analytics"],
    marketingChannels: ["LinkedIn", "Content marketing", "Webinars"],
    goalsAndKpis: {
      primaryGoal: "Increase qualified pipeline",
      secondaryGoals: ["Brand awareness", "Customer retention"],
      kpis: ["MQLs", "Conversion rate", "CAC"],
    },
    keywordsAndSeo: {
      primary: ["AI marketing", "marketing automation", "campaign management"],
      secondary: ["content workflow", "marketing operations"],
    },
    existingAssets: ["Brand guidelines PDF", "Case studies (3)"],
    currentFrustrations: ["Slow content turnaround", "No single source of truth"],
    existingTools: ["Salesforce", "Slack", "Google Analytics"],
    referenceBrands: ["Jasper", "Copy.ai", "Intercom"],
    campaignStrategist: {
      approach: "Council-driven",
      deliberationRounds: 3,
    },
  },
  updatedAt: new Date().toISOString(),
};

export const mockCampaigns: Campaign[] = [
  {
    campaignId: "campaign-001",
    orgId: ORG_ID,
    name: "Q2 Growth Push",
    status: "active",
    goal: "Generate 500 MQLs in Q2",
    timeline: "2025-04-01 to 2025-06-30",
    channels: ["LinkedIn", "Content", "Email"],
    createdAt: "2025-04-01T00:00:00Z",
    updatedAt: new Date().toISOString(),
  },
  {
    campaignId: "campaign-002",
    orgId: ORG_ID,
    name: "Product Launch — RaptorFlow 2.0",
    status: "draft",
    goal: "Drive awareness for v2 launch",
    timeline: "2025-05-01 to 2025-06-30",
    channels: ["Content", "Webinars"],
    createdAt: "2025-04-10T00:00:00Z",
    updatedAt: new Date().toISOString(),
  },
  {
    campaignId: "campaign-003",
    orgId: ORG_ID,
    name: "Enterprise Outreach",
    status: "paused",
    goal: "Book 20 enterprise demos",
    timeline: "2025-03-01 to 2025-05-31",
    channels: ["LinkedIn", "Cold email"],
    createdAt: "2025-03-01T00:00:00Z",
    updatedAt: new Date().toISOString(),
  },
];

export const mockCouncilSessions: CouncilSession[] = [
  {
    sessionId: "session-001",
    orgId: ORG_ID,
    campaignId: "campaign-001",
    sessionType: "strategic",
    status: "completed",
    createdAt: "2025-04-05T10:00:00Z",
  },
  {
    sessionId: "session-002",
    orgId: ORG_ID,
    campaignId: "campaign-001",
    sessionType: "tactical",
    status: "running",
    createdAt: new Date().toISOString(),
  },
];

export const mockMuseConversations: MuseConversation[] = [
  {
    conversationId: "conv-001",
    orgId: ORG_ID,
    route: "strategic",
    lastMessageAt: new Date().toISOString(),
    messageCount: 12,
  },
  {
    conversationId: "conv-002",
    orgId: ORG_ID,
    route: "content",
    lastMessageAt: new Date(Date.now() - 3600000).toISOString(),
    messageCount: 5,
  },
];

export const mockRipples: Ripple[] = [
  {
    rippleId: "ripple-001",
    orgId: ORG_ID,
    coreClaim:
      "LinkedIn thought leadership content drives 3x more engagement than product-focused content for B2B SaaS",
    keyReasoning:
      "Analysis of 50 campaigns shows ICP engages with strategic thinking before product features",
    prediction: "Shift to 70/30 strategic/product content ratio by Q3",
    source: "campaign-001",
    confidence: 0.82,
    protectionBand: "protected",
    createdAt: "2025-04-10T00:00:00Z",
  },
  {
    rippleId: "ripple-002",
    orgId: ORG_ID,
    coreClaim: "Email sequences with personalized video thumbnails see 40% higher open rates",
    keyReasoning: "A/B test across 10k send volume confirmed hypothesis",
    source: "campaign-003",
    confidence: 0.75,
    protectionBand: "important",
    createdAt: "2025-04-12T00:00:00Z",
  },
];

export const mockEssences: Essence[] = [
  {
    essenceId: "essence-001",
    orgId: ORG_ID,
    avatarKey: "ogilvy",
    content:
      "The best marketing doesn't feel like marketing — it feels like a conversation between friends who happen to know something valuable.",
    category: "positioning",
    createdAt: "2025-04-01T00:00:00Z",
  },
  {
    essenceId: "essence-002",
    orgId: ORG_ID,
    avatarKey: "cialdini",
    content:
      "Social proof works best when it's specific and unexpected. Generic testimonials are background noise.",
    category: "persuasion",
    createdAt: "2025-04-02T00:00:00Z",
  },
];

export const mockBillingStatus: BillingStatus = {
  plan: "starter",
  status: "active",
  currentPeriodEnd: "2025-05-01T00:00:00Z",
  invoiceCount: 3,
};

export const mockFoundationSnapshots: FoundationSnapshot[] = [
  {
    id: "snapshot-001",
    orgId: ORG_ID,
    foundationVersion: 1,
    sections: mockFoundation.sections,
    createdAt: "2025-04-01T00:00:00Z",
  },
  {
    id: "snapshot-002",
    orgId: ORG_ID,
    foundationVersion: 2,
    sections: mockFoundation.sections,
    createdAt: "2025-04-05T00:00:00Z",
  },
  {
    id: "snapshot-003",
    orgId: ORG_ID,
    foundationVersion: 3,
    sections: mockFoundation.sections,
    createdAt: "2025-04-10T00:00:00Z",
  },
];

const MOCK_DATA: Record<string, unknown> = {
  "/api/v1/foundation": mockFoundation,
  "/api/v1/campaigns": mockCampaigns,
  "/api/v1/council/history": mockCouncilSessions,
  "/api/v1/muse/history": mockMuseConversations,
  "/api/v1/ripples": mockRipples,
  "/api/v1/essences": mockEssences,
  "/api/v1/billing": mockBillingStatus,
  "/api/v1/foundation/snapshots": mockFoundationSnapshots,
};

export function getOfflineData(path: string): Promise<unknown> {
  return Promise.resolve(MOCK_DATA[path] ?? null);
}

const OFFLINE_MUTATION_RESULTS: Record<string, Record<string, unknown>> = {
  "POST:/api/v1/foundation": { id: "foundation-001", version: 1 },
  "POST:/api/v1/campaigns": { campaignId: "campaign-new-001", status: "draft" },
  "POST:/api/v1/council": { sessionId: "session-new-001", status: "queued" },
  "POST:/api/v1/muse": { conversationId: "conv-new-001" },
  "POST:/api/v1/ripples": { rippleId: "ripple-new-001" },
  "POST:/api/v1/essences": { essenceId: "essence-new-001" },
  "POST:/api/v1/prl/decay": { processed: 0 },
  "POST:/api/v1/foundation/scan": { scanId: "scan-new-001", status: "queued" },
  "POST:/api/v1/foundation/snapshots": { id: "snapshot-new-001", version: 99 },
  "POST:/api/v1/uploads": {
    uploadUrl: "https://mock-s3.local/upload",
    key: "mock-key",
    expiresAt: new Date(Date.now() + 3600000).toISOString(),
  },
  "POST:/api/v1/billing/orders": { orderId: "order-new-001", status: "pending" },
};

export function getOfflineMutationResult(path: string, method: string): unknown | null {
  const key = `${method}:${path}`;
  return OFFLINE_MUTATION_RESULTS[key] ?? null; // # FIXED: return null so api.ts throws 501 instead of silently faking success
}
