"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { useCouncilSessions, useStartCouncilSession } from "@/hooks/use-council";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CouncilPage(): React.ReactElement {
  const { data: sessions, isLoading, error } = useCouncilSessions();
  const startSession = useStartCouncilSession();

  return (
    <RouteShell
      eyebrow="Council"
      title="Council Sessions"
      description="AI agent deliberation sessions for campaign strategy, tactical adjustments, and crisis response."
      tags={["council", "deliberation", "strategy"]}
      rail={
        <Card>
          <CardHeader>
            <CardTitle>Session types</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div>
              <p className="font-medium">Strategic</p>
              <p className="text-[var(--muted-foreground)]">High-level campaign direction and goal alignment</p>
            </div>
            <div>
              <p className="font-medium">Tactical</p>
              <p className="text-[var(--muted-foreground)]">Channel-level adjustments and mid-campaign pivots</p>
            </div>
            <div>
              <p className="font-medium">War Room</p>
              <p className="text-[var(--muted-foreground)]">Crisis response and competitive reactions</p>
            </div>
            <div>
              <p className="font-medium">Replanning</p>
              <p className="text-[var(--muted-foreground)]">Budget and timeline revisions</p>
            </div>
          </CardContent>
        </Card>
      }
    >
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Session history</h2>
          <p className="text-sm text-[var(--muted-foreground)]">
            {sessions?.length ?? 0} sessions
          </p>
        </div>
        <Button
          size="sm"
          onClick={() => startSession.mutate({ campaignId: "campaign-001" })}
          disabled={startSession.isPending}
        >
          {startSession.isPending ? "Starting..." : "+ Start session"}
        </Button>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <div className="h-4 w-48 animate-pulse rounded bg-[var(--muted)]" />
                <div className="mt-2 h-3 w-full animate-pulse rounded bg-[var(--muted)]" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4 text-sm text-red-700">
            Failed to load sessions: {error.message}
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && sessions?.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-3xl">🏛️</p>
            <p className="mt-4 font-medium">No sessions yet</p>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">
              Start a council session to deliberate on your campaign
            </p>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && sessions && sessions.length > 0 && (
        <div className="space-y-3">
          {sessions.map((session) => {
            const statusColor =
              session.status === "running" || session.status === "streaming" ? "bg-blue-100 text-blue-700 border-blue-200" :
              session.status === "completed" ? "bg-green-100 text-green-700 border-green-200" :
              "bg-[var(--muted)]";
            return (
              <Card key={session.sessionId}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold capitalize">
                          {session.sessionType.replace("_", " ")}
                        </span>
                        <Badge className={statusColor} variant="outline">
                          {session.status}
                        </Badge>
                      </div>
                      <p className="mt-1 text-sm text-[var(--muted-foreground)]">
                        Campaign: {session.campaignId}
                      </p>
                      <p className="mt-0.5 text-xs text-[var(--muted-foreground)]">
                        {new Date(session.createdAt).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button asChild size="sm" variant="secondary">
                        <Link href={`/council/${session.sessionId}` as Route}>View</Link>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </RouteShell>
  );
}
