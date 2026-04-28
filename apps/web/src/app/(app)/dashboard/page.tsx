"use client";

import * as React from "react";
import { useState } from "react";
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { useDashboard } from "@/features/dashboard/hooks/useDashboard";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/cn";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { BrandHeader } from "@/components/brand/BrandHeader";
import { RfWindow, RfWindowGrid } from "@/components/windows";
import { StatusPill } from "@/components/windows/StatusPill";
import {
  BackpackIcon,
  AvatarIcon,
  TargetIcon,
  BellIcon,
  LightningBoltIcon,
  CalendarIcon,
  ChatBubbleIcon,
  HomeIcon,
} from "@radix-ui/react-icons";

function timeAgo(dateStr: string): string {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (seconds < 60) return `${Math.floor(seconds)}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

function momentumColour(score: number): string {
  if (score <= 3) return "text-[var(--destructive)]";
  if (score <= 6) return "text-[var(--primary)]";
  if (score <= 8) return "text-[var(--indigo-muse)]";
  return "text-[var(--leaf-confirm)]";
}

function momentumBg(score: number): string {
  if (score <= 3) return "bg-[var(--destructive-wash)] border-[var(--destructive)]/20";
  if (score <= 6) return "bg-[var(--amber-wash)] border-[var(--amber-stroke)]/30";
  if (score <= 8) return "bg-[var(--indigo-wash)] border-[var(--indigo-muse)]/20";
  return "bg-[var(--leaf-wash)] border-[var(--leaf-confirm)]/20";
}

function focusHref(text: string): string {
  const lower = text.toLowerCase();
  if (lower.includes("foundation") || lower.includes("scan")) return "/foundation";
  if (lower.includes("council")) return "/council";
  if (lower.includes("campaign") || lower.includes("move")) return "/campaigns";
  if (lower.includes("muse")) return "/muse";
  return "/dashboard";
}

export default function DashboardPage(): React.ReactElement {
  const queryClient = useQueryClient();
  const { data, isLoading } = useDashboard();

  if (isLoading) return <DashboardSkeleton />;

  const score = data?.todayWin?.momentumScore ?? 0;

  return (
    <GsapBridge stagger className="space-y-8">
      <BrandHeader
        eyebrow="Dashboard"
        title="The Office"
        description="Your daily briefing and operational overview."
        status={<StatusPill status="Live" tone="success" />}
      />

      {/* ── Today's Briefing ─────────────────────────────────── */}
      {data?.todayWin ? (
        <div className={cn("gsap-reveal card-elevated p-6 border transition-all", momentumBg(score))}>
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="status-dot-live" />
                <span className="eyebrow">Today&apos;s briefing</span>
              </div>
              <div className="display-sm">{data.todayWin.headline}</div>
              <div className="flex flex-wrap gap-2 mt-4">
                {data.todayWin.focusAreas.map((area: string, i: number) => (
                  <Link
                    key={i}
                    href={focusHref(area)}
                    className="text-xs bg-white border border-[var(--border)] rounded-full px-3 py-1.5 hover:border-[var(--primary)] hover:text-[var(--primary)] transition-all duration-200 text-[var(--ink-700)]"
                  >
                    {area}
                  </Link>
                ))}
              </div>
            </div>
            <div className="text-right shrink-0 ml-4">
              <div className={cn("text-4xl font-bold font-display", momentumColour(score))}>
                {score}
                <span className="text-sm font-normal text-[var(--ink-400)] ml-1">/10</span>
              </div>
              <div className="mono-label mt-1">momentum</div>
            </div>
          </div>
          <Link
            href="/daily-wins"
            className="text-xs text-[var(--primary)] mt-4 inline-block link-underline font-medium"
          >
            View full briefing →
          </Link>
        </div>
      ) : (
        <div className="gsap-reveal card-elevated p-8 border border-dashed border-[var(--border)] text-center">
          <div className="text-[var(--ink-500)] mb-4 body-muted">No briefing yet today</div>
          <GenerateBriefingButton />
        </div>
      )}

      {/* ── Stats Grid ───────────────────────────────────────── */}
      <RfWindowGrid columns={4} className="gsap-reveal">
        <StatCard
          label="Active campaigns"
          value={data?.stats.activeCampaigns ?? 0}
          total={data?.stats.totalCampaigns}
          href="/campaigns"
          colour="leaf"
          icon={BackpackIcon}
        />
        <StatCard
          label="Council sessions"
          value={data?.stats.councilSessions ?? 0}
          href="/council"
          colour="indigo"
          icon={AvatarIcon}
        />
        <StatCard
          label="Task completion"
          value={`${data?.stats.taskCompletionRate ?? 0}%`}
          subtitle="last 30 days"
          href="/campaigns"
          colour="amber"
          icon={TargetIcon}
        />
        <StatCard
          label="Foundation"
          value={
            data?.stats.foundationScore
              ? `${data.stats.foundationScore}/10`
              : `${data?.stats.foundationFields ?? 0} fields`
          }
          subtitle={data?.stats.foundationScore ? "positioning" : "filled"}
          href="/foundation"
          colour={
            !data?.stats.foundationScore
              ? "gray"
              : data.stats.foundationScore >= 7
              ? "leaf"
              : data.stats.foundationScore >= 4
              ? "amber"
              : "destructive"
          }
          icon={HomeIcon}
        />
      </RfWindowGrid>

      <RfWindowGrid columns={2} className="gsap-reveal">
        <StatCard
          label="Intel signals"
          value={data?.stats.intelUnread ?? 0}
          subtitle="unread"
          href="/intel"
          colour="amber"
          alert={(data?.stats.intelUnread ?? 0) > 0}
          icon={BellIcon}
        />
        <StatCard
          label="Active nudges"
          value={data?.stats.nudgeCount ?? 0}
          subtitle="waiting"
          href="/nudges"
          colour="indigo"
          alert={(data?.stats.nudgeCount ?? 0) > 0}
          icon={BellIcon}
        />
      </RfWindowGrid>

      {/* ── Activity & Nudges ─────────────────────────────────── */}
      <div className="gsap-reveal grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card-elevated p-6">
          <div className="flex justify-between items-center mb-5">
            <h2 className="h3">Activity</h2>
            <span className="mono-label">Last 7 days</span>
          </div>
          <div className="space-y-1">
            {!data?.activityFeed?.length && (
              <div className="text-[var(--ink-400)] text-sm text-center py-8 body-muted">
                No activity yet — create a campaign or run a council session to get started.
              </div>
            )}
            {data?.activityFeed.map((item) => (
              <div key={item.id} className="flex items-start gap-3 py-3 border-b border-[var(--border)] last:border-0 group">
                <span className="text-lg shrink-0">{item.icon}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-[var(--ink-900)]">{item.content}</p>
                  <p className="text-xs text-[var(--ink-400)] mono-label">{timeAgo(item.createdAt)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card-elevated p-6">
          <div className="flex justify-between items-center mb-5">
            <h2 className="h3">Nudges</h2>
            <Link href="/nudges" className="text-xs text-[var(--primary)] link-underline font-medium">
              See all
            </Link>
          </div>
          <div className="space-y-3">
            {!data?.nudges?.length && (
              <div className="text-[var(--ink-400)] text-sm text-center py-8 body-muted">
                All clear — no nudges right now.
              </div>
            )}
            {data?.nudges?.map((nudge) => (
              <div
                key={nudge.id}
                className={cn(
                  "rounded-[var(--radius-md)] p-4 border-l-[3px] transition-all duration-200 hover:translate-x-1",
                  nudge.type === "warning"
                    ? "border-[var(--primary)] bg-[var(--amber-wash)]"
                    : nudge.type === "action"
                    ? "border-[var(--indigo-muse)] bg-[var(--indigo-wash)]"
                    : nudge.type === "celebration"
                    ? "border-[var(--leaf-confirm)] bg-[var(--leaf-wash)]"
                    : "border-[var(--pod-creative)] bg-[var(--paper-150)]",
                )}
              >
                <div className="font-medium text-sm text-[var(--ink-900)]">{nudge.title}</div>
                <div className="text-xs text-[var(--ink-500)] mt-1 line-clamp-2">{nudge.body}</div>
                {nudge.ctaHref && (
                  <Link
                    href={nudge.ctaHref}
                    className="text-xs font-medium text-[var(--primary)] mt-2 inline-block link-underline"
                  >
                    {nudge.cta} →
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Quick Actions ────────────────────────────────────── */}
      <div className="gsap-reveal">
        <p className="eyebrow mb-4">Quick actions</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          <QuickAction href="/council" icon={LightningBoltIcon} label="Start Council session" />
          <QuickAction href="/campaigns" icon={BackpackIcon} label="New campaign" />
          <QuickAction href="/muse" icon={ChatBubbleIcon} label="Ask Muse" />
          <QuickAction href="/foundation" icon={HomeIcon} label="Update Foundation" />
        </div>
      </div>
    </GsapBridge>
  );
}

function StatCard({
  label,
  value,
  total,
  subtitle,
  href,
  colour,
  alert,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  total?: number;
  subtitle?: string;
  href: string;
  colour: "leaf" | "indigo" | "amber" | "destructive" | "gray";
  alert?: boolean;
  icon: React.ComponentType<{ className?: string }>;
}) {
  const colourMap = {
    leaf: "text-[var(--leaf-confirm)]",
    indigo: "text-[var(--indigo-muse)]",
    amber: "text-[var(--primary)]",
    destructive: "text-[var(--destructive)]",
    gray: "text-[var(--ink-700)]",
  };

  return (
    <Link
      href={href}
      className={cn(
        "card-elevated p-5 block group",
        alert && "border-[var(--primary)]/30 shadow-[var(--shadow-amber)]",
      )}
    >
      <div className="flex items-center gap-2 mb-3">
        <Icon className="w-3.5 h-3.5 text-[var(--ink-400)]" />
        <span className="mono-label">{label}</span>
      </div>
      <div className={cn("text-3xl font-bold font-display", colourMap[colour])}>
        {value}
        {total !== undefined && (
          <span className="text-sm font-normal text-[var(--ink-400)] ml-1">/ {total}</span>
        )}
      </div>
      {subtitle && <div className="mono-label mt-1">{subtitle}</div>}
    </Link>
  );
}

function QuickAction({
  href,
  icon: Icon,
  label,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="card-elevated p-4 flex items-center gap-3 group hover:border-[var(--primary)]/30"
    >
      <div className="w-9 h-9 rounded-[var(--radius)] bg-[var(--paper-150)] flex items-center justify-center group-hover:bg-[var(--amber-wash)] transition-colors duration-200">
        <Icon className="w-4 h-4 text-[var(--ink-500)] group-hover:text-[var(--primary)] transition-colors duration-200" />
      </div>
      <span className="text-sm font-medium text-[var(--ink-900)]">{label}</span>
    </Link>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-32 bg-[var(--paper-200)] rounded-[var(--radius-lg)]" />
      <div className="grid grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-24 bg-[var(--paper-200)] rounded-[var(--radius-lg)]" />
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 h-64 bg-[var(--paper-200)] rounded-[var(--radius-lg)]" />
        <div className="h-64 bg-[var(--paper-200)] rounded-[var(--radius-lg)]" />
      </div>
    </div>
  );
}

function GenerateBriefingButton() {
  const [loading, setLoading] = useState(false);
  const queryClient = useQueryClient();

  const generate = async () => {
    setLoading(true);
    try {
      await apiFetch("/api/daily-wins", { method: "POST", auth: true });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["daily-wins"] });
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={generate}
      disabled={loading}
      className="btn-primary disabled:opacity-50"
    >
      {loading ? "Generating…" : "Generate today's briefing"}
    </button>
  );
}
