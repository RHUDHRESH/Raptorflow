"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeftIcon } from "@radix-ui/react-icons";
import { useCouncilMessages, useCouncilSession } from "@/hooks/use-council";

export default function CouncilSessionPage(): React.ReactElement {
  const params = useParams<{ sessionId: string }>();
  const sessionId = params.sessionId;

  const sessionQuery = useCouncilSession(sessionId);
  const messagesQuery = useCouncilMessages(sessionId);

  const session = sessionQuery.data;
  const messages = messagesQuery.data ?? [];

  return (
    <div className="flex flex-col gap-8 py-2">
      <Link
        href="/council"
        className="flex w-fit items-center gap-2 hover:underline"
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 9,
          textTransform: "uppercase",
          letterSpacing: "0.16em",
          color: "var(--muted-foreground)",
        }}
      >
        <ArrowLeftIcon className="h-3 w-3" />
        Council Archive
      </Link>

      {sessionQuery.isLoading ? (
        <div className="grid gap-4">
          <div className="h-28 animate-pulse border border-[var(--border)] bg-[var(--card)]" />
          <div className="h-64 animate-pulse border border-[var(--border)] bg-[var(--card)]" />
        </div>
      ) : sessionQuery.error ? (
        <div className="border border-[var(--destructive)] p-6 font-mono text-sm text-[var(--destructive)]">
          Failed to load council session: {sessionQuery.error.message}
        </div>
      ) : !session ? (
        <div className="border border-dashed border-[var(--border)] p-12 text-center">
          <p className="font-serif text-2xl text-[var(--foreground)]">Session not found</p>
          <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--muted-foreground)]">
            The requested council session does not exist in the current tenant scope.
          </p>
        </div>
      ) : (
        <div className="grid items-start gap-8 xl:grid-cols-[1fr_320px]">
          <div className="border border-[var(--border)] bg-[var(--card)]">
            <div className="border-b border-[var(--border)] p-6">
              <p
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 9,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.18em",
                  color: "var(--muted-foreground)",
                  marginBottom: 8,
                }}
              >
                {session.sessionType.replace(/_/g, " ")}
              </p>
              <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 32, margin: 0, lineHeight: 1.1 }}>
                {session.campaignId || "Unassigned Campaign"}
              </h1>
              <p
                className="mt-3"
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 9,
                  textTransform: "uppercase",
                  letterSpacing: "0.14em",
                  color: "var(--muted-foreground)",
                }}
              >
                Session {session.sessionId}
              </p>
            </div>

            <div className="divide-y divide-[var(--border)]">
              {messagesQuery.isLoading ? (
                <div className="p-6 text-sm text-[var(--muted-foreground)]">Loading session messages…</div>
              ) : messages.length === 0 ? (
                <div className="p-6">
                  <p className="font-serif text-xl text-[var(--foreground)]">No recorded agent positions yet</p>
                  <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.16em] text-[var(--muted-foreground)]">
                    This session exists, but no persisted council messages have been written yet.
                  </p>
                </div>
              ) : (
                messages.map((message) => (
                  <div key={message.messageId} className="p-6">
                    <div className="mb-3 flex items-center gap-3">
                      <span
                        style={{
                          fontFamily: "'JetBrains Mono', monospace",
                          fontSize: 8,
                          fontWeight: 700,
                          textTransform: "uppercase",
                          letterSpacing: "0.14em",
                          color: "var(--amber-war)",
                          border: "1px solid var(--amber-war)",
                          padding: "2px 6px",
                        }}
                      >
                        Position
                      </span>
                    </div>
                    <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, lineHeight: 1.7, margin: 0 }}>
                      {message.content}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="space-y-4 xl:sticky xl:top-6">
            <div className="border border-[var(--border)] bg-[var(--card)]">
              <div className="border-b border-[var(--border)] px-4 py-3">
                <p
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 9,
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.16em",
                    color: "var(--muted-foreground)",
                  }}
                >
                  Session Intelligence
                </p>
              </div>
              {[
                { label: "Status", value: session.status },
                { label: "Type", value: session.sessionType.replace(/_/g, " ") },
                { label: "Campaign", value: session.campaignId || "None" },
                { label: "Messages", value: String(messages.length) },
                { label: "Created", value: new Date(session.createdAt).toLocaleString("en-IN") },
              ].map((row) => (
                <div key={row.label} className="flex items-center justify-between px-4 py-3">
                  <span
                    style={{
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: 9,
                      textTransform: "uppercase",
                      letterSpacing: "0.1em",
                      color: "var(--muted-foreground)",
                    }}
                  >
                    {row.label}
                  </span>
                  <span
                    style={{
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: 10,
                      fontWeight: 600,
                      color: "var(--foreground)",
                    }}
                  >
                    {row.value}
                  </span>
                </div>
              ))}
            </div>

            <Link
              href="/muse"
              className="flex items-center justify-center gap-2 border border-[var(--border)] py-3 transition-all hover:border-[var(--foreground)] hover:bg-[var(--foreground)] hover:text-[var(--background)]"
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.14em",
                color: "var(--foreground)",
              }}
            >
              Ask Muse about this session
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
