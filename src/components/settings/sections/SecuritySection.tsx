"use client";

import React from "react";
import { SettingsGroup, SettingsRow } from "../SettingsRow";

// ═══════════════════════════════════════════════════════════════
// SecuritySection - Security settings
// ═══════════════════════════════════════════════════════════════

export function SecuritySection() {
    return (
        <div className="space-y-8">
            {/* Page Header */}
            <div>
                <h2 className="text-2xl font-semibold text-[var(--ink)]">Security</h2>
                <p className="text-sm text-[var(--muted)] mt-1">
                    Manage your account security
                </p>
            </div>

            {/* Password */}
            <SettingsGroup title="Authentication">
                <SettingsRow
                    label="Password"
                    description="Last changed 3 months ago"
                    action={
                        <button className="text-sm text-[var(--ink)] font-medium hover:underline">
                            Change
                        </button>
                    }
                >
                    <span className="text-sm text-[var(--muted)]">••••••••</span>
                </SettingsRow>

                <SettingsRow
                    label="Two-factor authentication"
                    description="Add an extra layer of security"
                    isLast
                >
                    <span className="inline-flex items-center gap-1.5 px-2 py-1 bg-green-50 text-green-700 text-xs font-medium rounded-full">
                        <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                        Enabled
                    </span>
                    <button className="text-sm text-[var(--ink)] font-medium hover:underline ml-3">
                        Manage
                    </button>
                </SettingsRow>
            </SettingsGroup>

            {/* Sessions */}
            <SettingsGroup title="Sessions" description="Devices where you're logged in">
                <div className="space-y-4">
                    {/* Current Session */}
                    <div className="flex items-center justify-between p-4 bg-[var(--canvas)] border border-[var(--border)] rounded-xl">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-[var(--surface)] rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-[var(--muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <rect x="2" y="3" width="20" height="14" rx="2" strokeWidth="1.5" />
                                    <path d="M8 21h8M12 17v4" strokeWidth="1.5" />
                                </svg>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-[var(--ink)]">
                                    Windows · Chrome
                                </p>
                                <p className="text-xs text-[var(--muted)]">
                                    Current session · Mumbai, India
                                </p>
                            </div>
                        </div>
                        <span className="text-xs text-green-600 font-medium">Active now</span>
                    </div>

                    {/* Other Session */}
                    <div className="flex items-center justify-between p-4 bg-[var(--canvas)] border border-[var(--border)] rounded-xl">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-[var(--surface)] rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-[var(--muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <rect x="5" y="2" width="14" height="20" rx="2" strokeWidth="1.5" />
                                    <path d="M12 18h.01" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-[var(--ink)]">
                                    iPhone · Safari
                                </p>
                                <p className="text-xs text-[var(--muted)]">
                                    Last active 2 days ago · Mumbai, India
                                </p>
                            </div>
                        </div>
                        <button className="text-xs text-red-500 font-medium hover:underline">
                            Revoke
                        </button>
                    </div>
                </div>

                <div className="pt-4 mt-4 border-t border-[var(--border)]">
                    <button className="text-sm text-red-500 font-medium hover:underline">
                        Sign out of all devices
                    </button>
                </div>
            </SettingsGroup>
        </div>
    );
}
