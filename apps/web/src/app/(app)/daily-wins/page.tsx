"use client";

import type * as React from "react";
import { useMuseConversations } from "@/hooks/use-muse";
import { useCouncilSessions } from "@/hooks/use-council";
import { useRipples } from "@/hooks/use-prl";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function LoadingCard({ lines = 2 }: { lines?: number }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="space-y-2">
          {Array.from({ length: lines }).map((_, i) => (
            <div key={i} className="h-3 w-full animate-pulse rounded bg-[var(--muted)]" />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function DailyWinsPage(): React.ReactElement {
  const { data: museConversations, isLoading: museLoading } = useMuseConversations();
  const { data: councilSessions, isLoading: councilLoading } = useCouncilSessions();
  const { data: ripples, isLoading: ripplesLoading } = useRipples();

  const recentMuse = museConversations?.slice(0, 3) ?? [];
  const recentSessions = councilSessions?.filter(
    (s) => s.status === "completed" || s.status === "streaming" || s.status === "running"
  ).slice(0, 2) ?? [];
  const protectedRipples = ripples?.filter((r) => r.protectionBand === "protected" || r.protectionBand === "important").slice(0, 3) ?? [];

  return (
    <RouteShell
      eyebrow="Morning briefing"
      title="Daily Wins"
      description="Overnight intelligence summary, campaign progress, and your single recommended action for today."
      tags={["briefing", "muse", "council", "ripples"]}
    >
      <div className="grid gap-6 md:grid-cols-3">
        <div className="space-y-4 md:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Today&apos;s recommended actions</h2>
            <Badge variant="outline" className="text-xs">Prioritized by confidence</Badge>
          </div>

          {ripplesLoading ? (
            <LoadingCard lines={3} />
          ) : protectedRipples.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                <p className="text-3xl">🎯</p>
                <p className="mt-4 font-medium">No high-confidence insights</p>
                <p className="mt-1 text-sm text-[var(--muted-foreground)]">
                  Protected ripples from the PRL will appear here
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {protectedRipples.map((ripple) => (
                <Card key={ripple.rippleId}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        <p className="font-medium leading-snug">{ripple.coreClaim}</p>
                        <p className="mt-1 text-sm text-[var(--muted-foreground)]">
                          {ripple.keyReasoning}
                        </p>
                        {ripple.prediction && (
                          <p className="mt-1 text-xs italic text-[var(--muted-foreground)]">
                            Prediction: {ripple.prediction}
                          </p>
                        )}
                      </div>
                      <Badge
                        variant="outline"
                        className="flex-shrink-0"
                        title={`${(ripple.confidence * 100).toFixed(0)}% confidence`}
                      >
                        {(ripple.confidence * 100).toFixed(0)}%
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Muse conversations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {museLoading ? (
                <LoadingCard />
              ) : recentMuse.length === 0 ? (
                <p className="py-4 text-center text-sm text-[var(--muted-foreground)]">No recent conversations</p>
              ) : (
                recentMuse.map((conv) => (
                  <div key={conv.conversationId} className="flex items-center justify-between text-sm">
                    <span className="truncate capitalize">{conv.route.replace("_", " ")}</span>
                    <span className="ml-2 text-xs text-[var(--muted-foreground)]">{conv.messageCount} msgs</span>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Active sessions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {councilLoading ? (
                <LoadingCard />
              ) : recentSessions.length === 0 ? (
                <p className="py-4 text-center text-sm text-[var(--muted-foreground)]">No active sessions</p>
              ) : (
                recentSessions.map((session) => (
                  <div key={session.sessionId} className="flex items-center justify-between text-sm">
                    <span className="truncate capitalize">{session.sessionType.replace("_", " ")}</span>
                    <Badge
                      variant="outline"
                      className={
                        session.status === "running" || session.status === "streaming"
                          ? "bg-blue-50 text-blue-700 border-blue-200"
                          : "bg-green-50 text-green-700 border-green-200"
                      }
                    >
                      {session.status}
                    </Badge>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Campaign summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-[var(--muted-foreground)]">Active campaigns</span>
                <span className="font-medium">—</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--muted-foreground)]">Running sessions</span>
                <span className="font-medium">{recentSessions.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[var(--muted-foreground)]">High-value ripples</span>
                <span className="font-medium">{protectedRipples.length}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </RouteShell>
  );
}
