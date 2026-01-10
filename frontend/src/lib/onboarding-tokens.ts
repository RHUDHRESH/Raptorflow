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
    { id: 3, name: "Assessment", steps: [5, 6] },
    { id: 4, name: "Research", steps: [7, 8, 9] },
    { id: 5, name: "Positioning", steps: [10, 11, 12, 13, 14] },
    { id: 6, name: "Audience", steps: [15, 16] },
    { id: 7, name: "Messaging", steps: [17, 18, 19] },
    { id: 8, name: "Planning", steps: [20, 21, 22] },
    { id: 9, name: "Finalization", steps: [23, 24, 25] },
];

export const ONBOARDING_STEPS: { id: number; phase: number; name: string; required: boolean }[] = [
    { id: 1, phase: 1, name: "Evidence Vault", required: true },
    { id: 2, phase: 1, name: "Auto-Extraction", required: true },
    { id: 3, phase: 2, name: "Contradictions & Issues", required: true },
    { id: 4, phase: 2, name: "Validate Truth Sheet", required: true },
    { id: 5, phase: 3, name: "Brand & Asset Audit", required: false },
    { id: 6, phase: 3, name: "Offer & Pricing", required: true },
    { id: 7, phase: 4, name: "Market Research Brief", required: false },
    { id: 8, phase: 4, name: "Competitive Alternatives", required: false },
    { id: 9, phase: 4, name: "Competitive Ladder", required: false },
    { id: 10, phase: 5, name: "Market Category", required: true },
    { id: 11, phase: 5, name: "Differentiated Capabilities", required: true },
    { id: 12, phase: 5, name: "Capability Matrix", required: true },
    { id: 13, phase: 5, name: "Positioning Statements", required: true },
    { id: 14, phase: 5, name: "Focus & Sacrifice", required: true },
    { id: 15, phase: 6, name: "ICP Profiles", required: true },
    { id: 16, phase: 6, name: "Buying Process", required: false },
    { id: 17, phase: 7, name: "Messaging Guardrails", required: true },
    { id: 18, phase: 7, name: "Soundbites Library", required: true },
    { id: 19, phase: 7, name: "Message Hierarchy", required: true },
    { id: 20, phase: 8, name: "Brand Augmentation", required: false },
    { id: 21, phase: 8, name: "Channel Mapping", required: true },
    { id: 22, phase: 8, name: "TAM/SAM/SOM", required: false },
    { id: 23, phase: 9, name: "Validation To-Dos", required: false },
    { id: 24, phase: 9, name: "Final Synthesis", required: true },
    { id: 25, phase: 9, name: "Export", required: true },
];

export type StepStatus = "pending" | "in-progress" | "complete" | "blocked" | "error";

export interface StepState {
    id: number;
    status: StepStatus;
    data: Record<string, unknown>;
    savedAt: Date | null;
}
