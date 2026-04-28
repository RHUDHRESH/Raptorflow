"use client";

import type * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { DownloadIcon, MixerHorizontalIcon, ViewGridIcon } from "@radix-ui/react-icons";
import { contentApi } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { FileText } from "lucide-react";
import { renderGeneratedContent } from "@/components/content/renderer-registry";
import { AppPageFrame } from "@/components/layout/AppPageFrame";
import { AppEmptyState } from "@/components/layout/AppEmptyState";
import { AppLoadingState } from "@/components/layout/AppLoadingState";
import { AppErrorState } from "@/components/layout/AppErrorState";
import { AppPageSection } from "@/components/layout/AppPageSection";
import { StatusPill } from "@/components/windows/StatusPill";

export default function ContentPage(): React.ReactElement {
  const { data, isLoading, error } = useQuery({
    queryKey: ["content"],
    queryFn: () => contentApi.list(),
  });

  if (isLoading) {
    return (
      <AppPageFrame eyebrow="Content Engine" title="Content Ledger">
        <AppLoadingState label="Loading content archive..." />
      </AppPageFrame>
    );
  }

  if (error) {
    return (
      <AppPageFrame eyebrow="Content Engine" title="Content Ledger">
        <AppErrorState
          title="Failed to load content"
          description={error.message}
        />
      </AppPageFrame>
    );
  }

  const hasContent = (data?.length ?? 0) > 0;

  return (
    <AppPageFrame
      eyebrow="Content Engine"
      title="Content Ledger"
      description="Generated content from campaigns and council sessions."
      actions={
        <>
          <button disabled className="btn-secondary opacity-40 cursor-not-allowed">
            <MixerHorizontalIcon className="w-3.5 h-3.5" /> Filter
          </button>
          <button disabled className="btn-secondary opacity-40 cursor-not-allowed">
            <DownloadIcon className="w-3.5 h-3.5" /> Export
          </button>
        </>
      }
    >
      <GsapBridge stagger={true} className="space-y-4">
        {!hasContent ? (
          <AppEmptyState
            icon={<FileText className="w-6 h-6 text-[var(--ink-400)]" />}
            title="Content Archive Empty"
            description="No generated content has been persisted yet. Generate content from campaigns or the council."
          />
        ) : (
          data?.map((item) => (
            <AppPageSection
              key={item.contentId}
              eyebrow={item.contentType}
              title={String(item.body.headline ?? item.body.title ?? item.contentType)}
              actions={<StatusPill status={item.status} tone="neutral" />}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  {renderGeneratedContent(item.contentType, item.body)}
                </div>
                <span className="mono-label shrink-0">
                  {new Date(item.createdAt).toLocaleString()}
                </span>
              </div>
            </AppPageSection>
          ))
        )}
      </GsapBridge>
    </AppPageFrame>
  );
}
