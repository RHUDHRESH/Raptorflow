"use client";

import React, { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { ChevronDown, Check } from "lucide-react";

/* ══════════════════════════════════════════════════════════════════════════════
   BLUEPRINT SELECT — Technical Dropdown
   Features:
   - Technical label styling
   - Dropdown with paper texture
   - Options with technical codes
   - Pencil stroke on focus
   ══════════════════════════════════════════════════════════════════════════════ */

interface Option {
    value: string;
    label: string;
    code?: string;
    disabled?: boolean;
}

interface BlueprintSelectProps {
    options: Option[];
    value?: string;
    onChange?: (value: string) => void;
    label?: string;
    code?: string;
    placeholder?: string;
    disabled?: boolean;
    className?: string;
}

export function BlueprintSelect({
    options,
    value,
    onChange,
    label,
    code,
    placeholder = "Select option...",
    disabled = false,
    className,
}: BlueprintSelectProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const containerRef = useRef<HTMLDivElement>(null);
    const buttonRef = useRef<HTMLButtonElement>(null);

    const selectedOption = options.find((opt) => opt.value === value);

    // Close on outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Get dimensions for pencil stroke
    useEffect(() => {
        if (buttonRef.current) {
            const observer = new ResizeObserver((entries) => {
                for (const entry of entries) {
                    setDimensions({
                        width: entry.contentRect.width + 2,
                        height: entry.contentRect.height + 2,
                    });
                }
            });
            observer.observe(buttonRef.current);
            return () => observer.disconnect();
        }
    }, []);

    const pathLength = 2 * (dimensions.width + dimensions.height);

    return (
        <div ref={containerRef} className={cn("relative", className)}>
            {/* Label */}
            {label && (
                <div className="flex items-center gap-2 mb-2">
                    <span className="font-technical text-[var(--muted)]">{label.toUpperCase()}</span>
                    {code && (
                        <>
                            <div className="h-px flex-1 bg-[var(--blueprint-line)]" />
                            <span className="font-technical text-[var(--blueprint)]">{code}</span>
                        </>
                    )}
                </div>
            )}

            {/* Select button */}
            <div className="relative">
                {/* Pencil stroke */}
                {dimensions.width > 0 && (
                    <svg
                        className="absolute inset-0 pointer-events-none overflow-visible z-10"
                        style={{ left: -1, top: -1, width: dimensions.width, height: dimensions.height }}
                    >
                        <rect
                            x="0.5"
                            y="0.5"
                            width={dimensions.width - 1}
                            height={dimensions.height - 1}
                            rx="4"
                            ry="4"
                            fill="none"
                            stroke="var(--blueprint)"
                            strokeWidth="1.5"
                            strokeDasharray={pathLength}
                            strokeDashoffset={isOpen ? 0 : pathLength}
                            style={{ transition: "stroke-dashoffset 0.4s cubic-bezier(0.4, 0, 0.2, 1)" }}
                        />
                    </svg>
                )}

                <button
                    ref={buttonRef}
                    type="button"
                    disabled={disabled}
                    onClick={() => setIsOpen(!isOpen)}
                    className={cn(
                        "w-full h-10 px-4 flex items-center justify-between gap-2",
                        "bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)]",
                        "text-sm text-left transition-all duration-200",
                        "focus:outline-none focus:border-[var(--blueprint)]",
                        "ink-bleed-xs",
                        disabled && "opacity-50 cursor-not-allowed",
                        isOpen && "border-[var(--blueprint)]"
                    )}
                >
                    <span className={selectedOption ? "text-[var(--ink)]" : "text-[var(--placeholder)]"}>
                        {selectedOption?.label || placeholder}
                    </span>
                    <ChevronDown
                        size={14}
                        strokeWidth={1.5}
                        className={cn(
                            "text-[var(--muted)] transition-transform duration-200",
                            isOpen && "rotate-180"
                        )}
                    />
                </button>
            </div>

            {/* Dropdown */}
            {isOpen && (
                <div className="absolute z-50 w-full mt-1 py-1 bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-sm)] ink-bleed-md overflow-hidden">
                    {/* Corner marks */}
                    <div className="absolute -top-px -left-px w-3 h-3 border-t border-l border-[var(--blueprint)]" />
                    <div className="absolute -top-px -right-px w-3 h-3 border-t border-r border-[var(--blueprint)]" />

                    {options.map((option, index) => (
                        <button
                            key={option.value}
                            type="button"
                            disabled={option.disabled}
                            onClick={() => {
                                onChange?.(option.value);
                                setIsOpen(false);
                            }}
                            className={cn(
                                "w-full px-4 py-2 flex items-center gap-3 text-sm text-left",
                                "transition-colors duration-150",
                                option.value === value
                                    ? "bg-[var(--blueprint-light)] text-[var(--ink)]"
                                    : "text-[var(--secondary)] hover:bg-[var(--canvas)]",
                                option.disabled && "opacity-50 cursor-not-allowed"
                            )}
                        >
                            {/* Row number */}
                            <span className="font-technical text-[10px] text-[var(--muted)] w-4">
                                {String(index + 1).padStart(2, "0")}
                            </span>

                            <span className="flex-1">{option.label}</span>

                            {option.code && (
                                <span className="font-technical text-[var(--blueprint)]">{option.code}</span>
                            )}

                            {option.value === value && (
                                <Check size={14} strokeWidth={1.5} className="text-[var(--blueprint)]" />
                            )}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}

export default BlueprintSelect;
