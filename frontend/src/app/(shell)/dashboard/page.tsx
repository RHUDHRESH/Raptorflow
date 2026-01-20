"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { DashboardMetrics, Metric } from "@/components/dashboard/DashboardMetrics";
import { DashboardFocus } from "@/components/dashboard/DashboardFocus";
import { DashboardActivity, ActivityItem } from "@/components/dashboard/DashboardActivity";
import { useDashboardStore } from "@/stores/dashboardStore";
import { useAuth } from "@/components/auth/AuthProvider";
import { Activity, Target, Users, Zap, TrendingUp, Flame } from "lucide-react";

export default function DashboardPage() {
  const pageRef = useRef<HTMLDivElement>(null);
  const { summary, fetchSummary, isLoading } = useDashboardStore();
  const { user } = useAuth();

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  // Determine system status
  const systemStatus = !summary || (summary.active_campaigns.length === 0 && summary.active_moves.length === 0)
      ? "Attention"
      : "Nominal";

  // Primary focus move (first active)
  const primaryMove = summary?.active_moves?.length ? summary.active_moves[0] : null;

  // Extract user name from email
  const userName = user
    ? user.email.split("@")[0].charAt(0).toUpperCase() +
    user.email.split("@")[0].slice(1)
    : "Founder";

  // Metrics data from summary
  const metrics: Metric[] = [
    {
      label: "Evolution Index",
      value: summary?.evolution_index?.toFixed(1) || "1.0",
      icon: TrendingUp,
      trend: "up",
      trendValue: "Strategy Growth"
    },
    {
      label: "Active Moves",
      value: summary?.active_moves?.length || 0,
      icon: Zap,
    },
    {
      label: "Daily Streak",
      value: summary?.daily_wins_streak || 0,
      icon: Flame,
      trend: "up",
      trendValue: "Consistency"
    },
    {
      label: "Total Wins",
      value: summary?.workspace_stats?.total_wins || 0,
      icon: Target,
    },
  ];

  // Map Muse assets to Activity Items
  const recentActivity: ActivityItem[] = summary?.recent_muse_assets?.map(asset => ({
    id: asset.id,
    type: "asset",
    title: `Asset Created: ${asset.title}`,
    timestamp: new Date(asset.created_at).toLocaleDateString(),
    status: asset.status,
    href: "/muse"
  })) || [];

  // Entrance animation
  useEffect(() => {
    if (!pageRef.current) return;

    gsap.fromTo(
      "[data-fade]",
      { opacity: 0, y: 12 },
      {
        opacity: 1,
        y: 0,
        duration: 0.5,
        stagger: 0.08,
        ease: "power2.out",
      }
    );
  }, []);

  return (
    <div ref={pageRef} className="min-h-screen bg-[var(--canvas)] pb-16">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-12 pt-8">
        {/* Header */}
        <div data-fade>
          <DashboardHeader
            userName={userName}
            systemStatus={systemStatus}
          />
        </div>

        {/* Metrics row */}
        <div data-fade className="mt-10">
          <DashboardMetrics metrics={metrics} />
        </div>

        {/* Main content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 mt-12">
          {/* Primary Focus (takes 2/3 on desktop) */}
          <div data-fade className="lg:col-span-2">
            <DashboardFocus move={primaryMove} />
          </div>

          {/* Activity feed (takes 1/3 on desktop) */}
          <div data-fade className="lg:col-span-1">
            <DashboardActivity items={recentActivity} />
          </div>
        </div>

        {/* Footer meta */}
        <div
          data-fade
          className="mt-16 text-center text-[10px] font-mono text-[var(--ink-muted)] uppercase tracking-widest"
        >
          RaptorFlow OS v4.2 • Secure
        </div>
      </div>
    </div>
  );
}
