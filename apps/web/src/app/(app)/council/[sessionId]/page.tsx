"use client";

import * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { useCouncilSession, useCouncilMessages } from "@/hooks/use-council";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/cn";

const STATUS_COLORS: Record<string, string> = {
  queued: "bg-amber-100 text-amber-700 border-amber-200",
  running: "bg-blue-100 text-blue-700 border-blue-200",
  streaming: "bg-purple-100 text-purple-700 border-purple-200",
  completed: "bg-green-100 text-green-700 border-green-200",
  failed: "bg-red-100 text-red-700 border-red-200",
};

const AVATAR_COLORS: Record<string, string> = {
  strategist: "bg-[var(--primary)] text-[var(--primary-foreground)]",
  analyst: "bg-blue-500 text-white",
  creative: "bg-pink-500 text-white",
  executor: "bg-green-600 text-white",
  advisor: "bg-amber-500 text-white",
};

function getAvatarColor(avatarKey: string): string {
  return AVATAR_COLORS[avatarKey.toLowerCase()] ?? "bg-[var(--muted)] text-[var(--muted-foreground)]";
}

function AvatarBadge({ avatarKey }: { avatarKey: string }) {
  return (
    <span
      className={cn(
        "inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold",
        getAvatarColor(avatarKey)
      )}
    >
      {avatarKey.charAt(0).toUpperCase()}
    </span>
  );
}

export default function CouncilSessionPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}): React.ReactElement {
  const resolvedParams = React.use(params);
  const { sessionId } = resolvedParams;

  const { data: session, isLoading: sessionLoading, error: sessionError } = useCouncilSession(sessionId);
  const { data: messages, isLoading: messagesLoading, error: messagesError } = useCouncilMessages(sessionId);

  const isLoading = sessionLoading || messagesLoading;
  const hasError = sessionError || messagesError;

  const sessionRoute = "/council" as Route;

  return (
    <RouteShell
      eyebrow="Council"
      title={session ? `${session.sessionType.replace("_", " ")} session` : "Session detail"}
      description={
        session
          ? `Council deliberation for campaign ${session.campaignId}`
          : `Session ${sessionId}`
      }
      tags={["council", "session", "deliberation"]}
      backHref={sessionRoute}
      backLabel="Back to Council"
    >
      {isLoading && (
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex gap-3">
              <div className="h-7 w-7 flex-shrink-0 animate-pulse rounded-full bg-[var(--muted)]" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-32 animate-pulse rounded bg-[var(--muted)]" />
                <div className="h-3 w-full animate-pulse rounded bg-[var(--muted)]" />
              </div>
            </div>
          ))}
        </div>
      )}

      {hasError && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4 text-sm text-red-700">
            {sessionError ? `Session error: ${sessionError.message}` : ""}
            {messagesError ? `Messages error: ${messagesError.message}` : ""}
          </CardContent>
        </Card>
      )}

      {session && (
        <div className="mb-6 flex items-center gap-3">
          <Badge
            variant="outline"
            className={STATUS_COLORS[session.status] ?? ""}
          >
            {session.status}
          </Badge>
          <span className="text-sm text-[var(--muted-foreground)]">
            Campaign: <span className="font-medium text-[var(--foreground)]">{session.campaignId}</span>
          </span>
          <span className="text-sm text-[var(--muted-foreground)]">
            {new Date(session.createdAt).toLocaleString()}
          </span>
        </div>
      )}

      {messages && messages.length === 0 && !isLoading && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-3xl">🏛️</p>
            <p className="mt-4 font-medium">No messages yet</p>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">
              {session?.status === "running" || session?.status === "streaming"
                ? "The council is deliberating..."
                : "Messages will appear here once the session starts."}
            </p>
          </CardContent>
        </Card>
      )}

      {messages && messages.length > 0 && (
        <div className="space-y-4">
          {messages.map((msg, idx) => (
            <Card key={msg.messageId}>
              <CardContent className="p-4">
                <div className="flex gap-3">
                  <AvatarBadge avatarKey={msg.avatarKey} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-semibold capitalize">{msg.avatarKey}</span>
                      <span className="text-xs text-[var(--muted-foreground)]">
                        Round {msg.roundNumber}
                      </span>
                      <span className="text-xs text-[var(--muted-foreground)]">
                        {new Date(msg.createdAt).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </RouteShell>
  );
}
