// Global Animation Constants for RaptorFlow
// Use these throughout the app for consistent, performant animations

export const ANIMATION = {
    // Duration presets (in seconds)
    DURATIONS: {
        instant: 0.1,
        fast: 0.2,
        normal: 0.4,
        slow: 0.6,
        dramatic: 1.0
    },

    // Easing curves (cubic-bezier)
    EASINGS: {
        smooth: [0.4, 0, 0.2, 1],        // Standard easing - smooth and natural
        bounce: [0.34, 1.56, 0.64, 1],   // Playful bounce effect
        sharp: [0.4, 0, 0.6, 1],         // Snappy, quick response
        gentle: [0.4, 0, 0, 1]           // Soft landing, deceleration
    },

    // Stagger delays for sequential animations (in seconds)
    STAGGER: {
        fast: 0.05,
        normal: 0.1,
        slow: 0.15
    },

    // Scroll trigger defaults
    SCROLL: {
        threshold: 0.2,      // Element must be 20% visible
        once: true,          // Only animate once
        amount: 'some'       // Trigger when 'some' of element is visible
    },

    // Hover effect presets
    HOVER: {
        button: {
            scale: 1.05,
            duration: 0.2
        },
        card: {
            y: -8,
            scale: 1.02,
            duration: 0.3
        },
        icon: {
            rotate: 6,
            scale: 1.1,
            duration: 0.3
        }
    }
}

// Helper function to create consistent motion config
export const createMotionConfig = (type = 'normal', easing = 'smooth') => ({
    duration: ANIMATION.DURATIONS[type],
    ease: ANIMATION.EASINGS[easing]
})

// Helper for staggered children animations
export const createStaggerChildren = (speed = 'normal') => ({
    staggerChildren: ANIMATION.STAGGER[speed],
    delayChildren: ANIMATION.DURATIONS.fast
})

export default ANIMATION
