/**
 * RaptorFlow Office Feature Types
 *
 * Type-safe frontend models for the Office command desk.
 */

export interface OfficeState {
  activeCampaigns: number;
  activeCouncilSessions: number;
  openNudges: number;
  recentMuseConversations: number;
  updatedAt?: string;
}

export interface OfficeCampaignFront {
  campaignId: string;
  title: string;
  goal?: string;
  status: string;
  moveCount?: number;
  taskCount?: number;
  updatedAt?: string;
}

export interface OfficeMove {
  moveId: string;
  campaignId: string;
  sequenceNumber: number;
  moveType: string;
  title?: string;
  status: string;
  createdAt: string;
  expectedImpact?: string;
}

export interface OfficeArtifact {
  id: string;
  contentType: string;
  title?: string;
  createdAt: string;
  source?: string;
}

export interface OfficeAvatar {
  key: string;
  label: string;
  role: string;
  status: "available" | "busy" | "offline" | "unknown";
}

export interface OfficeCouncilActivity {
  sessionId?: string;
  status?: string;
  mode?: string;
  createdAt?: string;
  completedAt?: string;
}

export const CANONICAL_AVATARS: OfficeAvatar[] = [
  { key: "strategist", label: "Strategist", role: "Strategy", status: "unknown" },
  { key: "researcher", label: "Researcher", role: "Research", status: "unknown" },
  { key: "copywriter", label: "Copywriter", role: "Copy", status: "unknown" },
  { key: "growth_operator", label: "Growth Operator", role: "Growth Ops", status: "unknown" },
  { key: "analyst", label: "Analyst", role: "Analysis", status: "unknown" },
  {
    key: "creative_director",
    label: "Creative Director",
    role: "Creative Direction",
    status: "unknown",
  },
  { key: "proof_collector", label: "Proof Collector", role: "Proof", status: "unknown" },
];
