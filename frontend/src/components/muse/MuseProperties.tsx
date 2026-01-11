"use client";

import { MuseAsset } from "@/stores/museStore";
import { X, Calendar, Hash, Lock, MoreHorizontal, Trash2 } from "lucide-react";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE PROPERTIES
   Inspector panel for deep object editing.
   ══════════════════════════════════════════════════════════════════════════════ */

interface MusePropertiesProps {
    selectedAsset: MuseAsset | null;
    onClose: () => void;
    onDelete: (id: string) => void;
}

export function MuseProperties({ selectedAsset, onClose, onDelete }: MusePropertiesProps) {
    if (!selectedAsset) return null;

    return (
        <div className="absolute top-6 bottom-6 right-6 w-80 bg-[var(--paper)]/95 backdrop-blur border border-[var(--border)] rounded-[var(--radius-lg)] shadow-2xl z-50 flex flex-col animate-in slide-in-from-right-4 duration-300">
            {/* Header */}
            <div className="h-14 border-b border-[var(--border)] flex items-center justify-between px-4 bg-[var(--surface-subtle)]/50 rounded-t-[var(--radius-lg)]">
                <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--muted)]">
                    PROPERTIES
                </span>
                <button onClick={onClose} className="text-[var(--muted)] hover:text-[var(--ink)]">
                    <X size={16} />
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-5 space-y-6">

                {/* ID Block */}
                <div className="space-y-2">
                    <label className="text-[10px] uppercase font-bold text-[var(--muted)]">Object ID</label>
                    <div className="font-mono text-xs text-[var(--ink-secondary)] bg-[var(--surface)] p-2 rounded border border-[var(--structure)] select-all cursor-text">
                        {selectedAsset.id}
                    </div>
                </div>

                {/* Main Identity */}
                <div className="space-y-3">
                    <div className="space-y-1">
                        <label className="text-[10px] uppercase font-bold text-[var(--muted)]">Title</label>
                        <input
                            type="text"
                            defaultValue={selectedAsset.title}
                            className="w-full bg-[var(--surface)] border-b border-[var(--border)] focus:border-[var(--blueprint)] px-0 py-1.5 text-sm font-medium text-[var(--ink)] focus:outline-none transition-colors"
                        />
                    </div>

                    <div className="space-y-1">
                        <label className="text-[10px] uppercase font-bold text-[var(--muted)]">Type</label>
                        <div className="flex items-center gap-2">
                            <span className={cn(
                                "w-2 h-2 rounded-full",
                                selectedAsset.type === 'Email' ? "bg-blue-400" :
                                    selectedAsset.type === 'Social' ? "bg-pink-400" : "bg-emerald-400"
                            )} />
                            <select className="bg-transparent text-xs text-[var(--ink)] border-none focus:ring-0 cursor-pointer">
                                <option>{selectedAsset.type}</option>
                                <option>Email</option>
                                <option>Social</option>
                                <option>Strategy</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Metadata Grid */}
                <div>
                    <label className="text-[10px] uppercase font-bold text-[var(--muted)] mb-2 block">Metrics</label>
                    <div className="grid grid-cols-2 gap-3">
                        <div className="bg-[var(--surface)] p-3 rounded border border-[var(--structure-subtle)]">
                            <span className="text-[9px] text-[var(--muted)] uppercase block mb-1">Created</span>
                            <span className="text-xs font-mono text-[var(--ink)]">
                                {new Date(selectedAsset.createdAt).toLocaleDateString()}
                            </span>
                        </div>
                        <div className="bg-[var(--surface)] p-3 rounded border border-[var(--structure-subtle)]">
                            <span className="text-[9px] text-[var(--muted)] uppercase block mb-1">Words</span>
                            <span className="text-xs font-mono text-[var(--ink)]">
                                {selectedAsset.content.split(' ').length}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Content Preview */}
                <div className="space-y-2">
                    <label className="text-[10px] uppercase font-bold text-[var(--muted)]">Content Preview</label>
                    <div className="text-xs text-[var(--ink-secondary)] p-3 bg-[var(--surface)] rounded border border-[var(--structure-subtle)] h-32 overflow-y-auto leading-relaxed">
                        {selectedAsset.content}
                    </div>
                    <SecondaryButton size="sm" className="w-full">
                        Open Full Editor
                    </SecondaryButton>
                </div>

            </div>

            {/* Footer */}
            <div className="p-4 border-t border-[var(--border)] bg-[var(--surface-subtle)]/50 rounded-b-[var(--radius-lg)]">
                <button
                    onClick={() => onDelete(selectedAsset.id)}
                    className="w-full flex items-center justify-center gap-2 p-2 text-xs font-medium text-[var(--error)] hover:bg-[var(--error)]/5 rounded transition-colors"
                >
                    <Trash2 size={14} />
                    Delete Object
                </button>
            </div>
        </div>
    );
}
