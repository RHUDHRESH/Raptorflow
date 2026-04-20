"use client";

import * as React from "react";
import { use } from "react";
import type { Route } from "next";
import Link from "next/link";
import { ArrowLeftIcon, DrawingPinIcon, MixerHorizontalIcon, ChatBubbleIcon, PlayIcon } from "@radix-ui/react-icons";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AGENTS } from "@/lib/agents";
import { AgentPill } from "@/components/ui/agent-portrait";

const MOVE_DATA: Record<string, {
  title: string; 
  description: string; 
  status: string; 
  budget: number;
  timeline: string; 
  channels: string[]; 
  leadAgent: string;
  tasks: { id: string; title: string; status: string; assignee: string }[]
}> = {
  awareness: {
    title: "Brand Awareness Push",
    description: "Initial brand visibility on LinkedIn and Instagram. Ogilvy leads creative brief focusing on the 'Identity Gap' theory.",
    status: "completed",
    budget: 4000,
    timeline: "Week 1-2",
    channels: ["LinkedIn", "Instagram"],
    leadAgent: "ogilvy",
    tasks: [
      { id: "t1", title: "Write 3 ad creatives", status: "done", assignee: "ogilvy" },
      { id: "t2", title: "Segment ICP by job title", status: "done", assignee: "patel" },
      { id: "t3", title: "Deploy initial budget", status: "done", assignee: "media" },
    ],
  },
  consideration: {
    title: "Content Nurture Sprint",
    description: "3 blog posts + LinkedIn playbook targeting mid-funnel ICP. Godin leads narrative on 'remarkability'.",
    status: "active",
    budget: 8000,
    timeline: "Week 2-4",
    channels: ["Blog", "LinkedIn"],
    leadAgent: "godin",
    tasks: [
      { id: "t4", title: "Draft 'AI Marketing Ops' essay", status: "in_progress", assignee: "ogilvy" },
      { id: "t5", title: "Set up newsletter sequence", status: "pending", assignee: "wunderman" },
      { id: "t6", title: "Define tribe parameters", status: "done", assignee: "godin" },
    ],
  },
};

