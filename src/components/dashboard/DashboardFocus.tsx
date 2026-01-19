"use client";

import { useRouter } from "next/navigation";
import { Move } from "@/components/moves/types";
import { MoveCategoryIcon } from "@/components/moves/MoveCategoryIcon";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { ArrowRight, Target, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

/* ══════════════════════════════════════════════════════════════════════════════
   DASHBOARD FOCUS — The One Thing
   Quiet Luxury: Single clear directive, no animations, editorial calm.
   ══════════════════════════════════════════════════════════════════════════════ */

interface DashboardFocusProps {
    move: Move | null;
    className?: string;
}

export function DashboardFocus({ move, className }: DashboardFocusProps) {
    const router = useRouter();

    if (!move) {
        return <EmptyFocus />;
    }

    // Get current day data
    const currentDay = 1;
    const dayData = move.execution?.[currentDay - 1];
    const taskTitle = dayData?.pillarTask?.title || move.name;
    const taskDescription =
        dayData?.pillarTask?.description ||
        "Execute this core strategic action to drive momentum.";

    return (
        <section className={cn("space-y-4", className)}>
            {/* Section label */}
            <div className="flex items-center gap-3">
                <span className="font-technical text-[var(--blueprint)]">01</span>
                <div className="h-px flex-1 bg-[var(--border)]" />
                <span className="font-technical text-[var(--ink-muted)]">
                    PRIMARY FOCUS
                </span>
            </div>

            {/* Focus card */}
            <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-xl)] p-8 hover:border-[var(--ink-secondary)] transition-colors">
                {/* Header */}
                <div className="flex items-start gap-5 mb-6">
                    <div className="w-14 h-14 flex items-center justify-center rounded-[var(--radius-lg)] bg-[var(--surface)] border border-[var(--border)]">
                        <MoveCategoryIcon category={move.category} size={28} />
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 text-[var(--ink-muted)] text-xs font-mono uppercase tracking-wider mb-2">
                            <span>{move.category} Protocol</span>
                            <span className="text-[var(--border)]">•</span>
                            <span>
                                Day {currentDay} of {move.duration}
                            </span>
                        </div>
                        <h2 className="font-serif text-2xl lg:text-3xl text-[var(--ink)] leading-tight">
                            {taskTitle}
                        </h2>
                    </div>
                </div>

                {/* Description */}
                <p className="text-[var(--ink-secondary)] leading-relaxed mb-8 max-w-2xl">
                    {taskDescription}
                </p>

                {/* Footer */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pt-6 border-t border-[var(--border)]">
                    <div className="flex items-center gap-6 text-sm text-[var(--ink-muted)]">
                        <div className="flex items-center gap-2">
                            <Clock size={14} />
                            <span>Est. 45 min</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <Target size={14} />
                            <span>High Impact</span>
                        </div>
                    </div>

                    <BlueprintButton onClick={() => router.push(`/moves/${move.id}`)}>
                        Execute Protocol <ArrowRight size={16} className="ml-1" />
                    </BlueprintButton>
                </div>
            </div>
        </section>
    );
}

function EmptyFocus() {
    const router = useRouter();

    return (
        <section className="space-y-4">
            {/* Section label */}
            <div className="flex items-center gap-3">
                <span className="font-technical text-[var(--blueprint)]">01</span>
                <div className="h-px flex-1 bg-[var(--border)]" />
                <span className="font-technical text-[var(--ink-muted)]">
                    PRIMARY FOCUS
                </span>
            </div>

            {/* Empty state card */}
            <div className="bg-[var(--paper)] border border-dashed border-[var(--border)] rounded-[var(--radius-xl)] p-12 text-center">
                <div className="w-16 h-16 rounded-full bg-[var(--surface)] flex items-center justify-center mx-auto mb-6">
                    <Target size={28} className="text-[var(--ink-muted)]" />
                </div>
                <h3 className="font-serif text-2xl text-[var(--ink)] mb-3">
                    All Quiet.
                </h3>
                <p className="text-[var(--ink-secondary)] max-w-md mx-auto mb-8">
                    No active protocols detected. The board is clear. Initialize a new
                    strategic move to break the silence.
                </p>
                <BlueprintButton onClick={() => router.push("/moves?create=true")}>
                    Initialize Move
                </BlueprintButton>
            </div>
        </section>
    );
}
