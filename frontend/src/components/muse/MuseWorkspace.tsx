"use client";

import { useState, useEffect } from "react";
import { MuseAsset } from "@/stores/museStore";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { Copy, PenTool, Check } from "lucide-react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE WORKSPACE
   The Editor Canvas. Minimalist. Focus-driven.
   ══════════════════════════════════════════════════════════════════════════════ */

interface MuseWorkspaceProps {
    asset: MuseAsset | null;
    onUpdate: (content: string) => void;
    onClose?: () => void;
}

export function MuseWorkspace({ asset, onUpdate, onClose }: MuseWorkspaceProps) {
    const [content, setContent] = useState("");
    const [isDirty, setIsDirty] = useState(false);

    // Sync local state when asset changes
    useEffect(() => {
        if (asset) {
            setContent(asset.content);
            setIsDirty(false);
        } else {
            setContent("");
        }
    }, [asset]);

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const newContent = e.target.value;
        setContent(newContent);
        setIsDirty(newContent !== asset?.content);
    };

    const handleSave = () => {
        if (!asset) return;
        onUpdate(content);
        setIsDirty(false);
    };

    if (!asset) {
        return (
            <div className="h-full flex flex-col items-center justify-center bg-[var(--paper)] text-[var(--muted)]">
                <div className="text-center space-y-4">
                    <p className="font-serif text-2xl text-[var(--ink)] italic">Tabula Rasa</p>
                    <p className="text-[11px] font-mono uppercase tracking-widest max-w-xs mx-auto leading-relaxed">
                        Select an artifact to examine<br />or command Muse to generate.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col bg-[var(--paper)] border-l border-[var(--border)]">
            {/* Toolbar - Extremely Minimal */}
            <div className="h-14 flex items-center justify-between px-8 bg-[var(--paper)] sticky top-0 z-10 border-b border-[var(--border)]">
                <div className="flex flex-col">
                    <span className="text-[10px] font-mono uppercase tracking-widest text-[var(--muted)] truncate max-w-[200px]">
                        {asset.type} // {asset.id}
                    </span>
                </div>

                <div className="flex items-center gap-4">
                    <span className={cn(
                        "text-[10px] font-mono transition-opacity duration-300",
                        isDirty ? "opacity-100 text-[var(--ink)]" : "opacity-0"
                    )}>
                        UNSAVED
                    </span>
                    <button
                        onClick={handleSave}
                        disabled={!isDirty}
                        className={cn(
                            "text-[11px] uppercase font-bold tracking-wider transition-colors",
                            isDirty ? "text-[var(--blueprint)] hover:text-[var(--ink)]" : "text-[var(--muted)] cursor-not-allowed"
                        )}
                    >
                        Save
                    </button>
                </div>
            </div>

            {/* Editor Canvas */}
            <div className="flex-1 relative overflow-hidden flex flex-col">
                <div className="px-8 pt-8 pb-4">
                    <h1 className="font-serif text-3xl text-[var(--ink)]">{asset.title}</h1>
                </div>
                <textarea
                    value={content}
                    onChange={handleChange}
                    className="flex-1 w-full px-8 py-4 resize-none bg-[var(--paper)] text-[var(--ink)] font-mono text-[13px] leading-relaxed focus:outline-none"
                    placeholder="Start typing..."
                    spellCheck={false}
                />
            </div>
        </div>
    );
}
