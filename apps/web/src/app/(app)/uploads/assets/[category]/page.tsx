"use client";

import type * as React from "react";
import type { Route } from "next";
import { use } from "react";
import Link from "next/link";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const CATEGORY_META: Record<string, { title: string; description: string }> = {
  screenshots:         { title: "Competitor Screenshots", description: "Automated captures of competitor websites and ads." },
  "foundation-attachments": { title: "Foundation Attachments", description: "Documents and assets attached to your Foundation." },
  "content-exports":   { title: "Content Exports", description: "Exported campaign content, briefs, and creative assets." },
  "office-assets":     { title: "Office Scene Assets", description: "Agent avatars, speech bubble templates, zone maps." },
};

export default function CategoryAssetsPage({
  params,
}: {
  params: Promise<{ category: string }>;
}): React.ReactElement {
  const { category } = use(params);
  const meta = CATEGORY_META[category] ?? {
    title: category,
    description: "Assets in this category.",
  };

  return (
    <RouteShell
      eyebrow={`Assets / ${category}`}
      title={meta.title}
      description={meta.description}
      tags={["assets", "storage", category]}
      backHref={"/uploads/assets" as Route}
      backLabel="Back to Asset Library"
    >
      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-[var(--muted-foreground)]">
          Loading assets from storage…
        </p>
        <Button size="sm" variant="secondary">Refresh</Button>
      </div>

      {/* Honest degradation — S3 asset listing not yet wired */}
      <Card className="border-zinc-800 bg-zinc-900/40">
        <CardHeader>
          <CardTitle className="text-base font-mono text-xs uppercase tracking-widest text-zinc-500">
            Backend Pending
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-zinc-500">
          <p>
            Asset listing for <Badge variant="outline" className="font-mono text-xs">{category}</Badge> requires{" "}
            <code>uploadsApi.listAssets(category)</code> — paginated S3-backed asset listing per org.
          </p>
          <p>
            Once wired, this page will show a filterable grid of actual asset thumbnails with download and delete actions.
          </p>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
