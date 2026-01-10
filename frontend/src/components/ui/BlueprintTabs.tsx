"use client";

import React from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT TABS — Technical Tab Navigation
   Features:
   - Blueprint-style active indicator
   - Technical codes for each tab
   - Measurement ticks
   - Ink bleed on active tab
   ══════════════════════════════════════════════════════════════════════════════ */

interface Tab {
    id: string;
    label: string;
    code?: string;
    icon?: React.ReactNode;
    disabled?: boolean;
}

interface BlueprintTabsProps {
    tabs: Tab[];
    activeTab: string;
    onChange: (tabId: string) => void;
    variant?: "default" | "pills" | "underline";
    figure?: string;
    className?: string;
}

export function BlueprintTabs({
    tabs,
    activeTab,
    onChange,
    variant = "default",
    figure,
    className,
}: BlueprintTabsProps) {
    return (
        <div className={cn("w-full", className)}>
            {/* Figure annotation */}
            {figure && (
                <div className="flex items-center gap-3 mb-4">
                    <span className="font-technical text-[var(--blueprint)]">{figure}</span>
                    <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                    <span className="font-technical text-[var(--muted)]">
                        {tabs.length.toString().padStart(2, "0")} TABS
                    </span>
                </div>
            )}

            {/* Tabs container */}
            <div
                className={cn(
                    "relative flex items-center gap-1",
                    variant === "default" && "bg-[var(--canvas)] p-1 rounded-[var(--radius-md)] border border-[var(--border)]",
                    variant === "underline" && "border-b border-[var(--border)]"
                )}
            >
                {/* Measurement ticks at top */}
                {variant === "default" && (
                    <div className="absolute -top-3 left-0 right-0 flex justify-between px-2 pointer-events-none">
                        {tabs.map((_, i) => (
                            <div key={i} className="flex flex-col items-center">
                                <div className="h-1.5 w-px bg-[var(--blueprint-line)]" />
                            </div>
                        ))}
                    </div>
                )}

                {tabs.map((tab) => {
                    const isActive = tab.id === activeTab;

                    return (
                        <button
                            key={tab.id}
                            onClick={() => !tab.disabled && onChange(tab.id)}
                            disabled={tab.disabled}
                            className={cn(
                                "relative flex items-center gap-2 px-4 py-2 text-sm font-medium",
                                "transition-all duration-200",

                                // Default variant
                                variant === "default" && [
                                    "rounded-[var(--radius-sm)]",
                                    isActive
                                        ? "bg-[var(--paper)] text-[var(--ink)] ink-bleed-sm"
                                        : "text-[var(--secondary)] hover:text-[var(--ink)] hover:bg-[var(--paper)]/50",
                                ],

                                // Pills variant
                                variant === "pills" && [
                                    "rounded-full",
                                    isActive
                                        ? "bg-[var(--ink)] text-[var(--paper)]"
                                        : "text-[var(--secondary)] hover:bg-[var(--canvas)]",
                                ],

                                // Underline variant
                                variant === "underline" && [
                                    "pb-3 -mb-px",
                                    isActive
                                        ? "text-[var(--ink)] border-b-2 border-[var(--blueprint)]"
                                        : "text-[var(--secondary)] hover:text-[var(--ink)]",
                                ],

                                tab.disabled && "opacity-50 cursor-not-allowed"
                            )}
                        >
                            {/* Registration mark on active */}
                            {isActive && variant === "default" && (
                                <>
                                    <div className="absolute -top-0.5 -left-0.5 w-2 h-2 border-t border-l border-[var(--blueprint)]" />
                                    <div className="absolute -bottom-0.5 -right-0.5 w-2 h-2 border-b border-r border-[var(--blueprint)]" />
                                </>
                            )}

                            {tab.icon}
                            <span>{tab.label}</span>

                            {tab.code && (
                                <span className={cn(
                                    "font-technical text-[9px]",
                                    isActive ? "text-[var(--blueprint)]" : "text-[var(--muted)]"
                                )}>
                                    {tab.code}
                                </span>
                            )}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}

/* ══════════════════════════════════════════════════════════════════════════════
   TAB CONTENT WRAPPER
   ══════════════════════════════════════════════════════════════════════════════ */

interface TabContentProps {
    children: React.ReactNode;
    className?: string;
}

export function TabContent({ children, className }: TabContentProps) {
    return (
        <div className={cn("mt-6 ink-fade-in", className)}>
            {children}
        </div>
    );
}

export default BlueprintTabs;
