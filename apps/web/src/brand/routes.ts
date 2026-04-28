/**
 * RaptorFlow Canonical Route Metadata
 *
 * Single source of truth for app route labels, grouping, and descriptions.
 * Do not alter Next.js routing behavior here. This is metadata only.
 */

export interface RouteMeta {
  href: string;
  label: string;
  shortLabel: string;
  group: "workspace" | "intelligence" | "strategy" | "system";
  description: string;
}

export const routes: Record<string, RouteMeta> = {
  dashboard: {
    href: "/app/dashboard",
    label: "Dashboard",
    shortLabel: "Dash",
    group: "workspace",
    description: "Your daily briefing and operational overview.",
  },
  office: {
    href: "/office",
    label: "The Office",
    shortLabel: "Office",
    group: "workspace",
    description: "Where campaigns become moves.",
  },
  campaigns: {
    href: "/campaigns",
    label: "Campaigns",
    shortLabel: "Campaigns",
    group: "strategy",
    description: "Active marketing campaigns and moves.",
  },
  council: {
    href: "/council",
    label: "Council",
    shortLabel: "Council",
    group: "strategy",
    description: "Strategic council war room sessions.",
  },
  muse: {
    href: "/muse",
    label: "Muse",
    shortLabel: "Muse",
    group: "strategy",
    description: "AI creative partner and ideation.",
  },
  content: {
    href: "/content",
    label: "Content",
    shortLabel: "Content",
    group: "strategy",
    description: "Content ledger and editorial pipeline.",
  },
  foundation: {
    href: "/foundation",
    label: "Foundation",
    shortLabel: "Foundation",
    group: "system",
    description: "Brand positioning and foundation data.",
  },
  intel: {
    href: "/intel",
    label: "Intel",
    shortLabel: "Intel",
    group: "intelligence",
    description: "Market signals and intelligence feed.",
  },
  nudges: {
    href: "/nudges",
    label: "Nudges",
    shortLabel: "Nudges",
    group: "intelligence",
    description: "Actionable nudges and alerts.",
  },
  ripples: {
    href: "/ripples",
    label: "Ripples",
    shortLabel: "Ripples",
    group: "intelligence",
    description: "Impact tracking and ripple effects.",
  },
  uploads: {
    href: "/uploads",
    label: "Uploads",
    shortLabel: "Uploads",
    group: "workspace",
    description: "File uploads and asset management.",
  },
  settings: {
    href: "/settings",
    label: "Settings",
    shortLabel: "Settings",
    group: "system",
    description: "Account and workspace settings.",
  },
} as const;

/** Ordered groups for navigation rendering. */
export const routeGroups = [
  {
    key: "workspace" as const,
    label: "Workspace",
    routes: [routes.dashboard, routes.office, routes.uploads],
  },
  {
    key: "intelligence" as const,
    label: "Intelligence",
    routes: [routes.intel, routes.nudges, routes.ripples],
  },
  {
    key: "strategy" as const,
    label: "Strategy",
    routes: [routes.campaigns, routes.council, routes.muse, routes.content],
  },
  {
    key: "system" as const,
    label: "System",
    routes: [routes.foundation, routes.settings],
  },
];
