"use client";

import * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { useMemo } from "react";
import { useIntelDocuments, useIntelOverview } from "@/hooks/use-intel";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const FEED_TYPES = [
  { id: "website", label: "Website changes" },
  { id: "social", label: "Social activity" },
  { id: "ads", label: "Ad library" },
  { id: "seo", label: "SEO movements" },
] as const;

export default function IntelOverviewPage(): React.ReactElement {
  const { data: overviewData, isLoading: overviewLoading } = useIntelOverview();
  const { data: documentsData, isLoading: documentsLoading } = useIntelDocuments();

  const signals = overviewData?.signals ?? [];
  const docs = (documentsData?.documents ?? []) as Array<{
    document_id?: string;
    title?: string;
    source_type?: string;
    content_preview?: string;
    created_at?: string;
    url?: string;
    domain?: string;
    fetched_at?: string;
  }>;

  const stats = useMemo(() => {
    const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
    return {
      total: signals.length,
      highPriority: signals.filter((signal) => signal.severity === "high" || signal.severity === "critical").length,
      thisWeek: signals.filter((signal) => new Date(signal.createdAt).getTime() > weekAgo).length,
    };
  }, [signals]);

  return (
    <RouteShell
      eyebrow="Intel"
      title="Overview"
      description="Live intelligence feed from the backend signal stream and research documents."
      tags={["intel", "overview", "live"]}
      backHref={"/intel" as "/intel"}
      backLabel="Back to Intel"
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {FEED_TYPES.map((feed) => {
          const count = signals.filter((signal) => signal.type === feed.id).length;
          return (
            <Card key={feed.id} className="transition-shadow hover:shadow-md">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold">{count}</p>
                    <p className="text-sm text-[var(--muted-foreground)]">{feed.label}</p>
                  </div>
                  <Badge
                    variant="outline"
                    className={feed.id === "seo" ? "border-amber-200 bg-amber-50 text-amber-700" : "bg-blue-50 text-blue-700 border-blue-200"}
                  >
                    live
                  </Badge>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div>
        <h2 className="text-lg font-semibold">Recent artifacts</h2>
        <p className="text-sm text-[var(--muted-foreground)]">Latest documents returned by the intel backend</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {documentsLoading ? (
          <div className="col-span-full rounded-xl border border-[var(--border)] p-6 text-sm text-[var(--muted-foreground)]">
            Loading documents…
          </div>
        ) : docs.length === 0 ? (
          <div className="col-span-full rounded-xl border border-dashed border-[var(--border)] p-8 text-center text-sm text-[var(--muted-foreground)]">
            No research documents yet.
          </div>
        ) : (
          docs.map((artifact) => {
            const artifactId = artifact.document_id ?? artifact.url ?? artifact.title ?? "artifact";
            return (
              <Card key={artifactId} className="transition-shadow hover:shadow-md">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {artifact.source_type ?? "document"}
                        </Badge>
                        <span className="h-2 w-2 rounded-full bg-blue-500" />
                      </div>
                      <p className="mt-2 font-medium leading-snug">{artifact.title ?? artifact.url ?? "Research document"}</p>
                      <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                        {artifact.domain ?? artifact.source_type ?? "intel"} · {artifact.created_at ?? artifact.fetched_at ?? "recent"}
                      </p>
                      {artifact.content_preview && (
                        <p className="mt-2 text-sm text-[var(--muted-foreground)]">{artifact.content_preview}</p>
                      )}
                      <div className="mt-3">
                        <Link href={`/intel/overview/${artifactId}` as Route} className="text-xs text-[var(--accent)] hover:underline">
                          Open artifact →
                        </Link>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {overviewLoading ? (
        <Card className="border-amber-200 bg-amber-50/50">
          <CardContent className="p-4 text-sm text-amber-800">Loading overview metrics…</CardContent>
        </Card>
      ) : (
        <Card className="border-blue-200 bg-blue-50/50">
          <CardHeader>
            <CardTitle className="text-base">Overview metrics</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 text-sm md:grid-cols-3">
            <div>
              <p className="text-[var(--muted-foreground)]">Total signals</p>
              <p className="text-2xl font-semibold">{stats.total}</p>
            </div>
            <div>
              <p className="text-[var(--muted-foreground)]">This week</p>
              <p className="text-2xl font-semibold">{stats.thisWeek}</p>
            </div>
            <div>
              <p className="text-[var(--muted-foreground)]">High priority</p>
              <p className="text-2xl font-semibold text-red-600">{stats.highPriority}</p>
            </div>
          </CardContent>
        </Card>
      )}
    </RouteShell>
  );
}
