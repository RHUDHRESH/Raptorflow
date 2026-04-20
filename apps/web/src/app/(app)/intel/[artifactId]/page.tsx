"use client";

import type * as React from "react";
import { use } from "react";
import type { Route } from "next";
import Link from "next/link";
import { ArrowLeftIcon, FileTextIcon, MixerHorizontalIcon, MagnifyingGlassIcon, ChatBubbleIcon } from "@radix-ui/react-icons";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AGENT_MAP } from "@/lib/agents";
import { AgentPill } from "@/components/ui/agent-portrait";

const ARTIFACT_TYPES: Record<string, { label: string; description: string; source: string; significance: string }> = {
  "website-snapshot": { 
    label: "Website Snapshot", 
    description: "Full-page visual capture of competitor landing page. Detected shift in primary headline and hero offer.", 
    source: "Competitor Intelligence Node",
    significance: "high"
  },
  "ad-creative": { 
    label: "Ad Creative", 
    description: "Paid social creative detected on Meta Ad Library. Testing new 'Identity-led' positioning.", 
    source: "Ad Transparency Pipeline",
    significance: "medium"
  },
  "pricing-change": { 
    label: "Pricing Update", 
    description: "Structural change in pricing tiers detected via automated price-point monitoring.", 
    source: "Pricing Scraper",
    significance: "critical"
  },
};

export default function IntelArtifactPage({
  params
}: {
  params: Promise<{ artifactId: string }>;
}): React.ReactElement {
  const { artifactId } = use(params);
  const typeKey = Object.keys(ARTIFACT_TYPES).find(k => artifactId.includes(k)) || "website-snapshot";
  const artifact = ARTIFACT_TYPES[typeKey];
  const analyticsAgent = AGENT_MAP.get("analytics");

  return (
    <div className="flex flex-col gap-8 py-2">
      {/* ── Back nav ──────────────────────────────────── */}
      <Link
        href="/intel"
        className="flex items-center gap-2 mb-2 hover:underline w-fit"
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 9,
          textTransform: "uppercase",
          letterSpacing: "0.16em",
          color: "var(--muted-foreground)",
        }}
      >
        <ArrowLeftIcon className="h-3 w-3" />
        Intelligence Feed
      </Link>

      {/* ── Header ────────────────────────────────────────── */}
      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <FileTextIcon className="h-4 w-4" style={{ color: "var(--indigo-muse)" }} />
            <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "var(--muted-foreground)" }}>
              Artifact Reference: {artifactId}
            </p>
          </div>
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
            {artifact.label}
          </h1>
        </div>

        <div className="flex flex-col items-end gap-2">
          <Badge className={
            artifact.significance === "critical" ? "bg-red-500/10 text-red-500 border-red-500/20" :
            artifact.significance === "high" ? "bg-amber-500/10 text-amber-500 border-amber-500/20" :
            "bg-blue-500/10 text-blue-500 border-blue-500/20"
          }>
            {artifact.significance} significance
          </Badge>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.12em", color: "var(--muted-foreground)" }}>
            Source: {artifact.source}
          </p>
        </div>
      </header>

      {/* ── Main content ──────────────────────────────────── */}
      <div className="grid xl:grid-cols-[1fr_360px] gap-8 items-start">
        
        <div className="space-y-8">
          {/* Artifact Preview */}
          <section className="border-2 border-[var(--foreground)] bg-black overflow-hidden relative group">
            <div className="absolute top-4 right-4 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
               <button className="bg-[var(--foreground)] text-[var(--background)] p-3 shadow-2xl">
                 <MagnifyingGlassIcon className="w-5 h-5" />
               </button>
            </div>
            <div className="aspect-video bg-[var(--card)] flex flex-col items-center justify-center border-b border-[var(--border)]">
               <MixerHorizontalIcon className="h-12 w-12 text-[#BAB0A0] mb-4 animate-pulse" />
               <p className="text-[#9A948C] font-mono text-[10px] uppercase tracking-widest">Visual Stream Unavailable</p>
               <p className="text-[#9A948C] text-[9px] mt-1 font-mono uppercase tracking-[0.2em]">Hardware acceleration required for v8 render</p>
            </div>
            <div className="p-6 bg-[var(--card)]">
               <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24, marginBottom: 12 }}>Executive Summary</h3>
               <p className="text-[#6B655E] leading-relaxed font-light italic">
                 {artifact.description}
               </p>
            </div>
          </section>

          {/* Analysis Card */}
          <section className="border border-[var(--border)] bg-[var(--card)] p-8 relative">
            <div className="absolute left-0 top-8 bottom-8 w-1 bg-[var(--indigo-muse)]" />
            <div className="flex items-center justify-between mb-8">
               <div className="flex items-center gap-3">
                 {analyticsAgent && <AgentPill agent={analyticsAgent} size={24} />}
                 <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.18em", color: "var(--muted-foreground)" }}>
                   Agent Analysis
                 </p>
               </div>
            </div>
            <div className="space-y-6">
               <p className="text-[#2A2622] text-lg font-light leading-relaxed">
                 &ldquo;This shift indicates a move toward direct comparison. They are no longer competing on features, but on the <span className="text-[var(--indigo-muse)] underline decoration-indigo-500/30">identity gap</span> we identified in the last council session. We should expect a structural push on their pricing within 14 days.&rdquo;
               </p>
               <div className="pt-6 border-t border-[var(--border)] flex gap-8">
                  <div>
                    <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--muted-foreground)", marginBottom: 4 }}>Confidence</p>
                    <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22 }}>88%</p>
                  </div>
                  <div>
                    <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--muted-foreground)", marginBottom: 4 }}>Salience</p>
                    <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22 }}>9.2</p>
                  </div>
               </div>
            </div>
          </section>
        </div>

        {/* ── Sidebar Actions ───────────────────────────────── */}
        <aside className="space-y-6 sticky top-6">
          <div className="border border-[var(--border)] bg-[var(--card)] divide-y divide-[var(--border)]">
             <div className="px-5 py-4">
                <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.14em", color: "var(--muted-foreground)" }}>System Actions</p>
             </div>
             <button className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all group">
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>Send to Council</span>
                <ArrowLeftIcon className="w-4 h-4 rotate-180 group-hover:translate-x-1 transition-transform" />
             </button>
             <button className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all group">
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>Consult Muse</span>
                <ChatBubbleIcon className="w-4 h-4 group-hover:scale-110 transition-transform" />
             </button>
             <button className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all group">
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>Tag to Campaign</span>
                <MixerHorizontalIcon className="w-4 h-4 group-hover:rotate-90 transition-transform" />
             </button>
          </div>

          <div className="p-6 border border-[#E5DED4] bg-[#FBF8F2] space-y-4">
             <p className="text-[10px] uppercase font-bold tracking-widest text-[#6B655E]">Signal Context</p>
             <p className="text-xs text-[#6B655E] leading-relaxed font-mono">
                Detected via: <br/>
                <span className="text-[#4A4540]">Scraper_Node_Bombay_Alpha</span><br/>
                LATENCY: 44ms<br/>
                PROTOCOL: HTTP/2 (TLS 1.3)
             </p>
          </div>
        </aside>

      </div>
    </div>
  );
}
