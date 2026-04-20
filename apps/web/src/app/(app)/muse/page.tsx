"use client";

import React, { useEffect, useMemo, useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { Loader2, MessageSquare, Plus, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useMuseConversations, useMuseMessages, useSubmitMusePrompt } from "@/hooks/use-muse";

export default function MusePage(): React.ReactElement {
  const [inputValue, setInputValue] = useState("");
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);

  const conversationsQuery = useMuseConversations();
  const submitPrompt = useSubmitMusePrompt();

  const conversations = conversationsQuery.data ?? [];

  useEffect(() => {
    if (!selectedConversationId && conversations.length > 0) {
      setSelectedConversationId(conversations[0].conversationId);
    }
  }, [conversations, selectedConversationId]);

  const messagesQuery = useMuseMessages(selectedConversationId ?? "");
  const messages = useMemo(() => messagesQuery.data ?? [], [messagesQuery.data]);

  const handleSubmit = async (event?: React.FormEvent) => {
    event?.preventDefault();
    if (!inputValue.trim() || submitPrompt.isPending) return;

    const response = await submitPrompt.mutateAsync({
      conversationId: selectedConversationId ?? undefined,
      route: "strategic",
      message: inputValue.trim(),
    });

    if (!selectedConversationId) {
      setSelectedConversationId(response.conversationId);
    }

    setInputValue("");
  };

  const startFreshConversation = () => {
    setSelectedConversationId(null);
    setInputValue("");
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#FBF8F2]">
      <aside className="w-72 shrink-0 border-r border-[#E5DED4] bg-[#FBF8F2]">
        <div className="border-b border-[#D5CBC0] p-4">
          <Button
            onClick={startFreshConversation}
            className="h-10 w-full bg-[#D97757] text-black hover:bg-amber-400"
          >
            <Plus className="mr-2 h-4 w-4" />
            New Conversation
          </Button>
        </div>

        <ScrollArea className="h-[calc(100vh-73px)]">
          <div className="p-2">
            <div className="px-3 py-2 text-[9px] font-bold uppercase tracking-[0.2em] text-[#9A948C]">
              Past Conversations
            </div>

            {conversationsQuery.isLoading ? (
              <div className="space-y-2 p-2">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : conversations.length === 0 ? (
              <p className="px-4 py-8 text-center text-xs text-[#9A948C]">
                No persisted Muse conversations yet.
              </p>
            ) : (
              conversations.map((conversation) => (
                <button
                  key={conversation.conversationId}
                  onClick={() => setSelectedConversationId(conversation.conversationId)}
                  className={`w-full rounded-lg px-3 py-2.5 text-left transition-colors ${
                    selectedConversationId === conversation.conversationId
                      ? "bg-[#FBF8F2]"
                      : "hover:bg-[#F5F0E8]"
                  }`}
                >
                  <div className="truncate text-xs font-medium text-[#4A4540]">
                    {conversation.preview || conversation.route || "Conversation"}
                  </div>
                  <div className="mt-1 text-[10px] uppercase tracking-[0.14em] text-[#6B655E]">
                    {formatDistanceToNow(new Date(conversation.lastMessageAt || conversation.updated_at || Date.now()))} ago
                  </div>
                </button>
              ))
            )}
          </div>
        </ScrollArea>
      </aside>

      <main className="flex flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-[#E5DED4] px-6">
          <div className="flex items-center gap-3">
            <span className="text-base font-medium text-[#2A2622]">Muse</span>
            <Badge variant="outline" className="border-[#E5DED4] text-[10px] uppercase tracking-[0.14em] text-[#6B655E]">
              REST-backed
            </Badge>
          </div>
          <p className="text-[10px] uppercase tracking-[0.14em] text-[#9A948C]">
            Live token streaming is disabled until the backend supports it truthfully.
          </p>
        </header>

        <ScrollArea className="flex-1">
          <div className="mx-auto flex min-h-full max-w-3xl flex-col gap-6 px-6 py-10">
            {messagesQuery.isLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-16 w-3/4" />
                <Skeleton className="ml-auto h-16 w-2/3" />
                <Skeleton className="h-16 w-4/5" />
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-1 flex-col items-center justify-center gap-4 py-20 text-center">
                <div className="rounded-full border border-[#D97757]/20 bg-[#FBE9DE] p-5 text-[#D97757]">
                  <MessageSquare className="h-7 w-7" />
                </div>
                <div className="space-y-2">
                  <h1 className="text-2xl font-semibold tracking-tight text-[#2A2622]">
                    Ask anything about your marketing
                  </h1>
                  <p className="max-w-md text-sm text-[#6B655E]">
                    Muse now uses the persisted backend conversation flow. Send a prompt to create or continue a conversation.
                  </p>
                </div>
              </div>
            ) : (
              messages.map((message: any) => (
                <div
                  key={message.id ?? message.messageId}
                  className={`flex flex-col gap-1 ${
                    message.role === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      message.role === "user"
                        ? "rounded-tr-none border border-[#D97757]/20 bg-[#FBE9DE] text-[#2A2622]"
                        : "rounded-tl-none border border-[#E5DED4] bg-[#FBF8F2] text-[#4A4540]"
                    }`}
                  >
                    {message.content}
                  </div>
                  <div className="text-[10px] uppercase tracking-[0.14em] text-[#9A948C]">
                    {message.role}
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>

        <footer className="border-t border-[#D5CBC0] p-4 pb-8">
          <form onSubmit={handleSubmit} className="mx-auto flex max-w-3xl items-end gap-3">
            <Input
              value={inputValue}
              onChange={(event) => setInputValue(event.target.value)}
              placeholder="Ask Muse about strategy, campaigns, content, or intel."
              className="h-12 border-[#E5DED4] bg-[#FBF8F2] text-[#2A2622] placeholder:text-[#9A948C]"
            />
            <Button
              type="submit"
              disabled={!inputValue.trim() || submitPrompt.isPending}
              className="h-12 min-w-12 bg-[#D97757] px-4 text-black hover:bg-amber-400 disabled:bg-[#E5DED4] disabled:text-[#6B655E]"
            >
              {submitPrompt.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </footer>
      </main>
    </div>
  );
}
