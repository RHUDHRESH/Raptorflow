"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   AXIS DROPDOWN — Selector for perceptual map axes
   ══════════════════════════════════════════════════════════════════════════════ */

interface AxisOption {
    id: string;
    label: string;
    lowLabel: string;
    highLabel: string;
}

interface AxisDropdownProps {
    options: AxisOption[];
    selected: string;
    onSelect: (id: string) => void;
    position: "x" | "y";
    className?: string;
}

export const DEFAULT_AXIS_OPTIONS: AxisOption[] = [
    { id: "price", label: "Price", lowLabel: "Affordable", highLabel: "Premium" },
    { id: "features", label: "Features", lowLabel: "Simple", highLabel: "Comprehensive" },
    { id: "speed", label: "Speed", lowLabel: "Methodical", highLabel: "Rapid" },
    { id: "ux", label: "User Experience", lowLabel: "Technical", highLabel: "User-Friendly" },
    { id: "support", label: "Support", lowLabel: "Self-Serve", highLabel: "High-Touch" },
    { id: "customization", label: "Customization", lowLabel: "Opinionated", highLabel: "Flexible" },
    { id: "integration", label: "Integration", lowLabel: "Standalone", highLabel: "Connected" },
    { id: "market", label: "Market Focus", lowLabel: "Niche", highLabel: "Broad" },
];

export function AxisDropdown({ options, selected, onSelect, position, className = "" }: AxisDropdownProps) {
    const [isOpen, setIsOpen] = useState(false);
    const selectedOption = options.find(o => o.id === selected);

    return (
        <div className={`relative ${className}`}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--paper)] border border-[var(--border)] hover:border-[var(--ink)] transition-colors"
            >
                <span className="font-technical text-[10px] text-[var(--ink)]">
                    {selectedOption?.label || "Select"}
                </span>
                <ChevronDown size={12} className={`text-[var(--muted)] transition-transform ${isOpen ? "rotate-180" : ""}`} />
            </button>

            {isOpen && (
                <>
                    <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
                    <div className={`absolute z-50 mt-1 w-48 bg-[var(--paper)] border border-[var(--border)] rounded-xl shadow-xl overflow-hidden ${position === "y" ? "right-0" : "left-0"}`}>
                        {options.map((option) => (
                            <button
                                key={option.id}
                                onClick={() => { onSelect(option.id); setIsOpen(false); }}
                                className={`w-full text-left px-4 py-2 text-sm transition-colors ${option.id === selected
                                        ? "bg-[var(--ink)] text-[var(--paper)]"
                                        : "text-[var(--ink)] hover:bg-[var(--canvas)]"
                                    }`}
                            >
                                <span className="font-medium">{option.label}</span>
                                <span className="block text-[10px] opacity-70">
                                    {option.lowLabel} → {option.highLabel}
                                </span>
                            </button>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
