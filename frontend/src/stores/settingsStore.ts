"use client";

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// --- Types ---
export type Theme = "light" | "dark" | "system";
export type Density = "comfortable" | "compact";
export type AccentColor = "tan" | "ocean" | "forest" | "plum";

export interface UserProfile {
    fullName: string;
    email: string;
    initials: string;
}

export interface WorkspaceSettings {
    name: string;
    industry: string;
    website: string;
}

export interface NotificationSettings {
    weeklyDigest: { email: boolean; push: boolean };
    moveReminders: { email: boolean; push: boolean };
    teamActivity: { email: boolean; push: boolean };
}

export interface PreferenceSettings {
    theme: Theme;
    accentColor: AccentColor;
    density: Density;
    autoSave: boolean;
    commandPalette: boolean;
    animations: boolean;
}

export interface SettingsState {
    // Profile
    profile: UserProfile;
    setProfile: (profile: Partial<UserProfile>) => void;

    // Workspace
    workspace: WorkspaceSettings;
    setWorkspace: (workspace: Partial<WorkspaceSettings>) => void;

    // Notifications
    notifications: NotificationSettings;
    setNotifications: (notifications: Partial<NotificationSettings>) => void;
    toggleNotification: (
        type: keyof NotificationSettings,
        channel: 'email' | 'push'
    ) => void;

    // Preferences
    preferences: PreferenceSettings;
    setPreferences: (preferences: Partial<PreferenceSettings>) => void;
    setTheme: (theme: Theme) => void;
    setAccentColor: (color: AccentColor) => void;
    setDensity: (density: Density) => void;
    togglePreference: (key: 'autoSave' | 'commandPalette' | 'animations') => void;

    // Actions
    saveAll: () => void;
    resetToDefaults: () => void;
}

// --- Accent Color Values ---
export const ACCENT_COLORS: Record<AccentColor, { hex: string; label: string }> = {
    tan: { hex: "#a67c52", label: "Tan" },
    ocean: { hex: "#5D7290", label: "Ocean" },
    forest: { hex: "#4A7C59", label: "Forest" },
    plum: { hex: "#8B6B8B", label: "Plum" },
};

// --- Default Values ---
const DEFAULT_PROFILE: UserProfile = {
    fullName: "Bossman",
    email: "boss@company.com",
    initials: "BM",
};

const DEFAULT_WORKSPACE: WorkspaceSettings = {
    name: "Acme Corp",
    industry: "B2B SaaS",
    website: "https://acme.com",
};

const DEFAULT_NOTIFICATIONS: NotificationSettings = {
    weeklyDigest: { email: true, push: false },
    moveReminders: { email: true, push: true },
    teamActivity: { email: false, push: true },
};

const DEFAULT_PREFERENCES: PreferenceSettings = {
    theme: "light",
    accentColor: "tan",
    density: "comfortable",
    autoSave: true,
    commandPalette: true,
    animations: true,
};

