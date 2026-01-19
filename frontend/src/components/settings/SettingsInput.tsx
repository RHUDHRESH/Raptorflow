"use client";

import React from "react";
import { cn } from "@/lib/utils";

// ═══════════════════════════════════════════════════════════════
// SettingsInput - Styled input field
// ═══════════════════════════════════════════════════════════════

interface SettingsInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    /** Input label */
    label?: string;
    /** Helper text below input */
    helperText?: string;
    /** Error message */
    error?: string;
}

export function SettingsInput({
    label,
    helperText,
    error,
    className,
    ...props
}: SettingsInputProps) {
    return (
        <div className="w-full">
            {label && (
                <label className="block text-xs font-medium text-[var(--muted)] uppercase tracking-wider mb-2">
                    {label}
                </label>
            )}
            <input
                className={cn(
                    "w-full h-11 px-4 bg-[var(--canvas)] border rounded-xl text-sm text-[var(--ink)]",
                    "placeholder:text-[var(--muted)]",
                    "focus:outline-none focus:border-[var(--ink)] focus:ring-1 focus:ring-[var(--ink)]",
                    "transition-colors duration-150",
                    error
                        ? "border-red-400 focus:border-red-400 focus:ring-red-400"
                        : "border-[var(--border)]",
                    className
                )}
                {...props}
            />
            {helperText && !error && (
                <p className="text-xs text-[var(--muted)] mt-1.5">{helperText}</p>
            )}
            {error && (
                <p className="text-xs text-red-500 mt-1.5">{error}</p>
            )}
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════
// SettingsTextarea - Styled textarea field
// ═══════════════════════════════════════════════════════════════

interface SettingsTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
    label?: string;
    helperText?: string;
    error?: string;
}

export function SettingsTextarea({
    label,
    helperText,
    error,
    className,
    ...props
}: SettingsTextareaProps) {
    return (
        <div className="w-full">
            {label && (
                <label className="block text-xs font-medium text-[var(--muted)] uppercase tracking-wider mb-2">
                    {label}
                </label>
            )}
            <textarea
                className={cn(
                    "w-full p-4 bg-[var(--canvas)] border rounded-xl text-sm text-[var(--ink)] resize-none",
                    "placeholder:text-[var(--muted)]",
                    "focus:outline-none focus:border-[var(--ink)] focus:ring-1 focus:ring-[var(--ink)]",
                    "transition-colors duration-150",
                    error
                        ? "border-red-400 focus:border-red-400 focus:ring-red-400"
                        : "border-[var(--border)]",
                    className
                )}
                {...props}
            />
            {helperText && !error && (
                <p className="text-xs text-[var(--muted)] mt-1.5">{helperText}</p>
            )}
            {error && (
                <p className="text-xs text-red-500 mt-1.5">{error}</p>
            )}
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════
// SettingsSelect - Styled select dropdown
// ═══════════════════════════════════════════════════════════════

interface SettingsSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
    label?: string;
    options: { value: string; label: string }[];
}

export function SettingsSelect({
    label,
    options,
    className,
    ...props
}: SettingsSelectProps) {
    return (
        <div className="w-full">
            {label && (
                <label className="block text-xs font-medium text-[var(--muted)] uppercase tracking-wider mb-2">
                    {label}
                </label>
            )}
            <select
                className={cn(
                    "w-full h-11 px-4 bg-[var(--canvas)] border border-[var(--border)] rounded-xl text-sm text-[var(--ink)]",
                    "focus:outline-none focus:border-[var(--ink)]",
                    "transition-colors duration-150",
                    "appearance-none cursor-pointer",
                    className
                )}
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236B7280'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`,
                    backgroundRepeat: "no-repeat",
                    backgroundPosition: "right 12px center",
                    backgroundSize: "16px",
                }}
                {...props}
            >
                {options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                        {opt.label}
                    </option>
                ))}
            </select>
        </div>
    );
}
