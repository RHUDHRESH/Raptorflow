"use client";

import React, { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import { 
  Target, 
  Plus, 
  TrendingUp, 
  Users, 
  ShoppingCart, 
  Heart, 
  RefreshCcw, 
  Radio, 
  BarChart2, 
  ChevronRight 
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { CreateCampaignDrawer } from "@/components/campaigns/create-campaign-drawer";
import { cn } from "@/lib/cn";

interface Campaign {
  campaign_id: string;
  name: string;
  goal_type: "awareness" | "leads" | "conversion" | "retention" | "re_engagement";
  status: "draft" | "pending_approval" | "active" | "paused" | "completed";
  start_date: string;
  end_date: string;
  current_move_name: string;
  tasks_due_today: number;
  tasks_completed: number;
  tasks_total: number;
  progress_pct: number;
}

export default function CampaignsPage() {
  const router = useRouter();
  const { getToken } = useAuth();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["campaigns"],
    queryFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/campaigns`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to fetch campaigns");
      return res.json() as Promise<{ campaigns: Campaign[] }>;
    }
  });

  const campaigns = data?.campaigns || [];

  // Compute stats
  const activeCount = campaigns.filter(c => c.status === "active").length;
  const tasksDueToday = campaigns.reduce((acc, c) => acc + (c.status === "active" ? c.tasks_due_today : 0), 0);
  const completedCount = campaigns.filter(c => c.status === "completed").length;

  const GoalIcon = ({ type }: { type: Campaign["goal_type"] }) => {
    switch (type) {
      case "awareness": return <Radio className="w-3 h-3" />;
      case "leads": return <Users className="w-3 h-3" />;
      case "conversion": return <ShoppingCart className="w-3 h-3" />;
      case "retention": return <Heart className="w-3 h-3" />;
      case "re_engagement": return <RefreshCcw className="w-3 h-3" />;
      default: return null;
    }
  };

  const statusVariants = {
    active: "bg-green-500/10 text-green-500 border border-green-500/30 text-xs",
    draft: "bg-zinc-800 text-zinc-400 text-xs border-transparent",
    pending_approval: "bg-amber-500/10 text-amber-500 border border-amber-500/30 text-xs",
    paused: "bg-zinc-800 text-zinc-500 text-xs border-transparent",
    completed: "bg-blue-500/10 text-blue-400 border border-blue-500/30 text-xs",
  };

  const renderCampaignList = (statusFilter: string) => {
    const filtered = campaigns.filter(c => {
      if (statusFilter === "active") return c.status === "active";
      if (statusFilter === "draft") return c.status === "draft" || c.status === "pending_approval";
      if (statusFilter === "completed") return c.status === "completed";
      return true;
    });

    if (isLoading) {
      return (
        <div className="space-y-3">
          <Skeleton className="h-32 rounded-2xl w-full" />
          <Skeleton className="h-32 rounded-2xl w-full" />
          <Skeleton className="h-32 rounded-2xl w-full" />
        </div>
      );
    }

    if (filtered.length === 0) {
      return (
        <div className="py-16 flex flex-col items-center gap-4">
          <Target className="w-10 h-10 text-zinc-600" />
          <div className="text-center">
            <h3 className="text-lg text-white font-medium">No campaigns yet.</h3>
            <p className="text-sm text-zinc-400">Your Strategist is ready to build one.</p>
          </div>
          <Button 
            className="bg-amber-500 text-black hover:bg-amber-400 font-semibold rounded-lg"
            onClick={() => setDrawerOpen(true)}
          >
            Create a campaign
          </Button>
        </div>
      );
    }

    return filtered.map(c => (
      <div 
        key={c.campaign_id}
        onClick={() => router.push(`/app/campaigns/${c.campaign_id}`)}
        className="bg-[#1a1a1a] rounded-2xl p-5 border border-zinc-800 hover:border-zinc-700 cursor-pointer transition-colors mb-3 group"
      >
        <div className="flex justify-between items-start">
          <h4 className="text-base text-white font-semibold group-hover:text-amber-500 transition-colors">
            {c.name}
          </h4>
          <Badge className={cn("px-2 py-0.5 rounded-md", statusVariants[c.status])} variant="outline">
            {c.status.replace('_', ' ')}
          </Badge>
        </div>

        <div className="flex items-center gap-3 mt-2">
          <div className="flex items-center gap-1.5 bg-[#262626] rounded-full px-3 py-1 text-xs text-zinc-300">
            <GoalIcon type={c.goal_type} />
            <span className="capitalize">{c.goal_type.replace('_', ' ')}</span>
          </div>
          {c.tasks_due_today > 0 && (
            <div className="bg-amber-500/10 text-amber-500 text-xs rounded-full px-2 py-0.5 border border-amber-500/20">
              {c.tasks_due_today} due today
            </div>
          )}
        </div>

        <div className="mt-3">
          <div className="text-sm text-zinc-400 mb-2 truncate">
            {c.current_move_name}
          </div>
          <div className="w-full h-1 rounded-full bg-zinc-800 overflow-hidden">
            <div 
              className="bg-amber-500 h-full rounded-full transition-all duration-500" 
              style={{ width: `${c.progress_pct}%` }}
            />
          </div>
        </div>

        <div className="flex justify-between items-center mt-3">
          <div className="text-xs text-zinc-500">
            {new Date(c.start_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} – {new Date(c.end_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
          </div>
          <div className="text-xs text-amber-500 font-medium flex items-center gap-1">
            Open <ChevronRight className="w-3 h-3" />
          </div>
        </div>
      </div>
    ));
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 h-full bg-[#121212]">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-white tracking-tight">Campaigns</h1>
        <Button 
          className="bg-amber-500 text-black hover:bg-amber-400 font-semibold rounded-lg flex items-center gap-2"
          onClick={() => setDrawerOpen(true)}
        >
          <Plus className="w-4 h-4" />
          New campaign
        </Button>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-[#1a1a1a] rounded-xl p-5 border border-zinc-800">
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold mb-1">Active campaigns</p>
          <div className="text-3xl white font-bold">{isLoading ? <Skeleton className="h-8 w-12" /> : activeCount}</div>
        </div>
        <div className="bg-[#1a1a1a] rounded-xl p-5 border border-zinc-800">
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold mb-1">Tasks due today</p>
          <div className={cn("text-3xl font-bold", tasksDueToday > 0 ? "text-amber-500" : "text-white")}>
            {isLoading ? <Skeleton className="h-8 w-12" /> : tasksDueToday}
          </div>
        </div>
        <div className="bg-[#1a1a1a] rounded-xl p-5 border border-zinc-800">
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold mb-1">Completed</p>
          <div className="text-3xl white font-bold">{isLoading ? <Skeleton className="h-8 w-12" /> : completedCount}</div>
        </div>
      </div>

      {isError && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center justify-between">
          <p className="text-sm text-red-400">Couldn't load campaigns.</p>
          <Button variant="ghost" className="text-xs text-red-400 hover:text-red-300" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      )}

      <Tabs defaultValue="active" className="w-full">
        <TabsList className="bg-[#1a1a1a] border border-zinc-800 rounded-xl p-1 mb-6 flex gap-1 h-auto">
          {["active", "draft", "completed", "all"].map(tab => (
            <TabsTrigger 
              key={tab}
              value={tab}
              className="flex-1 text-sm text-zinc-400 data-[state=active]:text-white data-[state=active]:bg-[#262626] rounded-lg px-4 py-2 transition-all capitalize"
            >
              {tab}
            </TabsTrigger>
          ))}
        </TabsList>
        
        <TabsContent value="active" className="mt-0">{renderCampaignList("active")}</TabsContent>
        <TabsContent value="draft" className="mt-0">{renderCampaignList("draft")}</TabsContent>
        <TabsContent value="completed" className="mt-0">{renderCampaignList("completed")}</TabsContent>
        <TabsContent value="all" className="mt-0">{renderCampaignList("all")}</TabsContent>
      </Tabs>

      <CreateCampaignDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
    </div>
  );
}
