"use client";

import * as React from "react";
import { useRef, useEffect, useState } from "react";
import Link from "next/link";
import type { Route } from "next";
import { formatDistanceToNow } from "date-fns";
import { PlusIcon, Send, MessageSquare, ArrowRightIcon } from "lucide-react";
import {
  useMuseConversations,
  useCreateConversation,
  useSendMessage,
  usePatchConversation,
  type MuseMessage,
  type MuseConversation,
} from "@/features/muse/hooks";
import { Button } from "@/components/ui/button";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { cn } from "@/lib/cn";

const ROUTE_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  tactical: { bg: "bg-[var(--indigo-wash)]", text: "text-[var(--indigo-muse)]", border: "border-[var(--indigo-muse)]/30" },
  strategic: { bg: "bg-[var(--paper-150)]", text: "text-[var(--pod-creative)]", border: "border-[var(--pod-creative)]/30" },
  campaign: { bg: "bg-[var(--leaf-wash)]", text: "text-[var(--leaf-confirm)]", border: "border-[var(--leaf-confirm)]/30" },
  council: { bg: "bg-[var(--amber-wash)]", text: "text-[var(--primary)]", border: "border-[var(--primary)]/30" },
  foundation: { bg: "bg-[var(--paper-150)]", text: "text-[var(--ink-500)]", border: "border-[var(--ink-400)]/30" },
};

const SUGGESTION_CHIPS = [
  "Write me 3 subject lines for a re-engagement email",
  "What should our content strategy focus on this quarter?",
  "Should we launch a podcast?",
  "How do I improve our positioning?",
];

function RouteBadge({ route }: { route: string }): React.ReactElement {
  const colors = ROUTE_COLORS[route] ?? ROUTE_COLORS.foundation;
  return (
    <span
      className={cn(
        "inline-block border px-2 py-0.5 text-[8px] font-bold uppercase tracking-[0.14em] font-mono rounded-full",
        colors.bg, colors.text, colors.border
      )}
      style={{ borderWidth: 1, borderStyle: "solid" }}
    >
      {route}
    </span>
  );
}

function MessageBubble({
  message,
  onCouncilLink,
}: {
  message: MuseMessage;
  onCouncilLink?: (sessionId: string) => void;
}): React.ReactElement {
  const isUser = message.role === "user";
  return (
    <div className={cn("flex flex-col gap-1", isUser ? "items-end" : "items-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-[var(--radius-lg)] px-5 py-4 text-sm leading-relaxed border transition-all duration-200",
          isUser
            ? "rounded-tr-none bg-[var(--amber-wash)] border-[var(--primary)]/20 text-[var(--ink-900)]"
            : "rounded-tl-none bg-white border-[var(--border)] text-[var(--ink-900)]"
        )}
      >
        <p style={{ whiteSpace: "pre-wrap" }}>{message.content}</p>
      </div>
      <div className="flex items-center gap-2">
        {!isUser && message.route && <RouteBadge route={message.route} />}
        {isUser && (
          <span className="mono-label">you</span>
        )}
        {!isUser && !message.route && (
          <span className="mono-label">muse</span>
        )}
      </div>
    </div>
  );
}

