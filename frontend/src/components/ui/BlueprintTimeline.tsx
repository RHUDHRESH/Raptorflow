"use client";

import React, { useRef, useEffect } from "react";
import gsap from "gsap";
import { cn } from "@/lib/utils";
import { Check, Clock, AlertCircle, Circle } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT TIMELINE — Tactical Gantt
   A visual timeline for operation sequences
   ══════════════════════════════════════════════════════════════════════════════ */

interface TimelineEvent {
    id: string;
    title: string;
    description?: string;
    timestamp: string;
    duration?: string;
    code?: string;
    status?: "complete" | "current" | "pending" | "error" | "blocked";
    assignee?: string;
}

interface BlueprintTimelineProps {
    events: TimelineEvent[];
    figure?: string;
    className?: string;
    orientation?: "vertical" | "horizontal";
}

export function BlueprintTimeline({
    events,
    figure,
    className,
    orientation = "vertical"
}: BlueprintTimelineProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;
        const items = containerRef.current.querySelectorAll(".timeline-item");
        gsap.fromTo(items,
            { opacity: 0, x: -10 },
            { opacity: 1, x: 0, duration: 0.5, stagger: 0.1, ease: "power2.out" }
        );
    }, []);

    const statusConfig = {
        complete: { icon: Check, color: "var(--success)", bg: "var(--success-light)" },
        current: { icon: Clock, color: "var(--blueprint)", bg: "var(--blueprint-light)" },
        pending: { icon: Circle, color: "var(--muted)", bg: "var(--surface)" },
        error: { icon: AlertCircle, color: "var(--error)", bg: "var(--error-light)" },
        blocked: { icon: Circle, color: "var(--ink-secondary)", bg: "var(--border)" },
    };

    return (
        <div ref={containerRef} className={cn("relative", className)}>
            {/* Header */}
            {figure && (
                <div className="flex items-center gap-3 mb-8">
                    <span className="font-technical text-[var(--blueprint)]">{figure}</span>
                    <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                    <span className="font-technical text-[var(--muted)]">OP_SEQUENCE</span>
                </div>
            )}

            {/* Vertical Layout */}
            {orientation === "vertical" && (
                <div className="relative pl-6 space-y-8">
                    {/* Main Axis */}
                    <div className="absolute left-[11px] top-2 bottom-2 w-px bg-[var(--border)] dashed-line" />

                    {events.map((event, i) => {
                        const status = event.status || "pending";
                        const conf = statusConfig[status];
                        const Icon = conf.icon;

                        return (
                            <div key={event.id} className="timeline-item relative group">
                                {/* Node */}
                                <div className={cn(
                                    "absolute left-[-23px] w-6 h-6 rounded-full border-2 flex items-center justify-center z-10 transition-all duration-300",
                                    status === 'current' ? "scale-110 shadow-[0_0_10px_var(--blueprint)]" : "scale-100"
                                )} style={{
                                    borderColor: conf.color,
                                    backgroundColor: status === 'current' ? 'var(--paper)' : conf.bg
                                }}>
                                    <Icon size={12} color={conf.color} strokeWidth={2.5} />
                                </div>

                                {/* Content Card */}
                                <div className={cn(
                                    "p-4 rounded-[var(--radius)] border transition-all duration-300",
                                    status === 'current'
                                        ? "bg-[var(--surface)] border-[var(--blueprint)] shadow-sm"
                                        : "bg-[var(--paper)] border-[var(--structure)] hover:border-[var(--structure-strong)]"
                                )}>
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex items-center gap-2">
                                            <span className="font-mono text-[10px] text-[var(--muted)]">
                                                {String(i + 1).padStart(2, "0")}
                                            </span>
                                            <h4 className={cn("font-medium", status === 'complete' ? "text-[var(--ink-secondary)]" : "text-[var(--ink)]")}>
                                                {event.title}
                                            </h4>
                                            {event.code && (
                                                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[var(--surface)] text-[var(--ink-secondary)] border border-[var(--border)]">
                                                    {event.code}
                                                </span>
                                            )}
                                        </div>
                                        <span className="font-technical text-[var(--muted)] text-xs">{event.timestamp}</span>
                                    </div>

                                    {event.description && (
                                        <p className="text-sm text-[var(--ink-secondary)] leading-relaxed mb-3">
                                            {event.description}
                                        </p>
                                    )}

                                    {/* Event Metadata */}
                                    <div className="flex items-center gap-4 pt-3 border-t border-[var(--border-subtle)]">
                                        {event.assignee && (
                                            <div className="flex items-center gap-1.5 text-xs text-[var(--ink)]">
                                                <div className="w-4 h-4 rounded-full bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center text-[8px]">
                                                    {event.assignee.charAt(0)}
                                                </div>
                                                {event.assignee}
                                            </div>
                                        )}
                                        {event.duration && (
                                            <div className="flex items-center gap-1.5 text-xs text-[var(--muted)] font-mono">
                                                <Clock size={10} />
                                                {event.duration}
                                            </div>
                                        )}
                                        {status === 'complete' && (
                                            <div className="ml-auto text-xs text-[var(--success)] font-medium flex items-center gap-1">
                                                Confirmed <Check size={10} />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
