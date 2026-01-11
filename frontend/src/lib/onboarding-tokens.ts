/**
 * RaptorFlow Onboarding Design Tokens
 * Extracted from globals.css for TypeScript consumption
 */

export const tokens = {
    color: {
        // Canvas & Surfaces
        canvas: "var(--canvas)",
        canvasElevated: "var(--canvas-elevated)",
        surface: "var(--surface)",
        surfaceElevated: "var(--surface-elevated)",
        surfaceGlass: "var(--surface-glass)",

        // Text
        ink: "var(--ink)",
        secondary: "var(--secondary)",
        muted: "var(--muted)",
        placeholder: "var(--placeholder)",

        // Border
        border: "var(--border)",
        borderSubtle: "var(--border-subtle)",
        borderGlass: "var(--border-glass)",

        // Accent
        accent: "var(--accent)",
        accentHover: "var(--accent-hover)",
        accentLight: "var(--accent-light)",
        accentGlow: "var(--accent-glow)",

        // Semantic
        success: "var(--success)",
        successLight: "var(--success-light)",
        warning: "var(--warning)",
        warningLight: "var(--warning-light)",
        error: "var(--error)",
        errorLight: "var(--error-light)",
    },

    shadow: {
        xs: "var(--shadow-xs)",
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
        xl: "var(--shadow-xl)",
        inner: "var(--shadow-inner)",
        glow: "var(--shadow-glow)",
    },

    radius: {
        xs: "var(--radius-xs)",
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
        "2xl": "var(--radius-2xl)",
    },

    transition: {
        fast: "var(--transition-fast)",
        base: "var(--transition-base)",
        slow: "var(--transition-slow)",
        spring: "var(--transition-spring)",
    },

    typography: {
        fontSans: "var(--font-inter), system-ui, -apple-system, sans-serif",
        fontSerif: "var(--font-playfair), Georgia, serif",
    },
} as const;

// Onboarding-specific constants
export const ONBOARDING_PHASES: { id: number; name: string; steps: number[] }[] = [
    { id: 1, name: "Evidence Collection", steps: [1, 2] },
    { id: 2, name: "Validation", steps: [3, 4] },
    { id: 3, name: "Your Offer", steps: [5] },
    { id: 4, name: "Research", steps: [6, 7, 8] },
    { id: 5, name: "Positioning", steps: [9, 10, 11, 12, 13] },
    { id: 6, name: "Audience", steps: [14, 15] },
    { id: 7, name: "Messaging", steps: [16, 17, 18] },
    { id: 8, name: "Planning", steps: [19, 20, 21] },
    { id: 9, name: "Finalization", steps: [22, 23, 24] },
];

export const ONBOARDING_STEPS: { id: number; phase: number; name: string; required: boolean }[] = [
    { id: 1, phase: 1, name: "Evidence Vault", required: true },
    { id: 2, phase: 1, name: "Auto-Extraction", required: true },
    { id: 3, phase: 2, name: "Review Issues", required: true },
    { id: 4, phase: 2, name: "Review Your Facts", required: true },
    { id: 5, phase: 3, name: "Your Offer", required: true },
    { id: 6, phase: 4, name: "Research Brief", required: false },
    { id: 7, phase: 4, name: "Competitive Alternatives", required: false },
    { id: 8, phase: 4, name: "How You Compare", required: false },
    { id: 9, phase: 5, name: "Market Category", required: true },
    { id: 10, phase: 5, name: "What Makes You Different", required: true },
    { id: 11, phase: 5, name: "Capability Matrix", required: true },
    { id: 12, phase: 5, name: "Positioning Statements", required: true },
    { id: 13, phase: 5, name: "Strategic Focus", required: true },
    { id: 14, phase: 6, name: "Ideal Customers", required: true },
    { id: 15, phase: 6, name: "Buying Process", required: false },
    { id: 16, phase: 7, name: "Messaging Rules", required: true },
    { id: 17, phase: 7, name: "Soundbites", required: true },
    { id: 18, phase: 7, name: "Message Hierarchy", required: true },
    { id: 19, phase: 8, name: "Brand Assets", required: false },
    { id: 20, phase: 8, name: "Channel Strategy", required: true },
    { id: 21, phase: 8, name: "Market Sizing", required: false },
    { id: 22, phase: 9, name: "Validation Tasks", required: false },
    { id: 23, phase: 9, name: "Final Synthesis", required: true },
    { id: 24, phase: 9, name: "Export", required: true },
];

export type StepStatus = "pending" | "in-progress" | "complete" | "blocked" | "error";

export interface StepState {
    id: number;
    status: StepStatus;
    data: Record<string, unknown>;
    savedAt: Date | null;
}
