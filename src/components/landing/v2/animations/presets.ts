// Animation presets for Landing Page V2
// GSAP + Framer Motion timing configurations for consistency

// ═══════════════════════════════════════════════════════════════
// TIMING CONFIGS
// ═══════════════════════════════════════════════════════════════

export const TIMING = {
    // Micro-interactions
    micro: 0.15,
    fast: 0.25,
    medium: 0.4,
    slow: 0.6,

    // Page-level
    entrance: 0.8,
    stagger: 0.08,
    parallax: 1.2,
} as const;

// ═══════════════════════════════════════════════════════════════
// EASING CURVES
// ═══════════════════════════════════════════════════════════════

export const EASING = {
    // Smooth, premium feel
    smooth: [0.25, 0.1, 0.25, 1],
    smoothOut: [0, 0, 0.25, 1],
    smoothIn: [0.25, 0, 1, 1],

    // Dramatic entrances
    dramatic: [0.16, 1, 0.3, 1],

    // Bounce (use sparingly)
    bounce: [0.34, 1.56, 0.64, 1],

    // GSAP equivalents (string format)
    gsapSmooth: "power2.out",
    gsapDramatic: "expo.out",
    gsapSnap: "power3.inOut",
} as const;

// ═══════════════════════════════════════════════════════════════
// REVEAL ANIMATIONS (Framer Motion variants)
// ═══════════════════════════════════════════════════════════════

export const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: TIMING.medium,
            ease: EASING.smooth
        }
    }
};

export const fadeIn = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { duration: TIMING.slow }
    }
};

export const scaleIn = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: {
        opacity: 1,
        scale: 1,
        transition: {
            duration: TIMING.medium,
            ease: EASING.smooth
        }
    }
};

export const slideFromLeft = {
    hidden: { opacity: 0, x: -40 },
    visible: {
        opacity: 1,
        x: 0,
        transition: {
            duration: TIMING.medium,
            ease: EASING.smooth
        }
    }
};

export const slideFromRight = {
    hidden: { opacity: 0, x: 40 },
    visible: {
        opacity: 1,
        x: 0,
        transition: {
            duration: TIMING.medium,
            ease: EASING.smooth
        }
    }
};

// ═══════════════════════════════════════════════════════════════
// STAGGER CONTAINERS
// ═══════════════════════════════════════════════════════════════

export const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: TIMING.stagger,
            delayChildren: 0.1,
        }
    }
};

export const staggerContainerFast = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.05,
            delayChildren: 0.05,
        }
    }
};

// ═══════════════════════════════════════════════════════════════
// TEXT REVEAL (Character by character)
// ═══════════════════════════════════════════════════════════════

export const charReveal = {
    hidden: {
        opacity: 0,
        y: 20,
        rotateX: -90,
    },
    visible: {
        opacity: 1,
        y: 0,
        rotateX: 0,
        transition: {
            duration: TIMING.fast,
            ease: EASING.dramatic
        }
    }
};

export const wordReveal = {
    hidden: {
        opacity: 0,
        y: 40,
        clipPath: "inset(100% 0 0 0)",
    },
    visible: {
        opacity: 1,
        y: 0,
        clipPath: "inset(0% 0 0 0)",
        transition: {
            duration: TIMING.medium,
            ease: EASING.dramatic
        }
    }
};

// ═══════════════════════════════════════════════════════════════
// SCROLL TRIGGER DEFAULTS (for GSAP)
// ═══════════════════════════════════════════════════════════════

export const scrollTriggerDefaults = {
    start: "top 85%",
    end: "bottom 15%",
    toggleActions: "play none none reverse",
};

export const scrollTriggerOnce = {
    ...scrollTriggerDefaults,
    toggleActions: "play none none none",
    once: true,
};

// ═══════════════════════════════════════════════════════════════
// HOVER STATES
// ═══════════════════════════════════════════════════════════════

export const hoverLift = {
    scale: 1.02,
    y: -4,
    transition: { duration: TIMING.fast, ease: EASING.smooth }
};

export const hoverGlow = {
    boxShadow: "0 20px 40px rgba(0,0,0,0.08)",
    transition: { duration: TIMING.fast }
};

export const hoverScale = {
    scale: 1.05,
    transition: { duration: TIMING.fast, ease: EASING.smooth }
};

// ═══════════════════════════════════════════════════════════════
// GSAP ANIMATION FACTORIES
// ═══════════════════════════════════════════════════════════════

export const gsapPresets = {
    fadeUp: {
        from: { opacity: 0, y: 50 },
        to: { opacity: 1, y: 0, duration: TIMING.medium, ease: EASING.gsapSmooth },
    },
    fadeIn: {
        from: { opacity: 0 },
        to: { opacity: 1, duration: TIMING.slow, ease: EASING.gsapSmooth },
    },
    scaleIn: {
        from: { opacity: 0, scale: 0.9 },
        to: { opacity: 1, scale: 1, duration: TIMING.medium, ease: EASING.gsapDramatic },
    },
    slideUp: {
        from: { yPercent: 100, opacity: 0 },
        to: { yPercent: 0, opacity: 1, duration: TIMING.medium, ease: EASING.gsapDramatic },
    },
    maskReveal: {
        from: { clipPath: "inset(100% 0 0 0)" },
        to: { clipPath: "inset(0% 0 0 0)", duration: TIMING.slow, ease: EASING.gsapDramatic },
    },
};
