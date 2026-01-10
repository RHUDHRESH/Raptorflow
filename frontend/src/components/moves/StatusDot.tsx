"use client";

import { cn } from "@/lib/utils";
import { BlueprintTooltip } from "@/components/ui/BlueprintTooltip";

/* ══════════════════════════════════════════════════════════════════════════════
   PAPER TERMINAL — StatusDot
   Minimal status indicator with blueprint styling
   ══════════════════════════════════════════════════════════════════════════════ */

export type StatusType = "done" | "in-progress" | "blocked" | "attention" | "idea";
export type Status = StatusType;

interface StatusDotProps {
    status: Status;
    size?: "sm" | "md" | "lg";
    showTooltip?: boolean;
    pulse?: boolean;
    className?: string;
}

const statusConfig: Record<Status, { color: string; label: string; code: string }> = {
    done: { color: "var(--success)", label: "Complete", code: "DONE" },
    "in-progress": { color: "var(--blueprint)", label: "In Progress", code: "PROG" },
    blocked: { color: "var(--error)", label: "Blocked", code: "BLKD" },
    attention: { color: "var(--warning)", label: "Attention", code: "ATTN" },
    idea: { color: "var(--muted)", label: "Idea", code: "IDEA" },
};

const sizeClasses = {
    sm: "h-2 w-2",
    md: "h-2.5 w-2.5",
    lg: "h-3 w-3",
};

export function StatusDot({ status, size = "md", showTooltip = true, pulse = false, className }: StatusDotProps) {
    const config = statusConfig[status];

    const dot = (
        <span
            className={cn(
                "inline-block rounded-full shrink-0 transition-all",
                sizeClasses[size],
                pulse && "animate-pulse",
                className
            )}
            style={{ backgroundColor: config.color }}
            role="status"
            aria-label={config.label}
        />
    );

    if (!showTooltip) return dot;

    return (
        <BlueprintTooltip content={<span className="font-technical">{config.code} — {config.label}</span>}>
            {dot}
        </BlueprintTooltip>
    );
}
