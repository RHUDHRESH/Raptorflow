"use client";

import { useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import { useQueryClient } from "@tanstack/react-query";
import { getPusherClient } from "@/lib/pusher/client";
import { events } from "@/lib/pusher/server";
import { useToast } from "@/components/ui/toast";

export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  const { user } = useUser();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  useEffect(() => {
    if (!user?.id) return;

    const pusher = getPusherClient();
    const channel = pusher.subscribe(`private-user-${user.id}`);

    channel.bind(events.FOUNDATION_SAVED, (data: Record<string, unknown>) => {
      queryClient.invalidateQueries({ queryKey: ["foundation"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    });

    channel.bind(events.FOUNDATION_SCAN_COMPLETE, (data: Record<string, unknown>) => {
      queryClient.invalidateQueries({ queryKey: ["foundation"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast(
        `Foundation scan complete — score: ${(data.positioningScore as number) ?? "?"}/10`,
        "success",
      );
    });

    channel.bind(events.CAMPAIGN_EVALUATED, (data: Record<string, unknown>) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      queryClient.invalidateQueries({ queryKey: ["campaigns", data.campaignId as string] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast(`"${data.title}" evaluated — score: ${data.score}/10`, "success");
    });

    channel.bind(events.MOVES_GENERATED, (data: Record<string, unknown>) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", data.campaignId as string] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast(`${data.moveCount} moves generated`, "success");
    });

    channel.bind(events.COUNCIL_COMPLETE, (data: Record<string, unknown>) => {
      queryClient.invalidateQueries({ queryKey: ["council"] });
      queryClient.invalidateQueries({ queryKey: ["council", data.sessionId as string] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast("Council session complete", "success");
    });

    channel.bind(events.COUNCIL_STATUS_CHANGED, (data: Record<string, unknown>) => {
      queryClient.invalidateQueries({ queryKey: ["council", data.sessionId as string] });
    });

    channel.bind(events.INTEL_SIGNAL, (data: Record<string, unknown>) => {
      queryClient.invalidateQueries({ queryKey: ["intel"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      const severity = (data.severity as string) ?? "medium";
      const icon = severity === "critical" ? "🚨" : severity === "high" ? "⚠️" : "📡";
      toast(`${icon} ${data.title as string}`, "default");
    });

    channel.bind(events.DAILY_WIN_READY, (data: Record<string, unknown>) => {
      queryClient.invalidateQueries({ queryKey: ["daily-wins"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast(`Daily briefing ready — momentum: ${data.momentumScore as number}/10`, "success");
    });

    channel.bind(events.NUDGE_CREATED, (data: Record<string, unknown>) => {
      queryClient.invalidateQueries({ queryKey: ["nudges"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast(`💡 ${data.title as string}`, "default");
    });

    return () => {
      channel.unbind_all();
      pusher.unsubscribe(`private-user-${user.id}`);
    };
  }, [user?.id, queryClient, toast]);

  return <>{children}</>;
}
