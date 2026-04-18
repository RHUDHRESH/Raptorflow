"use client";

import type * as React from "react";
import { useState } from "react";
import type { Route } from "next";
import Link from "next/link";
import { MagnifyingGlassIcon, GlobeIcon, Share2Icon, TargetIcon, ActivityLogIcon, ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { useIntelSignals, useIntelOverview, useResearchRuns, useIntelDocuments } from "@/hooks/use-intel";
import { type ResearchRun, type IntelDocument } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDistanceToNow } from "date-fns";

const CATEGORIES = [
  { name: "All Intelligence", value: "" },
  { name: "Website Changes", value: "website" },
  { name: "Social Activity", value: "social" },
  { name: "Ad Library", value: "ads" },
  { name: "SEO Movements", value: "seo" },
];

export default function IntelPage(): React.ReactElement {
  const [activeCategory, setActiveCategory] = useState("");
  const [activeView, setActiveView] = useState<"feed" | "runs" | "documents">("feed");
  
  const { data: signals, isLoading: isSignalsLoading } = useIntelSignals(activeCategory);
  const { data: overview, isLoading: isOverviewLoading } = useIntelOverview();
  const { data: runs, isLoading: isRunsLoading } = useResearchRuns();
  const { data: documents, isLoading: isDocsLoading } = useIntelDocuments();
  
  // Stats from overview
  const stats = overview;
  
  // Icon mapper
  const getIcon = (category: string) => {
    switch (category) {
      case 'website': return GlobeIcon;
      case 'social': return Share2Icon;
      case 'ads': return TargetIcon;
      default: return ActivityLogIcon;
    }
  };

  return (
    <div className="h-[calc(100vh-theme(spacing.16))] flex flex-col font-body">
      <GsapBridge stagger={true} className="flex-1 flex overflow-hidden">
        
        {/* Left Column: Feeds */}
        <aside className="gsap-reveal w-64 border-r border-[var(--border)] bg-[var(--card)] flex flex-col h-full">
          <div className="p-4 border-b border-[var(--border)]">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--muted-foreground)]" />
              <input 
                type="text" 
                placeholder="Search intelligence..." 
                className="w-full bg-transparent border border-[var(--border)] rounded-none h-10 pl-9 pr-4 text-sm focus:outline-none focus:ring-1 focus:ring-[var(--primary)] font-mono"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-1">
            <div className="text-[10px] font-mono uppercase tracking-widest text-[var(--muted-foreground)] mb-4">Feed Categories</div>
            {CATEGORIES.map(feed => (
              <button 
                key={feed.name} 
                onClick={() => setActiveCategory(feed.value)}
                className={`w-full text-left px-3 py-2 text-sm font-mono tracking-tight transition-colors ${activeCategory === feed.value ? "bg-[var(--primary)] text-[var(--primary-foreground)]" : "text-[var(--foreground)] hover:bg-[var(--accent)]"}`}
              >
                {feed.name}
              </button>
            ))}
          </div>
        </aside>

        {/* Center Column: Timeline */}
        <main className="flex-1 border-r border-[var(--border)] flex flex-col h-full bg-[var(--background)]">
          <div className="p-6 border-b border-[var(--border)] flex items-center justify-between">
            <h1 className="font-[family-name:var(--font-display)] text-3xl">Intelligence</h1>
            <div className="flex gap-1 bg-[var(--card)] border border-[var(--border)] p-1">
               {(["feed", "runs", "documents"] as const).map(v => (
                 <button 
                   key={v}
                   onClick={() => setActiveView(v)}
                   className={`px-4 py-1.5 text-[9px] font-mono uppercase tracking-widest transition-colors ${activeView === v ? "bg-[var(--foreground)] text-[var(--background)]" : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"}`}
                 >
                   {v}
                 </button>
               ))}
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {activeView === "feed" && (
              <>
                {isSignalsLoading ? (
                  [1, 2, 3].map(i => <Skeleton key={i} className="h-40 w-full rounded-none" />)
                ) : (signals?.length ?? 0) === 0 ? (
                  <div className="text-center py-20 opacity-50">
                    <ActivityLogIcon className="w-10 h-10 mx-auto mb-4 text-[var(--muted-foreground)]" />
                    <p className="font-mono text-sm uppercase tracking-widest">Signal feed is not yet derived from the backend.</p>
                    <p className="mt-3 text-xs text-[var(--muted-foreground)]">Use Overview, Runs, and Documents for truthful intelligence until signal derivation is implemented.</p>
                  </div>
                ) : (
                  signals?.map(item => {
                    const Icon = getIcon(item.category);
                    return (
                      <div key={item.signalId} className="gsap-reveal border border-[var(--border)] bg-[var(--card)] p-5 hover:border-[var(--primary)] transition-colors relative group cursor-pointer block">
                        <div className={`absolute top-0 bottom-0 left-0 w-1 ${item.significance === 'high' || item.significance === 'critical' ? 'bg-[var(--destructive)]' : item.significance === 'medium' ? 'bg-[#c7772d]' : 'bg-[#5f8768]'}`} />
                        <div className="flex items-start gap-4">
                          <div className="h-10 w-10 border border-[var(--border)] flex items-center justify-center bg-[var(--background)] shrink-0">
                            <Icon className="h-4 w-4 text-[var(--muted-foreground)]" />
                          </div>
                          <div className="flex-1 space-y-2">
                             <div className="flex items-center justify-between">
                                <span className="font-mono text-xs uppercase tracking-widest text-[var(--primary)] font-bold">{item.competitorName}</span>
                                <ExclamationTriangleIcon className={`h-4 w-4 ${item.significance === 'high' || item.significance === 'critical' ? 'text-[var(--destructive)] opacity-100' : 'opacity-0'}`} />
                             </div>
                             <h3 className="font-[family-name:var(--font-display)] text-xl leading-tight">{item.title}</h3>
                             <p className="text-sm text-[var(--muted-foreground)] leading-relaxed">{item.description}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </>
            )}

            {activeView === "runs" && (
              <div className="space-y-4">
                {isRunsLoading ? [1,2].map(i => <Skeleton key={i} className="h-20 w-full" />) :
                 runs?.length === 0 ? <p className="text-center py-20 font-mono text-xs opacity-50">No research runs found.</p> :
                 runs?.map((run: ResearchRun) => (
                   <div key={run.run_id} className="p-5 border border-[var(--border)] bg-[var(--card)] flex items-center justify-between">
                      <div>
                        <h4 className="font-bold text-white tracking-tight">{run.title}</h4>
                        <p className="text-[10px] font-mono text-zinc-600 uppercase mt-1">{run.status} // {run.run_id}</p>
                      </div>
                      <div className="text-right">
                         <div className="text-xs font-mono text-zinc-400 mb-1">{run.progress}%</div>
                         <div className="w-32 h-1 bg-zinc-800"><div className="h-full bg-amber-500" style={{ width: `${run.progress}%` }} /></div>
                      </div>
                   </div>
                 ))
                }
              </div>
            )}

            {activeView === "documents" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {isDocsLoading ? [1,2,3,4].map(i => <Skeleton key={i} className="h-32 w-full" />) :
                 documents?.length === 0 ? <p className="text-center py-20 font-mono text-xs opacity-50 col-span-2">Archive empty.</p> :
                 documents?.map((doc: IntelDocument) => (
                   <div key={doc.document_id} className="p-6 border border-[var(--border)] bg-[var(--card)] space-y-3">
                      <div className="flex justify-between items-start">
                        <span className="text-[9px] font-mono text-amber-500 uppercase tracking-widest">{doc.source_type}</span>
                        <span className="text-[9px] font-mono text-zinc-600 tracking-widest">{new Date(doc.created_at).toLocaleDateString()}</span>
                      </div>
                      <h4 className="font-[family-name:var(--font-display)] text-lg text-white leading-tight">{doc.title}</h4>
                      <p className="text-xs text-zinc-500 line-clamp-2 leading-relaxed">{doc.content_preview}</p>
                   </div>
                 ))
                }
              </div>
            )}
          </div>
        </main>

        {/* Right Column: Analytics */}
        <aside className="gsap-reveal w-72 bg-[var(--card)] flex flex-col h-full">
          <div className="p-6 border-b border-[var(--border)]">
            <h2 className="font-[family-name:var(--font-display)] text-xl">Overview</h2>
          </div>
          <div className="p-6 space-y-8">
            {isOverviewLoading ? (
              <div className="space-y-4">
                 <Skeleton className="h-8 w-full" />
                 <Skeleton className="h-8 w-full" />
                 <Skeleton className="h-8 w-full" />
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between items-end border-b border-[var(--border)] pb-2">
                  <span className="text-sm text-[var(--muted-foreground)]">Competitors tracked</span>
                  <span className="font-mono text-xl">{stats?.monitored_count || 0}</span>
                </div>
                <div className="flex justify-between items-end border-b border-[var(--border)] pb-2">
                  <span className="text-sm text-[var(--muted-foreground)]">Items this week</span>
                  <span className="font-mono text-xl">{stats?.signals_24h || 0}</span>
                </div>
                <div className="flex justify-between items-end border-b border-[var(--border)] pb-2">
                  <span className="text-sm text-[var(--muted-foreground)] text-[var(--destructive)]">High priority</span>
                  <span className="font-mono text-xl text-[var(--destructive)]">{stats?.high_priority_count || 0}</span>
                </div>
              </div>
            )}
            
            
            <div className="pt-4">
              <div className="text-xs font-mono uppercase tracking-widest text-[var(--muted-foreground)] mb-4 flex items-center gap-2">
                <ActivityLogIcon className="h-3 w-3" /> Heatmap
              </div>
              {/* Pseudo Heatmap Visual - This is kept static as per v1 spec for visual weight */}
              <div className="grid grid-cols-4 gap-1">
                {Array.from({length: 16}).map((_, i) => (
                  <div key={i} className={`h-8 border border-[var(--border)] transition-opacity hover:opacity-80 ${i === 3 || i === 7 ? 'bg-[var(--destructive)]/80' : i === 2 || i === 9 ? 'bg-[var(--accent)]/50' : 'bg-[var(--background)]'}`} />
                ))}
              </div>
            </div>
          </div>
        </aside>

      </GsapBridge>
    </div>
  );
}
