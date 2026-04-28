/**
 * RaptorFlow Motion Constants
 *
 * Standard motion values aligned with globals.css.
 * Do not add heavy animation libraries in this phase.
 * Use existing CSS / Tailwind motion utilities.
 */

export const motion = {
  // Durations (ms)
  fast: 150,
  medium: 240,
  slow: 700,

  // Easing curves
  easeOut: "cubic-bezier(0.16, 1, 0.3, 1)",
  easeSoft: "cubic-bezier(0.4, 0, 0.2, 1)",
  easeInOut: "cubic-bezier(0.65, 0, 0.35, 1)",

  // CSS class names for common transitions
  hoverLift: {
    transition:
      "transform 240ms cubic-bezier(0.4, 0, 0.2, 1), box-shadow 240ms cubic-bezier(0.4, 0, 0.2, 1)",
    hoverTransform: "translateY(-2px)",
  },

  windowEnter: {
    transition:
      "opacity 700ms cubic-bezier(0.16, 1, 0.3, 1), transform 700ms cubic-bezier(0.16, 1, 0.3, 1)",
    initial: { opacity: 0, transform: "translateY(16px)" },
    final: { opacity: 1, transform: "translateY(0)" },
  },

  amberPulse: {
    animation: "amberPulse 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite",
  },
} as const;

/**
 * Reduced-motion helper.
 * Returns the given style object only when motion is not reduced.
 * In component usage, prefer CSS `@media (prefers-reduced-motion: reduce)`.
 */
export function withMotion<T extends object>(style: T, reduced?: T): T {
  if (typeof window === "undefined") return style;
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  return prefersReduced ? (reduced ?? ({} as T)) : style;
}
