"use client";

import React from "react";
import { CheckmarkCircle02Icon } from "hugeicons-react";
import { SettingsGroup } from "../SettingsRow";
import { cn } from "@/lib/utils";

// ═══════════════════════════════════════════════════════════════
// AppearanceSection - Theme and display settings
// ═══════════════════════════════════════════════════════════════

const ACCENT_COLORS = [
    { id: "blueprint", name: "Blueprint", value: "#3A5A7C" },
    { id: "forest", name: "Forest", value: "#2D5A3D" },
    { id: "amber", name: "Amber", value: "#8B6914" },
    { id: "plum", name: "Plum", value: "#6B3A7C" },
    { id: "slate", name: "Slate", value: "#4A5568" },
];

interface AppearanceData {
    accentColor: string;
}

interface AppearanceSectionProps {
    data: AppearanceData;
    onChange: (field: keyof AppearanceData, value: string) => void;
}

export function AppearanceSection({ data, onChange }: AppearanceSectionProps) {
    return (
        <div className="space-y-8">
            {/* Page Header */}
            <div>
                <h2 className="text-2xl font-semibold text-[var(--ink)]">Appearance</h2>
                <p className="text-sm text-[var(--muted)] mt-1">
                    Customize how RaptorFlow looks
                </p>
            </div>

            {/* Theme Notice */}
            <SettingsGroup title="Theme">
                <div className="p-4 bg-[var(--canvas)] border border-[var(--border)] rounded-xl">
                    <p className="text-sm text-[var(--ink)]">
                        RaptorFlow uses a light theme optimized for readability and the{" "}
                        <span className="font-medium">"quiet luxury"</span> aesthetic.
                    </p>
                    <p className="text-xs text-[var(--muted)] mt-2">
                        Dark mode is not available by design.
                    </p>
                </div>
            </SettingsGroup>

            {/* Accent Color */}
            <SettingsGroup title="Accent Color" description="Used for buttons, links, and highlights">
                <div className="flex flex-wrap gap-3">
                    {ACCENT_COLORS.map((color) => {
                        const isSelected = data.accentColor === color.id;

                        return (
                            <button
                                key={color.id}
                                onClick={() => onChange("accentColor", color.id)}
                                className={cn(
                                    "flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all",
                                    isSelected
                                        ? "border-[var(--ink)] bg-[var(--canvas)]"
                                        : "border-transparent hover:bg-[var(--canvas)]"
                                )}
                            >
                                <div
                                    className="w-10 h-10 rounded-full border-2 border-white shadow-md flex items-center justify-center"
                                    style={{ backgroundColor: color.value }}
                                >
                                    {isSelected && (
                                        React.createElement(CheckmarkCircle02Icon as any, {
                                            className: "w-4 h-4 text-white",
                                        })
                                    )}
                                </div>
                                <span className="text-xs text-[var(--muted)]">{color.name}</span>
                            </button>
                        );
                    })}
                </div>
            </SettingsGroup>
        </div>
    );
}

// Export accent colors for use in parent
export { ACCENT_COLORS };
