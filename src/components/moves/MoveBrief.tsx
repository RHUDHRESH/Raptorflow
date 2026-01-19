"use client";

import { cn } from "@/lib/utils";
import { MoveBriefData, MOVE_CATEGORIES } from "./types";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { MoveCategoryIcon } from "@/components/moves/MoveCategoryIcon";
import { Calendar, Target, Mic, BarChart3 } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   MOVE BRIEF — Strategy Lock Display
   Shows the AI-generated Move summary before confirmation
   ══════════════════════════════════════════════════════════════════════════════ */

interface MoveBriefProps {
    brief: MoveBriefData;
    className?: string;
}

export function MoveBrief({ brief, className }: MoveBriefProps) {
    const categoryInfo = MOVE_CATEGORIES[brief.category];

    return (
        <div className={cn("space-y-6", className)}>
            {/* Section Header */}
            <div className="space-y-2">
                <div className="flex items-center gap-3">
                    <span className="font-technical text-[var(--blueprint)]">STEP 03</span>
                    <div className="h-px flex-1 bg-[var(--structure-subtle)]" />
                    <span className="font-technical text-[var(--ink-muted)]">STRATEGY LOCK</span>
                </div>
                <h2 className="font-serif text-2xl text-[var(--ink)]">Your Move Brief</h2>
                <p className="text-sm text-[var(--ink-secondary)]">
                    Review and confirm your tactical sprint strategy.
                </p>
            </div>

            {/* Brief Card */}
            <BlueprintCard showCorners padding="lg" className="space-y-6">
                {/* Move Name & Category */}
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <MoveCategoryIcon category={brief.category} size={24} />
                        <BlueprintBadge variant="blueprint">{categoryInfo.tagline}</BlueprintBadge>
                    </div>
                    <h3 className="font-serif text-xl text-[var(--ink)]">
                        {brief.name}
                    </h3>
                </div>

                {/* Divider */}
                <div className="h-px bg-[var(--structure-subtle)]" />

                {/* Details Grid */}
                <div className="grid grid-cols-2 gap-6">
                    {/* Duration */}
                    <div className="flex items-start gap-3">
                        <div className="p-2 rounded-[var(--radius)] bg-[var(--surface)]">
                            <Calendar size={16} className="text-[var(--ink-muted)]" strokeWidth={1.5} />
                        </div>
                        <div>
                            <span className="label block mb-1">DURATION</span>
                            <span className="font-data text-[var(--ink)]">{brief.duration} DAYS</span>
                        </div>
                    </div>

                    {/* Tone */}
                    <div className="flex items-start gap-3">
                        <div className="p-2 rounded-[var(--radius)] bg-[var(--surface)]">
                            <Mic size={16} className="text-[var(--ink-muted)]" strokeWidth={1.5} />
                        </div>
                        <div>
                            <span className="label block mb-1">TONE</span>
                            <span className="text-sm font-medium text-[var(--ink)]">{brief.tone}</span>
                        </div>
                    </div>
                </div>

                {/* Goal */}
                <div className="flex items-start gap-3">
                    <div className="p-2 rounded-[var(--radius)] bg-[var(--surface)]">
                        <Target size={16} className="text-[var(--ink-muted)]" strokeWidth={1.5} />
                    </div>
                    <div className="flex-1">
                        <span className="label block mb-1">GOAL</span>
                        <p className="text-sm text-[var(--ink)]">{brief.goal}</p>
                    </div>
                </div>

                {/* Strategy */}
                <div>
                    <span className="label block mb-2">STRATEGY</span>
                    <p className="text-sm text-[var(--ink-secondary)] leading-relaxed">
                        {brief.strategy}
                    </p>
                </div>

                {/* Divider */}
                <div className="h-px bg-[var(--structure-subtle)]" />

                {/* Metrics to Track */}
                <div>
                    <div className="flex items-center gap-2 mb-3">
                        <BarChart3 size={14} className="text-[var(--blueprint)]" strokeWidth={1.5} />
                        <span className="label">KEY METRICS</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {brief.metrics.map((metric) => (
                            <span
                                key={metric}
                                className="rf-badge"
                            >
                                {metric}
                            </span>
                        ))}
                    </div>
                </div>
            </BlueprintCard>
        </div>
    );
}

export default MoveBrief;
