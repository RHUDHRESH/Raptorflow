"use client";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import dynamic from 'next/dynamic';
import { CreditCard, CheckCircle2, History } from "lucide-react";

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.SecondaryButton })), { ssr: false });

export const runtime = 'edge';

export default function BillingSettingsPage() {
    return (
        <div className="space-y-8 max-w-3xl">
            <div>
                <h2 className="text-xl font-semibold text-[var(--ink)]">Billing & Plans</h2>
                <p className="text-sm text-[var(--secondary)]">Manage your subscription and payment methods.</p>
            </div>

            {/* Current Plan */}
            <BlueprintCard showCorners className="bg-[var(--ink)] border-[var(--ink)] text-[var(--paper)]">
                <div className="flex items-start justify-between">
                    <div className="space-y-4">
                        <div className="space-y-1">
                            <div className="flex items-center gap-2">
                                <span className="font-technical text-[var(--blueprint)]">CURRENT PLAN</span>
                                <BlueprintBadge variant="blueprint" size="sm">PRO</BlueprintBadge>
                            </div>
                            <h3 className="text-2xl font-editorial">RaptorFlow Professional</h3>
                        </div>
                        <div className="flex flex-col gap-2 pt-2">
                            {["Unlimited Moves", "Using GPT-4o Model", "Advanced Analytics", "Priority Support"].map((feat, i) => (
                                <div key={i} className="flex items-center gap-2 text-sm text-[var(--paper)]/80">
                                    <CheckCircle2 size={14} className="text-[var(--success)]" />
                                    {feat}
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-3xl font-mono font-bold">$49<span className="text-sm font-normal text-[var(--paper)]/60">/mo</span></p>
                        <p className="text-xs text-[var(--paper)]/60 mb-4">Renews on Feb 12, 2026</p>
                        <SecondaryButton className="bg-[var(--paper)] text-[var(--ink)] hover:bg-[var(--paper)]/90 border-transparent">
                            Manage Subscription
                        </SecondaryButton>
                    </div>
                </div>
            </BlueprintCard>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <BlueprintCard title="Payment Method" code="PAY-01" padding="md" showCorners>
                    <div className="flex items-center justify-between p-3 border border-[var(--border)] rounded-[var(--radius-sm)] bg-[var(--canvas)]">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius-xs)]">
                                <CreditCard size={20} className="text-[var(--ink)]" />
                            </div>
                            <div>
                                <p className="text-sm font-bold text-[var(--ink)]">•••• 4242</p>
                                <p className="text-xs text-[var(--muted)]">Expires 12/28</p>
                            </div>
                        </div>
                        <button className="text-xs font-medium text-[var(--blueprint)] hover:underline">Edit</button>
                    </div>
                    <div className="mt-4">
                        <SecondaryButton size="sm" className="w-full justify-center">Add Payment Method</SecondaryButton>
                    </div>
                </BlueprintCard>

                <BlueprintCard title="Invoice History" code="INV-01" padding="none" showCorners>
                    <div className="divide-y divide-[var(--border-subtle)]">
                        {[
                            { date: "Jan 12, 2026", amount: "$49.00", status: "Paid" },
                            { date: "Dec 12, 2025", amount: "$49.00", status: "Paid" },
                            { date: "Nov 12, 2025", amount: "$49.00", status: "Paid" },
                        ].map((inv, i) => (
                            <div key={i} className="flex items-center justify-between p-3 hover:bg-[var(--canvas)] transition-colors cursor-pointer">
                                <div className="flex items-center gap-3">
                                    <History size={14} className="text-[var(--muted)]" />
                                    <span className="text-sm text-[var(--ink)]">{inv.date}</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="text-sm font-mono text-[var(--ink)]">{inv.amount}</span>
                                    <BlueprintBadge variant="success" size="sm">{inv.status}</BlueprintBadge>
                                </div>
                            </div>
                        ))}
                    </div>
                </BlueprintCard>
            </div>
        </div>
    );
}
