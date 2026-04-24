"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ASSET_CATEGORIES = [
  {
    id: "screenshots",
    label: "Competitor screenshots",
    description: "Automated captures of competitor websites and ads",
    count: 3,
    lastUpdated: "2025-04-10",
  },
  {
    id: "foundation-attachments",
    label: "Foundation attachments",
    description: "Documents and assets attached to your Foundation",
    count: 5,
    lastUpdated: "2025-04-08",
  },
  {
    id: "content-exports",
    label: "Content exports",
    description: "Exported campaign content, briefs, and creative assets",
    count: 12,
    lastUpdated: "2025-04-05",
  },
  {
    id: "office-assets",
    label: "Office scene assets",
    description: "Agent avatars, speech bubble templates, zone maps",
    count: 8,
    lastUpdated: "2025-03-20",
  },
];

export default function UploadAssetsPage(): React.ReactElement {
  return (
    <RouteShell
      eyebrow="Assets"
      title="Asset Library"
      description="Storage-backed artifacts organized by category — screenshots, Foundation attachments, content exports, and office scene assets."
      tags={["assets", "library", "s3"]}
      backHref={"/uploads" as Route}
      backLabel="Back to Uploads"
    >
      <div className="flex items-center justify-between">
        <p className="text-sm text-[var(--muted-foreground)]">
          {ASSET_CATEGORIES.reduce((sum, c) => sum + c.count, 0)} total assets
        </p>
        <Button size="sm" variant="secondary">Refresh from storage</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {ASSET_CATEGORIES.map((cat) => (
          <Card key={cat.id} className="transition-shadow hover:shadow-md">
            <CardContent className="p-6">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="font-semibold">{cat.label}</p>
                  <p className="mt-1 text-sm text-[var(--muted-foreground)]">{cat.description}</p>
                </div>
                <Badge variant="outline">{cat.count}</Badge>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <p className="text-xs text-[var(--muted-foreground)]">
                  Updated {cat.lastUpdated}
                </p>
                <Link
                  href={`/uploads/assets/${cat.id}` as Route}
                  className="text-xs text-[var(--accent)] hover:underline"
                >
                  Browse →
                </Link>
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
          <p><strong>Backend:</strong> Add <code>uploadsApi.listAssets(category)</code> — paginated S3-backed asset listing per org.</p>
          <p><strong>Category pages:</strong> Each <code>/uploads/assets/[category]</code> should show a grid of actual asset thumbnails from S3.</p>
          <p><strong>Asset preview:</strong> Clicking an asset opens <code>/uploads/assets/[category]/[assetId]</code> with full preview (PDF viewer, image lightbox, video player).</p>
          <p><strong>Upload to category:</strong> Allow direct upload to a specific category from the asset library.</p>
          <p><strong>Search:</strong> Full-text search across asset filenames and metadata.</p>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
