import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { RouteCard, RouteShell } from "@/components/layout/route-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const intelFeeds = [
  "competitor website snapshots",
  "social monitoring",
  "ad library captures",
  "SERP ranking changes"
];

const intelArtifacts = [
  { href: "/intel/overview" as Route, label: "Overview artifact" },
  { href: "/intel/alerts" as Route, label: "Alert stream" },
  { href: "/intel/diffs" as Route, label: "Diff archive" }
] as const satisfies ReadonlyArray<{ href: Route; label: string }>;

export default function IntelPage(): React.ReactElement {
  return (
    <RouteShell
      eyebrow="Intelligence"
      title="Intel"
      description="A dedicated surface for competitor snapshots, diffs, rankings, and alert triage."
      tags={["web", "social", "ads", "serp"]}
      rail={
        <Card>
          <CardHeader>
            <CardTitle>Surface links</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {intelArtifacts.map((item) => (
              <Link key={item.href} href={item.href} className="block text-[var(--foreground)]">
                {item.label}
              </Link>
            ))}
          </CardContent>
        </Card>
      }
    >
      <RouteCard
        title="Feed coverage"
        body="This scaffold reserves the main intelligence lanes the source corpus describes, but the data layer remains stubbed until the scraper pipeline is wired in."
      />
      <RouteCard
        title="Source coverage"
        body="Each monitoring lane has a route shell so future work can attach payloads, diff views, and alert actions without reshaping the app tree."
        footer={
          <div className="flex flex-wrap gap-2">
            {intelFeeds.map((feed) => (
              <span key={feed} className="rounded-full border border-[var(--border)] bg-white/80 px-3 py-1 text-xs">
                {feed}
              </span>
            ))}
          </div>
        }
      />
    </RouteShell>
  );
}
