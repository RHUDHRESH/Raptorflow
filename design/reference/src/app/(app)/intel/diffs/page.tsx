"use client";

import type * as React from "react";
import { useState } from "react";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const MOCK_DIFFS = [
  {
    id: "diff-001",
    subject: "Competitor homepage copy",
    source: "Weekly scrape",
    date: "2025-04-10",
    status: "reviewed",
    changes: "+2 additions, -1 removal, -3 modifications",
    summary: "Competitor X changed hero headline from 'Automate Your Marketing' to 'Enterprise Marketing Automation Built for Scale'.",
  },
  {
    id: "diff-002",
    subject: "Competitor pricing page",
    source: "Weekly scrape",
    date: "2025-04-10",
    status: "pending",
    changes: "+1 addition, -2 removals, +4 modifications",
    summary: "Competitor Y removed 'Starting at $49/mo' and now shows 'Contact us for pricing'.",
  },
  {
    id: "diff-003",
    subject: "Facebook ad creative",
    source: "Ad library monitor",
    date: "2025-04-08",
    status: "pending",
    changes: "+3 additions, -1 removal",
    summary: "Competitor X launched 3 new ad variations targeting 'marketing ops teams'. Theme shifted from product-features to social-proof.",
  },
  {
    id: "diff-004",
    subject: "LinkedIn company description",
    source: "Social monitor",
    date: "2025-04-05",
    status: "reviewed",
    changes: "+2 additions",
    summary: "Competitor Z added 'AI-powered' and '2025 Gartner Magic Quadrant' claims to their LinkedIn description.",
  },
];

export default function IntelDiffsPage(): React.ReactElement {
  const [filter, setFilter] = useState<"all" | "pending" | "reviewed">("all");

  const filtered = filter === "all" ? MOCK_DIFFS : MOCK_DIFFS.filter((d) => d.status === filter);

  return (
    <RouteShell
      eyebrow="Intel"
      title="Diff archive"
      description="Historical record of tracked document and creative changes — competitor websites, ad creatives, and brand positioning."
      tags={["intel", "diffs", "tracking"]}
      backHref={"/intel" as "/intel"}
      backLabel="Back to Intel"
    >
      <div className="flex items-center justify-between">
        <p className="text-sm text-[var(--muted-foreground)]">{filtered.length} tracked diffs</p>
        <div className="flex gap-2">
          {(["all", "pending", "reviewed"] as const).map((f) => (
            <Button
              key={f}
              size="sm"
              variant={filter === f ? "default" : "outline"}
              onClick={() => setFilter(f)}
              className="capitalize"
            >
              {f}
            </Button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        {filtered.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <p className="text-3xl">📄</p>
              <p className="mt-4 font-medium">No diffs in this category</p>
            </CardContent>
          </Card>
        )}

        {filtered.map((diff) => (
          <Card key={diff.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="font-semibold">{diff.subject}</p>
                    <Badge
                      variant="outline"
                      className={
                        diff.status === "pending"
                          ? "border-amber-200 bg-amber-50 text-amber-700"
                          : "border-green-200 bg-green-50 text-green-700"
                      }
                    >
                      {diff.status}
                    </Badge>
                    <Badge variant="outline" className="text-xs">{diff.source}</Badge>
                  </div>
                  <p className="mt-1 text-sm text-[var(--muted-foreground)]">{diff.summary}</p>
                  <div className="mt-2 flex items-center gap-4 text-xs text-[var(--muted-foreground)]">
                    <span>{diff.date}</span>
                    <span>{diff.changes}</span>
                  </div>
                </div>
                <div className="flex flex-col gap-1 flex-shrink-0">
                  <Button size="sm" variant="secondary">View diff</Button>
                  {diff.status === "pending" && (
                    <Button size="sm" variant="ghost">Mark reviewed</Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-amber-200 bg-amber-50/50">
        <CardHeader>
          <CardTitle className="text-base">📝 What to implement next</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-amber-800">
          <p><strong>Backend:</strong> Create <code>diffApi.list(filters)</code> and <code>diffApi.markReviewed(id)</code> — diffs stored in DB with reviewed_at timestamp.</p>
          <p><strong>Diff engine:</strong> Wire scraper pipeline to compare each new artifact against the previous version — use diff-match-patch or similar for text, pixel-diff for images.</p>
          <p><strong>Diff viewer:</strong> Build a side-by-side diff view component — green for additions, red for removals, yellow for modifications.</p>
          <p><strong>Notifications:</strong> When a new diff is detected, create an alert and optionally trigger a nudge.</p>
          <p><strong>Archive policy:</strong> Auto-archive diffs older than 90 days unless marked as ongoing tracking.</p>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
