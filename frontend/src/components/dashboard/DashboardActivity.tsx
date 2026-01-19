"use client";

import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import {
    Zap,
    Target,
    FileText,
    Users,
    CheckCircle,
    LucideIcon
} from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   DASHBOARD ACTIVITY — Recent Events Feed
   Quiet Luxury: Simple chronological list, minimal badges, clean typography.
   ══════════════════════════════════════════════════════════════════════════════ */

export interface ActivityItem {
    id: string;
    type: "move" | "campaign" | "cohort" | "asset" | "system";
    title: string;
    description?: string;
    timestamp: string;
    status?: "completed" | "active" | "pending";
    href?: string;
}

interface DashboardActivityProps {
    items: ActivityItem[];
    className?: string;
}

const typeIcons: Record<ActivityItem["type"], LucideIcon> = {
    move: Zap,
    campaign: Target,
    cohort: Users,
    asset: FileText,
    system: CheckCircle,
};

export function DashboardActivity({ items, className }: DashboardActivityProps) {
    const router = useRouter();

    if (items.length === 0) {
        return (
            <section className={cn("space-y-4", className)}>
                <SectionHeader />
                <EmptyActivity />
            </section>
        );
    }

    return (
        <section className={cn("space-y-4", className)}>
            <SectionHeader />

            <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] divide-y divide-[var(--border)]">
                {items.slice(0, 5).map((item) => {
                    const Icon = typeIcons[item.type];

                    return (
                        <div
                            key={item.id}
                            onClick={() => item.href && router.push(item.href)}
                            className={cn(
                                "flex items-start gap-4 p-4 transition-colors",
                                item.href && "cursor-pointer hover:bg-[var(--surface)]"
                            )}
                        >
                            {/* Icon */}
                            <div className="w-8 h-8 rounded-[var(--radius)] bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center flex-shrink-0">
                                <Icon size={14} className="text-[var(--ink-secondary)]" />
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                                <p className="text-sm text-[var(--ink)] font-medium leading-snug">
                                    {item.title}
                                </p>
                                {item.description && (
                                    <p className="text-xs text-[var(--ink-muted)] mt-0.5 line-clamp-1">
                                        {item.description}
                                    </p>
                                )}
                            </div>

                            {/* Meta */}
                            <div className="flex items-center gap-3 flex-shrink-0">
                                {item.status && (
                                    <span
                                        className={cn(
                                            "text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full",
                                            item.status === "completed" &&
                                            "bg-[var(--success-bg)] text-[var(--success)]",
                                            item.status === "active" &&
                                            "bg-[var(--info-bg)] text-[var(--info)]",
                                            item.status === "pending" &&
                                            "bg-[var(--surface)] text-[var(--ink-muted)]"
                                        )}
                                    >
                                        {item.status}
                                    </span>
                                )}
                                <span className="text-[11px] text-[var(--ink-muted)] font-mono">
                                    {item.timestamp}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </section>
    );
}

function SectionHeader() {
    return (
        <div className="flex items-center gap-3">
            <span className="font-technical text-[var(--blueprint)]">02</span>
            <div className="h-px flex-1 bg-[var(--border)]" />
            <span className="font-technical text-[var(--ink-muted)]">
                RECENT ACTIVITY
            </span>
        </div>
    );
}

function EmptyActivity() {
    return (
        <div className="bg-[var(--paper)] border border-dashed border-[var(--border)] rounded-[var(--radius-lg)] p-8 text-center">
            <p className="text-sm text-[var(--ink-muted)]">
                No recent activity. New events will appear here.
            </p>
        </div>
    );
}
