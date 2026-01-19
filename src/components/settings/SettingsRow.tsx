"use client";

import React, { ReactNode } from "react";

// ═══════════════════════════════════════════════════════════════
// SettingsRow - Standardized settings row with label and control
// ═══════════════════════════════════════════════════════════════

interface SettingsRowProps {
    /** Row label */
    label: string;
    /** Optional description text */
    description?: string;
    /** Control element (input, toggle, button, etc.) */
    children: ReactNode;
    /** Optional action on the right */
    action?: ReactNode;
    /** Whether this is the last row (no bottom border) */
    isLast?: boolean;
}

export function SettingsRow({
    label,
    description,
    children,
    action,
    isLast = false,
}: SettingsRowProps) {
    return (
        <div
            className={`
        flex items-center justify-between py-4
        ${isLast ? "" : "border-b border-[var(--border)]"}
      `}
        >
            <div className="flex-1 min-w-0 pr-4">
                <p className="text-sm font-medium text-[var(--ink)]">{label}</p>
                {description && (
                    <p className="text-xs text-[var(--muted)] mt-0.5 leading-relaxed">
                        {description}
                    </p>
                )}
            </div>
            <div className="flex items-center gap-3">
                {children}
                {action}
            </div>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════
// SettingsGroup - Groups related rows with a title
// ═══════════════════════════════════════════════════════════════

interface SettingsGroupProps {
    title?: string;
    description?: string;
    children: ReactNode;
}

export function SettingsGroup({ title, description, children }: SettingsGroupProps) {
    return (
        <div className="mb-8 last:mb-0">
            {title && (
                <div className="mb-4">
                    <h3 className="text-sm font-semibold text-[var(--ink)] uppercase tracking-wider">
                        {title}
                    </h3>
                    {description && (
                        <p className="text-xs text-[var(--muted)] mt-1">{description}</p>
                    )}
                </div>
            )}
            <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl p-6">
                {children}
            </div>
        </div>
    );
}
