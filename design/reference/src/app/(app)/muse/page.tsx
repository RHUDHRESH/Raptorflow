"use client";

import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  Send, 
  Plus, 
  MessageSquare, 
  MapPin, 
  X, 
  Terminal, 
  Loader2, 
  Sparkles,
  Search,
  History
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useMuseSocket, type Message } from "@/hooks/use-muse-socket";
import { useFoundationStore } from "@/state/foundation-store";
import { cn } from "@/lib/cn";
import { formatDistanceToNow } from "date-fns";

/**
 * Muse Page
 * 
 * RaptorFlow's conversational intelligence interface. Routes messages 
 * to specialized agents based on user intent and current workspace context.
 */
export default function MusePage() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const { sectionData } = useFoundationStore();
  const strategistName = sectionData.primary_goal?.strategistName || "Strategist";

  // Socket & Chat State
  const { 
    messages, 
    setMessages, 
    isStreaming, 
    sessionId, 
    setSessionId, 
    sendMessage,
    isConnected 
  } = useMuseSocket();

  const [inputValue, setInputValue] = useState("");
  const [context, setContext] = useState<{ label: string; id: string } | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // ─── API Queries ─────────────────────────────────────────────

  const { data: history, isLoading: historyLoading } = useQuery<any[]>({
    queryKey: ["muse", "history"],
    queryFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/muse/history`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.json();
    }
  });

  const startConversation = useMutation({
    mutationFn: async () => {
      const token = await getToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/muse/conversation`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.json();
    },
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setMessages([]);
    }
  });

  // ─── Effects ──────────────────────────────────────────────────

  // Auto-scroll on new messages or tokens
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Handle Input submission
  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputValue.trim() || isStreaming || !isConnected) return;

    if (!sessionId) {
      startConversation.mutate();
      // The sendMessage call will be handled by a subsequent effect or manual wait
      // For this MVP, we assume the session is pre-started or handled by the hook
    }

    sendMessage(inputValue, context ? { current_route: "/app/muse", campaign_id: context.id } : undefined);
    setInputValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // ─── Components ──────────────────────────────────────────────

  const starterChips = [
    "What should I post this week?",
    "How is my campaign doing?",
    "What are my competitors up to?",
    "Write me a LinkedIn post"
  ];

  return (
    <div className="flex h-screen bg-[#121212] overflow-hidden">
      {/* ─── Sidebar ─────────────────────────────────────────── */}
      <aside className="w-72 bg-[#0f0f0f] border-r border-zinc-800 flex flex-col shrink-0">
        <div className="p-4 border-b border-zinc-900">
          <Button 
            onClick={() => startConversation.mutate()}
            disabled={startConversation.isPending}
            className="w-full bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs uppercase tracking-widest h-10"
          >
            {startConversation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
            New Conversation
          </Button>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            <div className="px-3 py-2 text-[9px] font-bold text-zinc-600 uppercase tracking-widest flex items-center gap-2">
              <History className="w-3 h-3" /> Past Conversations
            </div>
            {historyLoading ? (
              <div className="p-4 space-y-2">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : history?.length === 0 ? (
              <p className="p-6 text-center text-xs text-zinc-600 italic">No past conversations</p>
            ) : (
              history?.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => setSessionId(conv.id)}
                  className={cn(
                    "w-full text-left px-3 py-2.5 rounded-lg transition-colors group",
                    sessionId === conv.id ? "bg-[#1a1a1a]" : "hover:bg-[#161616]"
                  )}
                >
                  <p className="text-xs text-zinc-300 font-medium truncate mb-1">
                    {conv.preview || "New Session"}
                  </p>
                  <span className="text-[9px] text-zinc-600 uppercase font-mono">
                    {formatDistanceToNow(new Date(conv.updated_at))} ago
                  </span>
                </button>
              ))
            )}
          </div>
        </ScrollArea>
      </aside>

      {/* ─── Main Chat Area ───────────────────────────────────── */}
      <main className="flex-1 flex flex-col relative">
        {/* Header */}
        <header className="h-14 border-b border-zinc-800 px-6 flex items-center justify-between bg-[#121212]/80 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
            <span className="text-base font-medium text-white tracking-tight">Muse</span>
            <div className="flex items-center gap-1.5 px-2 py-0.5 bg-zinc-900 border border-zinc-800 rounded-full">
              <span className={cn("w-1.5 h-1.5 rounded-full", isConnected ? "bg-green-500" : "bg-red-500 animate-pulse")} />
              <span className="text-[9px] uppercase font-mono text-zinc-500">{isConnected ? "Live" : "Connecting"}</span>
            </div>
          </div>
          {context && (
             <Badge variant="outline" className="bg-amber-500/10 border-amber-500/20 text-amber-500 text-[10px] gap-2 py-1 px-3">
                <MapPin className="w-3 h-3" />
                In context: {context.label}
                <X className="w-3 h-3 cursor-pointer hover:text-white" onClick={() => setContext(null)} />
             </Badge>
          )}
        </header>

        {/* Message List */}
        <ScrollArea className="flex-1" ref={scrollRef}>
          <div className="max-w-3xl mx-auto px-6 py-12 flex flex-col gap-8 min-h-full">
            {messages.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="text-center space-y-4">
                  <div className="w-16 h-16 bg-amber-500/10 border border-amber-500/20 rounded-full flex items-center justify-center text-3xl text-amber-500 font-serif mx-auto shadow-2xl shadow-amber-500/5">
                    {strategistName.charAt(0)}
                  </div>
                  <div className="space-y-1">
                    <h2 className="text-xl text-white font-bold tracking-tight">Ask anything about your marketing.</h2>
                    <p className="text-sm text-zinc-500 font-light">The Council is standing by to route your request.</p>
                  </div>
                </div>

                <div className="flex flex-wrap justify-center gap-2 max-w-lg">
                  {starterChips.map((chip) => (
                    <button
                      key={chip}
                      onClick={() => { setInputValue(chip); handleSubmit(); }}
                      className="bg-[#1a1a1a] rounded-full border border-zinc-800 px-4 py-2 text-xs text-zinc-400 hover:text-white hover:border-zinc-600 hover:bg-[#222222] transition-all cursor-pointer whitespace-nowrap"
                    >
                      {chip}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div 
                  key={msg.id} 
                  className={cn(
                    "flex flex-col gap-2",
                    msg.role === "user" ? "items-end" : "items-start"
                  )}
                >
                  <div className={cn(
                    "px-4 py-3 rounded-2xl text-sm leading-relaxed max-w-[85%]",
                    msg.role === "user" 
                      ? "bg-amber-500/10 border border-amber-500/20 text-white rounded-tr-none" 
                      : "bg-[#1a1a1a] border border-zinc-800 text-zinc-200 rounded-tl-none pr-6"
                  )}>
                    {msg.content}
                    {msg.isStreaming && (
                      <span className="ml-1 inline-block w-1 h-4 bg-amber-500 animate-pulse align-middle" />
                    )}
                  </div>
                  {msg.role === "assistant" && (
                    <div className="flex items-center gap-2 mt-1 ml-1">
                       <div className="w-5 h-5 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-[8px] font-bold text-zinc-500 uppercase">
                          {msg.agentKey?.charAt(0) || "RF"}
                       </div>
                       <span className="text-[10px] text-zinc-500 font-medium">
                          {msg.isStreaming ? (
                            <span className="flex items-center gap-1">
                               <span className="animate-pulse">●</span> typing...
                            </span>
                          ) : (
                            `Written by ${msg.agentName || "Strategist"}`
                          )}
                       </span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </ScrollArea>

        {/* Input Bar */}
        <footer className="p-4 bg-[#121212] border-t border-zinc-900 pb-8">
          <div className="max-w-3xl mx-auto space-y-4">
             <div className="relative group">
               <textarea
                 ref={inputRef}
                 value={inputValue}
                 onChange={(e) => setInputValue(e.target.value)}
                 onKeyDown={handleKeyDown}
                 placeholder="Ask anything about your marketing..."
                 rows={1}
                 style={{ scrollbarWidth: 'none' }}
                 className="w-full bg-[#1e1e1e] border border-zinc-800 rounded-2xl px-5 py-4 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/20 transition-all resize-none overflow-hidden min-h-[56px] pr-14"
                 onInput={(e) => {
                   const target = e.target as HTMLTextAreaElement;
                   target.style.height = "auto";
                   target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
                 }}
               />
               <Button 
                 onClick={() => handleSubmit()}
                 disabled={!inputValue.trim() || isStreaming || !isConnected}
                 className={cn(
                   "absolute right-2 bottom-2 w-10 h-10 rounded-xl p-0 transition-all",
                   inputValue.trim() && !isStreaming ? "bg-amber-500 text-black hover:bg-amber-400" : "bg-zinc-800 text-zinc-600 cursor-not-allowed"
                 )}
               >
                 {isStreaming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
               </Button>
             </div>
             <p className="text-[9px] text-center text-zinc-600 uppercase font-mono tracking-widest">
                Protected by RaptorFlow Privacy Shield · {strategistName} is monitoring
             </p>
          </div>
        </footer>
      </main>
    </div>
  );
}
