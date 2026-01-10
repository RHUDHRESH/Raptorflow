"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import gsap from "gsap";
import {
    User,
    Building,
    Bell,
    Shield,
    CreditCard,
    Save,
    Camera,
    Palette,
    Check,
    Zap
} from "lucide-react";
import { cn } from "@/lib/utils";
import dynamic from 'next/dynamic';
import { PageHeader, PageFooter } from "@/components/ui/PageHeader";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

const BlueprintButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.BlueprintButton })), { ssr: false });
const SecondaryButton = dynamic(() => import("@/components/ui/BlueprintButton").then(mod => ({ default: mod.SecondaryButton })), { ssr: false });

export const runtime = 'edge';

/* ══════════════════════════════════════════════════════════════════════════════
   SETTINGS — Clean, Professional Account Management
   With working persistence for all settings
   ══════════════════════════════════════════════════════════════════════════════ */

// Accent color options
const ACCENT_COLORS = [
    { id: "blueprint", name: "Blueprint", value: "#3A5A7C" },
    { id: "forest", name: "Forest", value: "#2D5A3D" },
    { id: "amber", name: "Amber", value: "#8B6914" },
    { id: "plum", name: "Plum", value: "#6B3A7C" },
    { id: "slate", name: "Slate", value: "#4A5568" },
];

// Settings types
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

