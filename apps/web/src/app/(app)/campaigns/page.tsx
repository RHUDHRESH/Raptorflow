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
             className="h-12 px-8 bg-[#2A2622] text-white font-bold uppercase tracking-widest text-[11px] rounded-none hover:bg-[#4A4540] transition-colors shadow-[0_10px_20px_rgba(42,38,34,0.08)]"
             onClick={() => setDrawerOpen(true)}
           >
             <PlusIcon className="w-4 h-4 mr-2" />
             Initiate Campaign
           </Button>
        </header>

        {/* ── Briefing Cards ──────────────────────────────────── */}
        <div className="gsap-reveal grid grid-cols-1 md:grid-cols-3 gap-[1px] bg-[#E5DED4] border border-[#E5DED4]">
           <div className="bg-white p-8 space-y-4">
              <p className="font-mono text-[9px] text-[#9A948C] uppercase tracking-widest">Active Fronts</p>
              <div className="text-4xl text-[#2A2622] font-[family-name:var(--font-display)]">
                {isLoading ? "..." : activeCount}
              </div>
           </div>
           <div className="bg-white p-8 space-y-4">
              <p className="font-mono text-[9px] text-[#9A948C] uppercase tracking-widest">Completed Initiatives</p>
              <div className="text-4xl text-[#2A2622] font-[family-name:var(--font-display)]">
                {isLoading ? "..." : completedCount}
              </div>
           </div>
           <div className="bg-white p-8 space-y-4">
              <p className="font-mono text-[9px] text-[#9A948C] uppercase tracking-widest">Network Salience</p>
              <div className="text-4xl text-green-600 font-[family-name:var(--font-display)]">94%</div>
           </div>
        </div>

        {/* ── Directory ───────────────────────────────────────── */}
        <div className="gsap-reveal space-y-6 mt-12">
           <div className="flex items-center justify-between">
              <h2 style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.14em", color: "var(--muted-foreground)" }}>
                 Campaign Log
              </h2>
              <div className="flex items-center gap-4">
                 <span className="text-[10px] font-mono text-[#BAB0A0] uppercase tracking-widest">Sort: By Hierarchy</span>
              </div>
           </div>

           <div className="border border-[#E5DED4] bg-white divide-y divide-[#E5DED4]">
              {isLoading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="p-12 animate-pulse bg-[#F5F0E8]/50" />
                ))
              ) : campaignList.length === 0 ? (
                <div className="p-20 text-center space-y-6">
                   <TargetIcon className="w-10 h-10 text-[#E5DED4] mx-auto" />
                   <div className="space-y-1">
                      <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24 }}>The board is empty.</p>
                      <p className="text-[#9A948C] font-mono text-[10px] uppercase tracking-widest">Zero active signals detected in tactical buffer.</p>
                   </div>
                </div>
              ) : (
                campaignList.map((c) => (
                  <Link 
                    key={c.campaignId}
                    href={`/campaigns/${c.campaignId}` as Route}
                    className="flex flex-col md:flex-row md:items-center justify-between p-8 group hover:bg-[#F5F0E8]/50 transition-colors gap-6"
                  >
                    <div className="flex items-center gap-6">
                       <div className="w-10 h-10 border border-[#E5DED4] flex items-center justify-center group-hover:bg-[#D97757] group-hover:border-[#D97757] transition-all">
                          <BackpackIcon className="w-4 h-4 text-[#9A948C] group-hover:text-[#2A2622] transition-colors" />
                       </div>
                       <div>
                          <h3 className="text-xl font-bold text-[#2A2622] group-hover:text-[#D97757] transition-colors uppercase tracking-tight">
                            {c.name}
                          </h3>
                          <div className="flex items-center gap-3 mt-1">
                             <span className="text-[10px] font-mono text-[#6B655E] uppercase tracking-widest">Goal: {c.goal_type.replace('_', ' ')}</span>
                             <span className="h-1 w-1 rounded-full bg-[#E5DED4]" />
                             <span className="text-[10px] font-mono text-[#6B655E] uppercase tracking-widest">{c.status}</span>
                          </div>
                       </div>
                    </div>

                    <div className="flex items-center gap-12">
                       <div className="hidden lg:block w-48 space-y-2">
                          <div className="flex items-center justify-between text-[8px] font-mono uppercase tracking-widest text-[#9A948C]">
                             <span>Progress</span>
                             <span>{c.progress_pct}%</span>
                          </div>
                          <div className="h-1 w-full bg-[#E5DED4] overflow-hidden">
                             <div 
                                className="h-full bg-[#D97757] transition-all duration-1000" 
                                style={{ width: `${c.progress_pct}%` }} 
                             />
                          </div>
                       </div>
                       
                       <div className="flex items-center gap-2">
                          <Badge variant="outline" className="border-[#E5DED4] rounded-none font-mono text-[9px] px-3 py-1 uppercase tracking-widest text-[#6B655E]">
                             {c.tasks_completed}/{c.tasks_total} Operations
                          </Badge>
                          <ChevronRightIcon className="w-5 h-5 text-[#BAB0A0] group-hover:text-[#2A2622] transition-colors" />
                       </div>
                    </div>
                  </Link>
                ))
              )}
           </div>
        </div>

        {/* ── System Footer ───────────────────────────────────── */}
        <footer className="gsap-reveal mt-20 p-10 border border-[#E5DED4] bg-white flex flex-col md:flex-row items-center justify-between gap-8">
           <div className="flex items-center gap-4">
              <LightningBoltIcon className="w-6 h-6 text-[#D97757]" />
              <div>
                 <p className="text-xs font-bold text-[#2A2622] uppercase tracking-tight">Ready for deployment?</p>
                 <p className="text-[10px] font-mono text-[#9A948C] uppercase tracking-widest">Strategist 01 is standing by for new instructions.</p>
              </div>
           </div>
           <Button 
             variant="outline" 
             className="border-[#E5DED4] text-[#6B655E] rounded-none h-12 px-8 font-mono text-[10px] uppercase tracking-widest hover:text-[#2A2622] hover:border-[#D5CBC0]"
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
