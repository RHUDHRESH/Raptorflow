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
        up: "text-[#2D5A3D]",
        down: "text-[#8B3A3A]",
        neutral: "text-[#9D9F9F]",
    };

    const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;

    return (
        <div className={cn(
            "relative p-5 rounded-md border border-[#C0C1BE]",
            "bg-[#FFFEF9] shadow-ink-sm group",
            className
        )}>
            {/* Blueprint grid */}
            <div className="absolute inset-0 bg-grid-blueprint opacity-20 rounded-md" />

            {/* Corner marks */}
            <div className="absolute -top-px -left-px w-3 h-3 border-t border-l border-[#3A5A7C]" />
            <div className="absolute -bottom-px -right-px w-3 h-3 border-b border-r border-[#3A5A7C]" />

            {/* Figure annotation */}
            {figure && (
                <div className="absolute -top-6 left-0 flex items-center gap-2">
                    <span className="font-mono text-[10px] tracking-widest text-[#3A5A7C]">{figure}</span>
                    <div className="h-px w-4 bg-[#C0C1BE]/50" />
                </div>
            )}

            {/* Content */}
            <div className="relative space-y-3">
                {/* Label row */}
                <div className="flex items-center gap-2">
                    <span className="font-mono text-[10px] tracking-widest text-[#9D9F9F]">{label.toUpperCase()}</span>
                    {code && (
                        <>
                            <div className="h-3 w-px bg-[#C0C1BE]/50" />
                            <span className="font-mono text-[10px] tracking-widest text-[#3A5A7C]">{code}</span>
                        </>
                    )}
                </div>

                {/* Value */}
                <div className="flex items-end gap-2">
                    <span className="text-4xl font-serif text-[#2D3538]">{value}</span>
                    {unit && (
                        <span className="font-mono text-[10px] text-[#9D9F9F] mb-1">{unit}</span>
                    )}
                </div>

                {/* Trend */}
                {trend && (
                    <div className={cn("flex items-center gap-1", trendColors[trend])}>
                        <TrendIcon size={14} strokeWidth={1.5} />
                        {trendValue && <span className="font-mono text-[10px] tracking-wide">{trendValue}</span>}
                    </div>
                )}
            </div>

            {/* Measurement ticks at bottom */}
            <div className="absolute bottom-0 left-5 right-5 flex justify-between opacity-0 group-hover:opacity-100 transition-opacity">
                {[...Array(6)].map((_, i) => (
                    <div key={i} className={cn("w-px", i % 2 === 0 ? "h-2 bg-[#3A5A7C]" : "h-1 bg-[#C0C1BE]")} />
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
