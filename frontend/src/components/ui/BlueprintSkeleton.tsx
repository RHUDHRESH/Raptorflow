"use client";

import React from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT SKELETON — Loading States
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintSkeletonProps {
    variant?: "text" | "title" | "avatar" | "card" | "row" | "chart";
    lines?: number;
    className?: string;
}

export function BlueprintSkeleton({
    variant = "text",
    lines = 1,
    className,
}: BlueprintSkeletonProps) {
    const baseClass = "bg-[var(--canvas)] animate-pulse rounded-[var(--radius-xs)]";

    if (variant === "text") {
        return (
            <div className={cn("space-y-2", className)}>
                {[...Array(lines)].map((_, i) => (
                    <div
                        key={i}
                        className={cn(baseClass, "h-4", i === lines - 1 && lines > 1 && "w-3/4")}
                    />
                ))}
            </div>
        );
    }

    if (variant === "title") {
        return (
            <div className={cn("space-y-3", className)}>
                <div className={cn(baseClass, "h-8 w-1/3")} />
                <div className={cn(baseClass, "h-4 w-2/3")} />
            </div>
        );
    }

    if (variant === "avatar") {
        return (
            <div className={cn("flex items-center gap-3", className)}>
                <div className={cn(baseClass, "w-10 h-10 rounded-[var(--radius-sm)]")} />
                <div className="space-y-2 flex-1">
                    <div className={cn(baseClass, "h-4 w-24")} />
                    <div className={cn(baseClass, "h-3 w-16")} />
                </div>
            </div>
        );
    }

    if (variant === "card") {
        return (
            <div className={cn(
                "relative p-6 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--paper)]",
                className
            )}>
                {/* Corner marks */}
                <div className="absolute -top-px -left-px w-3 h-3 border-t border-l border-[var(--blueprint-line)]" />
                <div className="absolute -bottom-px -right-px w-3 h-3 border-b border-r border-[var(--blueprint-line)]" />

                <div className="space-y-4">
                    <div className={cn(baseClass, "h-6 w-1/3")} />
                    <div className="space-y-2">
                        <div className={cn(baseClass, "h-4")} />
                        <div className={cn(baseClass, "h-4 w-5/6")} />
                        <div className={cn(baseClass, "h-4 w-2/3")} />
                    </div>
                </div>
            </div>
        );
    }

    if (variant === "row") {
        return (
            <div className={cn("flex items-center gap-4 py-3 border-b border-[var(--border-subtle)]", className)}>
                <div className={cn(baseClass, "w-4 h-4")} />
                <div className={cn(baseClass, "h-4 flex-1")} />
                <div className={cn(baseClass, "h-4 w-20")} />
                <div className={cn(baseClass, "h-4 w-16")} />
            </div>
        );
    }

    if (variant === "chart") {
        return (
            <div className={cn("relative h-48 p-4 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--paper)]", className)}>
                <div className="absolute inset-0 blueprint-grid opacity-20 rounded-[var(--radius-md)]" />
                <div className="relative flex items-end justify-between h-full gap-2">
                    {[40, 65, 35, 80, 55, 70, 45].map((h, i) => (
                        <div
                            key={i}
                            className={cn(baseClass, "flex-1")}
                            style={{ height: `${h}%` }}
                        />
                    ))}
                </div>
            </div>
        );
    }

    return <div className={cn(baseClass, "h-4", className)} />;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SKELETON GROUP
   ══════════════════════════════════════════════════════════════════════════════ */

interface SkeletonGroupProps {
    count: number;
    variant: BlueprintSkeletonProps["variant"];
    className?: string;
}

export function SkeletonGroup({ count, variant, className }: SkeletonGroupProps) {
    return (
        <div className={cn("space-y-4", className)}>
            {[...Array(count)].map((_, i) => (
                <BlueprintSkeleton key={i} variant={variant} />
            ))}
        </div>
    );
}

export default BlueprintSkeleton;
