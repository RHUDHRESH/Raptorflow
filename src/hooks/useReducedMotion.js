import { useEffect, useState } from 'react'

/**
 * Hook to detect if user prefers reduced motion
 * Respects system accessibility settings
 * @returns {boolean} - true if user prefers reduced motion
 */
export function useReducedMotion() {
    const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

    useEffect(() => {
        // Check if browser supports matchMedia
        if (typeof window === 'undefined' || !window.matchMedia) {
            return
        }

        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')

        // Set initial value
        setPrefersReducedMotion(mediaQuery.matches)

        // Listen for changes
        const handleChange = (event) => {
            setPrefersReducedMotion(event.matches)
        }

        // Modern browsers
        if (mediaQuery.addEventListener) {
            mediaQuery.addEventListener('change', handleChange)
            return () => mediaQuery.removeEventListener('change', handleChange)
        }
        // Fallback for older browsers
        else if (mediaQuery.addListener) {
            mediaQuery.addListener(handleChange)
            return () => mediaQuery.removeListener(handleChange)
        }
    }, [])

    return prefersReducedMotion
}

/**
 * Helper to get animation config based on reduced motion preference
 * @param {boolean} prefersReducedMotion - from useReducedMotion hook
 * @returns {object} - animation config for framer-motion
 */
export function getAnimationConfig(prefersReducedMotion) {
    return prefersReducedMotion
        ? {
            initial: { opacity: 1 },
            animate: { opacity: 1 },
            transition: { duration: 0 }
        }
        : undefined // Return undefined to use default framer-motion behavior
}

export default useReducedMotion
