import { Variants } from 'framer-motion';

/**
 * "Quiet Luxury" Animation System
 * Smooth, understated, and performant animations.
 */

export const transitions = {
  smooth: {
    duration: 0.5,
    ease: [0.25, 0.1, 0.25, 1.0] as const, // Cubic bezier for "editorial" feel
  },
  spring: {
    type: 'spring',
    stiffness: 300,
    damping: 30,
  },
};

export const delays = {
  stagger: 0.05,
};

export const animations = {
  // Fade in from transparent
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: 0.4 } },
  } as Variants,

  // Subtle slide up (for cards, list items)
  slideUp: {
    initial: { opacity: 0, y: 10 },
    animate: {
      opacity: 1,
      y: 0,
      transition: transitions.smooth,
    },
  } as Variants,

  // Slide down (for dropdowns, alerts)
  slideDown: {
    initial: { opacity: 0, y: -10 },
    animate: {
      opacity: 1,
      y: 0,
      transition: transitions.smooth,
    },
  } as Variants,

  // Scale in (for modals, popovers)
  scaleIn: {
    initial: { opacity: 0, scale: 0.96 },
    animate: {
      opacity: 1,
      scale: 1,
      transition: transitions.smooth,
    },
  } as Variants,

  // Stagger children container
  staggerContainer: {
    animate: {
      transition: {
        staggerChildren: 0.05,
      },
    },
  } as Variants,
};

// GSAP Helpers (if needed for complex timelines)
// export const gsapConfig = { ... };
