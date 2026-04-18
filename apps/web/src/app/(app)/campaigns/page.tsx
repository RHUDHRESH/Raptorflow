"use client";

import * as React from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import type { Route } from "next";
import { 
  PlusIcon, 
  TargetIcon, 
  DrawingPinIcon, 
  MixerHorizontalIcon, 
  ChevronRightIcon,
  LightningBoltIcon,
  BackpackIcon
} from "@radix-ui/react-icons";
import { useCampaigns } from "@/hooks/use-campaigns";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { CreateCampaignDrawer } from "@/components/campaigns/create-campaign-drawer";

export default function CampaignsPage(): React.ReactElement {
  const router = useRouter();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const { data: campaigns, isLoading } = useCampaigns();

  // Stats
  const campaignList = campaigns || [];
  const activeCount = campaignList.filter(c => c.status === "active").length;
  const completedCount = campaignList.filter(c => c.status === "completed").length;

  return (
    <div className="flex flex-col gap-12 py-2">
      <GsapBridge stagger={true}>
        
        {/* ── Header ────────────────────────────────────────── */}
        <header className="gsap-reveal flex items-end justify-between border-b-2 border-[var(--foreground)] pb-8">
           <div className="space-y-2">
             <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "var(--muted-foreground)" }}>
               Strategy Ledger // L1_COMMAND
             </p>
             <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 48, lineHeight: 1, margin: 0 }}>
               Campaigns
             </h1>
           </div>
           <Button 
             className="h-12 px-8 bg-white text-black font-bold uppercase tracking-widest text-[11px] rounded-none hover:bg-zinc-200 transition-colors shadow-[0_10px_20px_rgba(255,255,255,0.05)]"
             onClick={() => setDrawerOpen(true)}
           >
             <PlusIcon className="w-4 h-4 mr-2" />
             Initiate Campaign
           </Button>
        </header>

        {/* ── Briefing Cards ──────────────────────────────────── */}
        <div className="gsap-reveal grid grid-cols-1 md:grid-cols-3 gap-[1px] bg-zinc-800 border border-zinc-800">
           <div className="bg-[#0c0c0c] p-8 space-y-4">
              <p className="font-mono text-[9px] text-zinc-600 uppercase tracking-widest">Active Fronts</p>
              <div className="text-4xl text-white font-[family-name:var(--font-display)]">
                {isLoading ? "..." : activeCount}
              </div>
           </div>
           <div className="bg-[#0c0c0c] p-8 space-y-4">
              <p className="font-mono text-[9px] text-zinc-600 uppercase tracking-widest">Completed Initiatives</p>
              <div className="text-4xl text-white font-[family-name:var(--font-display)]">
                {isLoading ? "..." : completedCount}
              </div>
           </div>
           <div className="bg-[#0c0c0c] p-8 space-y-4">
              <p className="font-mono text-[9px] text-zinc-600 uppercase tracking-widest">Network Salience</p>
              <div className="text-4xl text-green-500 font-[family-name:var(--font-display)]">94%</div>
           </div>
        </div>

        {/* ── Directory ───────────────────────────────────────── */}
        <div className="gsap-reveal space-y-6 mt-12">
           <div className="flex items-center justify-between">
              <h2 style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.14em", color: "var(--muted-foreground)" }}>
                 Campaign Log
              </h2>
              <div className="flex items-center gap-4">
                 <span className="text-[10px] font-mono text-zinc-800 uppercase tracking-widest">Sort: By Hierarchy</span>
              </div>
           </div>

           <div className="border border-zinc-800 bg-[#0d0d0d] divide-y divide-zinc-900">
              {isLoading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="p-12 animate-pulse bg-zinc-900/10" />
                ))
              ) : campaignList.length === 0 ? (
                <div className="p-20 text-center space-y-6">
                   <TargetIcon className="w-10 h-10 text-zinc-800 mx-auto" />
                   <div className="space-y-1">
                      <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24 }}>The board is empty.</p>
                      <p className="text-zinc-600 font-mono text-[10px] uppercase tracking-widest">Zero active signals detected in tactical buffer.</p>
                   </div>
                </div>
              ) : (
                campaignList.map((c) => (
                  <Link 
                    key={c.campaignId}
                    href={`/campaigns/${c.campaignId}` as Route}
                    className="flex flex-col md:flex-row md:items-center justify-between p-8 group hover:bg-white/[0.01] transition-colors gap-6"
                  >
                    <div className="flex items-center gap-6">
                       <div className="w-10 h-10 border border-zinc-800 flex items-center justify-center group-hover:bg-amber-500 group-hover:border-amber-500 transition-all">
                          <BackpackIcon className="w-4 h-4 text-zinc-600 group-hover:text-black transition-colors" />
                       </div>
                       <div>
                          <h3 className="text-xl font-bold text-white group-hover:text-amber-500 transition-colors uppercase tracking-tight">
                            {c.name}
                          </h3>
                          <div className="flex items-center gap-3 mt-1">
                             <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">Goal: {c.goal_type.replace('_', ' ')}</span>
                             <span className="h-1 w-1 rounded-full bg-zinc-800" />
                             <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">{c.status}</span>
                          </div>
                       </div>
                    </div>

                    <div className="flex items-center gap-12">
                       <div className="hidden lg:block w-48 space-y-2">
                          <div className="flex items-center justify-between text-[8px] font-mono uppercase tracking-widest text-zinc-600">
                             <span>Progress</span>
                             <span>{c.progress_pct}%</span>
                          </div>
                          <div className="h-1 w-full bg-zinc-900 overflow-hidden">
                             <div 
                                className="h-full bg-amber-500 transition-all duration-1000" 
                                style={{ width: `${c.progress_pct}%` }} 
                             />
                          </div>
                       </div>
                       
                       <div className="flex items-center gap-2">
                          <Badge variant="outline" className="border-zinc-800 rounded-none font-mono text-[9px] px-3 py-1 uppercase tracking-widest text-zinc-500">
                             {c.tasks_completed}/{c.tasks_total} Operations
                          </Badge>
                          <ChevronRightIcon className="w-5 h-5 text-zinc-800 group-hover:text-white transition-colors" />
                       </div>
                    </div>
                  </Link>
                ))
              )}
           </div>
        </div>

        {/* ── System Footer ───────────────────────────────────── */}
        <footer className="gsap-reveal mt-20 p-10 border border-zinc-900 bg-[#0a0a0a] flex flex-col md:flex-row items-center justify-between gap-8">
           <div className="flex items-center gap-4">
              <LightningBoltIcon className="w-6 h-6 text-amber-500" />
              <div>
                 <p className="text-xs font-bold text-white uppercase tracking-tight">Ready for deployment?</p>
                 <p className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest">Strategist 01 is standing by for new instructions.</p>
              </div>
           </div>
           <Button 
             variant="outline" 
             className="border-zinc-800 text-zinc-500 rounded-none h-12 px-8 font-mono text-[10px] uppercase tracking-widest hover:text-white hover:border-zinc-600"
             onClick={() => setDrawerOpen(true)}
           >
             Open Deployment Interface
           </Button>
        </footer>

      </GsapBridge>

      <CreateCampaignDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
    </div>
  );
}
