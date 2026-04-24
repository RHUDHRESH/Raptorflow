"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { use } from "react";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const MOCK_ASSETS: Record<string, {
  filename: string; size: number; contentType: string; uploadedAt: string; uploadedBy: string;
}> = {
  "screenshot-001": { filename: "competitor_hero_screenshot.png", size: 892416, contentType: "image/png", uploadedAt: "2025-04-10T09:00:00Z", uploadedBy: "Sharp" },
  "screenshot-002": { filename: "competitor_pricing_page.png", size: 654321, contentType: "image/png", uploadedAt: "2025-04-09T14:30:00Z", uploadedBy: "Sharp" },
  "screenshot-003": { filename: "competitor_cta_section.png", size: 432123, contentType: "image/png", uploadedAt: "2025-04-08T11:15:00Z", uploadedBy: "Sharp" },
};

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function AssetDetailPage({
  params
}: {
  params: Promise<{ assetId: string }>;
}): React.ReactElement {
  const { assetId } = use(params);
  const asset = MOCK_ASSETS[assetId] ?? Object.values(MOCK_ASSETS)[0];

  return (
    <RouteShell
      eyebrow="Asset detail"
      title={asset.filename}
      description="S3-backed asset with org-scoped access control."
      tags={["asset", "storage"]}
      backHref={"/uploads/assets" as Route}
      backLabel="Back to Asset Library"
    >
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Preview</CardTitle>
            </CardHeader>
            <CardContent>
              {asset.contentType.startsWith("image/") ? (
                <div className="flex h-64 w-full items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--muted)]">
                  <p className="text-sm text-[var(--muted-foreground)]">
                    Image preview — requires S3 integration
                  </p>
                </div>
              ) : (
                <div className="flex h-64 w-full items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--muted)]">
                  <p className="text-sm text-[var(--muted-foreground)]">
                    Preview not available for {asset.contentType}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">File metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <p className="text-[var(--muted-foreground)]">Filename</p>
                <p className="font-mono text-xs">{asset.filename}</p>
              </div>
              <div>
                <p className="text-[var(--muted-foreground)]">Size</p>
                <p className="font-medium">{formatBytes(asset.size)}</p>
              </div>
              <div>
                <p className="text-[var(--muted-foreground)]">Type</p>
                <Badge variant="outline">{asset.contentType}</Badge>
              </div>
              <div>
                <p className="text-[var(--muted-foreground)]">Uploaded</p>
                <p className="font-medium">{new Date(asset.uploadedAt).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}</p>
              </div>
              <div>
                <p className="text-[var(--muted-foreground)]">Uploaded by</p>
                <p className="font-medium">{asset.uploadedBy}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full" size="sm" variant="secondary">Download</Button>
              <Button className="w-full" size="sm" variant="secondary">Copy S3 URL</Button>
              <Button className="w-full" size="sm" variant="destructive">Delete</Button>
            </CardContent>
          </Card>

          <Card className="border-amber-200 bg-amber-50/50">
            <CardHeader>
              <CardTitle className="text-base">📝 What to implement next</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-amber-800">
              <p><strong>Backend:</strong> Add <code>uploadsApi.getAsset(assetId)</code> returning S3 presigned URL + metadata.</p>
              <p><strong>Preview:</strong> Use S3 presigned URL to render actual image/file preview in the preview pane.</p>
              <p><strong>Provenance trail:</strong> Show which Foundation step, campaign, or council session this asset was created from.</p>
              <p><strong>Access control:</strong> Verify org membership before serving presigned URLs — assets are org-scoped.</p>
              <p><strong>PDF viewer:</strong> Embedded PDF viewer for document assets using react-pdf or similar.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </RouteShell>
  );
}
