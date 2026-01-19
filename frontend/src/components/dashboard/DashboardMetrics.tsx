"use client";

import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus, LucideIcon } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   DASHBOARD METRICS — Minimal Vital Statistics
   Quiet Luxury: Clean borders, no shadows, tabular data display.
   ══════════════════════════════════════════════════════════════════════════════ */

export interface Metric {
    label: string;
    value: string | number;
    trend?: "up" | "down" | "neutral";
    trendValue?: string;
    icon?: LucideIcon;
}

interface DashboardMetricsProps {
    metrics: Metric[];
    className?: string;
}

export function DashboardMetrics({ metrics, className }: DashboardMetricsProps) {
    return (
        <div className={cn("grid grid-cols-2 lg:grid-cols-4 gap-4", className)}>
            {metrics.map((metric, i) => (
                <MetricCard key={i} metric={metric} />
            ))}
        </div>
    );
}

function MetricCard({ metric }: { metric: Metric }) {
    const Icon = metric.icon;

    return (
        <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-5 hover:border-[var(--ink-secondary)] transition-colors">
            {/* Label row */}
            <div className="flex items-center justify-between mb-3">
                <span className="text-[11px] font-mono text-[var(--ink-muted)] uppercase tracking-wider">
                    {metric.label}
                </span>
                {Icon && <Icon size={14} className="text-[var(--ink-muted)]" />}
            </div>

            {/* Value */}
            <div className="text-2xl font-serif text-[var(--ink)] mb-1">
                {metric.value}
            </div>

            {/* Trend indicator */}
            {metric.trend && (
                <div
                    className={cn(
                        "flex items-center gap-1 text-xs font-medium",
                        metric.trend === "up" && "text-[var(--success)]",
                        metric.trend === "down" && "text-[var(--error)]",
                        metric.trend === "neutral" && "text-[var(--ink-muted)]"
                    )}
                >
                    {metric.trend === "up" && <TrendingUp size={12} />}
                    {metric.trend === "down" && <TrendingDown size={12} />}
                    {metric.trend === "neutral" && <Minus size={12} />}
                    <span>{metric.trendValue}</span>
                </div>
            )}
        </div>
    );
}
