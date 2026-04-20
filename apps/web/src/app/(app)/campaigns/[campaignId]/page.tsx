"use client";

import * as React from "react";
import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import type { Route } from "next";
import { 
  ChevronRightIcon, 
  ChevronDownIcon, 
  ExclamationTriangleIcon, 
  FileTextIcon, 
  BarChartIcon, 
  RocketIcon, 
  CheckCircledIcon, 
  TargetIcon,
  MixerHorizontalIcon,
  InfoCircledIcon,
  LightningBoltIcon
} from "@radix-ui/react-icons";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { campaignsApi } from "@/lib/api";
import type { CampaignDetail, Move, Task } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { cn } from "@/lib/cn";
import { AgentPill } from "@/components/ui/agent-portrait";
import { AGENT_MAP } from "@/lib/agents";

export default function CampaignDetailPage(): React.ReactElement {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const campaignId = params.campaignId as string;

  const [activeTab, setActiveTab] = useState<"overview" | "moves" | "tasks" | "performance">("overview");
  const [rationaleExpanded, setRationaleExpanded] = useState(true);
  const [taskFilter, setTaskFilter] = useState<"all" | "due" | "ready" | "completed" | "missed">("all");

  // ─── Queries ────────────────────────────────────────────────

  const { data: campaign, isLoading: isCampaignLoading } = useQuery<CampaignDetail>({
    queryKey: ["campaign", campaignId],
    queryFn: () => campaignsApi.get(campaignId)
  });

  const { data: movesData, isLoading: isMovesLoading } = useQuery<{ moves: Move[] }>({
    queryKey: ["campaign_moves", campaignId],
    enabled: activeTab === "moves" || activeTab === "overview",
    queryFn: () => campaignsApi.getMoves(campaignId)
  });

  const { data: tasksData, isLoading: isTasksLoading } = useQuery<{ tasks: Task[] }>({
    queryKey: ["campaign_tasks", campaignId],
    enabled: activeTab === "tasks" || activeTab === "overview",
    queryFn: () => campaignsApi.getTasks(campaignId)
  });

  const approveMutation = useMutation({
    mutationFn: () => campaignsApi.updateStatus(campaignId, "active"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaign", campaignId] });
    }
  });

  // ─── Rendering Helper Logic ──────────────────────────────────

  const formatDate = (date: string) => new Date(date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

  // ─── Final JSX ───────────────────────────────────────────────

  return (
    <div className="flex flex-col gap-8 py-2">
      <GsapBridge stagger={true}>
        
        {/* ── Breadcrumb ── */}
        <div className="gsap-reveal flex items-center gap-2 text-[10px] font-mono font-bold uppercase tracking-widest text-[#9A948C] mb-2">
           <Link href={"/campaigns" as Route} className="hover:text-[#2A2622] transition-colors">Ledger</Link>
           <ChevronRightIcon className="w-3 h-3" />
           <span className="text-[#6B655E]">Campaign Profile</span>
        </div>

        {/* ── Campaign Header Card ── */}
        <section className="gsap-reveal border-2 border-[var(--foreground)] bg-white p-8 md:p-10 relative overflow-hidden">
           {/* Visual Flourish */}
           <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/5 rotate-45 translate-x-16 -translate-y-16 border-b border-l border-amber-500/10" />
           
           {isCampaignLoading ? (
             <div className="space-y-6">
                <Skeleton className="h-12 w-64" />
                <Skeleton className="h-4 w-full" />
             </div>
           ) : campaign && (
             <div className="relative z-10">
               <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
                  <div>
                    <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 48, lineHeight: 1, margin: 0 }} className="text-[#2A2622] mb-4">
                      {campaign.name}
                    </h1>
                    <div className="flex items-center gap-4">
                       <Badge variant="outline" className="border-amber-500/50 text-amber-500 font-mono text-[9px] uppercase tracking-[0.2em] rounded-none px-3 py-1 bg-amber-500/5">
                          {campaign.status}
                       </Badge>
                       <span className="text-[10px] font-mono text-[#9A948C] uppercase tracking-widest">{campaign.goal_type.replace('_', ' ')}</span>
                       <span className="h-1 w-1 bg-[#E5DED4] rounded-full" />
                       <span className="text-[10px] font-mono text-[#9A948C] uppercase tracking-widest">Est: {formatDate(campaign.start_date)} – {formatDate(campaign.end_date)}</span>
                    </div>
                  </div>
                  <div className="flex gap-3">
                     <Button variant="outline" className="border-[#E5DED4] text-[10px] font-mono font-bold uppercase tracking-widest h-10 px-6 rounded-none hover:bg-[#F5F0E8] transition-colors">
                        Edit Strategy
                     </Button>
                     {campaign.status === 'pending_approval' && (
                       <Button 
                         className="bg-amber-500 text-black text-[10px] font-mono font-bold uppercase tracking-widest h-10 px-8 rounded-none hover:bg-amber-400"
                         onClick={() => approveMutation.mutate()}
                         disabled={approveMutation.isPending}
                       >
                         {approveMutation.isPending ? "AUTHORIZING..." : "Authorize Execution"}
                       </Button>
                     )}
                  </div>
               </div>

               {/* Progress Ledger */}
               <div className="grid md:grid-cols-3 gap-8 py-8 border-t border-[#D5CBC0]">
                  <div className="space-y-3">
                     <p className="font-mono text-[9px] text-[#9A948C] uppercase tracking-widest">Operational Success</p>
                     <div className="flex items-end gap-3">
                        <span className="text-3xl font-[family-name:var(--font-display)] text-[#2A2622]">{campaign.progress_pct}%</span>
                        <div className="flex-1 h-1.5 bg-[#F5F0E8] mb-2 relative overflow-hidden">
                           <div className="h-full bg-amber-500" style={{ width: `${campaign.progress_pct}%` }} />
                        </div>
                     </div>
                  </div>
                  <div className="space-y-3">
                     <p className="font-mono text-[9px] text-[#9A948C] uppercase tracking-widest">Tasks Cleared</p>
                     <p className="text-3xl font-[family-name:var(--font-display)] text-[#2A2622]">
                        {campaign.tasks_completed}<span className="text-[#9A948C] mx-2">/</span>{campaign.tasks_total}
                     </p>
                  </div>
                  <div className="space-y-3">
                     <p className="font-mono text-[9px] text-[#9A948C] uppercase tracking-widest">Today's Load</p>
                     <p className={cn("text-3xl font-[family-name:var(--font-display)]", (campaign.tasks_due_today ?? 0) > 0 ? "text-amber-500" : "text-[#9A948C]")}>
                        {campaign.tasks_due_today ?? 0} Directives
                     </p>
                  </div>
               </div>

               {/* Council Deck */}
               <div className="mt-4 border-t border-[#D5CBC0] pt-8">
                  <button 
                    onClick={() => setRationaleExpanded(!rationaleExpanded)}
                    className="flex items-center justify-between w-full group"
                  >
                     <p className="font-mono text-[9px] font-bold text-[#6B655E] uppercase tracking-widest">Executive Rationale // Council Analysis</p>
                     <ChevronDownIcon className={cn("w-4 h-4 text-[#9A948C] transition-transform", rationaleExpanded && "rotate-180")} />
                  </button>
                  {rationaleExpanded && (
                    <div className="mt-6 flex flex-col md:flex-row gap-8 animate-in fade-in slide-in-from-top-4 duration-500">
                       <div className="flex-1">
                          <p className="text-[#6B655E] text-sm leading-relaxed italic font-light font-serif">
                            "{campaign.council_rationale.synthesis}"
                          </p>
                       </div>
                       <div className="flex flex-wrap gap-2 h-fit md:w-64">
                           {campaign.council_rationale.participating_agents.map(agentKey => {
                             const ag = AGENT_MAP.get(agentKey);
                             if (!ag) return null;
                             return (<div key={agentKey} className="grayscale hover:grayscale-0 transition-all opacity-40 hover:opacity-100"><AgentPill agent={ag} size={24} /></div>);
                           })}
                       </div>
                    </div>
                  )}
               </div>
             </div>
           )}
        </section>

        {/* ── Tabs Buffer ── */}
        <section className="gsap-reveal mt-12">
           <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "overview" | "moves" | "tasks" | "performance")} className="w-full">
              <TabsList className="bg-transparent border-b border-[#D5CBC0] w-full justify-start h-auto p-0 rounded-none mb-10">
                {["overview", "moves", "tasks", "performance"].map(tab => (
                  <TabsTrigger 
                    key={tab}
                    value={tab}
                    className="px-8 py-3 text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-[#9A948C] data-[state=active]:text-[#2A2622] data-[state=active]:border-b-2 data-[state=active]:border-amber-500 rounded-none bg-transparent transition-all"
                  >
                    {tab}
                  </TabsTrigger>
                ))}
              </TabsList>

              {/* ── Overview Tab ── */}
              <TabsContent value="overview" className="mt-0">
                 <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                    
                    {/* Active Directives */}
                    <div className="space-y-6">
                       <div className="flex items-center justify-between">
                          <h3 className="text-xs font-mono font-bold text-[#6B655E] uppercase tracking-widest">Active Directives</h3>
                          <span className="text-[10px] font-mono text-[#BAB0A0] uppercase tracking-widest">Load Order</span>
                       </div>
                       <div className="border border-[#D5CBC0] bg-white divide-y divide-zinc-900">
                          {isTasksLoading ? (
                            <Skeleton className="h-40 w-full" />
                          ) : tasksData?.tasks.filter(t => t.status === 'due' || t.status === 'ready_for_review').slice(0, 5).map(task => (
                            <div 
                              key={task.task_id}
                              onClick={() => router.push(`/campaigns/${campaignId}/tasks/${task.task_id}` as Route)}
                              className="p-5 flex items-center justify-between group hover:bg-white/[0.01] transition-colors cursor-pointer"
                            >
                               <div className="flex items-center gap-4">
                                  <div className="w-1.5 h-1.5 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
                                  <div>
                                     <p className="text-[13px] font-medium text-[#9A948C] group-hover:text-[#2A2622] transition-colors">{task.title}</p>
                                     <p className="text-[9px] font-mono text-[#9A948C] uppercase tracking-widest">{task.channel} // {task.move_name}</p>
                                  </div>
                               </div>
                               <ChevronRightIcon className="w-4 h-4 text-[#BAB0A0] group-hover:text-amber-500 transition-colors" />
                            </div>
                          ))}
                          {(!tasksData || tasksData.tasks.filter(t => t.status === 'due' || t.status === 'ready_for_review').length === 0) && (
                            <div className="p-12 text-center">
                               <p className="text-[10px] font-mono text-[#9A948C] uppercase tracking-widest">Tactical queue empty.</p>
                            </div>
                          )}
                       </div>
                    </div>

                    {/* Operational Phase */}
                    <div className="space-y-6">
                       <h3 className="text-xs font-mono font-bold text-[#6B655E] uppercase tracking-widest">Operational Phase</h3>
                       {campaign?.current_move ? (
                         <div className="border-2 border-[#E5DED4] bg-white p-8 space-y-6">
                            <div className="space-y-2">
                               <p className="text-[9px] font-mono font-bold text-amber-500 uppercase tracking-widest">Current Initiative</p>
                               <h4 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 28 }} className="text-[#2A2622]">
                                 {campaign.current_move.name}
                               </h4>
                            </div>
                            <p className="text-[#6B655E] text-sm leading-relaxed italic font-light">
                               "{campaign.current_move.sub_goal}"
                            </p>
                            <div className="pt-4 border-t border-[#D5CBC0] grid grid-cols-2 gap-8">
                               <div>
                                  <p className="font-mono text-[8px] text-[#9A948C] uppercase tracking-widest mb-1">Timeline</p>
                                  <p className="text-sm font-bold text-[#2A2622] uppercase tracking-tight">Day {campaign.current_move.day_number} / {campaign.current_move.total_days}</p>
                               </div>
                               <div>
                                  <p className="font-mono text-[8px] text-[#9A948C] uppercase tracking-widest mb-1">Clearance</p>
                                  <p className="text-sm font-bold text-[#2A2622] uppercase tracking-tight">{campaign.current_move.tasks_completed} / {campaign.current_move.tasks_total} OPS</p>
                               </div>
                            </div>
                            <Button 
                              variant="outline" 
                              className="w-full border-[#E5DED4] text-[10px] font-mono uppercase tracking-[0.2em] h-10 rounded-none hover:bg-[#F5F0E8]"
                              onClick={() => setActiveTab('moves')}
                            >
                               View Full Sequence
                            </Button>
                         </div>
                       ) : (
                         <div className="border border-dashed border-[#E5DED4] p-12 text-center">
                            <TargetIcon className="w-8 h-8 text-[#BAB0A0] mx-auto mb-4" />
                            <p className="text-[10px] font-mono text-[#9A948C] uppercase tracking-widest">No active phase.</p>
                         </div>
                       )}
                    </div>
                 </div>
              </TabsContent>

              {/* ── Moves Tab ── */}
              <TabsContent value="moves" className="mt-0">
                 <div className="space-y-2 border border-[#E5DED4] bg-white divide-y divide-zinc-900">
                    {isMovesLoading ? (
                      <Skeleton className="h-64 w-full" />
                    ) : movesData?.moves.map((move) => (
                      <Link 
                        key={move.move_id}
                        href={`/campaigns/${campaignId}/moves/${move.move_id}` as Route}
                        className="p-8 flex items-center justify-between group hover:bg-white/[0.01] transition-colors"
                      >
                         <div className="flex items-start gap-8">
                            <div className={cn(
                              "w-10 h-10 border flex items-center justify-center font-mono text-xs font-bold transition-all",
                              move.status === 'active' ? "bg-amber-500 border-amber-500 text-black shadow-[0_0_15px_rgba(245,158,11,0.3)]" : 
                              move.status === 'completed' ? "bg-[#F5F0E8] border-[#E5DED4] text-[#6B655E]" :
                              "bg-transparent border-[#E5DED4] text-[#9A948C]"
                            )}>
                               {move.move_number}
                            </div>
                            <div>
                               <div className="flex items-center gap-3 mb-1">
                                  <h4 className="text-xl font-bold text-[#2A2622] tracking-tight uppercase group-hover:text-amber-500 transition-colors">{move.name}</h4>
                                  {move.status === 'active' && <Badge className="bg-amber-500 text-black text-[8px] font-bold uppercase tracking-widest px-1.5 h-4">Executing</Badge>}
                               </div>
                               <p className="text-[10px] font-mono text-[#6B655E] uppercase tracking-widest">{move.type} // {move.sub_goal}</p>
                               <p className="text-[10px] font-mono text-[#9A948C] uppercase tracking-widest mt-2">{formatDate(move.start_date)} – {formatDate(move.end_date)}</p>
                            </div>
                         </div>
                         <div className="flex items-center gap-8">
                            <div className="text-right hidden sm:block">
                               <p className="text-[9px] font-mono text-[#BAB0A0] uppercase tracking-widest mb-1">Completion</p>
                               <p className="text-xs font-bold text-[#6B655E] uppercase tracking-tight">{move.tasks_completed} / {move.tasks_total} OPS</p>
                            </div>
                            <ChevronRightIcon className="w-5 h-5 text-[#BAB0A0] group-hover:text-[#2A2622] transition-colors" />
                         </div>
                      </Link>
                    ))}
                 </div>
              </TabsContent>

              {/* ── Tasks Tab ── */}
              <TabsContent value="tasks" className="mt-0">
                 <div className="flex gap-4 mb-10 overflow-x-auto pb-2 scrollbar-hide">
                    {["all", "due", "ready", "completed", "missed"].map(f => (
                      <button
                        key={f}
                        onClick={() => setTaskFilter(f as any)}
                        className={cn(
                          "px-6 py-2 border-2 text-[9px] font-mono font-bold uppercase tracking-widest transition-all whitespace-nowrap",
                          taskFilter === f ? "border-amber-500 bg-amber-500 text-black" : "border-[#E5DED4] text-[#9A948C] hover:border-[#BAB0A0]"
                        )}
                      >
                        {f}
                      </button>
                    ))}
                 </div>
                 <div className="space-y-4">
                    {tasksData?.tasks.filter(t => {
                      if (taskFilter === 'all') return true;
                      if (taskFilter === 'due') return t.status === 'due' || t.status === 'pending';
                      if (taskFilter === 'ready') return t.status === 'ready_for_review';
                      return t.status === taskFilter;
                    }).map(task => (
                      <div 
                        key={task.task_id}
                        onClick={() => router.push(`/campaigns/${campaignId}/tasks/${task.task_id}` as Route)}
                        className="border border-[#D5CBC0] bg-white p-5 flex flex-col md:flex-row md:items-center justify-between group hover:border-[#BAB0A0] transition-all cursor-pointer gap-6"
                      >
                         <div className="flex items-center gap-5">
                            <div className="w-10 h-10 border border-[#D5CBC0] flex items-center justify-center group-hover:bg-[#F5F0E8] transition-colors">
                               {task.task_type === 'publish_content' ? <FileTextIcon className="w-4 h-4 text-[#9A948C]" /> : 
                                task.task_type === 'review_performance' ? <BarChartIcon className="w-4 h-4 text-[#9A948C]" /> :
                                <RocketIcon className="w-4 h-4 text-[#9A948C]" />}
                            </div>
                            <div>
                               <p className="text-[13px] font-bold text-[#9A948C] group-hover:text-amber-500 transition-colors uppercase tracking-tight">{task.title}</p>
                               <div className="flex items-center gap-3 mt-1">
                                  <span className="text-[9px] font-mono text-[#9A948C] uppercase tracking-widest">{task.channel}</span>
                                  <span className="text-[9px] font-mono text-[#BAB0A0] uppercase tracking-widest">//</span>
                                  <span className="text-[9px] font-mono text-[#9A948C] uppercase tracking-widest">{task.move_name}</span>
                               </div>
                            </div>
                         </div>
                         <div className="flex items-center gap-6 justify-between md:justify-end">
                            <div className="flex items-center gap-3">
                               <div className="text-right">
                                  <p className="text-[8px] font-mono text-[#9A948C] uppercase tracking-widest">Agent Link</p>
                                  <p className="text-[10px] font-bold text-[#6B655E] uppercase tracking-tight">{task.assigned_agent_name}</p>
                               </div>
                               <div className="w-6 h-6 border border-[#E5DED4] flex items-center justify-center font-mono text-[9px] text-[#6B655E]">
                                  {task.assigned_agent_name.charAt(0)}
                               </div>
                            </div>
                            <div className="flex items-center gap-4">
                               <Badge variant="outline" className={cn(
                                 "rounded-none border-[#E5DED4] font-mono text-[9px] px-3 py-1 uppercase tracking-widest",
                                 task.status === 'due' ? "text-amber-500 border-amber-900" :
                                 task.status === 'ready_for_review' ? "text-blue-500 border-blue-900" :
                                 "text-[#9A948C]"
                               )}>
                                 {task.status}
                               </Badge>
                               <ChevronRightIcon className="w-4 h-4 text-[#2A2622] group-hover:text-[#2A2622] transition-colors" />
                            </div>
                         </div>
                      </div>
                    ))}
                 </div>
              </TabsContent>

              {/* ── Performance Tab ── */}
              <TabsContent value="performance" className="mt-0">
                 <div className="border border-dashed border-[#E5DED4] p-24 text-center">
                    <BarChartIcon className="w-10 h-10 text-[#BAB0A0] mx-auto mb-6 opacity-30" />
                    <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24 }} className="text-[#9A948C]">Collecting Market Signals</p>
                    <p className="text-[10px] font-mono text-[#9A948C] uppercase tracking-widest mt-2 max-w-sm mx-auto leading-relaxed">
                      Performance matrix will materialize once the first phase completes and ingestion results are verified by the Council.
                    </p>
                 </div>
              </TabsContent>

           </Tabs>
        </section>

      </GsapBridge>
    </div>
  );
}
