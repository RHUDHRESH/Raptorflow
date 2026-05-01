"use client";

import * as React from "react";
import { use } from "react";
import type { Route } from "next";
import Link from "next/link";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useIntelDocuments } from "@/hooks/use-intel";

export default function IntelOverviewArtifactPage({
  params,
}: {
  params: Promise<{ artifactId: string }>;
}): React.ReactElement {
  const { artifactId } = use(params);
  const { data, isLoading } = useIntelDocuments();
  const docs = (data?.documents ?? []) as Array<{
    document_id?: string;
    title?: string;
    source_type?: string;
    content_preview?: string;
    created_at?: string;
    url?: string;
    domain?: string;
    fetched_at?: string;
  }>;

  const artifact = docs.find(
    (doc) => doc.document_id === artifactId || doc.url === artifactId || doc.title === artifactId,
  );

  if (isLoading) {
    return (
      <div className="py-8 text-sm text-[var(--muted-foreground)]">
        Loading artifact from backend…
      </div>
    );
  }

  if (!artifact) {
    return (
      <RouteShell
        eyebrow="Intel overview"
        title="Artifact not found"
        description="The requested artifact does not exist in the live intel backend."
        tags={["intel", "artifact"]}
      >
        <Button asChild variant="secondary">
          <Link href={"/intel/overview" as Route}>Back to overview</Link>
        </Button>
      </RouteShell>
    );
  }

  return (
    <RouteShell
      eyebrow="Intel overview"
      title={artifact.title ?? "Research artifact"}
      description={artifact.content_preview ?? artifact.url ?? "Live backend artifact"}
      tags={["intel", "artifact", artifact.source_type ?? "document"]}
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
                  {artifact.content_preview ?? "No preview text available."}
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
                  <Badge variant="outline">{artifact.source_type ?? "document"}</Badge>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Source</p>
                  <p className="font-medium">
                    {artifact.domain ?? artifact.source_type ?? "intel"}
                  </p>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Artifact ID</p>
                  <p className="font-mono text-xs">{artifact.document_id ?? artifactId}</p>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Captured</p>
                  <p className="font-medium">
                    {artifact.created_at ?? artifact.fetched_at ?? "recent"}
                  </p>
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
              <Button className="w-full" size="sm" variant="secondary">
                Request re-capture
              </Button>
              <Button className="w-full" size="sm" variant="secondary">
                Add to diff tracker
              </Button>
              <Button className="w-full" size="sm" variant="ghost">
                Dismiss artifact
              </Button>
            </CardContent>
          </Card>

          <Card className="border-amber-200 bg-amber-50/50">
            <CardHeader>
              <CardTitle className="text-base">Backend truth</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-amber-800">
              <p>This detail page is backed by the live intel document feed.</p>
              <p>
                If you need more artifact metadata, extend the intel backend rather than adding
                local mock data.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </RouteShell>
  );
}
