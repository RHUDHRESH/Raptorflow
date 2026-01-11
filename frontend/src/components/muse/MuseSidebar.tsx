"use client";

import { useState } from "react";
import { MuseAsset } from "@/stores/museStore";
import { cn } from "@/lib/utils";
import { History, FileText, Search, MoreHorizontal, MessageSquare, ChevronRight, Plus } from "lucide-react";
import { BlueprintButton } from "@/components/ui/BlueprintButton";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE SIDEBAR (MEMORY CORE)
   Manage Context, History, and Generated Artifacts.
   Quiet Luxury Update: Monochrome, typographic, expensive.
   ══════════════════════════════════════════════════════════════════════════════ */

interface MuseSidebarProps {
    assets: MuseAsset[];
    onAssetSelect: (asset: MuseAsset) => void;
    onNewChat: () => void;
}

export function MuseSidebar({ assets, onAssetSelect, onNewChat }: MuseSidebarProps) {
    const [activeTab, setActiveTab] = useState<'threads' | 'artifacts'>('artifacts');

    return (
        <div className="w-[280px] h-full flex flex-col border-r border-[var(--border)] bg-[var(--paper)]">
            {/* Header */}
            <div className="h-16 flex items-center px-4 border-b border-[var(--border)]">
                <button
                    onClick={onNewChat}
                    className="w-full h-9 flex items-center justify-center gap-2 text-[13px] font-medium text-[var(--ink)] border border-[var(--border)] rounded-[var(--radius-sm)] hover:bg-[var(--surface)] hover:border-[var(--ink)] transition-all"
                >
                    <Plus size={14} />
                    <span>New Session</span>
                </button>
            </div>

            {/* Tabs - Minimalist Text Toggle */}
            <div className="flex border-b border-[var(--border)]">
                <button
                    onClick={() => setActiveTab('threads')}
                    className={cn(
                        "flex-1 py-3 text-[11px] font-mono uppercase tracking-wider transition-colors border-b-2",
                        activeTab === 'threads'
                            ? "text-[var(--ink)] border-[var(--ink)]"
                            : "text-[var(--muted)] border-transparent hover:text-[var(--ink)]"
                    )}
                >
                    Context
                </button>
                <button
                    onClick={() => setActiveTab('artifacts')}
                    className={cn(
                        "flex-1 py-3 text-[11px] font-mono uppercase tracking-wider transition-colors border-b-2",
                        activeTab === 'artifacts'
                            ? "text-[var(--ink)] border-[var(--ink)]"
                            : "text-[var(--muted)] border-transparent hover:text-[var(--ink)]"
                    )}
                >
                    Artifacts
                </button>
            </div>

            {/* Content List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-1">
                {activeTab === 'artifacts' ? (
                    assets.length === 0 ? (
                        <div className="p-4 text-center">
                            <p className="text-[13px] font-serif italic text-[var(--muted)]">Tabula Rasa.</p>
                            <p className="text-[10px] text-[var(--muted)] mt-1">No artifacts utilized yet.</p>
                        </div>
                    ) : (
                        assets.map(asset => (
                            <button
                                key={asset.id}
                                onClick={() => onAssetSelect(asset)}
                                className="w-full flex items-start gap-3 p-3 rounded-none border-b border-[var(--border-subtle)] hover:bg-[var(--surface)] transition-all group text-left last:border-0"
                            >
                                <div className="mt-1 w-1 h-1 bg-[var(--ink)] rounded-full shrink-0 opacity-40 group-hover:opacity-100 transition-opacity" />
                                <div className="flex-1 min-w-0">
                                    <div className="text-[13px] font-medium text-[var(--ink)] truncate group-hover:underline decoration-1 underline-offset-4">
                                        {asset.title}
                                    </div>
                                    <div className="text-[10px] text-[var(--muted)] line-clamp-1 mt-1 font-mono uppercase tracking-wide">
                                        {asset.type}
                                    </div>
                                </div>
                            </button>
                        ))
                    )
                ) : (
                    <div className="p-2 space-y-1">
                        <div className="px-2 py-2 text-[10px] text-[var(--muted)] uppercase font-mono tracking-widest border-b border-[var(--border)] mb-2">
                            Recent Threads
                        </div>
                        {/* Mock Sessions - styled as simple list items */}
                        <button className="w-full flex items-center gap-3 p-2 text-[13px] text-[var(--ink)] hover:text-[var(--ink)] hover:bg-[var(--surface)] transition-colors text-left group">
                            <span className="font-mono text-[var(--muted)] text-[10px] group-hover:text-[var(--ink)]">01</span>
                            <span>Scale-up Q1 Strategy</span>
                        </button>
                        <button className="w-full flex items-center gap-3 p-2 text-[13px] text-[var(--ink)] hover:text-[var(--ink)] hover:bg-[var(--surface)] transition-colors text-left group">
                            <span className="font-mono text-[var(--muted)] text-[10px] group-hover:text-[var(--ink)]">02</span>
                            <span>LinkedIn Content Sprint</span>
                        </button>
                    </div>
                )}
            </div>

            {/* Footer - Minimal Status */}
            <div className="p-4 border-t border-[var(--border)] bg-[var(--paper)]">
                <div className="flex items-center justify-between text-[10px] font-mono text-[var(--muted)] uppercase tracking-wider">
                    <span>Muse Core v3.1</span>
                    <div className="flex items-center gap-1.5">
                        <div className="w-1.5 h-1.5 bg-[var(--success)] rounded-full" />
                        <span className="text-[var(--ink)]">Online</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
