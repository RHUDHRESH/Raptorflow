"use client";

import { useState, useRef, useEffect } from "react";
import { useMuseStore, MuseAsset } from "@/stores/museStore";
import { MuseSidebar } from "@/components/muse/MuseSidebar";
import { MuseMessage } from "@/components/muse/MuseMessage";
import { BlueprintModal } from "@/components/ui/BlueprintModal";
import { TemplateEditor } from "@/components/muse/TemplateEditor";
import { ArrowUp, Sparkles, Zap, Brain, Command } from "lucide-react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE V3.1 — QUIET LUXURY EDITION
   Strict grid, no gradients, editorial typography.
   ══════════════════════════════════════════════════════════════════════════════ */

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  asset?: MuseAsset;
  timestamp: number;
}

const generateId = () => Math.random().toString(36).substr(2, 9);

export default function MusePage() {
  const { assets, addAsset } = useMuseStore();
  const [activeAsset, setActiveAsset] = useState<MuseAsset | null>(null);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [reasoningMode, setReasoningMode] = useState<'fast' | 'deep'>('fast');
  const scrollRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'init',
      type: 'bot',
      content: "Muse Core active. Ready for input.",
      timestamp: Date.now()
    }
  ]);

  // Auto-scroll logic
  useEffect(() => {
    const timer = setTimeout(() => {
      scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
    return () => clearTimeout(timer);
  }, [messages, isThinking]);

  const handleSend = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { id: generateId(), type: 'user', content: input, timestamp: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsThinking(true);

    // AI Simulation
    setTimeout(() => {
      setIsThinking(false);
      const lower = userMsg.content.toLowerCase();
      let assetType: MuseAsset['type'] = 'Campaign';

      if (lower.includes('email')) assetType = 'Email';
      if (lower.includes('post') || lower.includes('linkedin')) assetType = 'Social';
      if (lower.includes('video') || lower.includes('script')) assetType = 'Script';

      const newAsset: MuseAsset = {
        id: `GEN-${Date.now()}`,
        title: userMsg.content.length > 30 ? `Draft: ${userMsg.content.substring(0, 30)}...` : `Draft: ${userMsg.content}`,
        type: assetType,
        content: `**Objective**: ${userMsg.content}\n**Strategy**: High-impact engagement.\n\n---\n\n**Draft Content**:\n\nSubject: The truth about scaling.\n\nMost founders get this wrong. They think scaling is about more ads. It's about more trust.\n\n[Rest of content placeholder]...`,
        tags: ["Draft", reasoningMode === 'deep' ? "Deep-Dive" : "Quick"],
        createdAt: new Date().toISOString(),
        source: "Muse"
      };
      addAsset(newAsset);

      const aiMsg: Message = {
        id: generateId(),
        type: 'bot',
        content: "Draft generated. Added to your artifacts.",
        asset: newAsset,
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, aiMsg]);
    }, reasoningMode === 'deep' ? 2500 : 1200);
  };

  const handleNewSession = () => {
    setMessages([{
      id: generateId(),
      type: 'bot',
      content: "Session cleared. Context reset.",
      timestamp: Date.now()
    }]);
  };

  return (
    <div className="h-[calc(100vh-64px)] w-full flex bg-[var(--paper)] overflow-hidden">

      {/* 1. LEFT: MEMORY CORE */}
      <MuseSidebar
        assets={assets}
        onAssetSelect={setActiveAsset}
        onNewChat={handleNewSession}
      />

      {/* 2. RIGHT: INTELLIGENCE FEED */}
      <div className="flex-1 flex flex-col relative bg-[var(--paper)]">

        {/* The Stream */}
        <div className="flex-1 overflow-y-auto px-12 py-8 scroll-smooth">
          <div className="max-w-2xl mx-auto pt-10">
            {messages.map((msg, idx) => (
              <MuseMessage
                key={msg.id}
                message={msg}
                onAssetClick={setActiveAsset}
                isLast={idx === messages.length - 1}
              />
            ))}

            {isThinking && (
              <div className="flex justify-start mb-12 animate-in fade-in pl-0 mt-8 text-[11px] font-mono uppercase tracking-widest text-[var(--muted)]">
                <span className="animate-pulse">Thinking...</span>
              </div>
            )}
            <div ref={scrollRef} className="h-4" />
          </div>
        </div>

        {/* The Input Area - Architectural & Solid */}
        <div className="bg-[var(--paper)] p-6 pb-8 z-20 border-t border-[var(--border)]">
          <div className="max-w-2xl mx-auto relative group">

            {/* Context Toggles - Subtle Text Links */}
            <div className="flex justify-center mb-4 gap-6">
              <button
                onClick={() => setReasoningMode('fast')}
                className={cn(
                  "text-[10px] font-mono uppercase tracking-widest transition-colors",
                  reasoningMode === 'fast' ? "text-[var(--ink)] underline underline-offset-4 decoration-1" : "text-[var(--muted)] hover:text-[var(--ink)]"
                )}
              >
                Standard Mode
              </button>
              <button
                onClick={() => setReasoningMode('deep')}
                className={cn(
                  "text-[10px] font-mono uppercase tracking-widest transition-colors",
                  reasoningMode === 'deep' ? "text-[var(--ink)] underline underline-offset-4 decoration-1" : "text-[var(--muted)] hover:text-[var(--ink)]"
                )}
              >
                Deep Reasoning
              </button>
            </div>

            {/* Main Input */}
            <form onSubmit={handleSend} className="relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={reasoningMode === 'deep' ? "Input strategic query..." : "Input command..."}
                className={cn(
                  "w-full bg-[var(--surface)] border border-[var(--border)] focus:border-[var(--ink)] rounded-none px-4 py-4 pr-14 text-[var(--ink)] placeholder:text-[var(--muted)] focus:outline-none transition-all font-medium text-[14px]",
                )}
                disabled={isThinking}
                autoFocus
              />

              <button
                type="submit"
                disabled={!input.trim() || isThinking}
                className={cn(
                  "absolute right-3 top-3 bottom-3 w-8 flex items-center justify-center transition-all",
                  input.trim()
                    ? "text-[var(--ink)]"
                    : "text-[var(--muted)]"
                )}
              >
                <ArrowUp size={18} strokeWidth={2} />
              </button>
            </form>
            <div className="mt-2 text-center">
              <span className="text-[9px] text-[var(--muted)] font-mono uppercase tracking-widest">
                Muse AI v3.1 // {reasoningMode === 'deep' ? 'Deep' : 'Fast'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Editor Modal */}
      <BlueprintModal
        isOpen={!!activeAsset}
        onClose={() => setActiveAsset(null)}
        title="Muse Editor"
        size="xl"
        code="EDT-01"
      >
        {activeAsset && (
          <TemplateEditor
            initialContent={activeAsset.content}
            onSave={() => setActiveAsset(null)}
            onCancel={() => setActiveAsset(null)}
          />
        )}
      </BlueprintModal>

    </div>
  );
}
