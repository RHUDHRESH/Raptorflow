"use client";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import dynamic from 'next/dynamic';

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.SecondaryButton })), { ssr: false });
const BlueprintAvatar = dynamic(() => import("@/components/ui/BlueprintAvatar").then(mod => ({ default: mod.BlueprintAvatar })), { ssr: false });

export const runtime = 'edge';

export default function ProfileSettingsPage() {
    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-xl font-semibold text-[var(--ink)]">Profile</h2>
                <p className="text-sm text-[var(--secondary)]">Manage your personal information and account access.</p>
            </div>

            <BlueprintCard title="Public Profile" code="PRF-01" padding="lg" showCorners>
                <div className="align-start gap-6">
                    <BlueprintAvatar initials="BM" size="lg" className="h-20 w-20 text-xl" />
                    <div className="space-y-4 flex-1">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs font-technical text-[var(--muted)]">DISPLAY NAME</label>
                                <input
                                    type="text"
                                    defaultValue="Bossman"
                                    className="w-full h-10 px-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] transition-colors blueprint-focus"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-technical text-[var(--muted)]">EMAIL ADDRESS</label>
                                <input
                                    type="email"
                                    defaultValue="bossman@raptorflow.ai"
                                    className="w-full h-10 px-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] transition-colors blueprint-focus"
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-technical text-[var(--muted)]">BIO / ROLE</label>
                            <textarea
                                defaultValue="Founder & CEO. Building the future of marketing automation."
                                className="w-full h-24 p-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] transition-colors resize-none blueprint-focus"
                            />
                        </div>
                    </div>
                </div>
                <div className="mt-6 flex justify-end gap-3 pt-6 border-t border-[var(--border-subtle)]">
                    <SecondaryButton>Cancel</SecondaryButton>
                    <BlueprintButton>Save Changes</BlueprintButton>
                </div>
            </BlueprintCard>

            <BlueprintCard title="Account Security" code="SEC-01" padding="lg" showCorners>
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h4 className="text-sm font-semibold text-[var(--ink)]">Password</h4>
                            <p className="text-xs text-[var(--secondary)]">Last changed 3 months ago</p>
                        </div>
                        <SecondaryButton size="sm">Update Password</SecondaryButton>
                    </div>
                    <div className="h-px bg-[var(--border-subtle)]" />
                    <div className="flex items-center justify-between">
                        <div>
                            <h4 className="text-sm font-semibold text-[var(--ink)]">Two-Factor Authentication</h4>
                            <p className="text-xs text-[var(--secondary)]">Add an extra layer of security to your account</p>
                        </div>
                        <BlueprintButton variant="secondary" size="sm">Enable 2FA</BlueprintButton>
                    </div>
                </div>
            </BlueprintCard>
        </div>
    );
}
