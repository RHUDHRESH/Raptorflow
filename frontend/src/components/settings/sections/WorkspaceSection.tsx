"use client";

import React from "react";
import { SettingsGroup } from "../SettingsRow";
import { SettingsInput, SettingsSelect } from "../SettingsInput";

// ═══════════════════════════════════════════════════════════════
// WorkspaceSection - Workspace configuration
// ═══════════════════════════════════════════════════════════════

interface WorkspaceData {
    name: string;
    industry: string;
    timezone: string;
}

interface WorkspaceSectionProps {
    data: WorkspaceData;
    onChange: (field: keyof WorkspaceData, value: string) => void;
    onSave: () => void;
    hasChanges: boolean;
    saving: boolean;
}

const INDUSTRIES = [
    { value: "b2b-saas", label: "B2B SaaS" },
    { value: "ecommerce", label: "E-commerce" },
    { value: "agency", label: "Agency" },
    { value: "consulting", label: "Consulting" },
    { value: "fintech", label: "Fintech" },
    { value: "healthcare", label: "Healthcare" },
    { value: "education", label: "Education" },
    { value: "other", label: "Other" },
];

const TIMEZONES = [
    { value: "Asia/Kolkata", label: "Asia/Kolkata (IST)" },
    { value: "America/New_York", label: "America/New_York (EST)" },
    { value: "America/Los_Angeles", label: "America/Los_Angeles (PST)" },
    { value: "Europe/London", label: "Europe/London (GMT)" },
    { value: "Europe/Paris", label: "Europe/Paris (CET)" },
    { value: "Asia/Tokyo", label: "Asia/Tokyo (JST)" },
    { value: "Australia/Sydney", label: "Australia/Sydney (AEST)" },
];

export function WorkspaceSection({
    data,
    onChange,
    onSave,
    hasChanges,
    saving,
}: WorkspaceSectionProps) {
    return (
        <div className="space-y-8">
            {/* Page Header */}
            <div>
                <h2 className="text-2xl font-semibold text-[var(--ink)]">Workspace</h2>
                <p className="text-sm text-[var(--muted)] mt-1">
                    Configure your workspace settings
                </p>
            </div>

            {/* General Settings */}
            <SettingsGroup title="General">
                <div className="space-y-5">
                    <SettingsInput
                        label="Workspace Name"
                        value={data.name}
                        onChange={(e) => onChange("name", e.target.value)}
                        placeholder="My Workspace"
                    />

                    <div className="grid grid-cols-2 gap-4">
                        <SettingsSelect
                            label="Industry"
                            value={data.industry}
                            onChange={(e) => onChange("industry", e.target.value)}
                            options={INDUSTRIES}
                        />

                        <SettingsSelect
                            label="Timezone"
                            value={data.timezone}
                            onChange={(e) => onChange("timezone", e.target.value)}
                            options={TIMEZONES}
                        />
                    </div>
                </div>
            </SettingsGroup>

            {/* Danger Zone */}
            <SettingsGroup title="Danger Zone" description="Irreversible actions">
                <div className="flex items-center justify-between py-2">
                    <div>
                        <p className="text-sm font-medium text-[var(--ink)]">Delete Workspace</p>
                        <p className="text-xs text-[var(--muted)] mt-0.5">
                            Permanently delete this workspace and all its data
                        </p>
                    </div>
                    <button className="px-4 py-2 border border-red-300 text-red-600 rounded-xl text-sm font-medium hover:bg-red-50 transition-colors">
                        Delete
                    </button>
                </div>
            </SettingsGroup>

            {/* Save Button */}
            {hasChanges && (
                <div className="flex justify-end pt-4 border-t border-[var(--border)]">
                    <button
                        onClick={onSave}
                        disabled={saving}
                        className="px-6 py-2.5 bg-[var(--ink)] text-[var(--canvas)] rounded-xl text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
                    >
                        {saving ? "Saving..." : "Save changes"}
                    </button>
                </div>
            )}
        </div>
    );
}
