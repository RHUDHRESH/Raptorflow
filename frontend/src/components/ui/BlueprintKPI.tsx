"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT KPI — Technical Key Performance Indicators
   Features:
   - Specs-style layout
   - Trend indicators
   - Technical labeling
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintKPIProps {
    label: string;
    value: string | number;
    code?: string;
    unit?: string;
    trend?: "up" | "down" | "neutral";
    trendValue?: string;
    figure?: string;
    className?: string;
}

export function BlueprintKPI({
    label,
    value,
    code,
    unit,
    trend,
    trendValue,
    figure,
    className,
}: BlueprintKPIProps) {
    const trendColors = {
        up: "text-[var(--success)]",
        down: "text-[var(--error)]",
        neutral: "text-[var(--muted)]",
    };

    const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;

    return (
        <div className={cn(
            "relative p-5 rounded-[var(--radius-md)] border border-[var(--border)]",
            "bg-[var(--paper)] ink-bleed-sm group",
            className
        )}>
            {/* Blueprint grid */}
            <div className="absolute inset-0 blueprint-grid opacity-20 rounded-[var(--radius-md)]" />

            {/* Corner marks */}
            <div className="absolute -top-px -left-px w-3 h-3 border-t border-l border-[var(--blueprint)]" />
            <div className="absolute -bottom-px -right-px w-3 h-3 border-b border-r border-[var(--blueprint)]" />

            {/* Figure annotation */}
            {figure && (
                <div className="absolute -top-6 left-0 flex items-center gap-2">
                    <span className="font-technical text-[var(--blueprint)]">{figure}</span>
                    <div className="h-px w-4 bg-[var(--blueprint-line)]" />
                </div>
            )}

            {/* Content */}
            <div className="relative space-y-3">
                {/* Label row */}
                <div className="flex items-center gap-2">
                    <span className="font-technical text-[var(--muted)]">{label.toUpperCase()}</span>
                    {code && (
                        <>
                            <div className="h-3 w-px bg-[var(--blueprint-line)]" />
                            <span className="font-technical text-[var(--blueprint)]">{code}</span>
                        </>
                    )}
                </div>

                {/* Value */}
                <div className="flex items-end gap-2">
                    <span className="text-4xl font-serif text-[var(--ink)]">{value}</span>
                    {unit && (
                        <span className="font-technical text-[var(--muted)] mb-1">{unit}</span>
                    )}
                </div>

                {/* Trend */}
                {trend && (
                    <div className={cn("flex items-center gap-1", trendColors[trend])}>
                        <TrendIcon size={14} strokeWidth={1.5} />
                        {trendValue && <span className="font-technical">{trendValue}</span>}
                    </div>
                )}
            </div>

            {/* Measurement ticks at bottom */}
            <div className="absolute bottom-0 left-5 right-5 flex justify-between opacity-0 group-hover:opacity-100 transition-opacity">
                {[...Array(6)].map((_, i) => (
                    <div key={i} className={cn("w-px", i % 2 === 0 ? "h-2 bg-[var(--blueprint)]" : "h-1 bg-[var(--blueprint-line)]")} />
                ))}
            </div>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   KPI GRID
   ══════════════════════════════════════════════════════════════════════════════ */

interface KPIGridProps {
    children: React.ReactNode;
    columns?: 2 | 3 | 4;
    className?: string;
}

export function KPIGrid({ children, columns = 4, className }: KPIGridProps) {
    const gridCols = {
        2: "grid-cols-2",
        3: "grid-cols-3",
        4: "grid-cols-4",
    };

    return (
        <div className={cn("grid gap-4", gridCols[columns], className)}>
            {children}
        </div>
    );
}

export default BlueprintKPI;
