"use client";

import type * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { DownloadIcon, MixerHorizontalIcon, ViewGridIcon } from "@radix-ui/react-icons";
import { contentApi } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

export default function ContentPage(): React.ReactElement {
  const { data, isLoading } = useQuery({
    queryKey: ["content"],
    queryFn: () => contentApi.list(),
  });

  return (
    <div className="min-h-[calc(100vh-theme(spacing.16))] bg-[var(--background)] p-8 md:p-12 font-body">
      <GsapBridge stagger={true} className="mx-auto max-w-[1400px]">
        {/* Header */}
        <div className="gsap-reveal flex items-end justify-between border-b-2 border-[var(--foreground)] pb-8 mb-12">
          <div>
            <p className="font-mono text-[10px] font-bold uppercase tracking-[0.25em] text-[var(--muted-foreground)] mb-2">
              Content Engine
            </p>
            <h1 className="font-[family-name:var(--font-display)] text-5xl">Content</h1>
          </div>
          <div className="flex gap-3">
            <button disabled className="border border-[var(--border)] bg-transparent px-4 h-10 font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)] flex items-center gap-2 opacity-40 cursor-not-allowed">
              <MixerHorizontalIcon className="h-3.5 w-3.5" /> Filter
            </button>
            <button disabled className="border border-[var(--border)] bg-transparent px-4 h-10 font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)] flex items-center gap-2 opacity-40 cursor-not-allowed">
              <ViewGridIcon className="h-3.5 w-3.5" /> Grid
            </button>
            <button disabled className="border border-[var(--border)] bg-transparent px-4 h-10 font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)] flex items-center gap-2 opacity-40 cursor-not-allowed">
              <DownloadIcon className="h-3.5 w-3.5" /> Export All
            </button>
          </div>
        </div>

        <div className="gsap-reveal space-y-4">
          {isLoading ? (
            <>
              <Skeleton className="h-28 w-full rounded-none" />
              <Skeleton className="h-28 w-full rounded-none" />
              <Skeleton className="h-28 w-full rounded-none" />
            </>
          ) : (data?.length ?? 0) === 0 ? (
            <div className="border border-[var(--border)] p-8">
              <p className="font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)] mb-4">
                Content Archive Empty
              </p>
              <p className="text-sm text-[var(--muted-foreground)] leading-relaxed">
                No generated content has been persisted for this tenant yet. This page now reflects the real backend content archive rather than a placeholder demo state.
              </p>
            </div>
          ) : (
            data?.map((item) => (
              <div key={item.contentId} className="border border-[var(--border)] bg-[var(--card)] p-6">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-mono text-[10px] uppercase tracking-widest text-[#D97757] mb-2">
                      {item.contentType}
                    </p>
                    <h2 className="font-[family-name:var(--font-display)] text-2xl leading-tight">
                      {String(item.body.headline ?? item.body.title ?? item.contentType)}
                    </h2>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-[9px] uppercase tracking-widest text-[var(--muted-foreground)]">
                      {item.status}
                    </p>
                    <p className="font-mono text-[9px] text-[var(--muted-foreground)] mt-1">
                      {new Date(item.createdAt).toLocaleString()}
                    </p>
                  </div>
                </div>
                <pre className="mt-4 overflow-x-auto whitespace-pre-wrap text-xs text-[var(--muted-foreground)]">
                  {JSON.stringify(item.body, null, 2)}
                </pre>
              </div>
            ))
          )}
        </div>
      </GsapBridge>
    </div>
  );
}