export default function CampaignMoveDetailPage({
  params
}: {
  params: Promise<{ campaignId: string; moveId: string }>;
}): React.ReactElement {
  const { campaignId, moveId } = use(params);
  const move = MOVE_DATA[moveId] ?? MOVE_DATA.consideration;
  const leadAgentConfig = AGENTS.find(a => a.key === move.leadAgent);

  return (
    <div className="flex flex-col gap-8 py-2">
      {/* ── Back nav ──────────────────────────────────── */}
      <Link
        href={`/campaigns/${campaignId}/moves` as Route}
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
        Move Sequence
      </Link>

      {/* ── Header ────────────────────────────────────────── */}
      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <DrawingPinIcon className="h-4 w-4" style={{ color: "var(--amber-war)" }} />
            <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "var(--muted-foreground)" }}>
               Move Detail // {moveId.toUpperCase()}
            </p>
          </div>
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
            {move.title}
          </h1>
        </div>

        <div className="flex flex-col items-end gap-2 text-right">
          <Badge className={
            move.status === "active" ? "bg-amber-500/10 text-amber-500 border-amber-500/20" :
            move.status === "completed" ? "bg-green-500/10 text-green-500 border-green-500/20" :
            "bg-[#E5DED4] text-[#6B655E]"
          }>
            {move.status}
          </Badge>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, color: "var(--foreground)" }}>
             ₹{move.budget.toLocaleString("en-IN")} Allocation
          </p>
        </div>
      </header>

      {/* ── Main content ──────────────────────────────────── */}
      <div className="grid xl:grid-cols-[1fr_360px] gap-8 items-start">
        
        <div className="space-y-8">
          {/* Move Overview */}
          <section className="border-2 border-[var(--foreground)] bg-[var(--card)] p-8">
             <div className="flex items-start justify-between mb-8">
                <div className="space-y-4 max-w-xl">
                   <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24 }}>Strategic Narrative</h3>
                   <p className="text-[#6B655E] font-light italic leading-relaxed">
                     &ldquo;{move.description}&rdquo;
                   </p>
                </div>
                {leadAgentConfig && (
                   <div className="text-right flex flex-col items-end gap-2">
                      <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--muted-foreground)" }}>
                        Lead Architect
                      </p>
                      <AgentPill agent={leadAgentConfig} size={24} />
                   </div>
                )}
             </div>

             <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pt-8 border-t border-[#E5DED4]">
                <div>
                   <p className="font-mono text-[8px] text-[#9A948C] uppercase tracking-widest mb-1">Timeline</p>
                   <p className="text-sm font-medium">{move.timeline}</p>
                </div>
                <div>
                   <p className="font-mono text-[8px] text-[#9A948C] uppercase tracking-widest mb-1">Channels</p>
                   <div className="flex gap-1 flex-wrap">
                      {move.channels.map(c => <Badge key={c} variant="outline" className="text-[9px] uppercase">{c}</Badge>)}
                   </div>
                </div>
                <div>
                   <p className="font-mono text-[8px] text-[#9A948C] uppercase tracking-widest mb-1">Tasks</p>
                   <p className="text-sm font-medium">{move.tasks.filter(t => t.status === "done").length}/{move.tasks.length} Done</p>
                </div>
                <div>
                   <p className="font-mono text-[8px] text-[#9A948C] uppercase tracking-widest mb-1">Efficiency</p>
                   <p className="text-sm font-medium text-green-500">92%</p>
                </div>
             </div>
          </section>

          {/* Task Ledger */}
          <section className="border border-[var(--border)] bg-[var(--card)]">
             <div className="px-6 py-4 border-b border-[var(--border)] flex items-center justify-between">
                <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.18em", color: "var(--muted-foreground)" }}>
                   Operational Ledger
                </p>
                <div className="flex items-center gap-2">
                   <Button variant="ghost" className="h-7 px-2 text-[9px] font-mono text-[#9A948C] uppercase">View All</Button>
                   <Button size="sm" className="h-7 px-3 bg-white text-black text-[9px] font-bold uppercase rounded-none">Create Task</Button>
                </div>
             </div>
             <div className="divide-y divide-[var(--border)]">
                {move.tasks.map(task => {
                   const agent = AGENTS.find(a => a.key === task.assignee);
                   return (
                     <div key={task.id} className="p-6 flex items-center justify-between group hover:bg-white/[0.02] transition-colors">
                        <div className="flex items-center gap-4">
                           <div className={`h-2 w-2 rounded-full ${
                             task.status === "done" ? "bg-green-500" :
                             task.status === "in_progress" ? "bg-amber-500 animate-pulse" : "bg-[#E5DED4]"
                           }`} />
                           <div>
                              <p className="text-sm text-[#2A2622] font-medium group-hover:text-amber-500 transition-colors uppercase tracking-tight">{task.title}</p>
                              <div className="flex items-center gap-3 mt-1">
                                 <span className="text-[9px] font-mono text-[#9A948C] uppercase tracking-widest">{task.status.replace("_", " ")}</span>
                                 <span className="text-[#BAB0A0]">|</span>
                                 {agent && (
                                   <div className="flex items-center gap-1.5 grayscale group-hover:grayscale-0 transition-all">
                                      <AgentPill agent={agent} size={14} />
                                      <span className="text-[9px] font-mono text-[#6B655E] uppercase">{agent.displayName}</span>
                                   </div>
                                 )}
                              </div>
                           </div>
                        </div>
                        <Link href={`/campaigns/${campaignId}/tasks/${task.id}` as Route}>
                          <Button variant="ghost" className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity">
                             <ArrowLeftIcon className="rotate-180" />
                          </Button>
                        </Link>
                     </div>
                   );
                })}
             </div>
          </section>
        </div>

        {/* ── Sidebar ────────────────────────────────────────── */}
        <aside className="space-y-6 sticky top-6">
           <div className="border border-[var(--border)] bg-[var(--card)] divide-y divide-[var(--border)]">
              <div className="px-5 py-4">
                 <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.14em", color: "var(--muted-foreground)" }}>Architectural Controls</p>
              </div>
              <button className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all group">
                 <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, fontWeight: 700, textTransform: "uppercase" }}>Execute Move</span>
                 <PlayIcon className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all group">
                 <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, fontWeight: 700, textTransform: "uppercase" }}>Re-plan Sequence</span>
                 <MixerHorizontalIcon className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
              </button>
              <button className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all group">
                 <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, fontWeight: 700, textTransform: "uppercase" }}>Discuss with Lead</span>
                 <ChatBubbleIcon className="w-4 h-4 group-hover:scale-110 transition-transform" />
              </button>
           </div>

           <div className="p-6 border border-[#E5DED4] bg-[#FBF8F2] space-y-4">
              <p className="text-[10px] uppercase font-bold tracking-widest text-[#6B655E]">Move Context</p>
              <p className="text-xs text-[#6B655E] font-light italic leading-relaxed">
                 Moves are sequential blocks of tactical execution. This move was authorized by the Council of 21 after the Q2 Performance Review.
              </p>
           </div>
        </aside>

      </div>
    </div>
  );
}