// --- Store ---
export const useSettingsStore = create<SettingsState>()(
    persist(
        (set, get) => ({
            // Profile
            profile: DEFAULT_PROFILE,
            setProfile: (profile) => set((state) => ({
                profile: { ...state.profile, ...profile }
            })),

            // Workspace
            workspace: DEFAULT_WORKSPACE,
            setWorkspace: (workspace) => set((state) => ({
                workspace: { ...state.workspace, ...workspace }
            })),

            // Notifications
            notifications: DEFAULT_NOTIFICATIONS,
            setNotifications: (notifications) => set((state) => ({
                notifications: { ...state.notifications, ...notifications }
            })),
            toggleNotification: (type, channel) => set((state) => ({
                notifications: {
                    ...state.notifications,
                    [type]: {
                        ...state.notifications[type],
                        [channel]: !state.notifications[type][channel]
                    }
                }
            })),

            // Preferences
            preferences: DEFAULT_PREFERENCES,
            setPreferences: (preferences) => set((state) => ({
                preferences: { ...state.preferences, ...preferences }
            })),
            setTheme: (theme) => {
                set((state) => ({
                    preferences: { ...state.preferences, theme }
                }));
                // Apply theme to document
                applyTheme(theme);
            },
            setAccentColor: (accentColor) => {
                set((state) => ({
                    preferences: { ...state.preferences, accentColor }
                }));
                // Apply accent color to document
                applyAccentColor(accentColor);
            },
            setDensity: (density) => set((state) => ({
                preferences: { ...state.preferences, density }
            })),
            togglePreference: (key) => set((state) => ({
                preferences: { ...state.preferences, [key]: !state.preferences[key] }
            })),

            // Actions
            saveAll: () => {
                // Persist is automatic with zustand persist middleware
                // Settings saved
            },
            resetToDefaults: () => set({
                profile: DEFAULT_PROFILE,
                workspace: DEFAULT_WORKSPACE,
                notifications: DEFAULT_NOTIFICATIONS,
                preferences: DEFAULT_PREFERENCES,
            }),
        }),
        {
            name: 'raptorflow-settings',
            // Apply settings on hydration
            onRehydrateStorage: () => (state) => {
                if (state) {
                    applyTheme(state.preferences.theme);
                    applyAccentColor(state.preferences.accentColor);
                }
            },
        }
    )
);

// --- Theme Application ---
// RaptorFlow enforces light mode only per brand guidelines
function applyTheme(_theme: Theme) {
    if (typeof window === 'undefined') return;

    const root = document.documentElement;

    // Always enforce light mode - RaptorFlow is a light-mode-only application
    // Dark mode tokens have been removed from globals.css
    root.classList.remove('dark');

    // Apply light mode tokens (matching globals.css)
    root.style.setProperty('--canvas', '#F5F3EE');
    root.style.setProperty('--canvas-elevated', '#F5F6F0');
    root.style.setProperty('--paper', '#FFFEF9');
    root.style.setProperty('--surface', '#FDFCFA');
    root.style.setProperty('--surface-elevated', '#FAFAF8');
    root.style.setProperty('--surface-glass', 'rgba(255, 255, 255, 0.85)');
    root.style.setProperty('--ink', '#1A1A1A');
    root.style.setProperty('--ink-secondary', '#4A4A4A');
    root.style.setProperty('--ink-muted', '#7A7A7A');
    root.style.setProperty('--ink-ghost', '#A0A0A0');
    root.style.setProperty('--secondary', '#5B5F61');
    root.style.setProperty('--muted', '#9D9F9F');
    root.style.setProperty('--placeholder', '#BCBDBA');
    root.style.setProperty('--structure', '#C8C6C0');
    root.style.setProperty('--structure-subtle', '#E0DED8');
    root.style.setProperty('--structure-strong', '#A0A09A');
    root.style.setProperty('--border', '#C0C1BE');
    root.style.setProperty('--border-subtle', '#E5E3DF');
}

// --- Accent Color Application ---
function applyAccentColor(color: AccentColor) {
    if (typeof window === 'undefined') return;

    const hex = ACCENT_COLORS[color].hex;
    const root = document.documentElement;

    root.style.setProperty('--accent', hex);

    // Calculate hover color (slightly darker)
    const hoverHex = adjustBrightness(hex, -15);
    root.style.setProperty('--accent-hover', hoverHex);

    // Calculate light variant
    root.style.setProperty('--accent-light', hexToRgba(hex, 0.08));
    root.style.setProperty('--accent-glow', hexToRgba(hex, 0.15));
}

// --- Color Utilities ---
function hexToRgba(hex: string, alpha: number): string {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function adjustBrightness(hex: string, percent: number): string {
    const num = parseInt(hex.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = Math.max(0, Math.min(255, (num >> 16) + amt));
    const G = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) + amt));
    const B = Math.max(0, Math.min(255, (num & 0x0000FF) + amt));
    return `#${(1 << 24 | R << 16 | G << 8 | B).toString(16).slice(1)}`;
}
