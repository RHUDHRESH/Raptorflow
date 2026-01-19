"use client";

import React from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT CHART — Technical Data Visualization
   Features:
   - Blueprint grid background
   - Measurement axes
   - Technical styling
   ══════════════════════════════════════════════════════════════════════════════ */

interface DataPoint {
    label: string;
    value: number;
    code?: string;
}

interface BlueprintChartProps {
    data: DataPoint[];
    type?: "bar" | "horizontal" | "line";
    figure?: string;
    title?: string;
    height?: number;
    showLabels?: boolean;
    showValues?: boolean;
    className?: string;
}

export function BlueprintChart({
    data,
    type = "bar",
    figure,
    title,
    height = 200,
    showLabels = true,
    showValues = true,
    className,
}: BlueprintChartProps) {
    const maxValue = Math.max(...data.map((d) => d.value));

    if (type === "horizontal") {
        return (
            <div className={cn("w-full", className)}>
                {/* Header */}
                {(figure || title) && (
                    <div className="flex items-center gap-3 mb-4">
                        {figure && <span className="font-technical text-[var(--blueprint)]">{figure}</span>}
                        {figure && <div className="h-px w-4 bg-[var(--blueprint-line)]" />}
                        {title && <span className="font-technical text-[var(--muted)]">{title.toUpperCase()}</span>}
                    </div>
                )}

                <div className="space-y-3">
                    {data.map((item, i) => {
                        const percentage = (item.value / maxValue) * 100;
                        return (
                            <div key={i} className="space-y-1">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <span className="font-technical text-[10px] text-[var(--muted)] w-4">
                                            {String(i + 1).padStart(2, "0")}
                                        </span>
                                        <span className="text-sm text-[var(--ink)]">{item.label}</span>
                                        {item.code && (
                                            <span className="font-technical text-[9px] text-[var(--blueprint)]">{item.code}</span>
                                        )}
                                    </div>
                                    {showValues && (
                                        <span className="font-technical text-[var(--ink)]">{item.value}</span>
                                    )}
                                </div>
                                <div className="h-2 bg-[var(--canvas)] rounded-full border border-[var(--border-subtle)] overflow-hidden">
                                    <div
                                        className="h-full bg-[var(--blueprint)] rounded-full transition-all duration-500"
                                        style={{ width: `${percentage}%` }}
                                    />
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        );
    }

    // Vertical bar chart
    return (
        <div className={cn("w-full", className)}>
            {/* Header */}
            {(figure || title) && (
                <div className="flex items-center gap-3 mb-4">
                    {figure && <span className="font-technical text-[var(--blueprint)]">{figure}</span>}
                    {figure && <div className="h-px flex-1 bg-[var(--blueprint-line)]" />}
                    {title && <span className="font-technical text-[var(--muted)]">{title.toUpperCase()}</span>}
                </div>
            )}

            {/* Chart container */}
            <div
                className="relative border border-[var(--border)] rounded-[var(--radius-md)] bg-[var(--paper)] p-4 overflow-hidden"
                style={{ height }}
            >
                {/* Blueprint grid */}
                <div className="absolute inset-0 blueprint-grid opacity-30" />

                {/* Y-axis labels */}
                <div className="absolute left-2 top-4 bottom-8 flex flex-col justify-between text-right">
                    {[100, 75, 50, 25, 0].map((tick) => (
                        <span key={tick} className="font-technical text-[8px] text-[var(--muted)]">
                            {Math.round((maxValue * tick) / 100)}
                        </span>
                    ))}
                </div>

                {/* Bars */}
                <div className="relative h-full pl-8 pr-2 flex items-end justify-between gap-2">
                    {data.map((item, i) => {
                        const percentage = (item.value / maxValue) * 100;
                        return (
                            <div key={i} className="flex-1 flex flex-col items-center group">
                                {/* Value on hover */}
                                {showValues && (
                                    <span className="font-technical text-[10px] text-[var(--blueprint)] opacity-0 group-hover:opacity-100 transition-opacity mb-1">
                                        {item.value}
                                    </span>
                                )}
                                {/* Bar */}
                                <div
                                    className="w-full bg-[var(--blueprint)] rounded-t-[var(--radius-xs)] transition-all duration-300 group-hover:bg-[var(--ink)]"
                                    style={{ height: `${percentage}%`, minHeight: 4 }}
                                />
                                {/* Label */}
                                {showLabels && (
                                    <span className="font-technical text-[8px] text-[var(--muted)] mt-2 truncate max-w-full">
                                        {item.code || item.label.slice(0, 3).toUpperCase()}
                                    </span>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Corner marks */}
                <div className="absolute -top-px -left-px w-3 h-3 border-t border-l border-[var(--blueprint)]" />
                <div className="absolute -bottom-px -right-px w-3 h-3 border-b border-r border-[var(--blueprint)]" />
            </div>
        </div>
    );
}

export default BlueprintChart;