const DEFAULT_SETTINGS: SettingsState = {
    profile: {
        displayName: "Bossman",
        email: "bossman@raptorflow.ai",
        bio: "Founder & CEO. Building the future of marketing.",
    },
    workspace: {
        name: "Bossman's Marketing HQ",
        industry: "B2B SaaS",
        timezone: "Asia/Kolkata (IST)",
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
};

export default function SettingsPage() {
    const pageRef = useRef<HTMLDivElement>(null);
    const router = useRouter();
    const [activeSection, setActiveSection] = useState("profile");
    const [settings, setSettings] = useState<SettingsState>(DEFAULT_SETTINGS);
    const [hasChanges, setHasChanges] = useState(false);
    const [saving, setSaving] = useState(false);

    // Load settings from localStorage on mount
    useEffect(() => {
        const savedSettings = localStorage.getItem("raptorflow_settings");
        if (savedSettings) {
            try {
                const parsed = JSON.parse(savedSettings);
                setSettings(prev => ({ ...prev, ...parsed }));
            } catch (e) {
                console.error("Failed to parse settings:", e);
            }
        }
    }, []);

    // Apply accent color to CSS
    useEffect(() => {
        const color = ACCENT_COLORS.find(c => c.id === settings.appearance.accentColor);
        if (color) {
            document.documentElement.style.setProperty("--blueprint", color.value);
            document.documentElement.style.setProperty("--accent-blue", color.value);
        }
    }, [settings.appearance.accentColor]);

    useEffect(() => {
        if (!pageRef.current) return;
        gsap.fromTo(pageRef.current, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4 });
    }, []);

    const updateSetting = useCallback(<K extends keyof SettingsState>(
        section: K,
        key: keyof SettingsState[K],
        value: SettingsState[K][typeof key]
    ) => {
        setSettings(prev => ({
            ...prev,
            [section]: {
                ...prev[section],
                [key]: value,
            },
        }));
        setHasChanges(true);
    }, []);

    const handleSave = async () => {
        setSaving(true);

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        // Save to localStorage
        localStorage.setItem("raptorflow_settings", JSON.stringify(settings));

        setSaving(false);
        setHasChanges(false);
        toast.success("Settings saved successfully");
    };

    const handleStartOnboarding = () => {
        // Navigate to onboarding session
        router.push('/onboarding/session/step/1');
    };

    const sections = [
        { id: "profile", label: "Profile", icon: User },
        { id: "workspace", label: "Workspace", icon: Building },
        { id: "appearance", label: "Appearance", icon: Palette },
        { id: "notifications", label: "Notifications", icon: Bell },
        { id: "security", label: "Security", icon: Shield },
        { id: "billing", label: "Billing", icon: CreditCard },
        { id: "onboarding", label: "Onboarding", icon: Zap }
    ];

    return (
        <div ref={pageRef} className="max-w-4xl mx-auto pb-12" style={{ opacity: 0 }}>
            {/* Header */}
            <PageHeader
                moduleCode="SETTINGS"
                descriptor="ACCOUNT"
                title="Settings"
                subtitle="Manage your account and preferences"
                actions={
                    hasChanges && (
                        <BlueprintButton onClick={handleSave} disabled={saving}>
                            {saving ? "Saving..." : <><Save size={16} /> Save Changes</>}
                        </BlueprintButton>
                    )
                }
            />

            <div className="flex gap-8">
                {/* Sidebar */}
                <nav className="w-48 shrink-0">
                    <ul className="space-y-1">
                        {sections.map((section) => {
                            const Icon = section.icon;
                            const isActive = activeSection === section.id;
                            return (
                                <li key={section.id}>
                                    <button
                                        onClick={() => setActiveSection(section.id)}
                                        className={cn(
                                            "w-full align-start gap-3 px-3 py-2 rounded-[var(--radius-sm)] text-sm transition-colors text-left",
                                            isActive
                                                ? "bg-[var(--ink)] text-[var(--paper)]"
                                                : "text-[var(--ink-secondary)] hover:bg-[var(--surface)]"
                                        )}
                                    >
                                        <Icon size={16} />
                                        {section.label}
                                    </button>
                                </li>
                            );
                        })}
                    </ul>
                </nav>

                {/* Content */}
                <div className="flex-1 space-y-6">

                    {/* PROFILE */}
                    {activeSection === "profile" && (
                        <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-6">
                            <h2 className="font-semibold text-[var(--ink)] mb-6">Profile Information</h2>

                            {/* Avatar */}
                            <div className="flex items-center gap-4 mb-6 pb-6 border-b border-[var(--structure-subtle)]">
                                <div className="w-16 h-16 rounded-full bg-[var(--blueprint)] flex items-center justify-center text-white text-xl font-bold">
                                    {settings.profile.displayName.slice(0, 2).toUpperCase()}
                                </div>
                                <div>
                                    <button className="text-sm text-[var(--blueprint)] hover:underline flex items-center gap-1">
                                        <Camera size={14} />
                                        Change photo
                                    </button>
                                    <p className="text-xs text-[var(--ink-muted)] mt-1">JPG, PNG. Max 2MB</p>
                                </div>
                            </div>

                            {/* Form */}
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-xs text-[var(--ink-muted)] mb-1.5 font-technical">DISPLAY NAME</label>
                                        <input
                                            type="text"
                                            value={settings.profile.displayName}
                                            onChange={(e) => updateSetting("profile", "displayName", e.target.value)}
                                            className="w-full h-10 px-3 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] focus:ring-2 focus:ring-[var(--blueprint-light)]"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs text-[var(--ink-muted)] mb-1.5 font-technical">EMAIL</label>
                                        <input
                                            type="email"
                                            value={settings.profile.email}
                                            onChange={(e) => updateSetting("profile", "email", e.target.value)}
                                            className="w-full h-10 px-3 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] focus:ring-2 focus:ring-[var(--blueprint-light)]"
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xs text-[var(--ink-muted)] mb-1.5 font-technical">BIO</label>
                                    <textarea
                                        value={settings.profile.bio}
                                        onChange={(e) => updateSetting("profile", "bio", e.target.value)}
                                        rows={3}
                                        className="w-full p-3 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] focus:ring-2 focus:ring-[var(--blueprint-light)] resize-none"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* WORKSPACE */}
                    {activeSection === "workspace" && (
                        <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-6">
                            <h2 className="font-semibold text-[var(--ink)] mb-6">Workspace Settings</h2>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-xs text-[var(--ink-muted)] mb-1.5 font-technical">WORKSPACE NAME</label>
                                    <input
                                        type="text"
                                        value={settings.workspace.name}
                                        onChange={(e) => updateSetting("workspace", "name", e.target.value)}
                                        className="w-full h-10 px-3 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)] focus:ring-2 focus:ring-[var(--blueprint-light)]"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-[var(--ink-muted)] mb-1.5 font-technical">INDUSTRY</label>
                                    <select
                                        value={settings.workspace.industry}
                                        onChange={(e) => updateSetting("workspace", "industry", e.target.value)}
                                        className="w-full h-10 px-3 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                    >
                                        <option>B2B SaaS</option>
                                        <option>E-commerce</option>
                                        <option>Agency</option>
                                        <option>Consulting</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-xs text-[var(--ink-muted)] mb-1.5 font-technical">TIMEZONE</label>
                                    <select
                                        value={settings.workspace.timezone}
                                        onChange={(e) => updateSetting("workspace", "timezone", e.target.value)}
                                        className="w-full h-10 px-3 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)] text-sm text-[var(--ink)] focus:outline-none focus:border-[var(--blueprint)]"
                                    >
                                        <option>Asia/Kolkata (IST)</option>
                                        <option>America/New_York (EST)</option>
                                        <option>America/Los_Angeles (PST)</option>
                                        <option>Europe/London (GMT)</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* APPEARANCE */}
                    {activeSection === "appearance" && (
                        <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-6">
                            <h2 className="font-semibold text-[var(--ink)] mb-6">Appearance</h2>

                            {/* Theme Notice */}
                            <div className="p-4 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)] mb-6">
                                <p className="text-sm text-[var(--ink-secondary)]">
                                    RaptorFlow uses a light theme optimized for readability and the "quiet luxury" aesthetic.
                                    Dark mode is not available by design.
                                </p>
                            </div>

                            {/* Accent Color */}
                            <div>
                                <label className="block text-xs text-[var(--ink-muted)] mb-3 font-technical">ACCENT COLOR</label>
                                <div className="flex flex-wrap gap-3">
                                    {ACCENT_COLORS.map((color) => (
                                        <button
                                            key={color.id}
                                            onClick={() => updateSetting("appearance", "accentColor", color.id)}
                                            className={cn(
                                                "relative flex flex-col items-center gap-2 p-3 rounded-[var(--radius-sm)] border-2 transition-all",
                                                settings.appearance.accentColor === color.id
                                                    ? "border-[var(--ink)] bg-[var(--surface)]"
                                                    : "border-transparent hover:bg-[var(--surface)]"
                                            )}
                                        >
                                            <div
                                                className="w-10 h-10 rounded-full border-2 border-white shadow-md flex items-center justify-center"
                                                style={{ backgroundColor: color.value }}
                                            >
                                                {settings.appearance.accentColor === color.id && (
                                                    <Check size={16} className="text-white" />
                                                )}
                                            </div>
                                            <span className="text-xs text-[var(--ink-secondary)]">{color.name}</span>
                                        </button>
                                    ))}
                                </div>
                                <p className="text-xs text-[var(--ink-muted)] mt-3">
                                    This changes the accent color used for buttons, links, and highlights throughout the app.
                                </p>
                            </div>
                        </div>
                    )}

                    {/* NOTIFICATIONS */}
                    {activeSection === "notifications" && (
                        <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-6">
                            <h2 className="font-semibold text-[var(--ink)] mb-6">Notification Preferences</h2>
                            <div className="space-y-4">
                                {[
                                    { id: "email" as const, label: "Email notifications", desc: "Updates about your campaigns and moves" },
                                    { id: "weekly" as const, label: "Weekly digest", desc: "Performance summary every Monday" },
                                    { id: "reminders" as const, label: "Execution reminders", desc: "Reminders for scheduled moves" },
                                    { id: "marketing" as const, label: "Product updates", desc: "New features and tips" }
                                ].map((item) => (
                                    <div key={item.id} className="flex items-center justify-between py-3 border-b border-[var(--structure-subtle)] last:border-0">
                                        <div>
                                            <p className="text-sm font-medium text-[var(--ink)]">{item.label}</p>
                                            <p className="text-xs text-[var(--ink-muted)]">{item.desc}</p>
                                        </div>
                                        <button
                                            onClick={() => updateSetting("notifications", item.id, !settings.notifications[item.id])}
                                            className={cn(
                                                "relative w-11 h-6 rounded-full transition-colors",
                                                settings.notifications[item.id] ? "bg-[var(--blueprint)]" : "bg-[var(--structure)]"
                                            )}
                                        >
                                            <div className={cn(
                                                "absolute top-[2px] left-[2px] w-5 h-5 bg-white rounded-full shadow-sm transition-transform",
                                                settings.notifications[item.id] && "translate-x-5"
                                            )} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* SECURITY */}
                    {activeSection === "security" && (
                        <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-6">
                            <h2 className="font-semibold text-[var(--ink)] mb-6">Security</h2>
                            <div className="space-y-4">
                                <div className="flex items-center justify-between py-3 border-b border-[var(--structure-subtle)]">
                                    <div>
                                        <p className="text-sm font-medium text-[var(--ink)]">Password</p>
                                        <p className="text-xs text-[var(--ink-muted)]">Last changed 3 months ago</p>
                                    </div>
                                    <SecondaryButton size="sm">Change</SecondaryButton>
                                </div>
                                <div className="flex items-center justify-between py-3 border-b border-[var(--structure-subtle)]">
                                    <div>
                                        <p className="text-sm font-medium text-[var(--ink)]">Two-factor authentication</p>
                                        <p className="text-xs text-[var(--success)]">Enabled</p>
                                    </div>
                                    <SecondaryButton size="sm">Manage</SecondaryButton>
                                </div>
                                <div className="flex items-center justify-between py-3">
                                    <div>
                                        <p className="text-sm font-medium text-[var(--ink)]">Active sessions</p>
                                        <p className="text-xs text-[var(--ink-muted)]">2 devices</p>
                                    </div>
                                    <button className="text-sm text-[var(--error)] hover:underline">Sign out all</button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* BILLING */}
                    {activeSection === "billing" && (
                        <>
                            <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <div>
                                        <h2 className="font-semibold text-[var(--ink)]">Current Plan</h2>
                                        <p className="text-sm text-[var(--ink-muted)]">Billed monthly</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-2xl font-bold text-[var(--ink)]">$49<span className="text-sm font-normal text-[var(--ink-muted)]">/mo</span></p>
                                        <p className="text-xs text-[var(--ink-muted)]">Pro Plan</p>
                                    </div>
                                </div>
                                <div className="flex gap-3">
                                    <SecondaryButton className="flex-1">Manage Subscription</SecondaryButton>
                                    <SecondaryButton className="flex-1">View Invoices</SecondaryButton>
                                </div>
                            </div>

                            <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-6">
                                <h3 className="font-semibold text-[var(--ink)] mb-4">Payment Method</h3>
                                <div className="flex items-center justify-between p-3 bg-[var(--surface)] rounded-[var(--radius-sm)]">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-6 bg-[var(--ink)] rounded text-[var(--paper)] text-[10px] font-bold flex items-center justify-center">VISA</div>
                                        <span className="text-sm text-[var(--ink)]">•••• •••• •••• 4242</span>
                                    </div>
                                    <button className="text-sm text-[var(--blueprint)] hover:underline">Update</button>
                                </div>
                            </div>
                        </>
                    )}

                    {/* ONBOARDING */}
                    {activeSection === "onboarding" && (
                        <div className="bg-[var(--paper)] border border-[var(--structure)] rounded-[var(--radius)] p-6">
                            <h2 className="font-semibold text-[var(--ink)] mb-6">Onboarding Setup</h2>

                            <div className="space-y-6">
                                {/* Onboarding Status */}
                                <div className="p-4 bg-[var(--surface)] border border-[var(--structure)] rounded-[var(--radius-sm)]">
                                    <div className="flex items-center gap-3 mb-3">
                                        <div className="w-8 h-8 bg-[var(--blueprint)] rounded-full flex items-center justify-center">
                                            <Zap size={16} className="text-white" />
                                        </div>
                                        <div>
                                            <h3 className="font-medium text-[var(--ink)]">Raptorflow Calibration</h3>
                                            <p className="text-sm text-[var(--ink-muted)]">Complete your workspace setup</p>
                                        </div>
                                    </div>
                                    <p className="text-sm text-[var(--ink-secondary)] leading-relaxed">
                                        Start the comprehensive onboarding process to configure your workspace,
                                        set up your brand voice, and unlock all Raptorflow features. This 25-step
                                        calibration ensures optimal performance for your marketing campaigns.
                                    </p>
                                </div>

                                {/* Onboarding Actions */}
                                <div className="flex gap-3">
                                    <BlueprintButton
                                        onClick={handleStartOnboarding}
                                        className="flex-1"
                                    >
                                        <Zap size={16} /> Start Onboarding
                                    </BlueprintButton>
                                    <SecondaryButton className="flex-1">
                                        View Progress
                                    </SecondaryButton>
                                </div>

                                {/* Quick Info */}
                                <div className="grid grid-cols-3 gap-4 mt-6">
                                    <div className="text-center p-3 bg-[var(--surface)] rounded-[var(--radius-sm)]">
                                        <div className="text-lg font-bold text-[var(--blueprint)]">25</div>
                                        <div className="text-xs text-[var(--ink-muted)]">Steps</div>
                                    </div>
                                    <div className="text-center p-3 bg-[var(--surface)] rounded-[var(--radius-sm)]">
                                        <div className="text-lg font-bold text-[var(--blueprint)]">~90m</div>
                                        <div className="text-xs text-[var(--ink-muted)]">Total Time</div>
                                    </div>
                                    <div className="text-center p-3 bg-[var(--surface)] rounded-[var(--radius-sm)]">
                                        <div className="text-lg font-bold text-[var(--blueprint)]">Full</div>
                                        <div className="text-xs text-[var(--ink-muted)]">Setup</div>
                                    </div>
                                </div>

                                {/* Additional Info */}
                                <div className="pt-4 border-t border-[var(--structure-subtle)]">
                                    <p className="text-xs text-[var(--ink-muted)]">
                                        Your progress is automatically saved. You can pause and resume the onboarding
                                        process at any time. Each step unlocks powerful features and insights.
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                </div>
            </div>

            <PageFooter document="SETTINGS" />
        </div>
    );
}
