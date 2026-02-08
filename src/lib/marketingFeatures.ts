import type { LucideIcon } from "lucide-react";
import { Brain, Compass, PenTool, Target } from "lucide-react";

export type MarketingFeature = {
  slug: string;
  title: string;
  subtitle: string;
  description: string;
  highlights: string[];
  image: string;
  icon: LucideIcon;
  primaryHref: string;
  primaryLabel: string;
  secondaryHref?: string;
  secondaryLabel?: string;
};

export const MARKETING_FEATURES: MarketingFeature[] = [
  {
    icon: Compass,
    slug: "marketing-foundation",
    title: "Marketing Foundation",
    subtitle: "Lay Your Strategic Groundwork",
    description:
      "Define your positioning, ideal customer profile, and messaging framework. Build the strategic foundation that guides all your marketing decisions.",
    highlights: ["ICP Definition", "Positioning Strategy", "Messaging Framework", "Channel Strategy"],
    image: "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=1600&q=80",
    primaryHref: "/foundation",
    primaryLabel: "Open Foundation",
  },
  {
    icon: Brain,
    slug: "cognitive-engine",
    title: "Cognitive Engine",
    subtitle: "AI That Understands Your Business",
    description:
      "Stateful AI analysis that supports better decisions. In reconstruction mode, only working integrations remain and failures are surfaced instead of hidden.",
    highlights: ["Error-Visible AI", "No Silent Fallbacks", "Workspace Scoped", "Integration-First"],
    image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1600&q=80",
    primaryHref: "/dashboard",
    primaryLabel: "Open Dashboard",
  },
  {
    icon: PenTool,
    slug: "muse",
    title: "Muse",
    subtitle: "Create Content That Converts",
    description:
      "AI-powered content generation that runs against real integrations. If the integration isn't configured, you will see a hard error (not fake content).",
    highlights: ["Prompts + Outputs", "Explicit Errors", "No Paywalls", "Workspace Scoped"],
    image: "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1600&q=80",
    primaryHref: "/muse",
    primaryLabel: "Open Muse",
  },
  {
    icon: Target,
    slug: "moves-campaigns",
    title: "Moves & Campaigns",
    subtitle: "Execute With Precision",
    description:
      "Plan campaigns, create weekly moves, track progress, and persist execution data to the database. No login walls, no payment gates.",
    highlights: ["Weekly Moves", "Campaign Planning", "Progress Tracking", "Database Persistence"],
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1600&q=80",
    primaryHref: "/moves",
    primaryLabel: "Open Moves",
    secondaryHref: "/campaigns",
    secondaryLabel: "Open Campaigns",
  },
];

export function getMarketingFeature(slug: string): MarketingFeature | undefined {
  return MARKETING_FEATURES.find((f) => f.slug === slug);
}

