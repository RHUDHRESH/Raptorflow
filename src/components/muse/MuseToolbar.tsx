"use client";

import { MousePointer2, Type, Image as ImageIcon, Sparkles, Link2, Hand, LayoutGrid, Settings2 } from "lucide-react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE TOOLBAR
   Precision tools for the marketing architect.
   ══════════════════════════════════════════════════════════════════════════════ */

export type CanvasTool = 'select' | 'hand' | 'connect' | 'text' | 'image' | 'ai';

interface MuseToolbarProps {
    activeTool: CanvasTool;
    onToolChange: (tool: CanvasTool) => void;
}

export function MuseToolbar({ activeTool, onToolChange }: MuseToolbarProps) {
    const tools: { id: CanvasTool, icon: any, label: string, shortcut: string }[] = [
        { id: 'select', icon: MousePointer2, label: 'Select', shortcut: 'V' },
        { id: 'hand', icon: Hand, label: 'Pan', shortcut: 'H' },
        { id: 'connect', icon: Link2, label: 'Connect', shortcut: 'C' },
        { id: 'text', icon: Type, label: 'Text', shortcut: 'T' },
        { id: 'ai', icon: Sparkles, label: 'Generate', shortcut: 'AI' },
    ];

    return (
        <div className="absolute top-6 left-6 flex flex-col gap-2 bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-1.5 shadow-xl shadow-[var(--ink)]/5 z-50">
            {tools.map(tool => (
                <button
                    key={tool.id}
                    onClick={() => onToolChange(tool.id)}
                    className={cn(
                        "w-10 h-10 flex items-center justify-center rounded-[var(--radius-md)] transition-all group relative",
                        activeTool === tool.id
                            ? "bg-[var(--ink)] text-[var(--paper)] shadow-sm"
                            : "text-[var(--ink-secondary)] hover:bg-[var(--surface)] hover:text-[var(--ink)]"
                    )}
                >
                    <tool.icon size={18} strokeWidth={activeTool === tool.id ? 2 : 1.5} />

                    {/* Tooltip */}
                    <div className="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-2 py-1 bg-[var(--ink)] text-[var(--paper)] text-[10px] font-medium rounded shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                        {tool.label} <span className="opacity-50 ml-1">({tool.shortcut})</span>
                    </div>
                </button>
            ))}

            <div className="w-full h-px bg-[var(--border)] my-1" />

            <button
                className="w-10 h-10 flex items-center justify-center rounded-[var(--radius-md)] text-[var(--ink-secondary)] hover:bg-[var(--surface)] hover:text-[var(--ink)] transition-colors"
                title="Grid Settings"
            >
                <LayoutGrid size={18} strokeWidth={1.5} />
            </button>
        </div>
    );
}
