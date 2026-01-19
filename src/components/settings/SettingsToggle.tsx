"use client";

import React from "react";
import { cn } from "@/lib/utils";

// ═══════════════════════════════════════════════════════════════
// SettingsToggle - Premium toggle switch
// ═══════════════════════════════════════════════════════════════

interface SettingsToggleProps {
    /** Current state */
    checked: boolean;
    /** Change handler */
    onChange: (checked: boolean) => void;
    /** Disabled state */
    disabled?: boolean;
    /** Size variant */
    size?: "sm" | "md";
    /** Aria label for accessibility */
    label?: string;
}

export function SettingsToggle({
    checked,
    onChange,
    disabled = false,
    size = "md",
    label,
}: SettingsToggleProps) {
    const sizes = {
        sm: {
            track: "w-9 h-5",
            knob: "w-4 h-4",
            translate: "translate-x-4",
        },
        md: {
            track: "w-11 h-6",
            knob: "w-5 h-5",
            translate: "translate-x-5",
        },
    };

    const s = sizes[size];

    return (
        <button
            type="button"
            role="switch"
            aria-checked={checked}
            aria-label={label}
            disabled={disabled}
            onClick={() => onChange(!checked)}
            className={cn(
                "relative rounded-full transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ink)] focus-visible:ring-offset-2",
                s.track,
                checked ? "bg-[var(--ink)]" : "bg-[var(--border)]",
                disabled && "opacity-50 cursor-not-allowed"
            )}
        >
            <span
                className={cn(
                    "absolute top-[2px] left-[2px] bg-white rounded-full shadow-sm transition-transform duration-200",
                    s.knob,
                    checked && s.translate
                )}
            />
        </button>
    );
}
