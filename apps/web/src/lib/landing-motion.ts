// ─── RaptorFlow Landing Motion Config ────────────────────────────────────────

export const landingMotion = {
  ease: "power3.out",
  softEase: "power2.out",
  duration: 0.8,
  fast: 0.45,
  stagger: 0.08,
  scrollStart: "top 75%",
  scrollOnce: true,
} as const;

export const revealFromBottom = {
  y: 36,
  opacity: 0,
  duration: 0.8,
  ease: "power3.out",
} as const;

export const revealFromLeft = {
  x: -32,
  opacity: 0,
  duration: 0.7,
  ease: "power3.out",
} as const;

export const scaleIn = {
  scale: 0.95,
  opacity: 0,
  duration: 0.6,
  ease: "power2.out",
} as const;
