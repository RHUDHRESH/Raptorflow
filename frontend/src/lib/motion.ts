import type { Variants } from "motion/react";

// Card entrance animation - opacity + slight y offset
export const cardEnter: Variants = {
    hidden: {
        opacity: 0,
        y: 6
    },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.3,
            ease: [0.25, 0.1, 0.25, 1]
        }
    }
};

// Staggered container for cards
export const staggerContainer: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.05,
            delayChildren: 0.1
        }
    }
};

// Card hover effect - subtle lift
export const cardHover = {
    rest: {
        y: 0,
        boxShadow: "0 1px 3px rgba(0,0,0,0.06)"
    },
    hover: {
        y: -2,
        boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
        transition: {
            duration: 0.2,
            ease: "easeOut"
        }
    }
};

// Icon rail active state - tiny pulse
export const iconPulse: Variants = {
    inactive: { scale: 1 },
    active: {
        scale: [1, 1.03, 1],
        transition: {
            duration: 0.3,
            ease: "easeInOut"
        }
    }
};

// Tab indicator slide
export const tabSlide: Variants = {
    hidden: { opacity: 0, x: -10 },
    visible: {
        opacity: 1,
        x: 0,
        transition: {
            duration: 0.2,
            ease: "easeOut"
        }
    }
};

// Content fade for tab switching
export const contentFade: Variants = {
    hidden: {
        opacity: 0,
        y: 4
    },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.2,
            ease: "easeOut"
        }
    },
    exit: {
        opacity: 0,
        y: -4,
        transition: {
            duration: 0.15
        }
    }
};

// Page transition
export const pageTransition: Variants = {
    initial: {
        opacity: 0
    },
    animate: {
        opacity: 1,
        transition: {
            duration: 0.3,
            ease: "easeOut"
        }
    },
    exit: {
        opacity: 0,
        transition: {
            duration: 0.15
        }
    }
};

// Sidebar item hover
export const sidebarItemHover = {
    rest: {
        backgroundColor: "transparent"
    },
    hover: {
        backgroundColor: "rgba(0, 0, 0, 0.04)",
        transition: {
            duration: 0.15
        }
    }
};

// Status dot color animation
export const statusDotPulse: Variants = {
    idle: { scale: 1 },
    pulse: {
        scale: [1, 1.2, 1],
        transition: {
            duration: 0.4,
            ease: "easeInOut"
        }
    }
};
