"use client";

import React from "react";
import { cn } from "@/lib/utils";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   BLUEPRINT BADGE ΓÇö Technical Status Labels
   Features:
   - Technical code styling
   - Multiple variants for status
   - Compact and strong sizes
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

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
        default: "bg-surface text-ink border-structure",
        success: "bg-[#2D3538] text-[#E8FAF0] border-[#E8FAF0]/20", // Dark ink background with light text for contrast (Quiet Luxury tweak)
        warning: "bg-[#2D3538] text-[#FAF2E8] border-[#FAF2E8]/20",
        error: "bg-[#2D3538] text-[#FAE8E8] border-[#FAE8E8]/20",
        info: "bg-accent-blue/10 text-accent-blue border-accent-blue/20",
        blueprint: "bg-accent-blue/10 text-accent-blue border-accent-blue/20",
        blackbox: "bg-ink text-canvas border-ink",
    };

    // For quiet luxury, "success", "warning" etc are often too bright. 
    // We strictly control them to be subtle or high contrast against ink.
    // However, sticking to the requested change, I will map them to the closest safe tokens.
    // Wait, the user wants "Quiet Luxury" which usually means avoiding standard green/red.
    // I will use tailored colors if available, or just standard ones but muted.
    // Let's stick to standard Tailwind classes if possible, but I don't have success-light defined.
    // Checked tailwind config mentally: I have 'success', 'warning', 'error' in 'functional'.
    // Usage: 'text-functional-success', 'bg-functional-success'. 
    // Let's assume standard names for now to pass build, but I'll use hex for safety if unsure.
    // Actually, I'll use the 'functional' token names I saw in previous context or just standard tailwind colors if I didn't see them.
    // Re-reading tailwind.config.ts summary in context: "functional" colors were defined. containing success, warning, error, info.
    // So I can use `text-functional-success` etc.

    const safeVariants = {
        default: "bg-surface text-ink border border-structure",
        success: "bg-functional-success/10 text-functional-success border border-functional-success/20",
        warning: "bg-functional-warning/10 text-functional-warning border border-functional-warning/20",
        error: "bg-functional-error/10 text-functional-error border border-functional-error/20",
        info: "bg-functional-info/10 text-functional-info border border-functional-info/20",
        blueprint: "bg-accent-blue/10 text-accent-blue border border-accent-blue/20",
        blackbox: "bg-ink text-canvas border border-ink",
    };

    const dotColors = {
        default: "bg-ink-muted",
        success: "bg-functional-success",
        warning: "bg-functional-warning",
        error: "bg-functional-error",
        info: "bg-functional-info",
        blueprint: "bg-accent-blue",
        blackbox: "bg-canvas",
    };

    const sizes = {
        xs: "px-1.5 py-0.5 text-[9px]",
        sm: "px-2 py-0.5 text-[10px]",
        md: "px-3 py-1 text-xs",
    };

    return (
        <span
            className={cn(
                "inline-flex items-center gap-1.5 rounded-xs font-mono tracking-wider uppercase",
                safeVariants[variant],
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

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   STATUS INDICATOR
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

interface StatusIndicatorProps {
    status: "active" | "inactive" | "pending" | "error";
    label?: string;
    className?: string;
}

export function StatusIndicator({ status, label, className }: StatusIndicatorProps) {
    const statusConfig = {
        active: { color: "bg-functional-success", label: "ACTIVE" },
        inactive: { color: "bg-structure", label: "INACTIVE" },
        pending: { color: "bg-functional-warning", label: "PENDING" },
        error: { color: "bg-functional-error", label: "ERROR" },
    };

    const config = statusConfig[status];

    return (
        <div className={cn("flex items-center gap-2", className)}>
            <span className="relative flex h-2 w-2">
                <span className={cn("absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping", config.color)} />
                <span className={cn("relative inline-flex rounded-full h-2 w-2", config.color)} />
            </span>
            <span className="font-mono text-[10px] tracking-widest text-ink-muted">{label || config.label}</span>
        </div>
    );
}

export default BlueprintBadge;
