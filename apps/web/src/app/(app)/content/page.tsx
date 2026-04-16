"use client";

import type * as React from "react";
import { DownloadIcon, ExternalLinkIcon, MixerHorizontalIcon, ViewGridIcon } from "@radix-ui/react-icons";
import { GsapBridge } from "@/components/ui/gsap-bridge";

const ASSETS = [
  { id: 1, type: "LinkedIn Playbook", title: "The 'Speed' Counter-Narrative", format: "Document", date: "Just now", agent: "Gary Vaynerchuk" },
  { id: 2, type: "Ad Creative", title: "Deep Integration Visual Hook", format: "Image", date: "2 hours ago", agent: "David Ogilvy" },
  { id: 3, type: "Email Sequence", title: "Win-back for Churned Onboarding Dropoffs", format: "Text", date: "Yesterday", agent: "Lester Wunderman" },
  { id: 4, type: "Landing Page Copy", title: "Enterprise Tier Reframing", format: "Copy", date: "2 days ago", agent: "Claude Hopkins" },
  { id: 5, type: "Video Script", title: "Founder Story - Why We Built This", format: "Script", date: "Last week", agent: "Seth Godin" },
  { id: 6, type: "SEO Article", title: "How Fast is Too Fast for Analytics?", format: "Blog", date: "Last week", agent: "Gary Vaynerchuk" },
];

export default function ContentPage(): React.ReactElement {
  return (
    <div className="min-h-[calc(100vh-theme(spacing.16))] bg-[var(--background)] p-8 md:p-12 font-body">
      <GsapBridge stagger={true} className="mx-auto max-w-[1400px]">
        
        {/* Header */}
        <header className="gsap-reveal flex flex-col md:flex-row md:items-end justify-between border-b border-[var(--border)] pb-6 mb-8 gap-6">
          <div>
            <h1 className="font-[family-name:var(--font-display)] text-5xl md:text-6xl mb-2">Content Vault</h1>
            <p className="text-[var(--muted-foreground)] font-mono text-sm tracking-widest uppercase">
              Artifacts produced by the Council. Ready for deployment.
            </p>
          </div>
          
          <div className="flex gap-4">
            <button className="flex h-10 items-center justify-center border border-[var(--border)] bg-[var(--card)] px-4 font-mono text-xs uppercase tracking-widest hover:border-[var(--foreground)] transition-colors">
              <MixerHorizontalIcon className="mr-2 h-3 w-3" /> Filter
            </button>
            <button className="flex h-10 items-center justify-center border border-[var(--border)] bg-[var(--card)] px-4 font-mono text-xs uppercase tracking-widest hover:border-[var(--foreground)] transition-colors">
              <ViewGridIcon className="mr-2 h-3 w-3" /> View
            </button>
          </div>
        </header>

        {/* Masonry Grid Simulation */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {ASSETS.map((asset, i) => (
            <div 
              key={asset.id} 
              className={`gsap-reveal group relative border border-[var(--border)] bg-[var(--card)] overflow-hidden cursor-pointer ${i === 1 || i === 4 ? 'md:row-span-2' : ''}`}
              style={{ minHeight: i === 1 || i === 4 ? '400px' : '250px' }}
            >
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              
              {/* Fake Content Background based on type */}
              <div className="absolute inset-0 opacity-20 flex items-center justify-center font-[family-name:var(--font-display)] text-[10rem] text-[var(--muted-foreground)] overflow-hidden select-none">
                {asset.format[0]}
              </div>

              {/* Top metadata */}
              <div className="absolute top-4 left-4 right-4 flex justify-between z-20">
                <span className="font-mono text-[10px] uppercase tracking-widest bg-[var(--primary)] text-[var(--primary-foreground)] px-2 py-1">
                  {asset.type}
                </span>
                <span className="font-mono text-[10px] uppercase tracking-widest text-[var(--muted-foreground)] bg-black/50 px-2 py-1 backdrop-blur-sm">
                  {asset.date}
                </span>
              </div>

              {/* Bottom Info & Hover Actions */}
              <div className="absolute bottom-4 left-4 right-4 z-20 transform translate-y-8 group-hover:translate-y-0 transition-transform duration-300">
                <div className="mb-4">
                  <h3 className="font-[family-name:var(--font-display)] text-2xl text-white leading-tight mb-2">{asset.title}</h3>
                  <p className="font-mono text-xs text-white/70 uppercase">Agent: {asset.agent}</p>
                </div>
                
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-100">
                  <button className="flex-1 bg-white text-black h-10 text-xs font-mono uppercase tracking-widest hover:bg-white/90 flex items-center justify-center">
                    <DownloadIcon className="mr-2 h-3 w-3" /> Download
                  </button>
                  <button className="h-10 w-10 border border-white/20 bg-black/50 backdrop-blur text-white flex items-center justify-center hover:bg-white/20">
                    <ExternalLinkIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

      </GsapBridge>
    </div>
  );
}
