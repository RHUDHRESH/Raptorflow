"use client";

import React from "react";
import { Camera02Icon } from "hugeicons-react";
import { SettingsGroup, SettingsRow } from "../SettingsRow";
import { SettingsInput, SettingsTextarea } from "../SettingsInput";

// ═══════════════════════════════════════════════════════════════
// ProfileSection - User profile settings
// ═══════════════════════════════════════════════════════════════

interface ProfileData {
    displayName: string;
    email: string;
    bio: string;
}

interface ProfileSectionProps {
    data: ProfileData;
    onChange: (field: keyof ProfileData, value: string) => void;
    onSave: () => void;
    hasChanges: boolean;
    saving: boolean;
}

export function ProfileSection({
    data,
    onChange,
    onSave,
    hasChanges,
    saving,
}: ProfileSectionProps) {
    const initials = data.displayName
        .split(" ")
        .map((n) => n[0])
        .join("")
        .slice(0, 2)
        .toUpperCase();

    return (
        <div className="space-y-8">
            {/* Page Header */}
            <div>
                <h2 className="text-2xl font-semibold text-[var(--ink)]">Profile</h2>
                <p className="text-sm text-[var(--muted)] mt-1">
                    Manage your personal information
                </p>
            </div>

            {/* Avatar Section */}
            <SettingsGroup title="Photo">
                <div className="flex items-center gap-6">
                    {/* Avatar */}
                    <div className="w-20 h-20 rounded-full bg-[var(--ink)] flex items-center justify-center text-[var(--canvas)] text-2xl font-bold">
                        {initials || "U"}
                    </div>

                    {/* Upload Actions */}
                    <div>
                        <button className="flex items-center gap-2 px-4 py-2 bg-[var(--canvas)] border border-[var(--border)] rounded-xl text-sm font-medium text-[var(--ink)] hover:border-[var(--ink)] transition-colors">
                            {React.createElement(Camera02Icon as any, { className: "w-4 h-4" })}
                            Change photo
                        </button>
                        <p className="text-xs text-[var(--muted)] mt-2">
                            JPG, PNG or GIF. Max 2MB.
                        </p>
                    </div>
                </div>
            </SettingsGroup>

            {/* Info Section */}
            <SettingsGroup title="Information">
                <div className="space-y-5">
                    <div className="grid grid-cols-2 gap-4">
                        <SettingsInput
                            label="Display Name"
                            value={data.displayName}
                            onChange={(e) => onChange("displayName", e.target.value)}
                            placeholder="Your name"
                        />
                        <SettingsInput
                            label="Email"
                            type="email"
                            value={data.email}
                            onChange={(e) => onChange("email", e.target.value)}
                            placeholder="you@example.com"
                        />
                    </div>

                    <SettingsTextarea
                        label="Bio"
                        value={data.bio}
                        onChange={(e) => onChange("bio", e.target.value)}
                        placeholder="Tell us about yourself..."
                        rows={3}
                        helperText="Brief description for your profile."
                    />
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
