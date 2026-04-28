/**
 * RaptorFlow Brand Tokens
 *
 * TypeScript mirrors of the CSS design system defined in globals.css.
 * Do not create a parallel theme that fights the CSS. These are canonical
 * references for use in components when JS-level access is needed.
 */

export const colors = {
  // Paper surfaces
  paper50: "#faf7f1",
  paper100: "#fbf8f2",
  paper150: "#f5f1e8",
  paper200: "#efe9dc",
  paper300: "#e6dfce",
  paper400: "#c9c0ab",

  // Ink scale
  ink900: "#2a2622",
  ink700: "#4a433c",
  ink500: "#7a7268",
  ink400: "#9c9384",
  ink300: "#bab0a0",

  // Amber primary
  amber: "#d97757",
  amberHover: "#c26645",
  amberWash: "#fbe9de",
  amberStroke: "#e89878",

  // Semantic
  leaf: "#5c8a5a",
  leafWash: "#e8f0e5",
  indigoMuse: "#5b5fb8",
  indigoWash: "#e8e9f4",
  destructive: "#c44a3f",
  destructiveWash: "#fbeae7",

  // Pod colors
  podCreative: "#8b6fc2",
  podDigital: "#4f87b8",
  podStrategy: "#b8556b",
  podSupport: "#c26f4a",
  podStrategist: "#4a433c",
} as const;

export const typography = {
  display: '"Instrument Serif", "DM Serif Display", ui-serif, serif',
  sans: '"DM Sans", "Inter", ui-sans-serif, system-ui, sans-serif',
  mono: '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace',
} as const;

export const radii = {
  xs: "4px",
  sm: "6px",
  md: "10px",
  lg: "12px",
  xl: "16px",
  "2xl": "20px",
  pill: "9999px",
} as const;

export const shadows = {
  xs: "0 1px 2px rgba(42, 38, 34, 0.04)",
  sm: "0 1px 2px rgba(42, 38, 34, 0.05), 0 1px 3px rgba(42, 38, 34, 0.04)",
  md: "0 2px 4px rgba(42, 38, 34, 0.04), 0 4px 12px rgba(42, 38, 34, 0.06)",
  lg: "0 4px 8px rgba(42, 38, 34, 0.04), 0 12px 32px rgba(42, 38, 34, 0.08)",
  amber: "0 0 0 3px rgba(217, 119, 87, 0.15), 0 6px 18px -6px rgba(217, 119, 87, 0.3)",
  inset: "inset 0 1px 0 rgba(255, 255, 255, 0.6)",
} as const;

export const spacing = {
  px: "1px",
  0.5: "0.125rem",
  1: "0.25rem",
  1.5: "0.375rem",
  2: "0.5rem",
  2.5: "0.625rem",
  3: "0.75rem",
  3.5: "0.875rem",
  4: "1rem",
  5: "1.25rem",
  6: "1.5rem",
  7: "1.75rem",
  8: "2rem",
  9: "2.25rem",
  10: "2.5rem",
  12: "3rem",
  14: "3.5rem",
  16: "4rem",
  20: "5rem",
  24: "6rem",
  28: "7rem",
  32: "8rem",
} as const;

export const zIndex = {
  base: 0,
  dropdown: 50,
  sticky: 100,
  fixed: 200,
  overlay: 300,
  modal: 400,
  popover: 500,
  toast: 600,
  tooltip: 700,
} as const;

export const semantic = {
  // Surfaces
  background: colors.paper100,
  card: "#ffffff",
  sidebar: colors.paper50,
  muted: colors.paper150,

  // Text
  foreground: colors.ink900,
  primaryText: colors.ink900,
  secondaryText: colors.ink700,
  mutedText: colors.ink500,
  hintText: colors.ink400,

  // Action
  primary: colors.amber,
  primaryHover: colors.amberHover,
  ring: colors.amber,

  // Borders
  border: colors.paper300,
  borderStrong: colors.paper400,
} as const;
