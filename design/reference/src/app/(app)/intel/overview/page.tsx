"use client";

import type * as React from "react";
import { useOfficeStore } from "@/state/office-store";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const FEED_TYPES = [
  { id: "competitor-screenshots", label: "Competitor screenshots", count: 3, last: "2h ago", severity: "info" },
  { id: "ad-library", label: "Ad library captures", count: 7, last: "4h ago", severity: "info" },
  { id: "serp-rankings", label: "SERP ranking changes", count: 12, last: "1h ago", severity: "warning" },
  { id: "social-monitoring", label: "Social monitoring", count: 5, last: "30m ago", severity: "info" },
];

const MOCK_ARTIFACTS = [
  { id: "screenshot-001", type: "Competitor screenshot", source: "Competitor intel", severity: "major", time: "2h ago", preview: "Screenshot of competitor pricing page" },
  { id: "ad-001", type: "Ad creative", source: "Ad library", severity: "warning", time: "4h ago", preview: "Facebook ad from competitor X" },
  { id: "ranking-001", type: "SERP change", source: "SEO monitor", severity: "info", time: "1h ago", preview: "Keyword 'marketing automation' moved from #3 to #7" },
  { id: "social-001", type: "Social mention", source: "Social monitor", severity: "info", time: "30m ago", preview: "Competitor Y mentioned in 3 new posts" },
];

export default function IntelOverviewPage(): React.ReactElement {
  const eventLog = useOfficeStore((s) => s.eventLog);

  const intelEvents = eventLog.filter(
    (e) => e.eventType === "intel_alert_received"
  );

  return (
    <RouteShell
      eyebrow="Intel"
      title="Overview"
      description="Aggregated intelligence feed from all monitoring channels — competitor screenshots, ad captures, SERP rankings, and social mentions."
      tags={["intel", "overview", "competitor"]}
      backHref={"/intel" as "/intel"}
      backLabel="Back to Intel"
    >
      {/* Feed summary cards */}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {FEED_TYPES.map((feed) => (
          <Card key={feed.id} className="transition-shadow hover:shadow-md">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold">{feed.count}</p>
                  <p className="text-sm text-[var(--muted-foreground)]">{feed.label}</p>
                </div>
                <Badge
                  variant="outline"
                  className={
                    feed.severity === "warning"
                      ? "border-amber-200 bg-amber-50 text-amber-700"
                      : "bg-blue-50 text-blue-700 border-blue-200"
                  }
                >
                  {feed.last}
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent artifacts */}
      <div>
        <h2 className="text-lg font-semibold">Recent artifacts</h2>
        <p className="text-sm text-[var(--muted-foreground)]">Latest captured intelligence across all channels</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {MOCK_ARTIFACTS.map((artifact) => (
          <Card key={artifact.id} className="transition-shadow hover:shadow-md">
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">{artifact.type}</Badge>
                    <span className={`h-2 w-2 rounded-full ${
                      artifact.severity === "major" ? "bg-red-500" :
                      artifact.severity === "warning" ? "bg-amber-500" : "bg-blue-500"
                    }`} />
                  </div>
                  <p className="mt-2 font-medium leading-snug">{artifact.preview}</p>
                  <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                    {artifact.source} · {artifact.time}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Live WebSocket events */}
      {intelEvents.length > 0 && (
        <Card className="border-blue-200 bg-blue-50/50">
          <CardHeader>
            <CardTitle className="text-base">Live intel alerts (WebSocket)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {intelEvents.slice(-5).reverse().map((e, i) => (
                <div key={i} className="flex items-center gap-3 rounded-lg border border-blue-200 bg-white px-3 py-2 text-sm">
                  <span className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                  <span className="flex-1 truncate font-mono text-xs">
                    {JSON.stringify(e.payload).slice(0, 80)}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="border-amber-200 bg-amber-50/50">
        <CardHeader>
          <CardTitle className="text-base">📝 What to implement next</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-amber-800">
          <p><strong>Backend:</strong> Create <code>intelApi.listArtifacts(filters)</code> and <code>intelApi.getArtifact(id)</code> — paginated, filterable by type and date range.</p>
          <p><strong>Scraper pipeline:</strong> Wire actual scraper workers to populate this page — competitor screenshots (Playwright), ad library (Facebook/Google APIs), SERP rankings (SerpApi), social monitoring.</p>
          <p><strong>Alert aggregation:</strong> Intel events from the WebSocket should be processed and stored in the DB, not just displayed in the event log.</p>
          <p><strong>Thumbnail generation:</strong> Generate thumbnails for screenshots and ad creatives for compact card display.</p>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
