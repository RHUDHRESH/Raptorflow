"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, Sparkles, User, ArrowRight, StopCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { MuseAsset } from "@/stores/museStore";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE CHAT — PAPER TERMINAL
   Minimalist, high-focus chat interface.
   ══════════════════════════════════════════════════════════════════════════════ */

interface Message {
    id: string;
    type: 'user' | 'bot';
    content: string;
    asset?: MuseAsset;
    suggestions?: string[];
    timestamp: number;
}

interface MuseChatProps {
    messages: Message[];
    isThinking: boolean;
    onSendMessage: (text: string) => void;
    onAssetSelect: (asset: MuseAsset) => void;
}

export function MuseChat({ messages, isThinking, onSendMessage, onAssetSelect }: MuseChatProps) {
    const [input, setInput] = useState("");
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isThinking]);

    const handleSubmit = (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim()) return;
        onSendMessage(input);
        setInput("");
    };

    return (
        <div className="flex-1 flex flex-col h-full bg-[var(--paper)]">
            {/* Chat Stream */}
            <div className="flex-1 overflow-y-auto p-8 space-y-8">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center opacity-40">
                        <Sparkles size={48} className="text-[var(--blueprint)] mb-4" />
                        <h2 className="font-serif text-2xl text-[var(--ink)]">Muse Engine Ready</h2>
                        <p className="font-mono text-sm text-[var(--muted)] mt-2">AWAITING INPUT COMMANDS</p>
                    </div>
                )}

                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={cn(
                            "flex gap-4 max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-2 duration-300",
                            msg.type === 'user' ? "justify-end" : "justify-start"
                        )}
                    >
                        {msg.type === 'bot' && (
                            <div className="w-8 h-8 rounded-none border border-[var(--ink)] bg-[var(--surface)] flex items-center justify-center shrink-0 mt-1">
                                <Bot size={16} className="text-[var(--ink)]" />
                            </div>
                        )}

                        <div className={cn(
                            "max-w-[80%]",
                            msg.type === 'user' ? "bg-[var(--surface)] border border-[var(--border)] p-4 rounded-none" : ""
                        )}>
                            {/* Message Content */}
                            <div className={cn(
                                "leading-relaxed whitespace-pre-wrap",
                                msg.type === 'user' ? "text-[var(--ink)] text-sm font-medium" : "text-[var(--ink)] text-sm"
                            )}>
                                {msg.content}
                            </div>

                            {/* Generated Asset Card */}
                            {msg.asset && (
                                <div
                                    onClick={() => onAssetSelect(msg.asset!)}
                                    className="mt-4 border border-[var(--blueprint)] bg-[var(--blueprint-light)]/5 p-4 cursor-pointer group hover:bg-[var(--blueprint-light)]/10 transition-colors"
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-2">
                                            <span className="text-[10px] font-mono uppercase bg-[var(--blueprint)] text-white px-1.5 py-0.5">
                                                {msg.asset.type}
                                            </span>
                                            <span className="text-xs font-bold text-[var(--blueprint)]">
                                                {msg.asset.title}
                                            </span>
                                        </div>
                                        <ArrowRight size={14} className="text-[var(--blueprint)] opacity-0 group-hover:opacity-100 transition-opacity" />
                                    </div>
                                    <p className="text-xs text-[var(--ink-secondary)] italic line-clamp-2 border-l-2 border-[var(--blueprint)]/30 pl-3">
                                        "{msg.asset.content}"
                                    </p>
                                </div>
                            )}

                            {/* Suggestions */}
                            {msg.suggestions && (
                                <div className="flex flex-wrap gap-2 mt-4">
                                    {msg.suggestions.map((s, i) => (
                                        <button
                                            key={i}
                                            onClick={() => onSendMessage(s)}
                                            className="px-3 py-1.5 text-xs text-[var(--ink-secondary)] border border-[var(--border)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-colors bg-[var(--paper)]"
                                        >
                                            {s}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        {msg.type === 'user' && (
                            <div className="w-8 h-8 bg-[var(--ink)] text-white flex items-center justify-center shrink-0 mt-1">
                                <User size={16} />
                            </div>
                        )}
                    </div>
                ))}

                {isThinking && (
                    <div className="flex gap-4 max-w-3xl mx-auto">
                        <div className="w-8 h-8 border border-[var(--ink)] flex items-center justify-center shrink-0">
                            <div className="w-1.5 h-1.5 bg-[var(--ink)] animate-ping" />
                        </div>
                        <div className="flex items-center gap-2 text-[var(--muted)] font-mono text-xs mt-2 uppercase tracking-widest">
                            Generating Response...
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} className="h-4" />
            </div>

            {/* Input Area */}
            <div className="p-6 border-t border-[var(--border)] bg-[var(--paper)]">
                <div className="max-w-3xl mx-auto relative">
                    <form onSubmit={handleSubmit} className="relative">
                        <input
                            ref={inputRef}
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Instruct Muse..."
                            className="w-full bg-[var(--surface-subtle)] border-b-2 border-[var(--border)] focus:border-[var(--blueprint)] px-4 py-4 pr-12 text-sm text-[var(--ink)] placeholder:text-[var(--muted)] focus:outline-none transition-colors font-medium"
                            disabled={isThinking}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isThinking}
                            className={cn(
                                "absolute right-3 top-1/2 -translate-y-1/2 p-2 transition-colors",
                                input.trim() ? "text-[var(--blueprint)]" : "text-[var(--muted)]"
                            )}
                        >
                            <Send size={18} />
                        </button>
                    </form>
                    <div className="absolute top-full left-0 mt-2 flex items-center gap-4 text-[10px] text-[var(--muted)] font-mono uppercase tracking-wider">
                        <span>Hit Enter to send</span>
                        <span>/ clears context</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
