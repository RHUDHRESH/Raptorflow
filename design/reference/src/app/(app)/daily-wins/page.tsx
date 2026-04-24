"use client";

import React, { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { 
  CheckCircle2, 
  ChevronRight, 
  Clock, 
  ArrowRight, 
  AlertCircle,
  FileText,
  Calendar,
  Sparkles,
  ChevronDown,
  ChevronUp,
  LayoutDashboard
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/cn";
import Link from "next/link";

interface DailyWin {
  win_id: string;
  generated_at: string;
  strategist_name: string;
  lead: {
    text: string;
    significance: string;
  };
  context: Array<{ text: string; source: string }>;
  todays_focus: {
    action: string;
    rationale: string;
    action_type: "approve_content" | "review_campaign" | "respond_to_intel" | "strategic_review";
    action_data: { task_id?: string; campaign_id?: string };
  };
  viewed_at: string | null;
  acted_on_at: string | null;
  status?: "not_started";
  message?: string;
}

/**
 * Daily Wins Page
 * 
 * The command-center dashboard for RaptorFlow. Delivers a curated, 
 * Strategist-driven briefing every morning.
 */
export default function DailyWinsPage() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const [archiveOpen, setArchiveOpen] = useState(false);

  // ─── Data Fetching ───────────────────────────────────────────

  const { data: win, isLoading, error, refetch } = useQuery<DailyWin>({
    queryKey: ["daily-wins", "today"],
    queryFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/daily-wins/today`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to load today's briefing.");
      return res.json();
    }
  });

  const { data: archive } = useQuery<Array<{ win_id: string; generated_at: string; lead_summary: string }>>({
    queryKey: ["daily-wins", "archive"],
    enabled: archiveOpen,
    queryFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/daily-wins/archive`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to load archive.");
      return res.json();
    }
  });

  const mutation = useMutation({
    mutationFn: async (winId: string) => {
      const token = await getToken();
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/daily-wins/${winId}/viewed`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` }
      });
    }
  });

  // ─── Rendering Helpers ───────────────────────────────────────

  if (isLoading) return <DailyWinsSkeleton />;

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-12 space-y-4">
        <AlertCircle className="w-12 h-12 text-red-500/50" />
        <p className="text-zinc-500 font-mono text-sm uppercase tracking-widest">
          Telemetry uplink failed
        </p>
        <Button variant="outline" onClick={() => refetch()} className="border-zinc-800 text-zinc-400 hover:text-white">
          Retry Uplink
        </Button>
      </div>
    );
  }

  // Not Started State
  if (win?.status === "not_started") {
    return (
      <div className="flex flex-col items-center justify-center pt-32 px-6">
        <div className="w-20 h-20 bg-amber-500/10 border border-amber-500/20 rounded-full flex items-center justify-center text-4xl text-amber-500 font-serif mb-6">
          {win.strategist_name.charAt(0)}
        </div>
        <h1 className="text-2xl text-white font-bold mb-2 tracking-tight">
          {win.strategist_name} is ready.
        </h1>
        <p className="text-zinc-500 text-center max-w-sm mb-8 leading-relaxed">
          {win.message || "I'll have your first briefing ready once you start a campaign."}
        </p>
        <Link href="/app/campaigns">
          <Button className="bg-amber-500 hover:bg-amber-400 text-black font-bold uppercase tracking-widest px-8">
            Create your first campaign <ChevronRight className="ml-2 w-4 h-4" />
          </Button>
        </Link>
      </div>
    );
  }

  // Final rendering of the win
  if (!win) return null;

  const handleMarkAsRead = () => {
    mutation.mutate(win.win_id);
  };

  const ctaLinks = {
    approve_content: "/app/content",
    review_campaign: `/app/campaigns/${win.todays_focus.action_data.campaign_id}`,
    respond_to_intel: "/app/intel",
    strategic_review: "/app/muse"
  };

  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-24">
      {/* ── Page Header ────────────────────────────────────────── */}
      <header className="flex items-end justify-between border-b border-zinc-900 pb-8">
        <div className="space-y-1">
          <p className="text-2xl font-light text-zinc-400">
            {format(new Date(), "EEEE, d MMMM")}
          </p>
          <h1 className="text-5xl text-white font-bold tracking-tight">
            Good morning.
          </h1>
        </div>
        <div className="flex items-center gap-3 bg-zinc-900/50 border border-zinc-800 rounded-full pl-2 pr-4 py-1.5">
          <div className="w-8 h-8 rounded-full bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-500 text-xs font-bold font-serif">
            {win.strategist_name.charAt(0)}
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] uppercase font-bold text-zinc-300 tracking-wider">
              {win.strategist_name}
            </span>
            <span className="text-[8px] uppercase font-mono text-zinc-600 font-bold">
              GEN: {format(new Date(win.generated_at), "h:mm aa")}
            </span>
          </div>
        </div>
      </header>

      {/* ── Section 1: The Lead ────────────────────────────────── */}
      <section className="relative bg-[#1a1a1a] rounded-2xl p-8 border border-zinc-800/80 group">
        <div className="absolute left-0 top-6 bottom-6 w-1 bg-amber-500 rounded-r-lg shadow-[0_0_12px_rgba(245,158,11,0.4)]" />
        
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-zinc-600" />
            <span className="text-xs uppercase tracking-[0.3em] font-bold text-zinc-500">
              Today's Lead
            </span>
          </div>
          
          <div className="space-y-5 text-lg text-zinc-300 font-light leading-relaxed max-w-3xl">
            {win.lead.text.split('\n\n').map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </div>

          <div className="pt-4">
            <Badge variant="outline" className="bg-zinc-800/40 border-zinc-800 text-[10px] text-zinc-400 font-normal px-4 py-1.5 rounded-full">
              Why this matters: <span className="text-zinc-200 ml-1.5">{win.lead.significance}</span>
            </Badge>
          </div>
        </div>
      </header>

      {/* ── Section 2: Context Items ────────────────────────────── */}
      {win.context && win.context.length > 0 && (
        <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {win.context.map((item, i) => (
            <div key={i} className="bg-[#262626] rounded-2xl p-6 border border-zinc-800 flex flex-col justify-between h-40">
              <div className="space-y-3">
                <span className="text-[9px] uppercase font-bold tracking-[0.2em] text-zinc-600">Context Item</span>
                <p className="text-sm text-zinc-300 line-clamp-3 leading-relaxed">
                  {item.text}
                </p>
              </div>
              <div className="flex items-center gap-1.5 opacity-50">
                <FileText className="w-3 h-3 text-zinc-500" />
                <span className="text-[9px] uppercase font-mono font-bold text-zinc-500 tracking-wider">
                  SOURCE: {item.source}
                </span>
              </div>
            </div>
          ))}
        </section>
      )}

      {/* ── Section 3: Today's Focus ────────────────────────────── */}
      <section className="bg-amber-500/5 rounded-2xl p-10 border border-amber-500/20 relative overflow-hidden group">
        {/* Animated Background Pulse */}
        <div className="absolute -right-20 -top-20 w-64 h-64 bg-amber-500/5 rounded-full blur-[80px] group-hover:bg-amber-500/10 transition-colors" />
        
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            <span className="text-xs uppercase tracking-[0.3em] font-bold text-amber-600">
              CRITICAL FOCUS
            </span>
          </div>

          <div className="space-y-2 max-w-2xl">
            <h2 className="text-3xl text-white font-bold tracking-tight">
              {win.todays_focus.action}
            </h2>
            <p className="text-base text-zinc-400 leading-relaxed italic">
              — {win.todays_focus.rationale}
            </p>
          </div>

          <Link href={ctaLinks[win.todays_focus.action_type] || "/app"}>
            <Button className="h-14 px-10 bg-amber-500 hover:bg-amber-400 text-black font-bold uppercase tracking-widest text-sm transition-all hover:translate-x-1">
              {win.todays_focus.action_type === 'approve_content' && "Review & Approve Content"}
              {win.todays_focus.action_type === 'review_campaign' && "Open Campaign Details"}
              {win.todays_focus.action_type === 'respond_to_intel' && "View Intel Directive"}
              {win.todays_focus.action_type === 'strategic_review' && "Consult the Muse"}
              <ArrowRight className="ml-3 w-5 h-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* ── Footer / Mark as Read ─────────────────────────────── */}
      <footer className="text-center pt-8">
        <button 
          onClick={handleMarkAsRead}
          className="text-zinc-600 hover:text-zinc-400 transition-colors text-xs font-mono uppercase tracking-[0.2em] underline underline-offset-8 decoration-zinc-800"
        >
          {win.viewed_at ? "Marked as read" : "Mark today's briefing as read"}
        </button>
      </footer>

      {/* ── Archive Section ───────────────────────────────────── */}
      <section className="pt-12 border-t border-zinc-900">
        <button 
          onClick={() => setArchiveOpen(!archiveOpen)}
          className="flex items-center gap-2 text-zinc-500 hover:text-white transition-colors text-xs font-bold uppercase tracking-widest"
        >
          {archiveOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          View Past Briefings
        </button>

        {archiveOpen && (
          <div className="mt-8 space-y-6">
            {!archive ? (
              <div className="space-y-4">
                {[1, 2, 3].map(i => <Skeleton key={i} className="h-10 w-full" />)}
              </div>
            ) : archive.length === 0 ? (
              <p className="text-zinc-600 text-xs italic font-mono uppercase tracking-widest">
                Archive is empty. Briefings accrue daily.
              </p>
            ) : (
              <div className="space-y-4 relative pl-4 border-l border-zinc-900 ml-2">
                {archive.map((item) => (
                  <Link 
                    key={item.win_id} 
                    href={`/app/daily-wins/${item.win_id}`}
                    className="flex flex-col group"
                  >
                    <div className="absolute -left-[5px] w-2 h-2 rounded-full bg-zinc-800 group-hover:bg-amber-500 transition-colors mt-1.5" />
                    <span className="text-[10px] uppercase font-bold text-zinc-500 tracking-widest leading-none">
                      {format(new Date(item.generated_at), "MMM d, yyyy")}
                    </span>
                    <span className="text-sm text-zinc-400 mt-1 line-clamp-1 group-hover:text-zinc-200">
                      {item.lead_summary}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

/**
 * Loading Skeleton
 */
function DailyWinsSkeleton() {
  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-24 animate-pulse">
      <header className="flex items-end justify-between border-b border-zinc-900 pb-8">
        <div className="space-y-3">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-12 w-64" />
        </div>
        <Skeleton className="h-12 w-32 rounded-full" />
      </header>
      <Skeleton className="h-64 w-full rounded-2xl" />
      <div className="grid grid-cols-2 gap-4">
        <Skeleton className="h-40 w-full rounded-2xl" />
        <Skeleton className="h-40 w-full rounded-2xl" />
      </div>
      <Skeleton className="h-56 w-full rounded-2xl" />
    </div>
  );
}
