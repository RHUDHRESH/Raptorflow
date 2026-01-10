"use client";

import React from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT DIVIDER — Technical Section Separators
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintDividerProps {
    label?: string;
    code?: string;
    variant?: "solid" | "dashed" | "blueprint";
    className?: string;
}

export function BlueprintDivider({
    label,
    code,
    variant = "solid",
    className,
}: BlueprintDividerProps) {
    if (label || code) {
        return (
            <div className={cn("flex items-center gap-3 py-4", className)}>
                <div className={cn(
                    "flex-1 h-px",
                    variant === "solid" && "bg-[var(--border)]",
                    variant === "dashed" && "border-t border-dashed border-[var(--border)]",
                    variant === "blueprint" && "bg-[var(--blueprint-line)]"
                )} />
                {code && <span className="font-technical text-[var(--blueprint)]">{code}</span>}
                {label && <span className="font-technical text-[var(--muted)]">{label.toUpperCase()}</span>}
                <div className={cn(
                    "flex-1 h-px",
                    variant === "solid" && "bg-[var(--border)]",
                    variant === "dashed" && "border-t border-dashed border-[var(--border)]",
                    variant === "blueprint" && "bg-[var(--blueprint-line)]"
                )} />
            </div>
        );
    }

    return (
        <div className={cn("relative py-4", className)}>
            <div className={cn(
                "h-px",
                variant === "solid" && "bg-[var(--border)]",
                variant === "dashed" && "border-t border-dashed border-[var(--border)]",
                variant === "blueprint" && "bg-[var(--blueprint-line)]"
            )} />
            {variant === "blueprint" && (
                <>
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 border-l border-t border-[var(--blueprint-line)] rotate-45" />
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 border-r border-b border-[var(--blueprint-line)] rotate-45" />
                </>
            )}
        </div>
    );
}

export default BlueprintDivider;
