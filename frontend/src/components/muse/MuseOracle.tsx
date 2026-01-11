"use client";

import { useState } from "react";
import { Sparkles, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE ORACLE
   The center of creation. Not a chat bar. An invocation field.
   ══════════════════════════════════════════════════════════════════════════════ */

interface MuseOracleProps {
    onInvoke: (prompt: string) => void;
    isThinking: boolean;
}

export function MuseOracle({ onInvoke, isThinking }: MuseOracleProps) {
    const [input, setInput] = useState("");
    const [isFocused, setIsFocused] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;
        onInvoke(input);
        setInput("");
    };

    return (
        <div className="absolute bottom-12 left-1/2 -translate-x-1/2 z-50 w-full max-w-2xl px-6">
            <form
                onSubmit={handleSubmit}
                className={cn(
                    "relative group transition-all duration-500",
                    isFocused ? "scale-105" : "scale-100"
                )}
            >
                {/* Glow Effect */}
                <div className={cn(
                    "absolute -inset-1 rounded-full blur-xl transition-opacity duration-500",
                    isFocused ? "bg-gradient-to-r from-[var(--blueprint)]/20 via-[var(--accent)]/20 to-[var(--blueprint)]/20 opacity-100" : "opacity-0"
                )} />

                {/* Main Input Container */}
                <div className={cn(
                    "relative flex items-center bg-[var(--paper)]/80 backdrop-blur-xl border transition-all duration-300 rounded-full",
                    isFocused
                        ? "border-[var(--blueprint)] shadow-2xl shadow-[var(--blueprint)]/10"
                        : "border-[var(--structure)] shadow-lg"
                )}>

                    {/* Icon */}
                    <div className="pl-6 pr-4">
                        {isThinking ? (
                            <div className="w-5 h-5 rounded-full border-2 border-[var(--blueprint)] border-t-transparent animate-spin" />
                        ) : (
                            <Sparkles
                                size={20}
                                className={cn(
                                    "transition-colors duration-300",
                                    isFocused ? "text-[var(--blueprint)]" : "text-[var(--muted)]"
                                )}
                            />
                        )}
                    </div>

                    {/* Input Field */}
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        placeholder="Invoke the Muse..."
                        className="flex-1 py-5 bg-transparent border-none text-lg text-[var(--ink)] placeholder:text-[var(--muted)]/60 focus:outline-none font-serif tracking-wide"
                        disabled={isThinking}
                    />

                    {/* Submit Action */}
                    <div className="pr-2">
                        <button
                            type="submit"
                            disabled={!input.trim() || isThinking}
                            className={cn(
                                "w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300",
                                input.trim()
                                    ? "bg-[var(--ink)] text-[var(--paper)] translate-x-0 opacity-100 rotate-0"
                                    : "bg-transparent text-transparent translate-x-4 opacity-0 -rotate-45 pointer-events-none"
                            )}
                        >
                            <ArrowRight size={18} />
                        </button>
                    </div>
                </div>

                {/* Helper Text */}
                <div className={cn(
                    "absolute top-full left-0 w-full text-center mt-4 transition-opacity duration-300",
                    isFocused ? "opacity-100" : "opacity-0"
                )}>
                    <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-[var(--muted)]">
                        Press Enter to Generate
                    </span>
                </div>
            </form>
        </div>
    );
}
