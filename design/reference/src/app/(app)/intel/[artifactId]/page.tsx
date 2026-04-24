"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { use } from "react";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ARTIFACT_TYPES: Record<string, { type: string; description: string; source: string }> = {
  "competitor-website-snapshot": { type: "Screenshot", description: "Competitor website captured via automated scraper.", source: "Competitor intel pipeline" },
  "ad-library-capture": { type: "Ad", description: "Facebook/Google ad creative captured from ad library.", source: "Ad intelligence pipeline" },
  "serp-ranking-change": { type: "Ranking", description: "SERP ranking change detected for tracked keyword.", source: "SEO monitoring pipeline" },
};

export default function IntelArtifactPage({
  params
}: {
  params: Promise<{ artifactId: string }>;
}): React.ReactElement {
  const { artifactId } = use(params);
  const artifact = ARTIFACT_TYPES[artifactId] ?? {
    type: "Artifact",
    description: `Intel artifact ${artifactId}`,
    source: "Unknown source",
  };

  return (
    <RouteShell
      eyebrow="Intel artifact"
      title={artifact.type}
      description={artifact.description}
      tags={["intel", "artifact"]}
      backHref={"/intel" as Route}
      backLabel="Back to Intel"
    >
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Artifact preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex h-64 w-full items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--muted)]">
                <p className="text-sm text-[var(--muted-foreground)]">
                  Artifact preview — scraper pipeline integration required
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Artifact metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-[var(--muted-foreground)]">Type</p>
                  <Badge variant="outline">{artifact.type}</Badge>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Source</p>
                  <p className="font-medium">{artifact.source}</p>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Artifact ID</p>
                  <p className="font-mono text-xs">{artifactId}</p>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Captured</p>
                  <p className="font-medium">Pipeline integration required</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full" size="sm" variant="secondary">Request re-capture</Button>
              <Button className="w-full" size="sm" variant="secondary">Add to diff tracker</Button>
              <Button className="w-full" size="sm" variant="ghost">Dismiss artifact</Button>
            </CardContent>
          </Card>

          <Card className="border-amber-200 bg-amber-50/50">
            <CardHeader>
              <CardTitle className="text-base">📝 Scraper pipeline required</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-amber-800">
              <p>This page awaits the intel scraper pipeline. Required components:</p>
              <ol className="list-inside list-decimal space-y-1">
                <li><strong>Screenshot pipeline:</strong> Playwright-based competitor website capture</li>
                <li><strong>Ad library scraper:</strong> Facebook Ad Library + Google Ad transparency API</li>
                <li><strong>SERP tracker:</strong> Automated ranking checks via SerpApi or custom scraper</li>
                <li><strong>Storage:</strong> S3-backed artifact storage with org-scoped access</li>
                <li><strong>API:</strong> <code>intelApi.getArtifact(id)</code> and <code>intelApi.listArtifacts(filters)</code></li>
              </ol>
              <p>Each artifact type needs a dedicated scraper worker in the jobs system.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </RouteShell>
  );
}