export default function MusePage(): React.ReactElement {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const convQuery = useMuseConversations();
  const createConv = useCreateConversation();
  const sendMessage = useSendMessage();
  const patchConv = usePatchConversation();

  const conversations: MuseConversation[] = convQuery.data ?? [];

  const selectedConv = conversations.find((c) => c.id === selectedId) ?? null;

  const [messages, setMessages] = useState<MuseMessage[]>([]);
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);
  const [pendingSessionId, setPendingSessionId] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedId) {
      setMessages([]);
      return;
    }
    setIsLoadingConversation(true);
    fetch(`/api/muse/conversations/${selectedId}`, {
      headers: { Authorization: `Bearer ${""}` },
    })
      .then((r) => r.json())
      .then((data: MuseConversation & { messages: MuseMessage[] }) => {
        setMessages(data.messages ?? []);
        setIsLoadingConversation(false);
      })
      .catch(() => setIsLoadingConversation(false));
  }, [selectedId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  async function handleNewConversation() {
    const result = await createConv.mutateAsync(undefined);
    setSelectedId(result.id);
    setMessages([]);
  }

  async function handleSend() {
    if (!input.trim() || !selectedId || sendMessage.isPending) return;
    const text = input.trim();
    setInput("");

    const userMsg: MuseMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: text,
      route: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const result = await sendMessage.mutateAsync({ conversationId: selectedId, message: text });

      if (result.sessionId) {
        setPendingSessionId(result.sessionId);
      }

      const assistantMsg: MuseMessage = {
        id: result.messageId,
        role: "assistant",
        content: result.response,
        route: result.route,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      if (messages.length === 0 && selectedConv?.title === "New conversation") {
        patchConv.mutate({ id: selectedId, title: text.slice(0, 50) });
      }
    } catch (err) {
      console.error("Send failed:", err);
      setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
    }
  }

  async function handleChip(message: string) {
    if (createConv.isPending) return;
    const result = await createConv.mutateAsync(message.slice(0, 50));
    setSelectedId(result.id);
    setMessages([]);
    setTimeout(() => {
      setInput(message);
      setTimeout(() => handleSend(), 50);
    }, 100);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden -mx-6 -my-8 md:-mx-10">
      <aside className="w-72 shrink-0 border-r border-[var(--border)] bg-[var(--sidebar-background)] flex flex-col paper-soft">
        <div className="border-b border-[var(--border)] p-4">
          <Button
            onClick={handleNewConversation}
            className="h-10 w-full"
          >
            <PlusIcon className="mr-2 h-4 w-4" />
            New Conversation
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="px-3 py-3 eyebrow">
            Conversations
          </div>

          {convQuery.isLoading ? (
            <div className="p-2 space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-12 rounded-[var(--radius)] bg-[var(--paper-200)] animate-pulse" />
              ))}
            </div>
          ) : conversations.length === 0 ? (
            <p className="px-4 py-8 text-center mono-label">
              No conversations yet
            </p>
          ) : (
            <div className="p-1">
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => setSelectedId(conv.id)}
                  className={cn(
                    "w-full rounded-[var(--radius)] px-3 py-3 text-left transition-all duration-200",
                    selectedId === conv.id ? "bg-[var(--amber-wash)] shadow-sm" : "hover:bg-[var(--paper-150)]"
                  )}
                >
                  <div className="truncate text-xs font-medium text-[var(--ink-900)]">
                    {conv.title}
                  </div>
                  <div className="mt-1">
                    <RouteBadge route={(conv as { route?: string }).route ?? "strategic"} />
                  </div>
                  <div className="mt-1 truncate mono-label">
                    {formatDistanceToNow(new Date(conv.updated_at), { addSuffix: true })}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </aside>

      <main className="flex flex-1 flex-col bg-[var(--background)] paper-soft">
        <header className="flex h-14 items-center justify-between border-b border-[var(--border)] px-6 bg-[var(--card)]">
          <div className="flex items-center gap-3">
            <MessageSquare className="h-4 w-4 text-[var(--primary)]" />
            <span className="text-sm font-medium text-[var(--ink-900)]">
              {selectedConv?.title || "Muse"}
            </span>
          </div>
          <span className="mono-label">RaptorFlow AI</span>
        </header>

        <div ref={scrollRef} className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="mx-auto flex max-w-3xl flex-col gap-6 px-6 py-8">
            {!selectedId ? (
              <div className="flex flex-col items-center justify-center gap-6 py-20">
                <div className="flex h-14 w-14 items-center justify-center rounded-full border-2 border-[var(--primary)]/30 bg-[var(--primary)]/10">
                  <MessageSquare className="h-6 w-6 text-[var(--primary)]" />
                </div>
                <div className="space-y-2 text-center">
                  <h1 className="display-sm">What can Muse help you with?</h1>
                  <p className="body-muted">Select a conversation or start something new</p>
                </div>
                <div className="flex flex-wrap justify-center gap-2 mt-4">
                  {SUGGESTION_CHIPS.map((chip) => (
                    <button
                      key={chip}
                      onClick={() => handleChip(chip)}
                      className="border border-[var(--border)] px-4 py-2 text-[10px] font-medium text-[var(--ink-500)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-all duration-200 rounded-[var(--radius)] bg-white"
                    >
                      {chip}
                    </button>
                  ))}
                </div>
              </div>
            ) : isLoadingConversation ? (
              <div className="space-y-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className={cn(`h-16 rounded-[var(--radius-lg)] bg-[var(--paper-200)] animate-pulse`, i % 2 === 1 ? "ml-auto max-w-[70%]" : "")} />
                ))}
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-6 py-16 text-center">
                <div className="space-y-3">
                  <p className="display-sm">Ask about strategy, campaigns, or your Foundation</p>
                  <p className="body-muted">Muse classifies your message and routes it to the right handler</p>
                </div>
                <div className="flex flex-wrap justify-center gap-2">
                  {SUGGESTION_CHIPS.map((chip) => (
                    <button
                      key={chip}
                      onClick={() => {
                        setInput(chip);
                        textareaRef.current?.focus();
                      }}
                      className="border border-[var(--border)] px-4 py-2 text-[10px] font-medium text-[var(--ink-500)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-all duration-200 rounded-[var(--radius)] bg-white"
                    >
                      {chip}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <GsapBridge stagger className="flex flex-col gap-6">
                {messages.map((msg) => (
                  <div key={msg.id}>
                    <MessageBubble message={msg} />
                    {msg.route === "council" && msg.role === "assistant" && pendingSessionId && (
                      <Link
                        href={`/council/${pendingSessionId}` as Route}
                        className="mt-2 ml-4 inline-flex items-center gap-2 mono-label text-[var(--primary)] link-underline"
                      >
                        → View Council Session <ArrowRightIcon className="h-3 w-3" />
                      </Link>
                    )}
                    {msg.route === "foundation" && msg.role === "assistant" && (
                      <Link
                        href="/foundation"
                        className="mt-2 ml-4 inline-flex items-center gap-2 mono-label text-[var(--ink-500)] link-underline"
                      >
                        → Update in Foundation <ArrowRightIcon className="h-3 w-3" />
                      </Link>
                    )}
                  </div>
                ))}
              </GsapBridge>
            )}
          </div>
        </div>

        <footer className="border-t border-[var(--border)] p-4 bg-[var(--card)]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="mx-auto flex max-w-3xl items-end gap-3"
          >
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask Muse… (Enter to send, Shift+Enter for newline)"
              rows={1}
              disabled={!selectedId || sendMessage.isPending}
              className="flex-1 resize-none rounded-[var(--radius)] border border-[var(--border)] bg-white px-4 py-3 text-sm text-[var(--ink-900)] placeholder:text-[var(--ink-300)] focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--primary)]/20 disabled:opacity-50 transition-all"
              style={{ minHeight: 48, maxHeight: 160, overflowY: "auto" }}
            />
            <Button
              type="submit"
              disabled={!input.trim() || !selectedId || sendMessage.isPending}
              className="h-12 w-12 shrink-0 p-0"
            >
              {sendMessage.isPending ? (
                <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
          {!selectedId && (
            <p className="mt-2 text-center mono-label">
              Select or create a conversation to start chatting
            </p>
          )}
        </footer>
      </main>
    </div>
  );
}
