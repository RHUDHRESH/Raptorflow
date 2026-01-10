"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { ChevronRight } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT LIST — Technical Numbered Lists
   Features:
   - Technical row numbers
   - Blueprint styling
   - Interactive items
   ══════════════════════════════════════════════════════════════════════════════ */

interface ListItem {
    id: string;
    title: string;
    subtitle?: string;
    code?: string;
    badge?: React.ReactNode;
    onClick?: () => void;
}

interface BlueprintListProps {
    items: ListItem[];
    figure?: string;
    title?: string;
    showNumbers?: boolean;
    className?: string;
}

export function BlueprintList({
    items,
    figure,
    title,
    showNumbers = true,
    className,
}: BlueprintListProps) {
    return (
        <div className={cn("w-full", className)}>
            {/* Header */}
            {(figure || title) && (
                <div className="flex items-center gap-3 mb-4">
                    {figure && <span className="font-technical text-[var(--blueprint)]">{figure}</span>}
                    <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                    {title && <span className="font-technical text-[var(--muted)]">{title.toUpperCase()}</span>}
                    <span className="font-technical text-[var(--blueprint)]">{items.length.toString().padStart(2, "0")}</span>
                </div>
            )}

            {/* List container */}
            <div className="border border-[var(--border)] rounded-[var(--radius-md)] overflow-hidden bg-[var(--paper)]">
                {items.map((item, i) => (
                    <div
                        key={item.id}
                        onClick={item.onClick}
                        className={cn(
                            "flex items-center gap-4 px-4 py-3 border-b border-[var(--border-subtle)] last:border-b-0",
                            "transition-colors duration-150",
                            item.onClick && "cursor-pointer hover:bg-[var(--canvas)] group"
                        )}
                    >
                        {/* Row number */}
                        {showNumbers && (
                            <span className="font-technical text-[var(--muted)] w-6">
                                {String(i + 1).padStart(2, "0")}
                            </span>
                        )}

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-medium text-[var(--ink)] truncate">
                                    {item.title}
                                </span>
                                {item.code && (
                                    <span className="font-technical text-[9px] text-[var(--blueprint)]">
                                        {item.code}
                                    </span>
                                )}
                            </div>
                            {item.subtitle && (
                                <span className="text-xs text-[var(--muted)] truncate block">
                                    {item.subtitle}
                                </span>
                            )}
                        </div>

                        {/* Badge */}
                        {item.badge}

                        {/* Arrow for clickable items */}
                        {item.onClick && (
                            <ChevronRight
                                size={14}
                                strokeWidth={1.5}
                                className="text-[var(--muted)] group-hover:text-[var(--blueprint)] group-hover:translate-x-1 transition-all"
                            />
                        )}
                    </div>
                ))}
            </div>

            {/* Footer measurement */}
            <div className="flex justify-center mt-2">
                <div className="flex items-center gap-px">
                    {[...Array(Math.min(items.length, 10))].map((_, i) => (
                        <div key={i} className={cn("w-px", i % 5 === 0 ? "h-3 bg-[var(--blueprint)]" : "h-1.5 bg-[var(--blueprint-line)]")} />
                    ))}
                </div>
            </div>
        </div>
    );
}

export default BlueprintList;
