"use client";

import React, { useState } from "react";
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
  LayoutDashboard,
  Trophy
} from "lucide-react";
import { dailyWinsApi } from "@/lib/api";
import type { DailyWin } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { cn } from "@/lib/cn";
import Link from "next/link";

/**
 * Daily Wins Page
 * 
 * The command-center dashboard for RaptorFlow. Delivers a curated, 
 * Strategist-driven briefing every morning.
 */
export default function DailyWinsPage() {
  const queryClient = useQueryClient();
  const [archiveOpen, setArchiveOpen] = useState(false);

  const { data: win, isLoading, error, refetch } = useQuery({
    queryKey: ["daily-wins", "today"],
    queryFn: () => dailyWinsApi.getToday(),
  });

  const { data: archive } = useQuery({
    queryKey: ["daily-wins", "archive"],
    enabled: archiveOpen,
    queryFn: () => dailyWinsApi.getArchive(),
  });

  const mutation = useMutation({
    mutationFn: (winId: string) => dailyWinsApi.markAsRead(winId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["daily-wins", "today"] });
    }
  });

  // ─── Rendering Helpers ───────────────────────────────────────

  if (isLoading) return <DailyWinsSkeleton />;

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-12 space-y-4">
        <AlertCircle className="w-12 h-12 text-red-500/50" />
        <p className="text-[#6B655E] font-mono text-sm uppercase tracking-widest">
          Telemetry uplink failed
        </p>
        <Button variant="outline" onClick={() => refetch()} className="border-[#E5DED4] text-[#6B655E] hover:text-[#2A2622]">
          Retry Uplink
        </Button>
      </div>
    );
  }

  // Not Started State
  if (!win) {
    return (
      <EmptyState
        icon={Trophy}
        title="No briefing generated yet"
        description="Your daily win briefing generates each morning. Create a campaign to get started."
        action={
          <Link href="/campaigns">
            <Button className="bg-[#D97757] hover:bg-amber-400 text-black font-bold uppercase tracking-widest px-8">
              Create your first campaign <ChevronRight className="ml-2 w-4 h-4" />
            </Button>
          </Link>
        }
      />
    );
  }

  // Final rendering of the win
  const handleMarkAsRead = () => {
    mutation.mutate(win.win_id);
  };

  const ctaLinks = {
    approve_content: "/content",
    review_campaign: `/campaigns/${win.todays_focus.action_data.campaign_id}`,
    respond_to_intel: "/intel",
    strategic_review: "/muse"
  };

  return (
    <div className="max-w-4xl mx-auto space-y-12 pb-24">
      {/* ── Page Header ────────────────────────────────────────── */}
      <header className="flex items-end justify-between border-b border-[#D5CBC0] pb-8">
        <div className="space-y-1">
          <p className="text-2xl font-light text-[#6B655E]">
            {format(new Date(), "EEEE, d MMMM")}
          </p>
          <h1 className="text-5xl text-[#2A2622] font-bold tracking-tight">
            Good morning.
          </h1>
        </div>
        <div className="flex items-center gap-3 bg-[#F5F0E8]/50 border border-[#E5DED4] rounded-full pl-2 pr-4 py-1.5">
          <div className="w-8 h-8 rounded-full bg-[#D97757]/20 border border-[#D97757]/30 flex items-center justify-center text-[#D97757] text-xs font-bold font-serif">
            {win.strategist_name.charAt(0)}
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] uppercase font-bold text-[#9A948C] tracking-wider">
              {win.strategist_name}
            </span>
            <span className="text-[8px] uppercase font-mono text-[#9A948C] font-bold">
              GEN: {format(new Date(win.generated_at), "h:mm aa")}
            </span>
          </div>
        </div>
      </header>

      {/* ── Section 1: The Lead ────────────────────────────────── */}
      <section className="relative bg-[#FBF8F2] rounded-2xl p-8 border border-[#E5DED4]/80 group">
        <div className="absolute left-0 top-6 bottom-6 w-1 bg-[#D97757] rounded-r-lg shadow-[0_0_12px_rgba(217,119,87,0.4)]" />
        
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-[#9A948C]" />
            <span className="text-xs uppercase tracking-[0.3em] font-bold text-[#6B655E]">
              Today's Lead
            </span>
          </div>
          
          <div className="space-y-5 text-lg text-[#9A948C] font-light leading-relaxed max-w-3xl">
            {win.lead.text.split('\n\n').map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </div>

          <div className="pt-4">
            <Badge variant="outline" className="bg-[#E5DED4]/40 border-[#E5DED4] text-[10px] text-[#6B655E] font-normal px-4 py-1.5 rounded-full">
              Why this matters: <span className="text-[#4A4540] ml-1.5">{win.lead.significance}</span>
            </Badge>
          </div>
        </div>
      </section>

      {/* ── Section 2: Context Items ────────────────────────────── */}
      {win.context && win.context.length > 0 && (
        <section className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {win.context.map((item, i) => (
            <div key={i} className="bg-[#262626] rounded-2xl p-6 border border-[#E5DED4] flex flex-col justify-between h-40">
              <div className="space-y-3">
                <span className="text-[9px] uppercase font-bold tracking-[0.2em] text-[#9A948C]">Context Item</span>
                <p className="text-sm text-[#9A948C] line-clamp-3 leading-relaxed">
                  {item.text}
                </p>
              </div>
              <div className="flex items-center gap-1.5 opacity-50">
                <FileText className="w-3 h-3 text-[#6B655E]" />
                <span className="text-[9px] uppercase font-mono font-bold text-[#6B655E] tracking-wider">
                  SOURCE: {item.source}
                </span>
              </div>
            </div>
          ))}
        </section>
      )}

      {/* ── Section 3: Today's Focus ────────────────────────────── */}
      <section className="bg-[#FBE9DE] rounded-2xl p-10 border border-[#D97757]/20 relative overflow-hidden group">
        {/* Animated Background Pulse */}
        <div className="absolute -right-20 -top-20 w-64 h-64 bg-[#FBE9DE] rounded-full blur-[80px] group-hover:bg-[#FBE9DE] transition-colors" />
        
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#D97757] animate-pulse" />
            <span className="text-xs uppercase tracking-[0.3em] font-bold text-[#C46A4D]">
              CRITICAL FOCUS
            </span>
          </div>

          <div className="space-y-2 max-w-2xl">
            <h2 className="text-3xl text-[#2A2622] font-bold tracking-tight">
              {win.todays_focus.action}
            </h2>
            <p className="text-base text-[#6B655E] leading-relaxed italic">
              — {win.todays_focus.rationale}
            </p>
          </div>

          <Link href={(ctaLinks[win.todays_focus.action_type] || "/daily-wins") as any}>
            <Button className="h-14 px-10 bg-[#D97757] hover:bg-amber-400 text-black font-bold uppercase tracking-widest text-sm transition-all hover:translate-x-1">
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
          className="text-[#9A948C] hover:text-[#6B655E] transition-colors text-xs font-mono uppercase tracking-[0.2em] underline underline-offset-8 decoration-zinc-800"
        >
          {win.viewed_at ? "Marked as read" : "Mark today's briefing as read"}
        </button>
      </footer>

      {/* ── Archive Section ───────────────────────────────────── */}
      <section className="pt-12 border-t border-[#D5CBC0]">
        <button 
          onClick={() => setArchiveOpen(!archiveOpen)}
          className="flex items-center gap-2 text-[#6B655E] hover:text-[#2A2622] transition-colors text-xs font-bold uppercase tracking-widest"
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
              <p className="text-[#9A948C] text-xs italic font-mono uppercase tracking-widest">
                Archive is empty. Briefings accrue daily.
              </p>
            ) : (
              <div className="space-y-4 relative pl-4 border-l border-[#D5CBC0] ml-2">
                {archive.map((item) => (
                  <Link 
                    key={item.win_id} 
                    href={`/daily-wins/${item.win_id}` as any}
                    className="flex flex-col group"
                  >
                    <div className="absolute -left-[5px] w-2 h-2 rounded-full bg-[#E5DED4] group-hover:bg-[#D97757] transition-colors mt-1.5" />
                    <span className="text-[10px] uppercase font-bold text-[#6B655E] tracking-widest leading-none">
                      {format(new Date(item.generated_at), "MMM d, yyyy")}
                    </span>
                    <span className="text-sm text-[#6B655E] mt-1 line-clamp-1 group-hover:text-[#4A4540]">
                      {item.lead.text}
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
      <header className="flex items-end justify-between border-b border-[#D5CBC0] pb-8">
        <div className="space-y-3">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-12 w-64" />
        </div>
        <Skeleton className="h-12 w-32 rounded-full" />
      </header>
      <Skeleton className="h-64 w-full rounded-2xl" />
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Skeleton className="h-40 w-full rounded-2xl" />
        <Skeleton className="h-40 w-full rounded-2xl" />
      </div>
      <Skeleton className="h-56 w-full rounded-2xl" />
    </div>
  );
}
