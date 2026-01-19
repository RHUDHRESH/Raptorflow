"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   DASHBOARD HEADER — Clean Editorial Style
   Quiet Luxury: Big whitespace, strong type hierarchy, one clear action.
   ══════════════════════════════════════════════════════════════════════════════ */

interface DashboardHeaderProps {
    userName?: string;
    systemStatus?: "Nominal" | "Attention" | "Critical";
    className?: string;
}

export function DashboardHeader({
    userName = "Founder",
    systemStatus = "Nominal",
    className,
}: DashboardHeaderProps) {
    const [greeting, setGreeting] = useState("Good morning");
    const [dateStr, setDateStr] = useState("");

    useEffect(() => {
        const now = new Date();
        const hour = now.getHours();

        if (hour < 12) setGreeting("Good morning");
        else if (hour < 18) setGreeting("Good afternoon");
        else setGreeting("Good evening");

        setDateStr(
            now.toLocaleDateString("en-US", {
                weekday: "long",
                month: "long",
                day: "numeric",
            })
        );
    }, []);

    return (
        <header className={cn("pb-8 border-b border-[var(--border)]", className)}>
            {/* Technical meta line */}
            <div className="flex items-center gap-3 mb-6">
                <span className="font-technical text-[var(--ink-secondary)] uppercase">
                    System Dashboard
                </span>
                <div className="h-px w-8 bg-[var(--border)]" />
                <span className="font-technical text-[var(--ink-muted)]">
                    {dateStr}
                </span>
            </div>

            {/* Main greeting */}
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
                <h1 className="font-serif text-4xl lg:text-5xl text-[var(--ink)] leading-tight">
                    {greeting}, {userName}.
                </h1>

                {/* Status badge */}
                <div
                    className={cn(
                        "inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono uppercase tracking-wide border",
                        systemStatus === "Nominal" &&
                        "bg-[var(--success-bg)] text-[var(--success)] border-[var(--success)]/20",
                        systemStatus === "Attention" &&
                        "bg-[var(--warning-bg)] text-[var(--warning)] border-[var(--warning)]/20",
                        systemStatus === "Critical" &&
                        "bg-[var(--error-bg)] text-[var(--error)] border-[var(--error)]/20"
                    )}
                >
                    <span
                        className={cn(
                            "w-1.5 h-1.5 rounded-full",
                            systemStatus === "Nominal" && "bg-[var(--success)]",
                            systemStatus === "Attention" && "bg-[var(--warning)]",
                            systemStatus === "Critical" && "bg-[var(--error)]"
                        )}
                    />
                    {systemStatus}
                </div>
            </div>
        </header>
    );
}
