"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { Inbox, Search, Plus, FolderOpen, Compass } from "lucide-react";
import { BlueprintButton } from "./BlueprintButton";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT EMPTY STATE — Premium Empty States
   ══════════════════════════════════════════════════════════════════════════════ */

interface BlueprintEmptyStateProps {
    icon?: React.ReactNode;
    title: string;
    description?: string;
    code?: string;
    action?: {
        label: string;
        onClick: () => void;
    };
    variant?: "default" | "search" | "folder" | "inbox";
    className?: string;
}

export function BlueprintEmptyState({
    icon,
    title,
    description,
    code,
    action,
    variant = "default",
    className,
}: BlueprintEmptyStateProps) {
    const variantIcons = {
        default: <Compass size={48} strokeWidth={1} className="text-[var(--blueprint)]" />,
        search: <Search size={48} strokeWidth={1} className="text-[var(--blueprint)]" />,
        folder: <FolderOpen size={48} strokeWidth={1} className="text-[var(--blueprint)]" />,
        inbox: <Inbox size={48} strokeWidth={1} className="text-[var(--blueprint)]" />,
    };

    return (
        <div className={cn(
            "relative flex flex-col items-center justify-center py-16 px-8 text-center",
            "bg-[var(--paper)] rounded-[var(--radius-lg)] border border-dashed border-[var(--border)]",
            className
        )}>
            {/* Blueprint grid background */}
            <div className="absolute inset-0 blueprint-grid opacity-20 rounded-[var(--radius-lg)]" />

            {/* Corner marks */}
            <div className="absolute -top-px -left-px w-4 h-4 border-t border-l border-[var(--blueprint)]" />
            <div className="absolute -top-px -right-px w-4 h-4 border-t border-r border-[var(--blueprint)]" />
            <div className="absolute -bottom-px -left-px w-4 h-4 border-b border-l border-[var(--blueprint)]" />
            <div className="absolute -bottom-px -right-px w-4 h-4 border-b border-r border-[var(--blueprint)]" />

            {/* Code */}
            {code && (
                <span className="font-technical text-[var(--blueprint)] mb-4">{code}</span>
            )}

            {/* Icon */}
            <div className="relative mb-6">
                {icon || variantIcons[variant]}
                {/* Crosshair marks around icon */}
                <div className="absolute top-1/2 -left-4 w-2 h-px bg-[var(--blueprint-line)]" />
                <div className="absolute top-1/2 -right-4 w-2 h-px bg-[var(--blueprint-line)]" />
                <div className="absolute -top-4 left-1/2 h-2 w-px bg-[var(--blueprint-line)]" />
                <div className="absolute -bottom-4 left-1/2 h-2 w-px bg-[var(--blueprint-line)]" />
            </div>

            {/* Title */}
            <h3 className="font-serif text-xl text-[var(--ink)] mb-2">{title}</h3>

            {/* Description */}
            {description && (
                <p className="text-sm text-[var(--secondary)] max-w-sm mb-6">{description}</p>
            )}

            {/* Action */}
            {action && (
                <BlueprintButton onClick={action.onClick} size="sm">
                    <Plus size={14} strokeWidth={1.5} />
                    {action.label}
                </BlueprintButton>
            )}
        </div>
    );
}

export default BlueprintEmptyState;
