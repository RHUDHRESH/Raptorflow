import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Core Monochrome
        "rf-bg": "var(--rf-bg)",
        "rf-card": "var(--rf-card)",
        "rf-ink": "var(--rf-ink)",
        "rf-subtle": "var(--rf-subtle)",
        "rf-muted": "var(--rf-muted)",
        
        // Primary Brand
        "rf-primary": "var(--rf-primary)",
        "rf-accent": "var(--rf-accent)",
        "rf-accent-2": "var(--rf-accent-2)",
        
        // Status Colors
        "rf-success": "var(--rf-success)",
        "rf-warn": "var(--rf-warn)",
        "rf-error": "var(--rf-error)",
        
        // Neutrals
        "rf-slate": "var(--rf-slate)",
        "rf-cloud": "var(--rf-cloud)",
        
        // shadcn/ui compatibility
        border: "var(--border)",
        input: "var(--input)",
        ring: "var(--ring)",
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: {
          DEFAULT: "var(--primary)",
          foreground: "var(--primary-foreground)",
        },
        secondary: {
          DEFAULT: "var(--secondary)",
          foreground: "var(--secondary-foreground)",
        },
        destructive: {
          DEFAULT: "var(--destructive)",
          foreground: "var(--destructive-foreground)",
        },
        muted: {
          DEFAULT: "var(--muted)",
          foreground: "var(--muted-foreground)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          foreground: "var(--accent-foreground)",
        },
        popover: {
          DEFAULT: "var(--popover)",
          foreground: "var(--popover-foreground)",
        },
        card: {
          DEFAULT: "var(--card)",
          foreground: "var(--card-foreground)",
        },
      },
      borderRadius: {
        "rf": "var(--radius)",
        "rf-lg": "var(--radius-lg)",
        "rf-xl": "var(--radius-xl)",
        "rf-2xl": "var(--radius-2xl)",
      },
      boxShadow: {
        "rf": "var(--rf-shadow)",
        "rf-lg": "var(--rf-shadow-lg)",
      },
      fontFamily: {
        sans: ["var(--font-inter)"],
        mono: ["var(--font-mono)"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;

