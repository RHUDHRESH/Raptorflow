"use client";

import { MuseAsset } from "@/stores/museStore";
import { cn } from "@/lib/utils";
import { Copy, ThumbsUp, ArrowRight, User, Terminal } from "lucide-react";
import { useState, useEffect } from "react";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE MESSAGE (EDITORIAL)
   Stream-based interaction. No bubbles. High-end typography.
   ══════════════════════════════════════════════════════════════════════════════ */

interface Message {
    id: string;
    type: 'user' | 'bot';
    content: string;
    asset?: MuseAsset;
    timestamp: number;
}

interface MuseMessageProps {
    message: Message;
    onAssetClick?: (asset: MuseAsset) => void;
    isLast?: boolean;
}

function TypewriterText({ text, speed = 5 }: { text: string; speed?: number }) {
    const [displayedText, setDisplayedText] = useState("");

    useEffect(() => {
        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                setDisplayedText((prev) => prev + text.charAt(i));
                i++;
            } else {
                clearInterval(timer);
            }
        }, speed);
        return () => clearInterval(timer);
    }, [text, speed]);

    return <span className="whitespace-pre-wrap leading-relaxed">{displayedText}</span>;
}

export function MuseMessage({ message, onAssetClick, isLast }: MuseMessageProps) {
    const isUser = message.type === 'user';
    // Only typewriter if it's the very last message and it's from the bot
    const shouldTypewriter = !isUser && isLast;

    if (isUser) {
        return (
            <div className="flex justify-end mb-12 animate-in fade-in slide-in-from-bottom-2 duration-500">
                <div className="flex flex-col items-end gap-2 max-w-xl">
                    <div className="bg-[var(--surface-subtle)] text-[var(--ink)] px-5 py-3 text-[14px] font-medium font-sans border border-[var(--border-subtle)] max-w-full">
                        {message.content}
                    </div>
                </div>
            </div>
        );
    }

    // AI / Editorial Response
    return (
        <div className="flex justify-start mb-16 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="max-w-2xl w-full pl-0">

                {/* 1. Header Marker */}
                <div className="flex items-center gap-3 mb-6 select-none opacity-50 group-hover:opacity-100 transition-opacity">
                    <div className="w-4 h-4 rounded-full bg-[var(--ink)] flex items-center justify-center">
                        <div className="w-1.5 h-1.5 bg-[var(--paper)] rounded-full" />
                    </div>
                    <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-[var(--ink)]">
                        Muse
                    </span>
                </div>

                {/* 2. Editorial Content */}
                <div className="pl-7 border-l border-[var(--border-subtle)] ml-2">
                    <div className="mb-8 text-[15px] text-[var(--ink)] font-serif leading-loose tracking-wide text-pretty">
                        {shouldTypewriter ? (
                            <TypewriterText text={message.content} />
                        ) : (
                            <span className="whitespace-pre-wrap leading-relaxed">{message.content}</span>
                        )}
                    </div>

                    {/* 3. Asset Card (If present) */}
                    {message.asset && (
                        <div className="mb-6 animate-in fade-in slide-in-from-bottom-2 duration-700 delay-300">
                            <div
                                onClick={() => onAssetClick?.(message.asset!)}
                                className="group relative bg-[var(--surface)] border border-[var(--border)] hover:border-[var(--ink)] transition-all cursor-pointer p-0 w-full max-w-lg"
                            >
                                <div className="p-6">
                                    <div className="flex items-baseline justify-between mb-4">
                                        <h3 className="text-lg font-bold text-[var(--ink)] font-serif group-hover:text-[var(--blueprint)] transition-colors">
                                            {message.asset.title}
                                        </h3>
                                        <span className="text-[9px] font-mono text-[var(--muted)] uppercase border border-[var(--border)] px-1.5 py-0.5 rounded-sm">
                                            {message.asset.type}
                                        </span>
                                    </div>
                                    <p className="text-xs text-[var(--ink-secondary)] line-clamp-2 font-mono opacity-80 mb-6">
                                        {message.asset.content}
                                    </p>
                                    <div className="flex items-center text-[10px] font-bold uppercase tracking-widest text-[var(--blueprint)] opacity-0 group-hover:opacity-100 transition-all transform translate-x-[-10px] group-hover:translate-x-0">
                                        Review Draft <ArrowRight size={12} className="ml-1" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 4. Utility Actions */}
                    <div className="flex gap-4 opacity-0 hover:opacity-100 transition-opacity duration-300">
                        <button className="text-[10px] uppercase font-mono text-[var(--muted)] hover:text-[var(--ink)] flex items-center gap-1">
                            <Copy size={10} /> Copy
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
