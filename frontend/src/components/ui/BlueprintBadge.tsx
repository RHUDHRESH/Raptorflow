"use client";

import React from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT BADGE — Technical Status Labels
   Features:
   - Technical code styling
   - Multiple variants for status
   - Compact and strong sizes
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintBadgeProps {
    children: React.ReactNode;
    variant?: "default" | "success" | "warning" | "error" | "info" | "blueprint" | "blackbox";
    size?: "xs" | "sm" | "md";
    code?: string;
    dot?: boolean;
    className?: string;
}

export function BlueprintBadge({
    children,
    variant = "default",
    size = "sm",
    code,
    dot = false,
    className,
}: BlueprintBadgeProps) {
    const variants = {
        default: "bg-[var(--canvas)] text-[var(--ink)] border-[var(--border)]",
        success: "bg-[var(--success-light)] text-[var(--success)] border-[var(--success)]/20",
        warning: "bg-[var(--warning-light)] text-[var(--warning)] border-[var(--warning)]/20",
        error: "bg-[var(--error-light)] text-[var(--error)] border-[var(--error)]/20",
        info: "bg-[var(--accent-blue-light)] text-[var(--accent-blue)] border-[var(--accent-blue)]/20",
        blueprint: "bg-[var(--blueprint-light)] text-[var(--blueprint)] border-[var(--blueprint)]/20",
        blackbox: "bg-[var(--ink)] text-[var(--canvas)] border-[var(--ink)]",
    };

    const dotColors = {
        default: "bg-[var(--muted)]",
        success: "bg-[var(--success)]",
        warning: "bg-[var(--warning)]",
        error: "bg-[var(--error)]",
        info: "bg-[var(--accent-blue)]",
        blueprint: "bg-[var(--blueprint)]",
        blackbox: "bg-[var(--canvas)]",
    };

    const sizes = {
        xs: "px-1.5 py-0.5 text-[9px]",
        sm: "px-2 py-0.5 text-[10px]",
        md: "px-3 py-1 text-xs",
    };

    return (
        <span
            className={cn(
                "inline-flex items-center gap-1.5 rounded-[var(--radius-xs)] border font-technical",
                variants[variant],
                sizes[size],
                className
            )}
        >
            {dot && <span className={cn("w-1.5 h-1.5 rounded-full", dotColors[variant])} />}
            {code && <span className="opacity-60">{code}:</span>}
            {children}
        </span>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   STATUS INDICATOR
   ══════════════════════════════════════════════════════════════════════════════ */

interface StatusIndicatorProps {
    status: "active" | "inactive" | "pending" | "error";
    label?: string;
    className?: string;
}

export function StatusIndicator({ status, label, className }: StatusIndicatorProps) {
    const statusConfig = {
        active: { color: "bg-[var(--success)]", label: "ACTIVE" },
        inactive: { color: "bg-[var(--muted)]", label: "INACTIVE" },
        pending: { color: "bg-[var(--warning)]", label: "PENDING" },
        error: { color: "bg-[var(--error)]", label: "ERROR" },
    };

    const config = statusConfig[status];

    return (
        <div className={cn("flex items-center gap-2", className)}>
            <span className="relative flex h-2 w-2">
                <span className={cn("absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping", config.color)} />
                <span className={cn("relative inline-flex rounded-full h-2 w-2", config.color)} />
            </span>
            <span className="font-technical text-[var(--muted)]">{label || config.label}</span>
        </div>
    );
}

export default BlueprintBadge;
