"use client";

import React, { useState, useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  ChevronRight, 
  ChevronDown, 
  AlertCircle, 
  FileText, 
  BarChart2, 
  TrendingUp, 
  CheckCircle, 
  Radio, 
  Users, 
  ShoppingCart, 
  Heart, 
  RefreshCcw,
  Target
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { cn } from "@/lib/cn";

/* ─── Types ─────────────────────────────────────────────────── */

interface CampaignDetail {
  campaign_id: string;
  name: string;
  goal_type: "awareness" | "leads" | "conversion" | "retention" | "re_engagement";
  status: "draft" | "pending_approval" | "active" | "paused" | "completed";
  start_date: string;
  end_date: string;
  progress_pct: number;
  tasks_completed: number;
  tasks_total: number;
  tasks_due_today: number;
  current_move?: {
    move_id: string;
    name: string;
    type: string;
    sub_goal: string;
    day_number: number;
    total_days: number;
    tasks_completed: number;
    tasks_total: number;
  };
  council_rationale: {
    synthesis: string;
    participating_agents: string[];
  };
  outcome_projection: string;
}

interface Move {
  move_id: string;
  move_number: number;
  name: string;
  type: string;
  sub_goal: string;
  start_date: string;
  end_date: string;
  status: "upcoming" | "active" | "completed" | "overdue";
  tasks_completed: number;
  tasks_total: number;
}

interface Task {
  task_id: string;
  title: string;
  task_type: "publish_content" | "review_performance" | "execute_ad" | "approve_content";
  channel: string;
  status: "pending" | "due" | "ready_for_review" | "approved" | "completed" | "missed";
  content_ready: boolean;
  assigned_agent_key: string;
  assigned_agent_name: string;
  scheduled_date: string;
  move_name: string;
}

/* ─── Main Component ────────────────────────────────────────── */

export default function CampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const campaignId = params.campaignId as string;

  const [activeTab, setActiveTab] = useState<"overview" | "moves" | "tasks" | "performance">("overview");
  const [rationaleExpanded, setRationaleExpanded] = useState(true);
  const [taskFilter, setTaskFilter] = useState<"all" | "due" | "ready" | "completed" | "missed">("all");

  // ─── Queries ────────────────────────────────────────────────

  const { data: campaign, isLoading: isCampaignLoading } = useQuery<CampaignDetail>({
    queryKey: ["campaign", campaignId],
    queryFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to fetch campaign details");
      return res.json();
    }
  });

  const { data: movesData, isLoading: isMovesLoading } = useQuery<{ moves: Move[] }>({
    queryKey: ["campaign_moves", campaignId],
    enabled: activeTab === "moves",
    queryFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}/moves`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to fetch moves");
      return res.json();
    }
  });

  const { data: tasksData, isLoading: isTasksLoading } = useQuery<{ tasks: Task[] }>({
    queryKey: ["campaign_tasks", campaignId],
    enabled: activeTab === "tasks" || activeTab === "overview",
    queryFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}/tasks`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to fetch tasks");
      return res.json();
    }
  });

  const approveMutation = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}/approve`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Approval failed");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaign", campaignId] });
      // Implicitly handled: show fixed toast in app (simplified here)
    }
  });

  // ─── Shared Components ───────────────────────────────────────

  const GoalChip = ({ type }: { type: CampaignDetail["goal_type"] }) => {
    const map = {
      awareness: { icon: Radio, label: "Awareness" },
      leads: { icon: Users, label: "Lead Generation" },
      conversion: { icon: ShoppingCart, label: "Conversion" },
      retention: { icon: Heart, label: "Retention" },
      re_engagement: { icon: RefreshCcw, label: "Re-engagement" },
    };
    const { icon: Icon, label } = map[type || "awareness"];
    return (
      <div className="bg-[#262626] rounded-full px-3 py-1 text-xs text-zinc-300 flex items-center gap-1.5 border border-zinc-700/50">
        <Icon className="w-3 h-3 text-zinc-400" />
        {label}
      </div>
    );
  };

  const statusVariants = {
    active: "bg-green-500/10 text-green-500 border border-green-500/30 text-xs",
    draft: "bg-zinc-800 text-zinc-400 text-xs border-transparent",
    pending_approval: "bg-amber-500/10 text-amber-500 border border-amber-500/30 text-xs",
    paused: "bg-zinc-800 text-zinc-500 text-xs border-transparent",
    completed: "bg-blue-500/10 text-blue-400 border border-blue-500/30 text-xs",
  };

  // ─── Rendering Helper Logic ──────────────────────────────────

  const formatDate = (date: string) => new Date(date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

  // ─── Final JSX ───────────────────────────────────────────────

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 bg-[#121212] min-h-screen">
      
      {/* ─── Breadcrumb ────────────────────────────────────────── */}
      <div className="flex items-center gap-2 text-sm mb-6 transition-opacity">
        <span 
          className="text-zinc-500 cursor-pointer hover:text-zinc-300 transition-colors"
          onClick={() => router.push('/app/campaigns')}
        >
          Campaigns
        </span>
        <ChevronRight className="w-4 h-4 text-zinc-700" />
        {isCampaignLoading ? (
          <Skeleton className="w-48 h-4 rounded" />
        ) : (
          <span className="text-white font-medium">{campaign?.name}</span>
        )}
      </div>

      {/* ─── Campaign Header Card ──────────────────────────────── */}
      <div className="bg-[#1a1a1a] rounded-2xl p-6 border border-zinc-800 mb-6">
        {isCampaignLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-8 w-64 rounded-md" />
            <Skeleton className="h-4 w-96 rounded-md" />
            <Skeleton className="h-2 w-full rounded-full" />
          </div>
        ) : campaign && (
          <>
            <div className="flex justify-between items-start mb-3">
              <h1 className="text-2xl text-white font-bold">{campaign.name}</h1>
              <Badge className={cn("px-2 py-0.5 rounded-md uppercase font-bold tracking-widest", statusVariants[campaign.status])} variant="outline">
                {campaign.status.replace('_', ' ')}
              </Badge>
            </div>

            <div className="flex items-center gap-4 mb-4 text-sm text-zinc-400">
              <GoalChip type={campaign.goal_type} />
              <span className="text-zinc-700">·</span>
              <div className="flex items-center gap-1.5 font-mono">
                {formatDate(campaign.start_date)} – {formatDate(campaign.end_date)}
              </div>
            </div>

            <div className="mb-4">
              <div className="flex justify-between mb-1.5">
                <span className="text-xs text-zinc-500 font-mono uppercase tracking-widest">
                  {campaign.tasks_completed} of {campaign.tasks_total} tasks completed
                </span>
                <span className={cn("text-xs font-mono uppercase tracking-widest font-bold", campaign.tasks_due_today > 0 ? "text-amber-500" : "text-zinc-500")}>
                  {campaign.tasks_due_today} due today
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-zinc-800 overflow-hidden">
                <div 
                  className="bg-amber-500 h-full rounded-full transition-all duration-700 shadow-[0_0_10px_rgba(245,158,11,0.3)]" 
                  style={{ width: `${campaign.progress_pct}%` }}
                />
              </div>
            </div>

            <div className="pt-2 border-t border-zinc-900 mt-4">
              <div 
                className="flex justify-between items-center cursor-pointer group"
                onClick={() => setRationaleExpanded(!rationaleExpanded)}
              >
                <span className="text-sm text-zinc-500 group-hover:text-zinc-400 transition-colors uppercase tracking-widest font-bold">Council rationale</span>
                <ChevronDown className={cn("w-4 h-4 text-zinc-600 transition-transform duration-300", rationaleExpanded && "rotate-180")} />
              </div>
              
              <div className={cn(
                "overflow-hidden transition-all duration-500 ease-in-out",
                rationaleExpanded ? "max-h-96 opacity-100 mt-4" : "max-h-0 opacity-0"
              )}>
                <div className="bg-[#0f0f0f] rounded-xl p-4 border-l-4 border-amber-500 mb-3">
                   <p className="text-sm text-zinc-300 italic leading-relaxed">
                     "{campaign.council_rationale.synthesis}"
                   </p>
                </div>
                <div className="flex flex-wrap gap-2 mt-4 ml-1">
                   {campaign.council_rationale.participating_agents.map(agent => (
                     <div key={agent} className="bg-zinc-800 rounded-full px-3 py-1 text-[10px] text-zinc-500 font-bold uppercase tracking-widest border border-zinc-700/30">
                       {agent}
                     </div>
                   ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* ─── Pending Approval Banner ───────────────────────────── */}
      {campaign?.status === 'pending_approval' && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 mb-6 flex items-center justify-between animate-in fade-in slide-in-from-top-2 duration-500">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-amber-500 shrink-0" />
            <div>
              <p className="text-sm text-white font-medium">Awaiting your approval</p>
              <p className="text-xs text-zinc-400">Review the campaign structure below, then approve to activate.</p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Button 
              size="sm" 
              className="bg-amber-500 text-black hover:bg-amber-400 font-bold h-9 px-4 uppercase text-[10px] tracking-widest"
              onClick={() => approveMutation.mutate()}
              disabled={approveMutation.isPending}
            >
              {approveMutation.isPending ? "Activating..." : "Approve Strategy →"}
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              className="text-zinc-500 hover:text-white transition-colors text-[10px] h-9 px-3 uppercase tracking-widest"
              onClick={() => setActiveTab('moves')}
            >
              Request changes
            </Button>
          </div>
        </div>
      )}

      {/* ─── Tabs List ─────────────────────────────────────────── */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="w-full">
        <TabsList className="bg-[#1a1a1a] border border-zinc-800 rounded-xl p-1 mb-6 flex gap-1 h-auto w-fit">
          {["overview", "moves", "tasks", "performance"].map(tab => (
            <TabsTrigger 
              key={tab}
              value={tab}
              className="text-[11px] uppercase tracking-[0.2em] font-bold text-zinc-500 data-[state=active]:text-white data-[state=active]:bg-[#262626] rounded-lg px-6 py-2.5 transition-all"
            >
              {tab}
            </TabsTrigger>
          ))}
        </TabsList>

        {/* ─── Overview Tab ────────────────────────────────────── */}
        <TabsContent value="overview" className="mt-0">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            
            {/* Left Card: Today's Tasks */}
            <div className="bg-[#1a1a1a] rounded-2xl border border-zinc-800 overflow-hidden flex flex-col h-full">
               <div className="px-5 py-4 border-b border-zinc-800 flex justify-between items-center bg-[#1f1f1f]/30">
                 <h3 className="text-sm text-white font-bold uppercase tracking-[0.15em]">Today's tasks</h3>
                 <Badge className="bg-amber-500/10 text-amber-500 border-amber-500/20 text-[10px] font-bold h-5 px-2 rounded-full">
                   {campaign?.tasks_due_today || 0}
                 </Badge>
               </div>

               <div className="flex-1">
                 {isTasksLoading ? (
                   <div className="p-3 space-y-1">
                     <Skeleton className="h-12 w-full rounded-xl" />
                     <Skeleton className="h-12 w-full rounded-xl" />
                     <Skeleton className="h-12 w-full rounded-xl" />
                   </div>
                 ) : (
                   () => {
                     const todayTasks = tasksData?.tasks.filter(t => t.status === 'due' || new Date(t.scheduled_date).toDateString() === new Date().toDateString()) || [];
                     if (todayTasks.length === 0) {
                       return (
                         <div className="py-24 flex flex-col items-center justify-center gap-2 opacity-40">
                            <CheckCircle className="w-8 h-8 text-zinc-500" />
                            <p className="text-xs text-zinc-500 font-mono uppercase tracking-widest">No tasks due today. You're ahead.</p>
                         </div>
                       );
                     }
                     return todayTasks.map(task => {
                        const Icon = { publish_content: FileText, review_performance: BarChart2, execute_ad: TrendingUp, approve_content: CheckCircle }[task.task_type] || FileText;
                        return (
                          <div 
                            key={task.task_id}
                            className="px-5 py-4 border-b border-zinc-800 last:border-0 flex items-center justify-between hover:bg-[#222222] transition-colors cursor-pointer group"
                            onClick={() => router.push(`/app/campaigns/${campaignId}/tasks/${task.task_id}`)}
                          >
                            <div className="flex items-center gap-3 min-w-0">
                               <Icon className="w-4 h-4 text-zinc-600 group-hover:text-amber-500 transition-colors" />
                               <span className="text-sm text-white font-medium truncate pr-4">{task.title}</span>
                            </div>
                            <div className="flex items-center gap-3 shrink-0">
                               <Badge variant="outline" className="bg-zinc-800/50 border-zinc-800 text-zinc-500 text-[9px] font-bold uppercase tracking-wider px-2">
                                 {task.channel}
                               </Badge>
                               {task.content_ready && (
                                 <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
                               )}
                               <span className="text-[10px] text-amber-500 font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">Open →</span>
                            </div>
                          </div>
                        );
                     })
                   }
                 )()}
               </div>
            </div>

            {/* Right Card: Current Move */}
            <div className="bg-[#1a1a1a] rounded-2xl border border-zinc-800 p-6 flex flex-col justify-center h-full min-h-[220px]">
               <h3 className="text-sm text-white font-bold uppercase tracking-[0.15em] mb-6">Current move</h3>
               
               {campaign?.current_move ? (
                 <div className="space-y-4">
                    <div className="inline-block bg-amber-500 text-black text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-[0.2em] mb-1">
                      NOW
                    </div>
                    <h4 className="text-xl text-white font-bold tracking-tight">{campaign.current_move.name}</h4>
                    <p className="text-sm text-zinc-400 italic font-light max-w-sm mb-6 leading-relaxed">
                      "{campaign.current_move.sub_goal}"
                    </p>
                    
                    <div>
                      <div className="flex justify-between items-center text-[10px] font-mono text-zinc-500 uppercase font-bold tracking-widest mb-1.5">
                        <span>Day {campaign.current_move.day_number} of {campaign.current_move.total_days}</span>
                        <span>{campaign.current_move.tasks_completed} of {campaign.current_move.tasks_total} tasks</span>
                      </div>
                      <div className="w-full h-1 rounded-full bg-zinc-800 overflow-hidden">
                        <div 
                          className="bg-amber-500 h-1 rounded-full" 
                          style={{ width: `${(campaign.current_move.tasks_completed / campaign.current_move.tasks_total) * 100}%` }}
                        />
                      </div>
                    </div>
                 </div>
               ) : (
                 <div className="text-center py-10 opacity-40">
                    <Target className="w-8 h-8 text-zinc-600 mx-auto mb-3" />
                    <p className="text-xs text-zinc-500 font-mono uppercase tracking-widest">No active move.</p>
                 </div>
               )}
            </div>
          </div>
        </TabsContent>

        {/* ─── Moves Tab ───────────────────────────────────────── */}
        <TabsContent value="moves" className="mt-0">
          <div className="flex flex-col py-2 max-w-2xl">
            {isMovesLoading ? (
              <div className="space-y-6">
                <Skeleton className="h-24 w-full rounded-2xl" />
                <Skeleton className="h-24 w-full rounded-2xl" />
                <Skeleton className="h-24 w-full rounded-2xl" />
              </div>
            ) : (
              movesData?.moves.map((move, i) => (
                <div key={move.move_id} className="flex items-start gap-4 grow">
                  <div className="w-10 flex-shrink-0 flex flex-col items-center">
                    <div className={cn(
                      "w-8 h-8 rounded-full flex items-center justify-center text-xs font-mono font-bold flex-shrink-0 border transition-colors",
                      move.status === 'completed' ? "bg-green-500/10 text-green-500 border-green-500/30 shadow-[0_0_10px_rgba(34,197,94,0.15)]" :
                      move.status === 'active' ? "bg-amber-500/10 text-amber-500 border-amber-500/50 shadow-[0_0_10px_rgba(245,158,11,0.15)]" :
                      "bg-zinc-800 text-zinc-500 border-zinc-700"
                    )}>
                      {move.status === 'completed' ? <CheckCircle className="w-4 h-4" /> : move.move_number}
                    </div>
                    {move.status === 'active' && (
                      <span className="text-[8px] text-amber-500 font-bold uppercase tracking-widest mt-1.5">NOW</span>
                    )}
                    {i !== movesData.moves.length - 1 && (
                      <div className="w-px flex-1 min-h-[4rem] bg-zinc-800 mx-auto my-3" />
                    )}
                  </div>

                  <div className="flex-1 pb-10 group">
                    <div className="flex items-center gap-3 mb-1.5">
                       <h4 className="text-base text-white font-bold group-hover:text-amber-500 transition-colors tracking-tight">{move.name}</h4>
                       {move.status === 'active' && <Badge className="bg-amber-500 text-black text-[8px] font-bold uppercase tracking-widest h-4 px-1.5">Active</Badge>}
                    </div>
                    <div className="flex items-center gap-3 mb-3">
                       <div className="bg-[#262626] rounded-full px-2.5 py-0.5 text-[9px] text-zinc-400 font-bold uppercase tracking-widest border border-zinc-800/50">
                          {move.type.replace('_', ' ')}
                       </div>
                       <span className="text-[10px] text-zinc-600 font-mono tracking-tighter uppercase italic">
                          {formatDate(move.start_date)} – {formatDate(move.end_date)}
                       </span>
                    </div>
                    <p className="text-sm text-zinc-400 italic font-light mb-4 leading-relaxed line-clamp-2">
                       "{move.sub_goal}"
                    </p>
                    <div className="space-y-1.5">
                       <div className="flex justify-between items-center text-[9px] font-mono text-zinc-600 uppercase font-bold tracking-widest">
                          <span>{move.tasks_completed} / {move.tasks_total} Tasks</span>
                       </div>
                       <div className="w-full h-1 rounded-full bg-zinc-800 overflow-hidden">
                          <div 
                            className={cn(
                              "h-1 rounded-full transition-all duration-1000",
                              move.status === 'active' ? "bg-amber-500" : move.status === 'completed' ? "bg-green-500" : "bg-zinc-600"
                            )}
                            style={{ width: `${(move.tasks_completed / move.tasks_total) * 100}%` }}
                          />
                       </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </TabsContent>

        {/* ─── Tasks Tab ───────────────────────────────────────── */}
        <TabsContent value="tasks" className="mt-0">
          <div className="flex gap-2 mb-6 flex-wrap">
            {["all", "due", "ready", "completed", "missed"].map(f => (
              <button
                key={f}
                onClick={() => setTaskFilter(f as any)}
                className={cn(
                  "px-5 py-2.5 rounded-full border text-[10px] font-bold uppercase tracking-widest transition-all",
                  taskFilter === f 
                    ? "border-amber-500 text-white bg-amber-500/10 shadow-[0_0_10px_rgba(245,158,11,0.1)]" 
                    : "border-zinc-800 text-zinc-500 hover:border-zinc-700 hover:text-zinc-300"
                )}
              >
                {f.replace('_', ' ')}
              </button>
            ))}
          </div>

          <div className="flex flex-col gap-2">
            {isTasksLoading ? (
               <div className="space-y-2">
                 {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-20 w-full rounded-2xl" />)}
               </div>
            ) : (
              () => {
                const filteredTasks = tasksData?.tasks.filter(t => {
                  if (taskFilter === 'all') return true;
                  if (taskFilter === 'due') return t.status === 'due';
                  if (taskFilter === 'ready') return t.status === 'ready_for_review';
                  if (taskFilter === 'completed') return t.status === 'completed';
                  if (taskFilter === 'missed') return t.status === 'missed';
                  return true;
                }) || [];

                if (filteredTasks.length === 0) {
                  return (
                    <div className="py-24 flex flex-col items-center justify-center gap-2 opacity-40">
                       <Target className="w-8 h-8 text-zinc-500" />
                       <p className="text-xs text-zinc-500 font-mono uppercase tracking-widest">No {taskFilter} tasks.</p>
                    </div>
                  );
                }

                return filteredTasks.map(task => {
                  const Icon = { publish_content: FileText, review_performance: BarChart2, execute_ad: TrendingUp, approve_content: FileText }[task.task_type] || FileText;
                  return (
                    <div 
                      key={task.task_id}
                      onClick={() => router.push(`/app/campaigns/${campaignId}/tasks/${task.task_id}`)}
                      className="bg-[#1a1a1a] rounded-xl border border-zinc-800 px-5 py-4 flex items-center gap-4 hover:border-zinc-700 cursor-pointer transition-all group"
                    >
                      <div className="flex-shrink-0">
                         <Icon className={cn("w-5 h-5", task.task_type === 'review_performance' ? "text-blue-500" : task.task_type === 'execute_ad' ? "text-orange-500" : "text-zinc-600")} />
                      </div>
                      
                      <div className="flex-1 min-w-0 pr-4">
                        <h4 className="text-sm text-white font-semibold truncate mb-1 group-hover:text-amber-500 transition-colors">{task.title}</h4>
                        <div className="flex items-center gap-2 text-[10px] font-bold">
                           <span className="text-zinc-500 uppercase tracking-widest">{task.move_name}</span>
                           <span className="text-zinc-800">·</span>
                           <span className="text-zinc-500 uppercase tracking-widest">{task.channel}</span>
                           <span className="text-zinc-800">·</span>
                           <span className="text-zinc-600 font-mono italic">{formatDate(task.scheduled_date)}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 shrink-0">
                        {task.content_ready && (
                           <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" title="Content ready" />
                        )}
                        <div className="w-6 h-6 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-[10px] text-zinc-400 font-bold uppercase shadow-inner">
                           {task.assigned_agent_name.charAt(0)}
                        </div>
                        <Badge variant="outline" className={cn(
                          "rounded-full px-3 py-0.5 text-[9px] font-bold uppercase tracking-widest",
                          task.status === 'due' ? "bg-amber-500/10 text-amber-500 border-amber-500/30" :
                          task.status === 'ready_for_review' ? "bg-blue-500/10 text-blue-400 border-blue-500/30" :
                          task.status === 'approved' ? "bg-green-500/10 text-green-500" :
                          task.status === 'completed' ? "bg-zinc-800 text-zinc-500" :
                          task.status === 'missed' ? "bg-red-500/10 text-red-400 border-red-500/30" :
                          "bg-zinc-900 text-zinc-600"
                        )}>
                          {task.status === 'ready_for_review' ? 'Review' : task.status}
                        </Badge>
                        <ChevronRight className="w-4 h-4 text-zinc-700 group-hover:text-zinc-400 transition-colors" />
                      </div>
                    </div>
                  );
                });
              }
            )()}
          </div>
        </TabsContent>

        {/* ─── Performance Tab ──────────────────────────────────── */}
        <TabsContent value="performance" className="mt-0">
           <div className="py-24 flex flex-col items-center justify-center gap-3 animate-in fade-in duration-700">
             <div className="w-16 h-16 bg-[#1a1a1a] rounded-2xl flex items-center justify-center border border-zinc-800 mb-2">
                <BarChart2 className="w-8 h-8 text-zinc-700" />
             </div>
             <p className="text-lg text-white font-medium tracking-tight">Performance data</p>
             <p className="text-sm text-zinc-500 text-center max-w-xs leading-relaxed font-light">
               Appears here once your campaign has active tasks and live market ingestion results to report.
             </p>
           </div>
        </TabsContent>

      </Tabs>
    </div>
  );
}
