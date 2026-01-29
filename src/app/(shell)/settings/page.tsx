"use client";

import React, { useState, useEffect, useCallback } from "react";
import { notify } from "@/lib/notifications";
import { useAuth } from "@/components/auth/AuthProvider";
import { BCMIndicator } from "@/components/bcm/BCMIndicator";
import { BCMRebuildDialog } from "@/components/bcm/BCMRebuildDialog";
import { BCMExportButton } from "@/components/bcm/BCMExportButton";

// Settings components
import { SettingsNav } from "@/components/settings/SettingsNav";
import {
    ProfileSection,
    WorkspaceSection,
    AppearanceSection,
    NotificationsSection,
    SecuritySection,
    BillingSection,
    ACCENT_COLORS,
} from "@/components/settings/sections";

// ═══════════════════════════════════════════════════════════════
// Settings Page - Clean, Modular, Quiet Luxury
// ═══════════════════════════════════════════════════════════════

// Settings state types
interface SettingsState {
    profile: {
        displayName: string;
        email: string;
        bio: string;
    };
    workspace: {
        name: string;
        industry: string;
        timezone: string;
    };
    notifications: {
        email: boolean;
        weekly: boolean;
        reminders: boolean;
        marketing: boolean;
    };
    appearance: {
        accentColor: string;
    };
}

export default function SettingsPage() {
    const { user, profileStatus } = useAuth();
    const [hasChanges, setHasChanges] = useState(false);
    const [saving, setSaving] = useState(false);

    // Initialize settings with user data
    // Use UseEffect to update if profile loads later?
    // Or just Init state fn? Init state fn runs once.
    // Better to use useEffect to sync state when profile updates.

    const [settings, setSettings] = useState<SettingsState>(() => ({
        profile: {
            displayName: user?.fullName || (user?.email
                ? user.email.split("@")[0].charAt(0).toUpperCase() +
                user.email.split("@")[0].slice(1)
                : "User"),
            email: user?.email || "user@example.com",
            bio: "Building the future of marketing.",
        },
        workspace: {
            name: `${user?.fullName?.split(' ')[0] || (user?.email
                ? user.email.split("@")[0].charAt(0).toUpperCase() +
                user.email.split("@")[0].slice(1)
                : "User")
                }'s Marketing HQ`,
            industry: "b2b-saas",
            timezone: "Asia/Kolkata",
        },
        notifications: {
            email: true,
            weekly: true,
            reminders: true,
            marketing: false,
        },
        appearance: {
            accentColor: "blueprint",
        },
    }));

    // Update state when user data loads
    useEffect(() => {
        if (user) {
            setSettings(prev => ({
                ...prev,
                profile: {
                    ...prev.profile,
                    displayName: user.fullName || prev.profile.displayName,
                    email: user.email || prev.profile.email,
                },
                workspace: {
                    ...prev.workspace,
                    name: `${user.fullName?.split(' ')[0] || "My"}'s Marketing HQ`
                }
            }));
        }
    }, [user]);

    // Load settings from localStorage on mount
    useEffect(() => {
        const savedSettings = localStorage.getItem("raptorflow_settings");
        if (savedSettings) {
            try {
                const parsed = JSON.parse(savedSettings);
                setSettings((prev) => ({ ...prev, ...parsed }));
            } catch (e) {
                console.error("Failed to parse settings:", e);
            }
        }
    }, []);

    // Apply accent color to CSS
    useEffect(() => {
        const color = ACCENT_COLORS.find(
            (c) => c.id === settings.appearance.accentColor
        );
        if (color) {
            document.documentElement.style.setProperty("--blueprint", color.value);
            document.documentElement.style.setProperty("--accent-blue", color.value);
        }
    }, [settings.appearance.accentColor]);

    // Generic update function
    const updateSetting = useCallback(
        <K extends keyof SettingsState>(
            section: K,
            key: keyof SettingsState[K],
            value: SettingsState[K][typeof key]
        ) => {
            setSettings((prev) => ({
                ...prev,
                [section]: {
                    ...prev[section],
                    [key]: value,
                },
            }));
            setHasChanges(true);
        },
        []
    );

    // Save handler
    const handleSave = async () => {
        setSaving(true);
        await new Promise((resolve) => setTimeout(resolve, 500));
        localStorage.setItem("raptorflow_settings", JSON.stringify(settings));
        setSaving(false);
        setHasChanges(false);
        notify.success("Settings saved successfully");
    };

    return (
        <div className="min-h-[calc(100vh-80px)] bg-[var(--canvas)]">
            <div className="max-w-5xl mx-auto px-8 py-10">
                <div className="flex gap-12">
                    {/* Left Navigation */}
                    <SettingsNav />

                    {/* Main Content */}
                    <main className="flex-1 max-w-2xl space-y-8">
                        <ProfileSection
                            data={settings.profile}
                            onChange={(field, value) => updateSetting("profile", field, value)}
                            onSave={handleSave}
                            hasChanges={hasChanges}
                            saving={saving}
                        />

                        {/* BCM Management Section */}
                        {profileStatus?.workspaceId && (
                            <div className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <h3 className="text-lg font-serif text-[var(--ink)]">Business Context</h3>
                                    <div className="flex items-center gap-3">
                                        <BCMIndicator workspaceId={profileStatus.workspaceId} />
                                        <BCMRebuildDialog workspaceId={profileStatus.workspaceId} />
                                        <BCMExportButton workspaceId={profileStatus.workspaceId} />
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <p className="text-sm text-[var(--muted)]">
                                        Manage your Business Context Manifest (BCM) which contains your ICP profiles, messaging framework, and strategic positioning data.
                                    </p>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                        <div className="p-3 bg-[var(--surface)] rounded-[var(--radius)]">
                                            <div className="font-medium text-[var(--ink)] mb-1">ICP Profiles</div>
                                            <div className="text-[var(--muted)]">Target customer segments and personas</div>
                                        </div>
                                        <div className="p-3 bg-[var(--surface)] rounded-[var(--radius)]">
                                            <div className="font-medium text-[var(--ink)] mb-1">Messaging Framework</div>
                                            <div className="text-[var(--muted)]">Value propositions and communication strategy</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </main>
                </div>
            </div>
        </div>
    );
}
