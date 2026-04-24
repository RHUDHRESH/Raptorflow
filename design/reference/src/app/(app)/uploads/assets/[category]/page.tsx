"use client";

import * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const CATEGORY_META: Record<string, { label: string; description: string }> = {
  screenshots: { label: "Competitor screenshots", description: "Automated captures of competitor websites and ads" },
  "foundation-attachments": { label: "Foundation attachments", description: "Documents and assets attached to your Foundation" },
  "content-exports": { label: "Content exports", description: "Exported campaign content, briefs, and creative assets" },
  "office-assets": { label: "Office scene assets", description: "Agent avatars, speech bubble templates, zone maps" },
};

export default function AssetCategoryPage({
  params,
}: {
  params: Promise<{ category: string }>;
}): React.ReactElement {
  const resolvedParams = React.use(params);
  const { category } = resolvedParams;

  const meta = CATEGORY_META[category] ?? { label: category, description: `Assets in the "${category}" category` };

  return (
    <RouteShell
      eyebrow="Assets"
      title={meta.label}
      description={meta.description}
      tags={["assets", "library", category]}
      backHref="/uploads/assets"
      backLabel="Back to Asset Library"
    >
      <div className="flex items-center justify-between">
        <Badge variant="outline">{category}</Badge>
        <Button size="sm" variant="secondary">Upload to category</Button>
      </div>

      <Card>
        <CardContent className="flex flex-col items-center justify-center py-16 text-center">
          <p className="text-3xl">📁</p>
          <p className="mt-4 font-medium">Asset listing coming soon</p>
          <p className="mt-1 text-sm text-[var(--muted-foreground)]">
            This page will display assets from S3 for the <strong>{category}</strong> category.
            Backend integration with <code>uploadsApi.listAssets()</code> is pending.
          </p>
          <p className="mt-4 text-xs text-[var(--muted-foreground)]">
            Each asset card will show: thumbnail, filename, size, upload date, and action buttons.
          </p>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <div className="flex aspect-video items-center justify-center rounded-lg border border-dashed border-[var(--border)] bg-[var(--muted)]">
                <span className="text-2xl text-[var(--muted-foreground)]">📄</span>
              </div>
              <div className="mt-3 space-y-1">
                <div className="h-3 w-24 animate-pulse rounded bg-[var(--muted)]" />
                <div className="h-3 w-16 animate-pulse rounded bg-[var(--muted)]" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </RouteShell>
  );
}
