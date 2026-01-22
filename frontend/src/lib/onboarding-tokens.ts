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
    { id: 1, name: "Calibration", steps: [1, 2, 3, 4] },
    { id: 2, name: "Commerce", steps: [5] },
    { id: 3, name: "Intelligence", steps: [6, 7, 8] },
    { id: 4, name: "Strategy", steps: [9, 10, 11, 12, 13] },
    { id: 5, name: "Messaging", steps: [14, 15, 16, 17, 18, 19] },
    { id: 6, name: "Tactics", steps: [20, 21, 22, 23] },
];

export const ONBOARDING_STEPS: { id: number; phase: number; name: string; required: boolean }[] = [
    { id: 1, phase: 1, name: "Evidence Vault", required: true },
    { id: 2, phase: 1, name: "Brand Synthesis", required: true },
    { id: 3, phase: 1, name: "Strategic Integrity", required: true },
    { id: 4, phase: 1, name: "Truth Confirmation", required: true },
    { id: 5, phase: 2, name: "The Offer", required: true },
    { id: 6, phase: 3, name: "Market Intelligence", required: true },
    { id: 7, phase: 3, name: "Competitive Landscape", required: true },
    { id: 8, phase: 3, name: "Comparative Angle", required: true },
    { id: 9, phase: 4, name: "Market Category", required: true },
    { id: 10, phase: 4, name: "Product Capabilities", required: true },
    { id: 11, phase: 4, name: "Perceptual Map", required: true },
    { id: 12, phase: 4, name: "Position Grid", required: true },
    { id: 13, phase: 4, name: "Gap Analysis", required: true },
    { id: 14, phase: 5, name: "Positioning Statements", required: true },
    { id: 15, phase: 5, name: "Focus & Sacrifice", required: true },
    { id: 16, phase: 5, name: "ICP Personas", required: true },
    { id: 17, phase: 5, name: "Market Education", required: false },
    { id: 18, phase: 5, name: "Messaging Rules", required: true },
    { id: 19, phase: 5, name: "Soundbites Library", required: true },
    { id: 20, phase: 6, name: "Channel Mapping", required: true },
    { id: 21, phase: 6, name: "Market Sizing", required: false },
    { id: 22, phase: 6, name: "Validation Tasks", required: false },
    { id: 23, phase: 6, name: "Onboarding Finish", required: true },
];

export type StepStatus = "pending" | "in-progress" | "complete" | "blocked" | "error";

export interface StepState {
    id: number;
    status: StepStatus;
    data: Record<string, unknown>;
    savedAt: Date | null;
}
