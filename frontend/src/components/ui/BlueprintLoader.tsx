"use client";

import React from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT LOADER — Technical Loading States
   Features:
   - Spinning blueprint-style loader
   - Skeleton loading with grid pattern
   - Pencil stroke animation
   - Technical measurement indicators
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintLoaderProps {
    size?: "sm" | "md" | "lg";
    variant?: "spinner" | "skeleton" | "pulse";
    className?: string;
    showMeasurements?: boolean;
}

export function BlueprintLoader({
    size = "md",
    variant = "spinner",
    className,
    showMeasurements = false,
}: BlueprintLoaderProps) {
    const sizes = {
        sm: "w-4 h-4",
        md: "w-8 h-8",
        lg: "w-12 h-12",
    };

    const skeletonSizes = {
        sm: "h-4",
        md: "h-6",
        lg: "h-8",
    };

    if (variant === "spinner") {
        return (
            <div className={cn("relative", sizes[size], className)}>
                {/* Outer ring */}
                <div className={cn(
                    "absolute inset-0 border-2 border-[var(--border)] border-t-[var(--blueprint)]",
                    "rounded-full animate-spin"
                )} />

                {/* Inner ring */}
                <div className={cn(
                    "absolute inset-2 border border-[var(--structure-subtle)] border-t-[var(--blueprint)]/50",
                    "rounded-full animate-spin",
                    "animation-delay-150"
                )} />

                {/* Center dot */}
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 bg-[var(--blueprint)] rounded-full animate-pulse" />
                </div>

                {/* Measurement indicators */}
                {showMeasurements && (
                    <>
                        <div className="absolute -top-6 left-1/2 -translate-x-1/2 font-technical text-[8px] text-[var(--blueprint)]">
                            {size === "sm" ? "16px" : size === "md" ? "32px" : "48px"}
                        </div>
                        <div className="absolute -left-8 top-1/2 -translate-y-1/2 font-technical text-[8px] text-[var(--blueprint)] rotate-90">
                            {size === "sm" ? "16px" : size === "md" ? "32px" : "48px"}
                        </div>
                    </>
                )}
            </div>
        );
    }

    if (variant === "skeleton") {
        return (
            <div className={cn("relative", className)}>
                {/* Blueprint grid background */}
                <div className="absolute inset-0 blueprint-grid opacity-30 rounded-[var(--radius-sm)]" />

                {/* Skeleton content */}
                <div className="space-y-3">
                    <div className={cn(
                        "bg-[var(--structure-subtle)] rounded-[var(--radius-sm)] animate-pulse",
                        skeletonSizes[size]
                    )} />
                    <div className={cn(
                        "bg-[var(--structure-subtle)] rounded-[var(--radius-sm)] animate-pulse w-3/4",
                        skeletonSizes[size]
                    )} />
                    <div className={cn(
                        "bg-[var(--structure-subtle)] rounded-[var(--radius-sm)] animate-pulse w-1/2",
                        skeletonSizes[size]
                    )} />
                </div>

                {/* Corner marks */}
                <div className="absolute -top-px -left-px w-3 h-3 border-t border-l border-[var(--blueprint)]/30" />
                <div className="absolute -top-px -right-px w-3 h-3 border-t border-r border-[var(--blueprint)]/30" />
                <div className="absolute -bottom-px -left-px w-3 h-3 border-b border-l border-[var(--blueprint)]/30" />
                <div className="absolute -bottom-px -right-px w-3 h-3 border-b border-r border-[var(--blueprint)]/30" />
            </div>
        );
    }

    if (variant === "pulse") {
        return (
            <div className={cn("relative", className)}>
                {/* Blueprint card container */}
                <div className="relative bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] p-4">
                    {/* Blueprint grid background */}
                    <div className="absolute inset-0 blueprint-grid opacity-20 rounded-[var(--radius-sm)]" />

                    {/* Pencil stroke animation */}
                    <div className="absolute inset-0 rounded-[var(--radius-sm)] overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[var(--blueprint)] to-transparent opacity-20 animate-pulse" />
                    </div>

                    {/* Content */}
                    <div className="relative z-10 flex items-center justify-center">
                        <div className={cn(
                            "w-2 h-2 bg-[var(--blueprint)] rounded-full animate-ping",
                            size === "lg" && "w-3 h-3"
                        )} />
                    </div>

                    {/* Corner marks */}
                    <div className="absolute -top-px -left-px w-3 h-3 border-t border-l border-[var(--blueprint)]" />
                    <div className="absolute -top-px -right-px w-3 h-3 border-t border-r border-[var(--blueprint)]" />
                    <div className="absolute -bottom-px -left-px w-3 h-3 border-b border-l border-[var(--blueprint)]" />
                    <div className="absolute -bottom-px -right-px w-3 h-3 border-b border-r border-[var(--blueprint)]" />
                </div>
            </div>
        );
    }

    return null;
}

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT LOADING CARD — Full page loading state
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintLoadingCardProps {
    title?: string;
    message?: string;
    showProgress?: boolean;
    progress?: number;
    className?: string;
}

export function BlueprintLoadingCard({
    title = "Loading System...",
    message = "Initializing your workspace",
    showProgress = false,
    progress = 0,
    className,
}: BlueprintLoadingCardProps) {
    return (
        <div className={cn(
            "relative max-w-md mx-auto p-8 text-center",
            "bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius-lg)]",
            className
        )}>
            {/* Blueprint grid background */}
            <div className="absolute inset-0 blueprint-grid opacity-30 rounded-[var(--radius-lg)]" />

            {/* Corner marks */}
            <div className="absolute -top-px -left-px w-4 h-4 border-t border-l border-[var(--blueprint)]" />
            <div className="absolute -top-px -right-px w-4 h-4 border-t border-r border-[var(--blueprint)]" />
            <div className="absolute -bottom-px -left-px w-4 h-4 border-b border-l border-[var(--blueprint)]" />
            <div className="absolute -bottom-px -right-px w-4 h-4 border-b border-r border-[var(--blueprint)]" />

            {/* Content */}
            <div className="relative z-10">
                {/* Loader */}
                <div className="mb-6">
                    <BlueprintLoader size="lg" variant="spinner" />
                </div>

                {/* Title */}
                <h3 className="font-technical text-[var(--blueprint)] mb-2">{title}</h3>

                {/* Message */}
                <p className="text-sm text-[var(--ink-secondary)] mb-6">{message}</p>

                {/* Progress bar */}
                {showProgress && (
                    <div className="w-full">
                        <div className="flex items-center justify-between mb-2">
                            <span className="font-technical text-[10px] text-[var(--ink-muted)]">
                                PROGRESS
                            </span>
                            <span className="font-technical text-[10px] text-[var(--ink-muted)]">
                                {Math.round(progress)}%
                            </span>
                        </div>
                        <div className="w-full h-1 bg-[var(--structure)] rounded-full overflow-hidden">
                            <div
                                className="h-full bg-[var(--blueprint)] transition-all duration-300"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default BlueprintLoader;
