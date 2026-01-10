"use client";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import dynamic from 'next/dynamic';
import { Shield, Key, Smartphone, History, LogOut } from "lucide-react";

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.SecondaryButton })), { ssr: false });

export const runtime = 'edge';

export default function SecuritySettingsPage() {
    return (
        <div className="space-y-8 max-w-3xl">
            <div>
                <h2 className="text-xl font-semibold text-[var(--ink)]">Security</h2>
                <p className="text-sm text-[var(--secondary)]">Protect your account and review login activity.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <BlueprintCard title="Authentication" code="SEC-01" padding="lg" showCorners>
                    <div className="space-y-6">
                        <div className="align-start gap-3">
                            <div className="p-2 bg-[var(--surface)] rounded-[var(--radius-sm)]">
                                <Key size={20} className="text-[var(--ink)]" />
                            </div>
                            <div className="flex-1">
                                <h4 className="text-sm font-semibold text-[var(--ink)]">Password</h4>
                                <p className="text-xs text-[var(--secondary)] mb-3">Last changed 90 days ago.</p>
                                <SecondaryButton size="sm">Change Password</SecondaryButton>
                            </div>
                        </div>
                        <div className="h-px bg-[var(--border-subtle)]" />
                        <div className="align-start gap-3">
                            <div className="p-2 bg-[var(--surface)] rounded-[var(--radius-sm)]">
                                <Smartphone size={20} className="text-[var(--ink)]" />
                            </div>
                            <div className="flex-1">
                                <h4 className="text-sm font-semibold text-[var(--ink)]">2-Step Verification</h4>
                                <p className="text-xs text-[var(--secondary)] mb-3">Add additional security to your account.</p>
                                <BlueprintButton variant="secondary" size="sm">Enable 2FA</BlueprintButton>
                            </div>
                        </div>
                    </div>
                </BlueprintCard>

                <BlueprintCard title="Active Sessions" code="SES-01" padding="none" showCorners>
                    <div className="divide-y divide-[var(--border-subtle)]">
                        {[
                            { device: "Chrome / Windows", loc: "New York, USA", active: true, time: "Now" },
                            { device: "Safari / iPhone 14", loc: "New York, USA", active: false, time: "2h ago" },
                            { device: "Chrome / Mac", loc: "London, UK", active: false, time: "3d ago" },
                        ].map((session, i) => (
                            <div key={i} className="p-4 align-between hover:bg-[var(--canvas)] transition-colors">
                                <div>
                                    <div className="align-center gap-2">
                                        <p className="text-sm font-medium text-[var(--ink)]">{session.device}</p>
                                        {session.active && <BlueprintBadge variant="success" size="sm" dot>Current</BlueprintBadge>}
                                    </div>
                                    <p className="text-xs text-[var(--muted)]">{session.loc} • {session.time}</p>
                                </div>
                                {!session.active && (
                                    <button className="text-[var(--muted)] hover:text-[var(--ink)] transition-colors">
                                        <LogOut size={14} />
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                    <div className="p-3 border-t border-[var(--border-subtle)] bg-[var(--canvas)] text-center">
                        <button className="text-xs text-[var(--warning)] font-medium hover:underline">Sign out of all other sessions</button>
                    </div>
                </BlueprintCard>
            </div>

            <BlueprintCard title="Audit Log" code="AUD-01" padding="none" showCorners>
                <div className="p-4 bg-[var(--canvas)] border-b border-[var(--border-subtle)]">
                    <span className="text-xs font-technical text-[var(--muted)]">RECENT SENSITIVE ACTIONS</span>
                </div>
                <div className="divide-y divide-[var(--border-subtle)]">
                    {[
                        { action: "API Key Created", user: "Bossman", time: "Today, 10:23 AM" },
                        { action: "Billing Updated", user: "Sarah K.", time: "Yesterday, 4:15 PM" },
                        { action: "Member Removed", user: "Bossman", time: "Jan 2, 2:00 PM" },
                    ].map((log, i) => (
                        <div key={i} className="p-4 align-between hover:bg-[var(--canvas)] transition-colors">
                            <div className="align-center gap-3">
                                <History size={14} className="text-[var(--muted)]" />
                                <span className="text-sm font-medium text-[var(--ink)]">{log.action}</span>
                            </div>
                            <span className="text-xs text-[var(--muted)]">{log.user} • {log.time}</span>
                        </div>
                    ))}
                </div>
            </BlueprintCard>
        </div>
    );
}
