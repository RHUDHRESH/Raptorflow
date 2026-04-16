"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  ChevronRight, 
  Calendar, 
  Clock, 
  Loader2, 
  FileText, 
  BarChart2, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  MessageSquare,
  AlertCircle,
  ExternalLink,
  RefreshCw,
  Edit2
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/cn";

/* ─── Types ─────────────────────────────────────────────────── */

interface TaskDetail {
  task_id: string;
  title: string;
  task_type: "publish_content" | "review_performance" | "execute_ad" | "approve_content";
  channel: string;
  status: string;
  scheduled_date: string;
  description: string;
  content_ready: boolean;
  assigned_agent_key: string;
  assigned_agent_name: string;
  move_name: string;
  campaign_name: string;
  content: {
    content_id: string;
    body: string;
    headline: string | null;
    hashtags: string[] | null;
    image_direction: string | null;
    posting_time: string | null;
    format: "social_post" | "email" | "ad_copy" | "long_form";
  } | null;
  performance_summary: {
    metrics: Array<{ label: string; value: string; vs_target: "above" | "on" | "below"; trend: string }>;
    recommendation: string;
  } | null;
  ad_instruction: string | null;
  ad_reasoning: string | null;
}

/* ─── Main Component ────────────────────────────────────────── */

export default function TaskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  
  const campaignId = params.campaignId as string;
  const taskId = params.taskId as string;

  const [revisionOpen, setRevisionOpen] = useState(false);
  const [revisionNotes, setRevisionNotes] = useState("");
  const [skipOpen, setSkipOpen] = useState(false);
  const [skipReason, setSkipReason] = useState("");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // ─── Toast Logic ───────────────────────────────────────────
  useEffect(() => {
    if (toastMessage) {
      const timer = setTimeout(() => setToastMessage(null), 2500);
      return () => clearTimeout(timer);
    }
  }, [toastMessage]);

  // ─── Queries ────────────────────────────────────────────────
  const { data: task, isLoading, isError, refetch } = useQuery<TaskDetail>({
    queryKey: ["task", taskId],
    queryFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}/tasks/${taskId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to fetch task details");
      return res.json();
    }
  });

  // ─── Mutations ──────────────────────────────────────────────
  const approveMutation = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}/tasks/${taskId}/approve`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Approval failed");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["task", taskId] });
      setToastMessage("Approved ✓");
      setTimeout(() => router.push(`/app/campaigns/${campaignId}`), 1000);
    }
  });

  const revisionMutation = useMutation({
    mutationFn: async (notes: string) => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}/tasks/${taskId}/request-revision`, {
        method: "PATCH",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ revision_notes: notes })
      });
      if (!res.ok) throw new Error("Revision request failed");
      return res.json();
    },
    onSuccess: () => {
      setRevisionOpen(false);
      setRevisionNotes("");
      queryClient.invalidateQueries({ queryKey: ["task", taskId] });
      setToastMessage("Revision requested");
    }
  });

  const completeMutation = useMutation({
    mutationFn: async (reason?: string) => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns/${campaignId}/tasks/${taskId}/complete`, {
        method: "PATCH",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ override_reason: reason })
      });
      if (!res.ok) throw new Error("Completion failed");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["task", taskId] });
      setToastMessage(skipOpen ? "Task skipped" : "Task completed ✓");
      setTimeout(() => router.push(`/app/campaigns/${campaignId}`), 1000);
    }
  });

  // ─── Rendering Helpers ──────────────────────────────────────────

  if (isLoading) return <TaskSkeleton />;
  if (isError || !task) return <TaskErrorState onRetry={refetch} />;

  const statusVariants: Record<string, string> = {
    pending: "bg-zinc-800 text-zinc-500",
    due: "bg-amber-500/10 text-amber-500 border border-amber-500/30",
    ready_for_review: "bg-blue-500/10 text-blue-400 border border-blue-500/30",
    approved: "bg-green-500/10 text-green-500 border border-green-500/30",
    completed: "bg-zinc-700 text-zinc-400",
    missed: "bg-red-500/10 text-red-400 border border-red-500/30",
  };

  const formattedDate = new Date(task.scheduled_date).toLocaleDateString(undefined, {
    weekday: 'long', month: 'short', day: 'numeric'
  });

  // ─── Final JSX ─────────────────────────────────────────────────

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 bg-[#121212] min-h-screen pb-32">
      
      {/* ─── Breadcrumb ─────────────────────────────────────────── */}
      <div className="flex items-center gap-2 text-sm mb-6 transition-opacity">
        <span 
          className="text-zinc-500 cursor-pointer hover:text-zinc-300 transition-colors capitalize px-1"
          onClick={() => router.push('/app/campaigns')}
        >
          Campaigns
        </span>
        <ChevronRight className="w-4 h-4 text-zinc-700" />
        <span 
          className="text-zinc-500 cursor-pointer hover:text-zinc-300 transition-colors truncate max-w-[200px] px-1"
          onClick={() => router.push(`/app/campaigns/${campaignId}`)}
        >
          {task.campaign_name}
        </span>
        <ChevronRight className="w-4 h-4 text-zinc-700" />
        <span className="text-white font-medium px-1 truncate flex-1">{task.title}</span>
      </div>

      {/* ─── Task Header Card ───────────────────────────────────── */}
      <div className="bg-[#1a1a1a] rounded-2xl p-6 border border-zinc-800 mb-5">
        <div className="flex justify-between items-start mb-4">
          <h1 className="text-xl text-white font-bold leading-tight flex-1 mr-4">{task.title}</h1>
          <div className="flex items-center gap-2 shrink-0">
             {task.content_ready && (
               <Badge className="bg-green-500/10 text-green-500 border border-green-500/30 rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-widest h-6">
                 Content ready
               </Badge>
             )}
             <Badge className={cn("px-3 py-1 rounded-full text-[10px] uppercase font-serif tracking-[0.2em] h-6", statusVariants[task.status] || "bg-zinc-800 text-zinc-500")} variant="outline">
                {task.status.replace('_', ' ')}
             </Badge>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-y-2 gap-x-4 text-sm text-zinc-400 border-t border-zinc-900 pt-4">
           <Badge variant="outline" className="bg-zinc-800 border-transparent rounded-full px-3 py-1 text-[10px] font-bold text-zinc-400 uppercase tracking-widest h-6">
              {task.channel}
           </Badge>
           <span className="text-zinc-800">·</span>
           <div className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-tighter">
              <Calendar className="w-4 h-4 text-zinc-600" />
              {formattedDate}
           </div>
           <span className="text-zinc-800">·</span>
           <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-[10px] font-bold text-zinc-300 uppercase shadow-inner">
                 {task.assigned_agent_name.charAt(0)}
              </div>
              <span className="text-[11px] font-bold uppercase tracking-widest">{task.assigned_agent_name}</span>
           </div>
        </div>

        {task.description && (
          <p className="text-sm text-zinc-400 mt-4 leading-relaxed font-light italic border-l-2 border-zinc-800 pl-4 py-1">
            {task.description}
          </p>
        )}
      </div>

      {/* ─── Task Surface Routing ──────────────────────────────── */}

      {/* SURFACE A: Content Review (publish_content | approve_content) */}
      {(task.task_type === "publish_content" || task.task_type === "approve_content") && (
        <div className="animate-in fade-in duration-500">
          <div className="bg-[#0f0f0f] rounded-2xl border border-zinc-800 overflow-hidden mb-5 flex flex-col min-h-[300px]">
             
             {/* Content Header */}
             <div className="px-5 py-3 border-b border-zinc-800 flex justify-between items-center bg-[#121212]">
                <div className="flex items-center gap-2.5">
                   <div className="w-6 h-6 bg-zinc-900 border border-zinc-800 rounded-full text-[10px] font-bold text-zinc-400 flex items-center justify-center">
                      {task.assigned_agent_name.charAt(0)}
                   </div>
                   <span className="text-[10px] uppercase font-bold text-zinc-500 tracking-widest">
                      Written by {task.assigned_agent_name}
                   </span>
                </div>
                {task.content && (
                  <Badge className="bg-zinc-900 border-zinc-800 text-zinc-600 text-[9px] font-bold px-2 py-0.5 rounded-full uppercase tracking-tighter">
                     {task.content.format.replace('_', ' ')}
                  </Badge>
                )}
             </div>

             {/* Content Body */}
             <div className="px-8 py-10 flex-1">
                {task.content ? (
                  <div className="space-y-6">
                    {task.content.format === "social_post" && (
                      <div className="space-y-6">
                         {task.content.headline && (
                           <h3 className="text-sm text-zinc-400 font-medium tracking-tight mb-3">
                             {task.content.headline}
                           </h3>
                         )}
                         <div className="text-lg text-white font-light leading-relaxed whitespace-pre-wrap font-serif selection:bg-amber-500/20">
                           {task.content.body}
                         </div>
                         {task.content.hashtags && task.content.hashtags.length > 0 && (
                           <div className="flex flex-wrap gap-2 mt-6">
                              {task.content.hashtags.map(h => (
                                <span key={h} className="text-[11px] font-mono text-amber-500 bg-amber-500/5 px-2.5 py-1 rounded-full border border-amber-500/10">
                                   #{h}
                                </span>
                              ))}
                           </div>
                         )}
                         {task.content.posting_time && (
                           <div className="mt-8 pt-4 border-t border-zinc-900 flex items-center gap-2.5 text-[10px] font-bold text-zinc-600 uppercase tracking-widest">
                              <Clock className="w-3.5 h-3.5" />
                              Suggested Window: <span className="text-zinc-400">{task.content.posting_time}</span>
                           </div>
                         )}
                         {task.content.image_direction && (
                           <div className="mt-8 bg-zinc-900/50 border border-zinc-800/80 rounded-xl p-6 transition-all group shadow-inner">
                              <p className="text-[10px] text-zinc-600 font-bold uppercase tracking-[0.2em] mb-3 group-hover:text-zinc-400 transition-colors">Visual Directive</p>
                              <p className="text-sm text-zinc-300 italic font-light leading-relaxed">
                                "{task.content.image_direction}"
                              </p>
                           </div>
                         )}
                      </div>
                    )}

                    {task.content.format === "email" && (
                      <div className="space-y-10">
                         <div className="bg-zinc-900 opacity-80 border border-zinc-800/50 rounded-xl p-5 space-y-1">
                            <span className="text-[10px] font-mono font-bold text-zinc-600 uppercase tracking-widest">Subject</span>
                            <p className="text-sm text-white font-semibold font-serif underline decoration-amber-500/30 underline-offset-4 decoration-2">{task.content.headline}</p>
                         </div>
                         <div className="text-[15px] text-zinc-100 font-light leading-loose whitespace-pre-wrap max-w-2xl font-serif">
                           {task.content.body}
                         </div>
                      </div>
                    )}

                    {task.content.format === "ad_copy" && (
                      <div className="space-y-8">
                         {task.content.headline && (
                           <h2 className="text-2xl text-white font-bold tracking-tight leading-tight">{task.content.headline}</h2>
                         )}
                         <div className="text-base text-zinc-200 font-light leading-relaxed max-w-2xl">
                           {task.content.body}
                         </div>
                      </div>
                    )}

                    {task.content.format === "long_form" && (
                      <div className="text-base text-zinc-200 font-light leading-relaxed whitespace-pre-wrap max-w-2xl">
                        {task.content.body}
                      </div>
                    )}

                    <div className="pt-8 flex justify-end">
                       <span className="text-[10px] font-mono text-zinc-700 tracking-tighter uppercase font-bold">
                          {task.content.body.split(/\s+/).length} words · {task.content.body.length} characters
                       </span>
                    </div>
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center py-20 animate-in fade-in duration-700">
                    <Loader2 className="w-8 h-8 text-zinc-800 animate-spin" />
                    <p className="text-sm text-zinc-500 font-medium mt-4">Content synthesis in progress...</p>
                    <p className="text-xs text-zinc-700 mt-1 uppercase tracking-widest font-bold">Uplink established · Awaiting ingestion</p>
                  </div>
                )}
             </div>
          </div>

          {/* Action Bar */}
          <div className="bg-[#1a1a1a] border border-zinc-800 rounded-2xl p-6 mb-5 space-y-6">
             <div className="flex flex-col md:flex-row gap-4">
                <Button 
                  className="flex-1 bg-amber-500 hover:bg-amber-400 text-black font-bold uppercase tracking-[0.1em] h-14 text-sm"
                  disabled={!task.content || approveMutation.isPending || task.status === 'completed' || task.status === 'approved'}
                  onClick={() => approveMutation.mutate()}
                >
                  {approveMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : "Approve and Schedule →"}
                </Button>
                
                <Button 
                  variant="outline"
                  className="flex-1 border-zinc-700 text-zinc-300 hover:bg-zinc-800 hover:border-zinc-500 h-14 font-bold uppercase tracking-[0.1em] text-xs"
                  onClick={() => setRevisionOpen(!revisionOpen)}
                  disabled={task.status === 'completed'}
                >
                   {revisionOpen ? "Close panel" : <><Edit2 className="w-4 h-4 mr-2" /> Request Edits</>}
                </Button>

                <Button 
                  variant="outline"
                  className="px-6 border-zinc-700 text-zinc-500 hover:border-amber-500/30 hover:text-amber-500 h-14 font-bold uppercase tracking-[0.1em] text-[10px] transition-all"
                  onClick={() => {
                    setRevisionOpen(true);
                    setRevisionNotes("Please regenerate this content with a fresh approach.");
                  }}
                  disabled={task.status === 'completed'}
                >
                   <RefreshCw className="w-4 h-4 mr-2" /> Regenerate
                </Button>
             </div>

             {/* Revision Panel */}
             <div className={cn(
               "overflow-hidden transition-all duration-500 ease-in-out border-zinc-900",
               revisionOpen ? "max-h-[400px] mt-6 pt-6 border-t" : "max-h-0 opacity-0"
             )}>
                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-3 block">Revision Feedback</label>
                <textarea 
                  rows={3}
                  className="w-full bg-[#0f0f0f] border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white placeholder:text-zinc-700 focus:border-amber-500 focus:outline-none resize-none transition-all"
                  placeholder="e.g. Make it sound more technical and bold. Emphasize the organic extraction process..."
                  value={revisionNotes}
                  onChange={(e) => setRevisionNotes(e.target.value)}
                />
                <div className="flex gap-3 mt-4">
                   <Button 
                    className="flex-1 bg-amber-500 text-black font-bold uppercase tracking-widest text-xs h-10"
                    disabled={!revisionNotes.trim() || revisionMutation.isPending}
                    onClick={() => revisionMutation.mutate(revisionNotes)}
                   >
                     {revisionMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin text-black" /> : "Send for Revision"}
                   </Button>
                   <Button 
                    variant="ghost" 
                    className="px-6 text-zinc-500 hover:text-white uppercase font-bold tracking-widest text-xs h-10"
                    onClick={() => setRevisionOpen(false)}
                   >
                     Cancel
                   </Button>
                </div>
             </div>

             {/* Skip Row */}
             <div className="flex items-center justify-between pt-6 border-t border-zinc-900 group">
                <span className="text-[10px] text-zinc-600 font-bold uppercase tracking-widest">Procedural override</span>
                <button 
                  onClick={() => setSkipOpen(!skipOpen)}
                  className="text-[10px] font-bold text-zinc-600 hover:text-red-500/80 transition-colors uppercase tracking-[0.2em] underline decoration-zinc-800 underline-offset-4"
                >
                  Skip this task
                </button>
             </div>

             {/* Skip Dialog */}
             {skipOpen && (
               <div className="mt-4 bg-[#262626] rounded-xl p-5 border border-zinc-700/50 animate-in slide-in-from-top-2 duration-300">
                  <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-widest mb-3">Reason for skipping (optional)</p>
                  <input 
                    className="w-full bg-[#1a1a1a] border border-zinc-700 rounded-lg px-4 py-2 text-sm text-white focus:border-red-500/50 outline-none mb-4 transition-all"
                    placeholder="e.g. Budget shift, channel pivot..."
                    value={skipReason}
                    onChange={(e) => setSkipReason(e.target.value)}
                  />
                  <div className="flex gap-3">
                    <Button 
                      className="flex-1 border border-red-500/30 text-red-400 h-9 rounded-lg font-bold uppercase tracking-widest text-[10px] hover:bg-red-500/10 transition-colors"
                      onClick={() => completeMutation.mutate(skipReason || "Skipped by user")}
                      disabled={completeMutation.isPending}
                    >
                      {completeMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Confirm Skip"}
                    </Button>
                    <Button 
                      variant="ghost" 
                      className="px-6 text-zinc-500 font-bold uppercase tracking-widest h-9 text-[10px]"
                      onClick={() => setSkipOpen(false)}
                    >
                      Cancel
                    </Button>
                  </div>
               </div>
             )}
          </div>
        </div>
      )}

      {/* SURFACE B: Performance Review */}
      {task.task_type === "review_performance" && (
        <div className="animate-in fade-in duration-500">
           <h2 className="text-base text-white font-bold uppercase tracking-[0.1em] mb-6">Execution Telemetry</h2>
           
           {task.performance_summary ? (
             <div className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                   {task.performance_summary.metrics.map((m, i) => (
                     <div key={i} className="bg-[#1a1a1a] rounded-2xl border border-zinc-800 p-6 flex flex-col gap-5 group hover:border-zinc-700 transition-colors shadow-sm">
                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest leading-none">
                          {m.label}
                        </span>
                        <div className="space-y-2">
                           <p className="text-3xl text-white font-bold leading-none font-serif tracking-tight">{m.value}</p>
                           <div className="flex items-center gap-2">
                              {m.vs_target === 'above' ? (
                                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-green-500/10 text-green-500 rounded-full text-[9px] font-bold uppercase tracking-tighter">
                                   <TrendingUp className="w-3 h-3" /> above target
                                </div>
                              ) : m.vs_target === 'below' ? (
                                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-red-500/10 text-red-400 rounded-full text-[9px] font-bold uppercase tracking-tighter">
                                   <TrendingDown className="w-3 h-3" /> below target
                                </div>
                              ) : (
                                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-zinc-800 text-zinc-400 rounded-full text-[9px] font-bold uppercase tracking-tighter">
                                   <Minus className="w-3 h-3" /> on target
                                </div>
                              )}
                           </div>
                        </div>
                     </div>
                   ))}
                </div>

                <div className="bg-blue-500/5 border border-blue-500/20 rounded-2xl p-8 space-y-6 relative overflow-hidden group">
                   <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                      <MessageSquare className="w-12 h-12 text-blue-500" />
                   </div>
                   <div className="space-y-3 relative z-10">
                      <span className="text-[10px] font-bold text-blue-500 uppercase tracking-[0.2em] flex items-center gap-2">
                         <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
                         Analytics Director Recommendation
                      </span>
                      <p className="text-lg text-zinc-200 font-light leading-relaxed max-w-2xl italic">
                         "{task.performance_summary.recommendation}"
                      </p>
                   </div>
                </div>
             </div>
           ) : (
             <div className="bg-[#1a1a1a] rounded-2xl border border-zinc-800 p-16 text-center opacity-60">
                <BarChart2 className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
                <p className="text-base text-zinc-300 font-bold uppercase tracking-widest">Performance Telemetry Absent</p>
                <p className="text-xs text-zinc-500 mt-2 max-w-xs mx-auto leading-relaxed">
                   Check back once the execution cycle is complete and live market signals have been ingested.
                </p>
             </div>
           )}

           <div className="bg-[#1a1a1a] border border-zinc-800 rounded-2xl p-6 mt-6">
              <Button 
                className="w-full bg-amber-500 hover:bg-amber-400 text-black font-bold uppercase tracking-[0.1em] h-14"
                disabled={completeMutation.isPending || task.status === 'completed'}
                onClick={() => completeMutation.mutate()}
              >
                {completeMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : "Mark Review Complete →"}
              </Button>
           </div>
        </div>
      )}

      {/* SURFACE C: Execute Ad Move */}
      {task.task_type === "execute_ad" && (
        <div className="animate-in fade-in duration-500 space-y-6">
           <div className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-10 space-y-8 relative overflow-hidden shadow-inner">
              <div className="absolute top-0 right-0 p-8 opacity-10">
                 <AlertCircle className="w-24 h-24 text-amber-500" />
              </div>
              <div className="space-y-3 relative z-10">
                 <span className="text-[10px] font-bold text-amber-600 uppercase tracking-[0.3em]">Operational Directive</span>
                 <h2 className="text-3xl text-white font-bold tracking-tight max-w-xl leading-snug font-serif">
                   {task.ad_instruction || task.description}
                 </h2>
              </div>
              <Button 
                variant="outline"
                className="w-full h-14 border-zinc-700 text-zinc-300 bg-black/10 hover:border-zinc-500 hover:bg-black/20 hover:text-white font-bold uppercase tracking-widest text-xs"
                onClick={() => window.open('#', '_blank')}
              >
                 Open Platform Manager <ExternalLink className="w-4 h-4 ml-2" />
              </Button>
           </div>

           <div className="bg-[#1a1a1a] border border-zinc-800 rounded-2xl p-8 space-y-6">
              <div className="flex items-start gap-4">
                 <div className="w-10 h-10 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-sm font-bold text-zinc-400 uppercase flex-shrink-0">
                    {task.assigned_agent_name.charAt(0)}
                 </div>
                 <div className="space-y-2">
                    <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Strategic Logic</p>
                    <p className="text-base text-zinc-300 font-light italic leading-relaxed">
                       "{task.ad_reasoning || "Based on the recent shift in channel CPA, we must adjust budget allocation to preserve efficiency."}"
                    </p>
                 </div>
              </div>
           </div>

           <div className="bg-[#1a1a1a] border border-zinc-800 rounded-2xl p-6">
              <Button 
                 className="w-full bg-amber-500 hover:bg-amber-400 text-black font-bold uppercase tracking-widest h-14"
                 disabled={completeMutation.isPending || task.status === 'completed'}
                 onClick={() => completeMutation.mutate()}
              >
                 {completeMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : "I've Executed This Move"}
              </Button>
           </div>
        </div>
      )}

      {/* ─── Toast System ────────────────────────────────────────── */}
      {toastMessage && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-[100] bg-[#1a1a1a] border border-zinc-700 rounded-xl px-10 py-4 text-xs font-bold uppercase tracking-widest text-white shadow-[0_10px_40px_rgba(0,0,0,0.8)] animate-in fade-in slide-in-from-bottom-5 duration-300">
           {toastMessage}
        </div>
      )}

    </div>
  );
}

// ─── Auxiliary Components ────────────────────────────────────────

function TaskSkeleton() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-8 animate-pulse space-y-8">
      <Skeleton className="h-6 w-64 rounded" />
      <Skeleton className="h-40 w-full rounded-2xl" />
      <Skeleton className="h-[400px] w-full rounded-2xl" />
      <Skeleton className="h-28 w-full rounded-2xl" />
    </div>
  );
}

function TaskErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-40 gap-4">
       <div className="text-sm text-red-500 bg-red-500/5 px-4 py-2 border border-red-500/20 rounded-lg uppercase font-bold tracking-widest">
          Telemetry Failure
       </div>
       <p className="text-zinc-500 text-xs font-mono mb-4 text-center">COULD NOT RESOLVE TASK UPLINK.</p>
       <Button variant="ghost" className="text-zinc-400 font-bold uppercase tracking-widest text-[10px]" onClick={onRetry}>
          Retry Connection
       </Button>
    </div>
  );
}

function Link({ href, className, children }: { href: string; className?: string; children: React.ReactNode }) {
  return <a href={href} className={className}>{children}</a>;
}
