"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { MagnifyingGlassIcon, GlobeIcon, Share2Icon, TargetIcon, ActivityLogIcon, ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { GsapBridge } from "@/components/ui/gsap-bridge";

const FEEDS = [
  { name: "All Intelligence", active: true },
  { name: "Website Changes", active: false },
  { name: "Social Activity", active: false },
  { name: "Ad Library", active: false },
  { name: "SEO Movements", active: false },
];

const TIMELINE = [
  { 
    id: 1, 
    source: "Website", 
    icon: GlobeIcon, 
    competitor: "Luminous Brands", 
    level: "high", 
    time: "2 hours ago",
    title: "Updated Pricing Page Architecture",
    desc: "Changed mid-tier pricing from ₹50K to ₹40K. Added new benefit claim focusing heavily on integration speed. Strategic implication: They are aggressively targeting our core ICP."
  },
  { 
    id: 2, 
    source: "Social", 
    icon: Share2Icon, 
    competitor: "Apex Studio", 
    level: "low", 
    time: "Today 9:15 AM",
    title: "Published 'AI in Marketing' Manifesto",
    desc: "Posted 2,000 word thought leadership piece on LinkedIn. Audience engagement is currently average."
  },
  { 
    id: 3, 
    source: "Ads", 
    icon: TargetIcon, 
    competitor: "Nexus Flow", 
    level: "medium", 
    time: "Yesterday",
    title: "Launched Regional Ad Campaign",
    desc: "20+ new ads across Instagram and Facebook. Focus on enterprise features. Estimated spend: ₹500K+."
  },
];

export default function IntelPage(): React.ReactElement {
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
            {FEEDS.map(feed => (
              <button 
                key={feed.name} 
                className={`w-full text-left px-3 py-2 text-sm font-mono tracking-tight transition-colors ${feed.active ? "bg-[var(--primary)] text-[var(--primary-foreground)]" : "text-[var(--foreground)] hover:bg-[var(--accent)]"}`}
              >
                {feed.name}
              </button>
            ))}
          </div>
        </aside>

        {/* Center Column: Timeline */}
        <main className="flex-1 border-r border-[var(--border)] flex flex-col h-full bg-[var(--background)]">
          <div className="p-6 border-b border-[var(--border)] flex items-center justify-between">
            <h1 className="font-[family-name:var(--font-display)] text-3xl">Intelligence Feed</h1>
            <div className="flex items-center gap-2 text-xs font-mono uppercase text-[var(--muted-foreground)]">
              <span>Sort:</span>
              <select className="bg-transparent border-none outline-none text-[var(--foreground)] cursor-pointer">
                <option>Newest first</option>
                <option>Most significant</option>
              </select>
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {TIMELINE.map(item => (
              <div key={item.id} className="gsap-reveal border border-[var(--border)] bg-[var(--card)] p-5 hover:border-[var(--primary)] transition-colors relative group cursor-pointer block">
                {/* Alert Badge Line */}
                <div className={`absolute top-0 bottom-0 left-0 w-1 ${item.level === 'high' ? 'bg-[var(--destructive)]' : item.level === 'medium' ? 'bg-[#c7772d]' : 'bg-[#5f8768]'}`} />
                
                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 border border-[var(--border)] flex items-center justify-center bg-[var(--background)] shrink-0">
                    <item.icon className="h-4 w-4 text-[var(--muted-foreground)]" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs uppercase tracking-widest text-[var(--primary)] font-bold">{item.competitor}</span>
                        <span className="text-[10px] text-[var(--muted-foreground)]">•</span>
                        <span className="text-[10px] font-mono text-[var(--muted-foreground)] uppercase">{item.time}</span>
                      </div>
                      <ExclamationTriangleIcon className={`h-4 w-4 ${item.level === 'high' ? 'text-[var(--destructive)] opacity-100' : 'opacity-0'}`} />
                    </div>
                    
                    <h3 className="font-[family-name:var(--font-display)] text-xl leading-tight">{item.title}</h3>
                    <p className="text-sm text-[var(--muted-foreground)] leading-relaxed">{item.desc}</p>
                    
                    <div className="pt-3 flex gap-4 text-xs font-mono uppercase opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="text-[var(--primary)] hover:underline border-b border-transparent">Full details →</button>
                      <button className="text-[var(--muted-foreground)] hover:text-[var(--foreground)]">Discuss in Muse</button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </main>

        {/* Right Column: Analytics */}
        <aside className="gsap-reveal w-72 bg-[var(--card)] flex flex-col h-full">
          <div className="p-6 border-b border-[var(--border)]">
            <h2 className="font-[family-name:var(--font-display)] text-xl">Overview</h2>
          </div>
          <div className="p-6 space-y-8">
            <div className="space-y-4">
              <div className="flex justify-between items-end border-b border-[var(--border)] pb-2">
                <span className="text-sm text-[var(--muted-foreground)]">Competitors tracked</span>
                <span className="font-mono text-xl">12</span>
              </div>
              <div className="flex justify-between items-end border-b border-[var(--border)] pb-2">
                <span className="text-sm text-[var(--muted-foreground)]">Items this week</span>
                <span className="font-mono text-xl">47</span>
              </div>
              <div className="flex justify-between items-end border-b border-[var(--border)] pb-2">
                <span className="text-sm text-[var(--muted-foreground)] text-[var(--destructive)]">High priority</span>
                <span className="font-mono text-xl text-[var(--destructive)]">3</span>
              </div>
            </div>
            
            <div className="pt-4">
              <div className="text-xs font-mono uppercase tracking-widest text-[var(--muted-foreground)] mb-4 flex items-center gap-2">
                <ActivityLogIcon className="h-3 w-3" /> Heatmap
              </div>
              {/* Pseudo Heatmap Visual */}
              <div className="grid grid-cols-4 gap-1">
                {Array.from({length: 16}).map((_, i) => (
                  <div key={i} className={`h-8 border border-[var(--border)] ${i === 3 || i === 7 ? 'bg-[var(--destructive)]/80' : i === 2 || i === 9 ? 'bg-[var(--accent)]/50' : 'bg-[var(--background)]'}`} />
                ))}
              </div>
            </div>
          </div>
        </aside>

      </GsapBridge>
    </div>
  );
}
