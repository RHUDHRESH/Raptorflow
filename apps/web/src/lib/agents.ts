/**
 * RAPTORFLOW AGENT REGISTRY
 * Single source of truth for all 21 agents.
 * portrait: null = use brutalist monogram filler (intentional, not broken)
 */

export type AgentPod = "creative" | "digital" | "strategy" | "support" | "strategist";

export interface AgentConfig {
  key: string;
  displayName: string;
  shortName: string; // 2-char monogram
  role: string;
  pod: AgentPod;
  color: string; // CSS var or hex — used on canvas + UI
  portrait: string | null; // /agents/{name}.png or null → filler
  essenceCore: string; // Single-sentence identity summary
  zone: string; // Default office zone
}

export const AGENTS: AgentConfig[] = [
  /* ── Campaign Strategist ───────────────────────────────────── */
  {
    key: "strategist",
    displayName: "The Strategist",
    shortName: "ST",
    role: "Campaign Strategist",
    pod: "strategist",
    color: "#2A2529",
    portrait: null,
    essenceCore: "Synthesises expert disagreement into executable action for real businesses.",
    zone: "strategist-office",
  },

  /* ── Creative Pod ──────────────────────────────────────────── */
  {
    key: "ogilvy",
    displayName: "David Ogilvy",
    shortName: "OG",
    role: "Creative Director",
    pod: "creative",
    color: "#7c3aed",
    portrait: "/agents/ogilvy.png",
    essenceCore: "Research precedes creativity. The headline carries 80% of advertising weight.",
    zone: "creative-pod",
  },
  {
    key: "bernbach",
    displayName: "Bill Bernbach",
    shortName: "BB",
    role: "Creative Maverick",
    pod: "creative",
    color: "#0d9488",
    portrait: "/agents/bernbach.png",
    essenceCore:
      "Originality is the most powerful differentiator. Rules exist to be broken wisely.",
    zone: "creative-pod",
  },
  {
    key: "hopkins",
    displayName: "Claude Hopkins",
    shortName: "CH",
    role: "Direct Response Pioneer",
    pod: "creative",
    color: "#b45309",
    portrait: "/agents/hopkins.png",
    essenceCore:
      "Advertising is a science. Every ad is an experiment that produces actionable data.",
    zone: "creative-pod",
  },
  {
    key: "draper",
    displayName: "Don Draper",
    shortName: "DD",
    role: "Brand Storyteller",
    pod: "creative",
    color: "#6b21a8",
    portrait: "/agents/draper.png",
    essenceCore: "Every product is a story waiting to be told. Find the one true thing.",
    zone: "creative-pod",
  },

  /* ── Digital Pod ───────────────────────────────────────────── */
  {
    key: "patel",
    displayName: "Neil Patel",
    shortName: "NP",
    role: "Platform Intelligence",
    pod: "digital",
    color: "#0369a1",
    portrait: "/agents/patel.png",
    essenceCore: "Platform context changes faster than any framework. Distribution > content.",
    zone: "digital-pod",
  },
  {
    key: "vaynerchuk",
    displayName: "Gary Vaynerchuk",
    shortName: "GV",
    role: "Attention Strategist",
    pod: "digital",
    color: "#d97706",
    portrait: "/agents/vaynerchuk.png",
    essenceCore: "Attention is the scarcest resource. Authenticity is the only way to hold it.",
    zone: "digital-pod",
  },
  {
    key: "sharp",
    displayName: "Byron Sharp",
    shortName: "BS",
    role: "Brand Science",
    pod: "digital",
    color: "#15803d",
    portrait: null,
    essenceCore: "Brands grow by reaching new buyers. Mental availability beats differentiation.",
    zone: "digital-pod",
  },
  {
    key: "godin",
    displayName: "Seth Godin",
    shortName: "SG",
    role: "Tribe Builder",
    pod: "digital",
    color: "#4338ca",
    portrait: "/agents/godin.png",
    essenceCore: "Marketing exists to create connections. Ask who it's for before what to say.",
    zone: "digital-pod",
  },

  /* ── Strategy Pod ──────────────────────────────────────────── */
  {
    key: "kotler",
    displayName: "Philip Kotler",
    shortName: "PK",
    role: "Marketing Systems",
    pod: "strategy",
    color: "#0f766e",
    portrait: null,
    essenceCore:
      "Marketing is a systematic discipline. Price, product, place, promotion are one system.",
    zone: "conference-room",
  },
  {
    key: "ries",
    displayName: "Al Ries",
    shortName: "AR",
    role: "Positioning Strategist",
    pod: "strategy",
    color: "#be123c",
    portrait: null,
    essenceCore: "The battle is for the mind. Own a word, not a product.",
    zone: "conference-room",
  },
  {
    key: "cialdini",
    displayName: "Robert Cialdini",
    shortName: "RC",
    role: "Influence Architect",
    pod: "strategy",
    color: "#a16207",
    portrait: null,
    essenceCore:
      "The six principles are not manipulation — they are how human psychology actually works.",
    zone: "conference-room",
  },
  {
    key: "sutherland",
    displayName: "Rory Sutherland",
    shortName: "RS",
    role: "Behavioral Economist",
    pod: "strategy",
    color: "#9333ea",
    portrait: null,
    essenceCore: "The rational solution is almost always inferior to the psychological solution.",
    zone: "conference-room",
  },

  /* ── Support Wing ──────────────────────────────────────────── */
  {
    key: "qa-director",
    displayName: "QA Director",
    shortName: "QA",
    role: "Quality Assurance",
    pod: "support",
    color: "#dc2626",
    portrait: null,
    essenceCore: "The user should never receive something that embarrasses or misleads them.",
    zone: "research-station",
  },
  {
    key: "legal",
    displayName: "Legal Advisor",
    shortName: "LA",
    role: "Risk Identification",
    pod: "support",
    color: "#64748b",
    portrait: null,
    essenceCore: "Risk identification, not legal advice. Flag first, escalate to humans.",
    zone: "research-station",
  },
  {
    key: "analytics",
    displayName: "Analytics Director",
    shortName: "AD",
    role: "Performance Intelligence",
    pod: "support",
    color: "#0284c7",
    portrait: null,
    essenceCore:
      "Performance data tells a story. Understanding it requires statistics and business judgment.",
    zone: "research-station",
  },
  {
    key: "brand",
    displayName: "Brand Manager",
    shortName: "BM",
    role: "Brand Consistency",
    pod: "support",
    color: "#db2777",
    portrait: null,
    essenceCore: "Brand consistency is not cosmetic — it is the structural asset that compounds.",
    zone: "research-station",
  },
  {
    key: "research",
    displayName: "Research Lead",
    shortName: "RL",
    role: "Market Intelligence",
    pod: "support",
    color: "#7c3aed",
    portrait: null,
    essenceCore: "Strategy requires evidence. Evidence requires systematic research.",
    zone: "research-station",
  },
  {
    key: "media",
    displayName: "Media Buyer",
    shortName: "MB",
    role: "Budget Allocation",
    pod: "support",
    color: "#059669",
    portrait: null,
    essenceCore:
      "Advertising budget is finite. Imprecise allocation is waste as real as any other.",
    zone: "intern-bay",
  },
  {
    key: "pr",
    displayName: "PR Director",
    shortName: "PR",
    role: "Reputation Management",
    pod: "support",
    color: "#ca8a04",
    portrait: null,
    essenceCore:
      "A brand's reputation is its most valuable and fragile asset. Prevention beats reaction.",
    zone: "intern-bay",
  },
  {
    key: "growth",
    displayName: "Growth Hacker",
    shortName: "GH",
    role: "Growth Engineering",
    pod: "support",
    color: "#ea580c",
    portrait: null,
    essenceCore:
      "Growth is an engineering problem, not a creativity problem. Find the latent mechanism.",
    zone: "intern-bay",
  },
];

/** Lookup by key */
export const AGENT_MAP = new Map<string, AgentConfig>(AGENTS.map((a) => [a.key, a]));

/** Agents in a zone */
export function agentsInZone(zoneId: string): AgentConfig[] {
  return AGENTS.filter((a) => a.zone === zoneId);
}
