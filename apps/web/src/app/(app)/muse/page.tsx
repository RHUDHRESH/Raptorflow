"use client";

import type * as React from "react";
import { useState } from "react";
import { useMuseConversations, useSubmitMusePrompt } from "@/hooks/use-muse";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ROUTES = [
  { id: "strategic", label: "Strategic", description: "High-level campaign direction and competitive positioning" },
  { id: "content", label: "Content", description: "Copy, messaging, and content strategy" },
  { id: "tactical", label: "Tactical", description: "Channel-specific execution and optimization" },
  { id: "foundation_update", label: "Foundation update", description: "Suggest changes to the Foundation based on new evidence" },
];

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

export default function MusePage(): React.ReactElement {
  const { data: conversations, isLoading } = useMuseConversations();
  const submitPrompt = useSubmitMusePrompt();

  const [selectedRoute, setSelectedRoute] = useState<string>("strategic");
  const [message, setMessage] = useState("");
  const [activeTab, setActiveTab] = useState<"chat" | "history">("chat");

  const handleSubmit = async () => {
    if (!message.trim()) return;
    try {
      await submitPrompt.mutateAsync({
        route: selectedRoute as "strategic" | "content" | "tactical" | "foundation_update",
        message: message.trim(),
      });
      setMessage("");
    } catch (err) {
      console.error("Failed to submit prompt:", err);
    }
  };

  return (
    <RouteShell
      eyebrow="Muse"
      title="Muse AI"
      description="Spatially-aware AI chat shell. Route your question to get contextually relevant answers from the Strategist, grounded in your Foundation."
      tags={["ai", "muse", "chat", "groq"]}
    >
      <div className="grid gap-4 xl:grid-cols-4">
        {/* Route selector sidebar */}
        <div className="space-y-3 xl:col-span-1">
          <p className="text-xs font-medium uppercase tracking-[0.16em] text-[var(--muted-foreground)]">
            Route
          </p>
          {ROUTES.map((route) => (
            <button
              key={route.id}
              onClick={() => setSelectedRoute(route.id)}
              className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                selectedRoute === route.id
                  ? "border-[var(--accent)] bg-accent/10 text-[var(--accent)]"
                  : "border-[var(--border)] bg-white text-[var(--foreground)] hover:border-[var(--accent)]"
              }`}
            >
              <p className="font-medium">{route.label}</p>
              <p className="mt-0.5 text-xs text-[var(--muted-foreground)]">{route.description}</p>
            </button>
          ))}
        </div>

        {/* Chat area */}
        <div className="space-y-4 xl:col-span-3">
          <div className="flex gap-2 border-b border-[var(--border)] pb-2">
            <button
              onClick={() => setActiveTab("chat")}
              className={`px-3 py-1 text-sm ${activeTab === "chat" ? "border-b-2 border-[var(--accent)] text-[var(--accent)]" : "text-[var(--muted-foreground)]"}`}
            >
              Chat
            </button>
            <button
              onClick={() => setActiveTab("history")}
              className={`px-3 py-1 text-sm ${activeTab === "history" ? "border-b-2 border-[var(--accent)] text-[var(--accent)]" : "text-[var(--muted-foreground)]"}`}
            >
              History
            </button>
          </div>

          {activeTab === "chat" && (
            <>
              <Card>
                <CardContent className="p-6">
                  <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-[var(--border)]">
                    <p className="text-sm text-[var(--muted-foreground)]">
                      Type a message below to start a conversation with Muse
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Ask Muse</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <textarea
                    className="w-full rounded-lg border border-[var(--border)] bg-white p-3 text-sm placeholder:text-[var(--muted-foreground)] focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]"
                    rows={3}
                    placeholder={`Ask about your ${selectedRoute.replace("_", " ")} strategy...`}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                        handleSubmit();
                      }
                    }}
                  />
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-[var(--muted-foreground)]">
                      Ctrl+Enter to send
                    </p>
                    <Button
                      size="sm"
                      onClick={handleSubmit}
                      disabled={submitPrompt.isPending || !message.trim()}
                    >
                      {submitPrompt.isPending ? "Thinking..." : "Send"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </>
          )}

          {activeTab === "history" && (
            <div className="space-y-3">
              {isLoading ? (
                <>
                  <LoadingCard />
                  <LoadingCard />
                </>
              ) : conversations && conversations.length > 0 ? (
                conversations.map((conv) => (
                  <Card key={conv.conversationId}>
                    <CardContent className="flex items-center justify-between p-4">
                      <div>
                        <Badge variant="outline" className="mb-1 text-xs">{conv.route.replace("_", " ")}</Badge>
                        <p className="text-sm font-medium capitalize">{conv.route.replace("_", " ")}</p>
                        <p className="mt-0.5 text-xs text-[var(--muted-foreground)]">
                          {conv.messageCount} messages · {new Date(conv.lastMessageAt).toLocaleDateString()}
                        </p>
                      </div>
                      <Button size="sm" variant="ghost">Resume →</Button>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                    <p className="text-3xl">💬</p>
                    <p className="mt-4 font-medium">No conversations yet</p>
                    <p className="mt-1 text-sm text-[var(--muted-foreground)]">
                      Start a chat above to create your first Muse conversation
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>

      <Card className="border-amber-200 bg-amber-50/50">
        <CardHeader>
          <CardTitle className="text-base">📝 What to implement next</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-amber-800">
          <p><strong>Streaming response:</strong> Muse responses should stream token-by-token using SSE (Server-Sent Events) or WebSocket — currently waits for full response.</p>
          <p><strong>Context injection:</strong> Before sending the prompt, inject the current Foundation sections and campaign context into the prompt for grounded answers.</p>
          <p><strong>Citation system:</strong> When Muse references Foundation data, show inline citations linking back to the specific Foundation step.</p>
          <p><strong>Route classifier:</strong> If no route is explicitly selected, use a classifier to auto-route the incoming message to the most relevant route.</p>
          <p><strong>Speech synthesis:</strong> Optional text-to-speech playback of Muse responses in the Office canvas.</p>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
