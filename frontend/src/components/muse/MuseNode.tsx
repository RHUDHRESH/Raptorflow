"use client";

import { motion } from "framer-motion";
import { MuseAsset } from "@/stores/museStore";
import { cn } from "@/lib/utils";
import { FileText, GripHorizontal } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   MUSE NODE (TECHNICAL)
   A precise block of intelligence.
   ══════════════════════════════════════════════════════════════════════════════ */

interface MuseNodeProps {
    asset: MuseAsset;
    x: number;
    y: number;
    isSelected: boolean;
    onSelect: () => void;
}

export function MuseNode({ asset, x, y, isSelected, onSelect }: MuseNodeProps) {
    return (
        <motion.div
            drag
            dragMomentum={false}
            initial={{ opacity: 0, scale: 0.9, x, y }}
            animate={{ opacity: 1, scale: 1, x, y }}
            whileDrag={{ scale: 1.05, cursor: "grabbing", zIndex: 100 }}
            whileHover={{ scale: 1.01, zIndex: 50 }}
            onClick={(e) => { e.stopPropagation(); onSelect(); }}
            className={cn(
                "absolute w-[280px] bg-[var(--paper)] shadow-lg cursor-grab overflow-hidden transition-all duration-200",
                // Selection Ring
                isSelected
                    ? "ring-2 ring-[var(--blueprint)] ring-offset-2 ring-offset-[var(--paper)] shadow-2xl"
                    : "ring-1 ring-[var(--border)] hover:ring-[var(--ink-muted)]"
            )}
            style={{ borderRadius: '2px' }} // Sharp technical corners
        >
            {/* Grip / Header */}
            <div className={cn(
                "h-6 flex items-center px-2 select-none border-b border-[var(--border-subtle)]",
                isSelected ? "bg-[var(--blueprint)]" : "bg-[var(--surface)]"
            )}>
                <div className={cn(
                    "w-1.5 h-1.5 rounded-full mr-2",
                    isSelected ? "bg-white" : "bg-[var(--blueprint)]"
                )} />
                <span className={cn(
                    "text-[9px] font-mono uppercase tracking-widest truncate",
                    isSelected ? "text-white" : "text-[var(--ink-muted)]"
                )}>
                    {asset.type} // {asset.id.slice(-4)}
                </span>
                <div className="ml-auto">
                    <GripHorizontal size={12} className={isSelected ? "text-white/50" : "text-[var(--border)]"} />
                </div>
            </div>

            {/* Content */}
            <div className="p-4 bg-[var(--paper)]">
                <h3 className="font-bold text-sm text-[var(--ink)] mb-2 leading-tight">
                    {asset.title}
                </h3>
                <div className="h-px w-8 bg-[var(--blueprint)]/50 mb-3" />
                <p className="text-[11px] text-[var(--ink-secondary)] line-clamp-4 font-mono leading-relaxed opacity-80">
                    {asset.content}
                </p>
            </div>

            {/* Ports */}
            {isSelected && (
                <>
                    {/* Top */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-[var(--paper)] border border-[var(--blueprint)] rounded-full hover:bg-[var(--blueprint)] transition-colors" />
                    {/* Bottom */}
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 bg-[var(--paper)] border border-[var(--blueprint)] rounded-full hover:bg-[var(--blueprint)] transition-colors" />
                    {/* Right */}
                    <div className="absolute top-1/2 right-0 translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-[var(--paper)] border border-[var(--blueprint)] rounded-full hover:bg-[var(--blueprint)] transition-colors" />
                    {/* Left */}
                    <div className="absolute top-1/2 left-0 -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-[var(--paper)] border border-[var(--blueprint)] rounded-full hover:bg-[var(--blueprint)] transition-colors" />
                </>
            )}
        </motion.div>
    );
}
