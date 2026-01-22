"use client";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { useAuth } from "@/components/auth/AuthProvider";
import dynamic from 'next/dynamic';

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.SecondaryButton })), { ssr: false });
const BlueprintAvatar = dynamic(() => import("@/components/ui/BlueprintAvatar").then(mod => ({ default: mod.BlueprintAvatar })), { ssr: false });

export const runtime = 'edge';

export default function ProfileSettingsPage() {
    const { user } = useAuth();

    // Extract user info
    const displayName = user ? user.email.split('@')[0].charAt(0).toUpperCase() + user.email.split('@')[0].slice(1) : "User";
    const email = user?.email || "user@example.com";
    const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-xl font-semibold text-[var(--ink)]">Profile</h2>
                <p className="text-sm text-[var(--secondary)]">Manage your personal information and account access.</p>
            </div>

            <BlueprintCard title="Public Profile" code="PRF-01" padding="lg" showCorners>
                <div className="align-start gap-6">
                    <div className="h-20 w-20 rounded-full bg-[var(--blueprint)] text-white text-xl font-bold flex items-center justify-center">{initials}</div>
                    <div className="space-y-4 flex-1">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs font-technical text-[var(--muted)]">DISPLAY NAME</label>
                                <input
                                    type="text"
                                    defaultValue={displayName}
                                    className="w-full h-10 px-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] transition-colors blueprint-focus"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-technical text-[var(--muted)]">EMAIL ADDRESS</label>
                                <input
                                    type="email"
                                    defaultValue={email}
                                    className="w-full h-10 px-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] transition-colors blueprint-focus"
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-technical text-[var(--muted)]">BIO / ROLE</label>
                            <textarea
                                defaultValue="Building the future of marketing automation."
                                className="w-full h-24 p-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] transition-colors resize-none blueprint-focus"
                            />
                        </div>
                    </div>
                </div>
                <div className="mt-6 flex justify-end gap-3 pt-6 border-t border-[var(--border-subtle)]">
                    <button className="bg-[var(--paper)] text-[var(--ink)] hover:bg-[var(--paper)]/90 border-transparent">Cancel</button>
                    <button className="bg-[var(--blueprint)] text-[var(--paper)] hover:bg-[var(--blueprint)]/90 border-transparent">Save Changes</button>
                </div>
            </BlueprintCard>

            <BlueprintCard title="Account Security" code="SEC-01" padding="lg" showCorners>
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h4 className="text-sm font-semibold text-[var(--ink)]">Password</h4>
                            <p className="text-xs text-[var(--secondary)]">Last changed 3 months ago</p>
                        </div>
                        <button className="bg-[var(--blueprint)] text-[var(--paper)] hover:bg-[var(--blueprint)]/90 border-transparent">Update Password</button>
                    </div>
                    <div className="h-px bg-[var(--border-subtle)]" />
                    <div className="flex items-center justify-between">
                        <div>
                            <h4 className="text-sm font-semibold text-[var(--ink)]">Two-Factor Authentication</h4>
                            <p className="text-xs text-[var(--secondary)]">Add an extra layer of security to your account</p>
                        </div>
                        <button className="bg-[var(--blueprint)] text-[var(--paper)] hover:bg-[var(--blueprint)]/90 border-transparent">Enable 2FA</button>
                    </div>
                </div>
            </BlueprintCard>
        </div>
    );
}
