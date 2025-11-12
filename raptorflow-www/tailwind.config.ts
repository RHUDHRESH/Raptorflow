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
        "rf-bg": "var(--rf-bg)",
        "rf-card": "var(--rf-card)",
        "rf-ink": "var(--rf-ink)",
        "rf-subtle": "var(--rf-subtle)",
        "rf-mineshaft": "var(--rf-mineshaft)",
        "rf-akaroa": "var(--rf-akaroa)",
        "rf-accent": "var(--rf-accent)",
        "rf-accent-2": "var(--rf-accent-2)",
        "rf-warn": "var(--rf-warn)",
      },
      borderRadius: {
        "xl": "var(--radius-xl)",
        "2xl": "var(--radius-2xl)",
      },
      boxShadow: {
        "rf": "var(--rf-shadow)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;

