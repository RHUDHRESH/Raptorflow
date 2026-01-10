"use client";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { Check, Info } from "lucide-react";
import { cn } from "@/lib/utils";

export default function AppearanceSettingsPage() {
    // RaptorFlow enforces light mode only - theme selection is disabled
    const currentTheme = "light";

    return (
        <div className="space-y-8 max-w-2xl">
            <div>
                <h2 className="text-xl font-semibold text-[var(--ink)]">Appearance</h2>
                <p className="text-sm text-[var(--secondary)]">Customize the look and feel of your workspace.</p>
            </div>

            <BlueprintCard title="Theme" code="APP-01" padding="lg" showCorners>
                <div className="mb-4 p-3 bg-[var(--surface)] border border-[var(--structure-subtle)] rounded-[var(--radius)] flex items-start gap-3">
                    <Info size={16} className="text-[var(--blueprint)] mt-0.5 shrink-0" />
                    <p className="text-xs text-[var(--ink-secondary)]">
                        RaptorFlow uses a curated light theme designed for clarity and focus.
                        The warm ivory canvas and precise typography are core to the RaptorFlow experience.
                    </p>
                </div>
                <div className="grid grid-cols-3 gap-4">
                    {[
                        { id: "light", label: "Light", color: "bg-[#F3F4EE]", active: true },
                        { id: "dark", label: "Dark", color: "bg-[#0E1112]", disabled: true },
                        { id: "system", label: "System", color: "bg-gradient-to-r from-[#F3F4EE] to-[#0E1112]", disabled: true },
                    ].map((mode) => (
                        <div
                            key={mode.id}
                            className={cn(
                                "relative rounded-[var(--radius)] border-2 transition-all p-1",
                                mode.active
                                    ? "border-[var(--blueprint)] cursor-default"
                                    : "border-transparent opacity-50 cursor-not-allowed"
                            )}
                        >
                            <div className={cn("h-24 w-full rounded-[var(--radius-sm)] mb-2 shadow-sm border border-[var(--border)]", mode.color)} />
                            <div className="flex items-center justify-between px-1">
                                <span className={cn(
                                    "text-sm font-medium",
                                    mode.active ? "text-[var(--ink)]" : "text-[var(--ink-muted)]"
                                )}>{mode.label}</span>
                                {mode.active && <Check size={14} className="text-[var(--blueprint)]" />}
                            </div>
                            {mode.disabled && (
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <span className="text-[9px] font-mono uppercase tracking-wider text-[var(--ink-muted)] bg-[var(--paper)] px-2 py-0.5 rounded-[var(--radius)]">
                                        Coming Soon
                                    </span>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </BlueprintCard>

            <BlueprintCard title="Reduce Motion" code="ACC-01" padding="lg" showCorners>
                <div className="flex items-center justify-between">
                    <div>
                        <h4 className="text-sm font-semibold text-[var(--ink)]">Reduce Interface Motion</h4>
                        <p className="text-xs text-[var(--secondary)]">Minimize animations for a simpler experience.</p>
                    </div>
                    {/* Toggle switch - currently display only */}
                    <div className="w-10 h-6 rounded-full bg-[var(--border)] relative cursor-not-allowed opacity-50">
                        <div className="absolute top-1 left-1 w-4 h-4 rounded-full bg-[var(--paper)] shadow-sm" />
                    </div>
                </div>
            </BlueprintCard>

            <div className="p-4 bg-[var(--surface)] border border-[var(--structure-subtle)] rounded-[var(--radius)]">
                <p className="text-xs text-[var(--ink-muted)] text-center">
                    Additional appearance options will be available in future updates.
                </p>
            </div>
        </div>
    );
}
