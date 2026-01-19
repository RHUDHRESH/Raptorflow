/** @type {import('tailwindcss').Config} */
import colors from "tailwindcss/colors"

module.exports = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                // ... (standard colors)
                slate: colors.slate,
                gray: colors.gray,
                zinc: colors.zinc,
                neutral: colors.neutral,
                stone: colors.stone,
                red: colors.red,
                orange: colors.orange,
                amber: colors.amber,
                yellow: colors.yellow,
                lime: colors.lime,
                green: colors.green,
                emerald: colors.emerald,
                teal: colors.teal,
                cyan: colors.cyan,
                sky: colors.sky,
                blue: colors.blue,
                indigo: colors.indigo,
                violet: colors.violet,
                purple: colors.purple,
                fuchsia: colors.fuchsia,
                pink: colors.pink,
                rose: colors.rose,

                // Mapped to CSS Variables for "Diffused" Theme
                canvas: "var(--canvas)",
                paper: "var(--paper)",
                surface: "var(--surface)",
                "paper-glass": "var(--paper-glass)",
                "surface-glass": "var(--surface-glass)",

                ink: {
                    DEFAULT: "var(--ink)",
                    secondary: "var(--ink-secondary)",
                    muted: "var(--ink-muted)",
                },

                border: {
                    DEFAULT: "var(--border)",
                    subtle: "var(--border-subtle)",
                    highlight: "var(--border-highlight)",
                },

                primary: {
                    DEFAULT: "var(--primary)",
                    foreground: "var(--primary-foreground)",
                },

                accent: {
                    cyan: "var(--accent-cyan)",
                    purple: "var(--accent-purple)",
                    pink: "var(--accent-pink)",
                    amber: "var(--accent-amber)",
                },

                success: "var(--success)",
                warning: "var(--warning)",
                error: "var(--error)",
                info: "var(--info)",
            },

            borderRadius: {
                "2xl": "24px",
                "xl": "16px",
                "lg": "12px",
                "md": "8px",
                "sm": "4px",
                "xs": "2px",
            },

            fontFamily: {
                sans: ["var(--font-inter)", "Inter", "system-ui", "sans-serif"],
                serif: ["var(--font-playfair)", "Playfair Display", "serif"],
                mono: ["var(--font-geist-mono)", "SF Mono", "monospace"],
            },

            boxShadow: {
                "xs": "var(--shadow-xs)",
                "sm": "var(--shadow-sm)",
                "md": "var(--shadow-md)",
                "lg": "var(--shadow-lg)",
                "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
                "lift": "var(--shadow-lift)",
                "colored": "var(--shadow-colored)",
            },

            keyframes: {
                aurora: {
                    "0%": { backgroundPosition: "0% 50%" },
                    "50%": { backgroundPosition: "100% 50%" },
                    "100%": { backgroundPosition: "0% 50%" },
                },
                float: {
                    "0%, 100%": { transform: "translateY(0)" },
                    "50%": { transform: "translateY(-10px)" },
                },
            },
            animation: {
                aurora: "aurora 15s ease infinite",
                float: "float 6s ease-in-out infinite",
            },
        },
    },
    plugins: [],
}
