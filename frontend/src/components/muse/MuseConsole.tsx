"use client";

import { useRef, useEffect, useState } from "react";
import { Send, Terminal, Sparkles, ChevronRight, Command } from "lucide-react";
import { cn } from "@/lib/utils";
import { MuseAsset } from "@/stores/museStore";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE CONSOLE
   The "Brain" of the operation. Technical logs, not chat bubbles.
   ══════════════════════════════════════════════════════════════════════════════ */

interface LogEntry {
    id: string;
    type: 'user' | 'system' | 'error';
    content: string;
    timestamp: number;
    relatedAssetId?: string;
}

interface MuseConsoleProps {
    logs: LogEntry[];
    isProcessing: boolean;
    onCommand: (cmd: string) => void;
    onAssetClick: (assetId: string) => void;
}

export function MuseConsole({ logs, isProcessing, onCommand, onAssetClick }: MuseConsoleProps) {
    const [input, setInput] = useState("");
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom of logs
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs, isProcessing]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;
        onCommand(input);
        setInput("");
    };

    return (
        <div className="flex flex-col h-full bg-[var(--surface)] border-r border-[var(--border)] font-mono text-sm">
            {/* Header */}
            <div className="h-12 flex items-center px-4 border-b border-[var(--border)] bg-[var(--paper)]">
                <div className="flex items-center gap-2 text-[var(--muted)]">
                    <Terminal size={14} />
                    <span className="text-[10px] uppercase tracking-widest">System Console</span>
                </div>
            </div>

            {/* Log Stream */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
                {logs.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-[var(--muted)] opacity-50">
                        <Sparkles size={24} className="mb-2" />
                        <p className="text-xs uppercase tracking-wider">Awaiting Input</p>
                    </div>
                )}

                {logs.map((log) => (
                    <div key={log.id} className="group flex items-start gap-3 animate-in fade-in duration-200">
                        {/* Timestamp */}
                        <span className="text-[10px] text-[var(--muted)] mt-0.5 opacity-50 font-mono w-10 shrink-0">
                            {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' })}
                        </span>

                        {/* Line Marker */}
                        <div className={cn(
                            "w-0.5 h-3 mt-1 shrink-0",
                            log.type === 'user' ? "bg-[var(--blueprint)]" :
                                log.type === 'error' ? "bg-[var(--error)]" : "bg-[var(--success)]"
                        )} />

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                            <div className={cn(
                                "break-words leading-relaxed",
                                log.type === 'user' ? "text-[var(--ink)] font-medium" : "text-[var(--ink-secondary)]"
                            )}>
                                {log.type === 'user' && <span className="text-[var(--blueprint)] mr-2">›</span>}
                                {log.content}
                            </div>

                            {/* Actions / Links */}
                            {log.relatedAssetId && (
                                <button
                                    onClick={() => onAssetClick(log.relatedAssetId!)}
                                    className="mt-1 flex items-center gap-1 text-[10px] uppercase text-[var(--blueprint)] hover:underline decoration-[var(--blueprint)]/50 underline-offset-2"
                                >
                                    View Output <ChevronRight size={10} />
                                </button>
                            )}
                        </div>
                    </div>
                ))}

                {isProcessing && (
                    <div className="flex items-center gap-2 pl-14 text-[var(--blueprint)] animate-pulse">
                        <span className="w-1.5 h-4 bg-[var(--blueprint)] block" />
                        <span className="text-xs uppercase tracking-wider">Processing...</span>
                    </div>
                )}
            </div>

            {/* Command Input */}
            <div className="p-4 bg-[var(--paper)] border-t border-[var(--border)]">
                <form onSubmit={handleSubmit} className="relative group">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--blueprint)] pointer-events-none transition-opacity group-focus-within:opacity-100 opacity-50">
                        <ChevronRight size={16} />
                    </span>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Enter command or prompt..."
                        className="w-full bg-[var(--surface-subtle)] border border-[var(--border)] rounded-[2px] py-2.5 pl-8 pr-10 text-sm focus:outline-none focus:border-[var(--blueprint)] focus:bg-[var(--paper)] transition-all placeholder:text-[var(--muted)]"
                        autoFocus
                    />
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 pointer-events-none">
                        <Command size={10} className="text-[var(--muted)]" />
                        <span className="text-[10px] text-[var(--muted)] font-mono">ENTER</span>
                    </div>
                </form>
            </div>
        </div>
    );
}
