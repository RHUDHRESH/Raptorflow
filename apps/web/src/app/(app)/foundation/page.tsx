import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { RouteShell } from "@/components/layout/route-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const screens = [
  { slug: "url", title: "URL" },
  { slug: "identity-confirmation", title: "Identity Confirmation" },
  { slug: "business-stage-and-team", title: "Business Stage and Team" },
  { slug: "what-you-actually-sell", title: "What You Actually Sell" },
  { slug: "the-problem-you-solve", title: "The Problem You Solve" },
  { slug: "primary-icp", title: "Primary ICP" },
  { slug: "secondary-icps", title: "Secondary ICPs" },
  { slug: "competitive-landscape", title: "Competitive Landscape" },
  { slug: "competitive-differentiation", title: "Competitive Differentiation" },
  { slug: "positioning-statement", title: "Positioning Statement" },
  { slug: "brand-personality", title: "Brand Personality" },
  { slug: "voice-in-practice", title: "Voice in Practice" },
  { slug: "content-territories", title: "Content Territories" },
  { slug: "marketing-channels", title: "Marketing Channels" },
  { slug: "goals-and-kpis", title: "Goals and KPIs" },
  { slug: "keywords-and-seo", title: "Keywords and SEO" },
  { slug: "existing-assets", title: "Existing Assets" },
  { slug: "current-frustrations", title: "Current Frustrations" },
  { slug: "existing-tools", title: "Existing Tools" },
  { slug: "reference-brands", title: "Reference Brands" },
  { slug: "campaign-strategist", title: "Campaign Strategist" }
];

export default function FoundationPage(): React.ReactElement {
  return (
    <RouteShell
      eyebrow="Foundation"
      title="Twenty-one screen scaffold"
      description="The Foundation is now broken into explicit route surfaces so each screen can be implemented independently."
      tags={["scan", "versioned", "prompt-injection"]}
      rail={
        <Card>
          <CardHeader>
            <CardTitle>Foundation flows</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p>Quick scan, deep scan, and version history all get their own future hooks.</p>
            <Link href={"/foundation/url" as Route} className="block text-[var(--foreground)]">
              Start at URL
            </Link>
          </CardContent>
        </Card>
      }
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {screens.map((screen, index) => (
          <Link key={screen.slug} href={`/foundation/${screen.slug}` as Route}>
            <Card className="h-full transition-transform hover:-translate-y-0.5">
              <CardHeader>
                <CardTitle>
                  Screen {index + 1}: {screen.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-[var(--muted-foreground)]">
                Reserved route content, form contract, websocket hooks, and autosave behavior.
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </RouteShell>
  );
}
