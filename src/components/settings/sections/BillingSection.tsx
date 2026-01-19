"use client";

import React from "react";
import { SettingsGroup } from "../SettingsRow";

// ═══════════════════════════════════════════════════════════════
// BillingSection - Plan and payment settings
// ═══════════════════════════════════════════════════════════════

export function BillingSection() {
    return (
        <div className="space-y-8">
            {/* Page Header */}
            <div>
                <h2 className="text-2xl font-semibold text-[var(--ink)]">Billing</h2>
                <p className="text-sm text-[var(--muted)] mt-1">
                    Manage your subscription and payment
                </p>
            </div>

            {/* Current Plan */}
            <SettingsGroup title="Current Plan">
                <div className="flex items-center justify-between p-4 bg-[var(--canvas)] border border-[var(--border)] rounded-xl">
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-lg font-semibold text-[var(--ink)]">Glide</h3>
                            <span className="px-2 py-0.5 bg-[var(--ink)] text-[var(--canvas)] text-xs font-medium rounded-full">
                                Pro
                            </span>
                        </div>
                        <p className="text-sm text-[var(--muted)] mt-1">
                            Billed monthly · Renews Jan 31, 2026
                        </p>
                    </div>
                    <div className="text-right">
                        <p className="text-2xl font-bold text-[var(--ink)]">
                            $79
                            <span className="text-sm font-normal text-[var(--muted)]">/mo</span>
                        </p>
                    </div>
                </div>

                <div className="flex gap-3 mt-4">
                    <button className="flex-1 px-4 py-2.5 bg-[var(--ink)] text-[var(--canvas)] rounded-xl text-sm font-medium hover:opacity-90 transition-opacity">
                        Upgrade Plan
                    </button>
                    <button className="flex-1 px-4 py-2.5 border border-[var(--border)] text-[var(--ink)] rounded-xl text-sm font-medium hover:border-[var(--ink)] transition-colors">
                        Manage Subscription
                    </button>
                </div>
            </SettingsGroup>

            {/* Payment Method */}
            <SettingsGroup title="Payment Method">
                <div className="flex items-center justify-between p-4 bg-[var(--canvas)] border border-[var(--border)] rounded-xl">
                    <div className="flex items-center gap-4">
                        {/* Card Icon */}
                        <div className="w-12 h-8 bg-[var(--ink)] rounded text-[var(--canvas)] text-xs font-bold flex items-center justify-center">
                            VISA
                        </div>
                        <div>
                            <p className="text-sm font-medium text-[var(--ink)]">
                                •••• •••• •••• 4242
                            </p>
                            <p className="text-xs text-[var(--muted)]">Expires 12/28</p>
                        </div>
                    </div>
                    <button className="text-sm text-[var(--ink)] font-medium hover:underline">
                        Update
                    </button>
                </div>
            </SettingsGroup>

            {/* Billing History */}
            <SettingsGroup title="Billing History">
                <div className="space-y-3">
                    {[
                        { date: "Jan 1, 2026", amount: "$79.00", status: "Paid" },
                        { date: "Dec 1, 2025", amount: "$79.00", status: "Paid" },
                        { date: "Nov 1, 2025", amount: "$79.00", status: "Paid" },
                    ].map((invoice, i) => (
                        <div
                            key={i}
                            className="flex items-center justify-between py-3 border-b border-[var(--border)] last:border-0"
                        >
                            <div className="flex items-center gap-4">
                                <span className="text-sm text-[var(--ink)]">{invoice.date}</span>
                                <span className="text-sm font-medium text-[var(--ink)]">
                                    {invoice.amount}
                                </span>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className="text-xs text-green-600 font-medium">{invoice.status}</span>
                                <button className="text-xs text-[var(--ink)] hover:underline">
                                    Download
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                <button className="text-sm text-[var(--ink)] font-medium hover:underline mt-4">
                    View all invoices →
                </button>
            </SettingsGroup>
        </div>
    );
}
