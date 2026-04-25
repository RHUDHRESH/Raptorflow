"use client";

import type * as React from "react";
import { useState, useMemo } from "react";
import { MagnifyingGlassIcon, GlobeIcon, Share2Icon, TargetIcon, ActivityLogIcon, ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { useIntelSignals, useIntelOverview } from "@/hooks/use-intel";
import type { IntelSignal } from "@/hooks/use-intel";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { Radar } from "lucide-react";

const CATEGORIES = [
  { name: "All Intelligence", value: "" },
  { name: "Website Changes", value: "website" },
  { name: "Social Activity", value: "social" },
  { name: "Ad Library", value: "ads" },
  { name: "SEO Movements", value: "seo" },
];

export default function IntelPage(): React.ReactElement {
  const [activeCategory, setActiveCategory] = useState("");
  const [activeView] = useState<"feed">("feed");
  
  const { data: signalsData, isLoading: isSignalsLoading } = useIntelSignals(activeCategory);
  const signals = signalsData?.signals;
  const { data: overviewData, isLoading: isOverviewLoading } = useIntelOverview();
  
  const stats = useMemo(() => {
    if (!overviewData?.signals) return { total: 0, highPriority: 0, thisWeek: 0 };
    const all = overviewData.signals;
    const now = Date.now();
    const weekAgo = now - 7 * 24 * 60 * 60 * 1000;
    return {
      total: all.length,
      highPriority: all.filter(s => s.severity === "high" || s.severity === "critical").length,
      thisWeek: all.filter(s => new Date(s.created_at).getTime() > weekAgo).length,
    };
  }, [overviewData]);
  
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
               <button className="px-4 py-1.5 text-[9px] font-mono uppercase tracking-widest transition-colors bg-[var(--foreground)] text-[var(--background)]">feed</button>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {activeView === "feed" && (
              <>
                {isSignalsLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-40 w-full rounded-none" />)}
                  </div>
                ) : (signals?.length ?? 0) === 0 ? (
                  <EmptyState
                    icon={Radar}
                    title="No signals detected"
                    description="Run a sweep to scan for competitive intelligence."
                  />
                ) : (
                  signals?.map(item => {
                    const Icon = getIcon(item.type);
                    return (
                      <div key={item.id} className="gsap-reveal border border-[var(--border)] bg-[var(--card)] p-5 hover:border-[var(--primary)] transition-colors relative group cursor-pointer block">
                        <div className={`absolute top-0 bottom-0 left-0 w-1 ${item.severity === 'high' || item.severity === 'critical' ? 'bg-[var(--destructive)]' : item.severity === 'medium' ? 'bg-[#c7772d]' : 'bg-[#5f8768]'}`} />
                        <div className="flex items-start gap-4">
                          <div className="h-10 w-10 border border-[var(--border)] flex items-center justify-center bg-[var(--background)] shrink-0">
                            <Icon className="h-4 w-4 text-[var(--muted-foreground)]" />
                          </div>
                          <div className="flex-1 space-y-2">
                             <div className="flex items-center justify-between">
                                <span className="font-mono text-xs uppercase tracking-widest text-[var(--primary)] font-bold">{item.source}</span>
                                <ExclamationTriangleIcon className={`h-4 w-4 ${item.severity === 'high' || item.severity === 'critical' ? 'text-[var(--destructive)] opacity-100' : 'opacity-0'}`} />
                             </div>
                             <h3 className="font-[family-name:var(--font-display)] text-xl leading-tight">{item.title}</h3>
                             <p className="text-sm text-[var(--muted-foreground)] leading-relaxed">{item.summary}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </>
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
                  <span className="text-sm text-[var(--muted-foreground)]">Total signals</span>
                  <span className="font-mono text-xl">{stats.total}</span>
                </div>
                <div className="flex justify-between items-end border-b border-[var(--border)] pb-2">
                  <span className="text-sm text-[var(--muted-foreground)]">This week</span>
                  <span className="font-mono text-xl">{stats.thisWeek}</span>
                </div>
                <div className="flex justify-between items-end border-b border-[var(--border)] pb-2">
                  <span className="text-sm text-[var(--muted-foreground)] text-[var(--destructive)]">High priority</span>
                  <span className="font-mono text-xl text-[var(--destructive)]">{stats.highPriority}</span>
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
