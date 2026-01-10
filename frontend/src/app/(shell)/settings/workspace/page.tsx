"use client";

import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import dynamic from 'next/dynamic';
import { Users, Building, Globe } from "lucide-react";

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.SecondaryButton })), { ssr: false });

export const runtime = 'edge';

export default function WorkspaceSettingsPage() {
    return (
        <div className="space-y-8 max-w-3xl">
            <div>
                <h2 className="text-xl font-semibold text-[var(--ink)]">Workspace</h2>
                <p className="text-sm text-[var(--secondary)]">Manage your team and organizational settings.</p>
            </div>

            <BlueprintCard title="Organization Details" code="ORG-01" padding="lg" showCorners>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <label className="text-xs font-technical text-[var(--muted)]">WORKSPACE NAME</label>
                        <div className="align-center gap-2">
                            <Building size={16} className="text-[var(--muted)]" />
                            <input
                                type="text"
                                defaultValue="RaptorFlow HQ"
                                className="flex-1 h-10 px-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] transition-colors blueprint-focus"
                            />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-technical text-[var(--muted)]">WORKSPACE URL</label>
                        <div className="align-center gap-2">
                            <Globe size={16} className="text-[var(--muted)]" />
                            <div className="flex-1 align-center h-10 px-3 bg-[var(--canvas)] border border-[var(--border)] rounded-[var(--radius-sm)]">
                                <span className="text-sm text-[var(--muted)]">raptorflow.ai/</span>
                                <input
                                    type="text"
                                    defaultValue="hq"
                                    className="flex-1 bg-transparent text-sm text-[var(--ink)] focus:outline-none blueprint-focus"
                                />
                            </div>
                        </div>
                    </div>
                </div>
                <div className="mt-6 flex justify-end">
                    <BlueprintButton>Update Workspace</BlueprintButton>
                </div>
            </BlueprintCard>

            <BlueprintCard title="Team Members" code="TEAM-01" padding="none" showCorners>
                <div className="p-4 border-b border-[var(--border-subtle)] align-between bg-[var(--canvas)]">
                    <div className="align-center gap-2">
                        <Users size={14} className="text-[var(--muted)]" />
                        <span className="text-xs font-technical text-[var(--muted)]">3 ACTIVE MEMBERS</span>
                    </div>
                    <SecondaryButton size="sm">Invite Member</SecondaryButton>
                </div>
                <div className="divide-y divide-[var(--border-subtle)]">
                    {[
                        { name: "Bossman", email: "bossman@raptorflow.ai", role: "Owner", status: "Active" },
                        { name: "Sarah K.", email: "sarah@raptorflow.ai", role: "Admin", status: "Active" },
                        { name: "John Doe", email: "john@raptorflow.ai", role: "Editor", status: "Pending" },
                    ].map((member, i) => (
                        <div key={i} className="p-4 align-between group hover:bg-[var(--canvas)] transition-colors">
                            <div className="align-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-[var(--ink)] text-[var(--paper)] align-center justify-center text-xs font-bold">
                                    {member.name.substring(0, 2).toUpperCase()}
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-[var(--ink)]">{member.name}</p>
                                    <p className="text-xs text-[var(--secondary)]">{member.email}</p>
                                </div>
                            </div>
                            <div className="align-center gap-4">
                                <BlueprintBadge variant={member.status === "Active" ? "default" : "warning"}>{member.role}</BlueprintBadge>
                                <button className="text-xs text-[var(--muted)] hover:text-[var(--error)] transition-colors opacity-0 group-hover:opacity-100">Remove</button>
                            </div>
                        </div>
                    ))}
                </div>
            </BlueprintCard>
        </div>
    );
}
