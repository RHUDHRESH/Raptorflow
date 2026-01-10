"use client";

import React from "react";
import { Loader2, RefreshCw, AlertTriangle, XCircle, HelpCircle } from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";

/* ══════════════════════════════════════════════════════════════════════════════
   STEP LOADING STATE — Consistent loading UI for AI processing
   ══════════════════════════════════════════════════════════════════════════════ */

interface StepLoadingStateProps {
    title?: string;
    message?: string;
    progress?: number;
    stage?: string;
    onCancel?: () => void;
    variant?: "default" | "compact" | "inline";
}

export function StepLoadingState({
    title = "Processing...",
    message = "Please wait while we analyze your data",
    progress,
    stage,
    onCancel,
    variant = "default",
}: StepLoadingStateProps) {
    if (variant === "inline") {
        return (
            <div className="flex items-center gap-2 font-technical text-[var(--blueprint)]">
                <Loader2 size={12} className="animate-spin" />
                <span>{stage || message}</span>
            </div>
        );
    }

    if (variant === "compact") {
        return (
            <BlueprintCard showCorners padding="md">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-[var(--radius-md)] bg-[var(--blueprint)] flex items-center justify-center ink-bleed-sm">
                        <Loader2 size={18} className="text-[var(--paper)] animate-spin" />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-sm font-semibold text-[var(--ink)]">{title}</h3>
                        <p className="font-technical text-[var(--muted)]">{stage || message}</p>
                    </div>
                    {progress !== undefined && (
                        <span className="font-technical text-[var(--blueprint)]">{progress}%</span>
                    )}
                </div>
            </BlueprintCard>
        );
    }

    return (
        <div className="flex flex-col items-center justify-center py-16 text-center space-y-6">
            <div className="w-16 h-16 rounded-[var(--radius-md)] bg-[var(--blueprint)] flex items-center justify-center ink-bleed-md">
                <Loader2 size={30} className="text-[var(--paper)] animate-spin" />
            </div>
            <div>
                <h3 className="font-serif text-xl text-[var(--ink)] mb-2">{title}</h3>
                <p className="text-sm text-[var(--secondary)] max-w-md mx-auto">{message}</p>
                {stage && (
                    <p className="font-technical text-[var(--blueprint)] mt-2">{stage}</p>
                )}
            </div>
            {progress !== undefined && (
                <div className="w-48">
                    <div className="flex items-center justify-between font-technical text-[var(--muted)] mb-2">
                        <span>PROGRESS</span>
                        <span>{progress}%</span>
                    </div>
                    <div className="h-2 bg-[var(--canvas)] rounded-full overflow-hidden border border-[var(--border-subtle)]">
                        <div
                            className="h-full bg-[var(--blueprint)] rounded-full transition-all"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            )}
            {onCancel && (
                <SecondaryButton size="sm" onClick={onCancel}>
                    Cancel
                </SecondaryButton>
            )}
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   STEP ERROR STATE — Consistent error UI with retry
   ══════════════════════════════════════════════════════════════════════════════ */

interface StepErrorStateProps {
    title?: string;
    message: string;
    details?: string;
    onRetry?: () => void;
    onSkip?: () => void;
    variant?: "error" | "warning" | "blocked";
}

export function StepErrorState({
    title,
    message,
    details,
    onRetry,
    onSkip,
    variant = "error",
}: StepErrorStateProps) {
    const config = {
        error: {
            icon: XCircle,
            color: "text-[var(--error)]",
            bg: "bg-[var(--error)]",
            border: "border-[var(--error)]/30",
            bgLight: "bg-[var(--error-light)]",
            defaultTitle: "Something went wrong",
        },
        warning: {
            icon: AlertTriangle,
            color: "text-[var(--warning)]",
            bg: "bg-[var(--warning)]",
            border: "border-[var(--warning)]/30",
            bgLight: "bg-[var(--warning-light)]",
            defaultTitle: "Action required",
        },
        blocked: {
            icon: HelpCircle,
            color: "text-[var(--muted)]",
            bg: "bg-[var(--muted)]",
            border: "border-[var(--border)]",
            bgLight: "bg-[var(--canvas)]",
            defaultTitle: "Cannot proceed",
        },
    };

    const { icon: Icon, color, bg, border, bgLight, defaultTitle } = config[variant];

    return (
        <BlueprintCard showCorners padding="lg" className={`${border} ${bgLight}`}>
            <div className="flex flex-col items-center text-center space-y-4">
                <div className={`w-14 h-14 rounded-[var(--radius-md)] ${bg} flex items-center justify-center ink-bleed-sm`}>
                    <Icon size={26} className="text-[var(--paper)]" />
                </div>
                <div>
                    <h3 className="font-serif text-lg text-[var(--ink)] mb-1">{title || defaultTitle}</h3>
                    <p className="text-sm text-[var(--secondary)]">{message}</p>
                    {details && (
                        <p className="font-technical text-[var(--muted)] mt-2">{details}</p>
                    )}
                </div>
                <div className="flex gap-3">
                    {onRetry && (
                        <BlueprintButton size="sm" onClick={onRetry}>
                            <RefreshCw size={12} strokeWidth={1.5} />
                            Try Again
                        </BlueprintButton>
                    )}
                    {onSkip && (
                        <SecondaryButton size="sm" onClick={onSkip}>
                            Skip for Now
                        </SecondaryButton>
                    )}
                </div>
            </div>
        </BlueprintCard>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   STEP EMPTY STATE — For missing data scenarios
   ══════════════════════════════════════════════════════════════════════════════ */

interface StepEmptyStateProps {
    title: string;
    description: string;
    actionLabel?: string;
    onAction?: () => void;
    icon?: React.ElementType;
}

export function StepEmptyState({
    title,
    description,
    actionLabel,
    onAction,
    icon: Icon = HelpCircle,
}: StepEmptyStateProps) {
    return (
        <BlueprintCard showCorners padding="lg" className="text-center">
            <div className="flex flex-col items-center space-y-4">
                <div className="w-12 h-12 rounded-[var(--radius-md)] bg-[var(--canvas)] border border-[var(--border)] flex items-center justify-center">
                    <Icon size={22} className="text-[var(--muted)]" />
                </div>
                <div>
                    <h3 className="text-sm font-semibold text-[var(--ink)] mb-1">{title}</h3>
                    <p className="text-sm text-[var(--secondary)]">{description}</p>
                </div>
                {actionLabel && onAction && (
                    <BlueprintButton size="sm" onClick={onAction}>
                        {actionLabel}
                    </BlueprintButton>
                )}
            </div>
        </BlueprintCard>
    );
}
