"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiFetch<DashboardData>("/api/dashboard"),
    staleTime: 30_000,
    refetchOnWindowFocus: true,
  });
}

export interface DashboardData {
  stats: {
    activeCampaigns: number;
    totalCampaigns: number;
    councilSessions: number;
    taskCompletionRate: number;
    foundationScore: number | null;
    foundationFields: number;
    intelUnread: number;
    nudgeCount: number;
  };
  todayWin: {
    headline: string;
    momentumScore: number;
    focusAreas: string[];
  } | null;
  nudges: Array<{
    id: string;
    type: string;
    title: string;
    body: string;
    cta: string | null;
    ctaHref: string | null;
    priority: number;
  }>;
  activityFeed: Array<{
    id: string;
    type: string;
    content: string;
    createdAt: string;
    icon: string;
    colour: string;
  }>;
  foundation: {
    companyName: string;
    fieldsFilledCount: number;
    positioningScore: number | null;
  };
}
