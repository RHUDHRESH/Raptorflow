// Re-export token values for TypeScript usage
// Aligned with RaptorFlow blueprint: Monochrome base with strategic accents
export const TOKENS = {
  colors: {
    // Core Monochrome
    bg: "#FFFFFF",
    card: "#F0F2F5",
    ink: "#0B0B0E",
    subtle: "#4D536D",
    muted: "#B7BDC7",
    
    // Primary Brand
    primary: "#28295A",      // Deep Indigo
    accent: "#51BAFF",       // Sky Blue
    accent2: "#09BE99",      // Emerald
    
    // Status
    success: "#09BE99",      // Emerald
    warn: "#F59E0B",         // Amber
    error: "#EF4444",        // Crimson
    
    // Neutrals
    slate: "#4D536D",
    cloud: "#F0F2F5",
  },
  effects: {
    glass: "rgba(255,255,255,.06)",
    ring: "rgba(81,186,255,.45)",
    shadow: "0 4px 12px rgba(0,0,0,.08)",
    shadowLg: "0 10px 30px rgba(0,0,0,.12)",
  },
  radii: {
    sm: "6px",
    lg: "12px",
    xl: "18px",
    "2xl": "24px",
  },
  typography: {
    fontInter: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontMono: "'JetBrains Mono', 'Fira Code', monospace",
    sizes: {
      h1: "40px",      // 40-48px per blueprint
      h2: "32px",      // 28-36px
      h3: "24px",      // 22-26px
      body: "17px",    // 17-18px base
    },
  },
} as const;

