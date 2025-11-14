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

