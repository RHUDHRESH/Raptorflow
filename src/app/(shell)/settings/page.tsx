"use client";

import React, { useState, useEffect, useCallback } from "react";
import { notify } from "@/lib/notifications";
import { useAuth } from "@/components/auth/AuthProvider";

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
    const { user, profile } = useAuth();
    const [hasChanges, setHasChanges] = useState(false);
    const [saving, setSaving] = useState(false);

    // Initialize settings with user data
    // Use UseEffect to update if profile loads later? 
    // Or just Init state fn? Init state fn runs once. 
    // Better to use useEffect to sync state when profile updates.

    const [settings, setSettings] = useState<SettingsState>(() => ({
        profile: {
            displayName: profile?.full_name || (user
                ? user.email.split("@")[0].charAt(0).toUpperCase() +
                user.email.split("@")[0].slice(1)
                : "User"),
            email: user?.email || "user@example.com",
            bio: "Building the future of marketing.",
        },
        workspace: {
            name: `${profile?.full_name?.split(' ')[0] || (user
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

    // Update state when profile loads
    useEffect(() => {
        if (profile) {
            setSettings(prev => ({
                ...prev,
                profile: {
                    ...prev.profile,
                    displayName: profile.full_name || prev.profile.displayName,
                    email: user?.email || prev.profile.email,
                },
                workspace: {
                    ...prev.workspace,
                    name: `${profile.full_name?.split(' ')[0] || "My"}'s Marketing HQ`
                }
            }));
        }
    }, [profile, user?.email]);

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
                    <main className="flex-1 max-w-2xl">
                        <ProfileSection
                            data={settings.profile}
                            onChange={(field, value) => updateSetting("profile", field, value)}
                            onSave={handleSave}
                            hasChanges={hasChanges}
                            saving={saving}
                        />
                    </main>
                </div>
            </div>
        </div>
    );
}
