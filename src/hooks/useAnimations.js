import { useState, useEffect, useRef, useCallback } from 'react'

/**
 * Hook to track mouse position
 * Used for parallax effects, tilt cards, cursor following
 */
export function useMousePosition() {
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

    useEffect(() => {
        const updateMousePosition = (e) => {
            setMousePosition({ x: e.clientX, y: e.clientY })
        }

        window.addEventListener('mousemove', updateMousePosition)
        return () => window.removeEventListener('mousemove', updateMousePosition)
    }, [])

    return mousePosition
}

/**
 * Hook for 3D tilt effect on cards
 * Returns style object to apply to element
 */
export function useTiltEffect(ref, options = {}) {
    const { maxTilt = 10, perspective = 1000, scale = 1.05 } = options
    const [tiltStyle, setTiltStyle] = useState({})

    const handleMouseMove = useCallback((e) => {
        if (!ref.current) return

        const rect = ref.current.getBoundingClientRect()
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        const centerX = rect.width / 2
        const centerY = rect.height / 2

        const rotateX = ((y - centerY) / centerY) * maxTilt
        const rotateY = ((centerX - x) / centerX) * maxTilt

        setTiltStyle({
            transform: `perspective(${perspective}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(${scale})`,
            transition: 'transform 0.1s ease-out'
        })
    }, [maxTilt, perspective, scale])

    const handleMouseLeave = useCallback(() => {
        setTiltStyle({
            transform: 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1)',
            transition: 'transform 0.5s cubic-bezier(0.23, 1, 0.32, 1)'
        })
    }, [])

    useEffect(() => {
        const element = ref.current
        if (!element) return

        element.addEventListener('mousemove', handleMouseMove)
        element.addEventListener('mouseleave', handleMouseLeave)

        return () => {
            element.removeEventListener('mousemove', handleMouseMove)
            element.removeEventListener('mouseleave', handleMouseLeave)
        }
    }, [handleMouseMove, handleMouseLeave])

    return tiltStyle
}

/**
 * Hook for smooth scroll progress tracking
 * Returns progress from 0 to 1
 */
export function useScrollProgress() {
    const [progress, setProgress] = useState(0)

    useEffect(() => {
        const updateProgress = () => {
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
            const currentProgress = window.scrollY / scrollHeight
            setProgress(currentProgress)
        }

        window.addEventListener('scroll', updateProgress, { passive: true })
        updateProgress()

        return () => window.removeEventListener('scroll', updateProgress)
    }, [])

    return progress
}

/**
 * Hook for detecting scroll direction
 * Returns 'up', 'down', or null
 */
export function useScrollDirection() {
    const [scrollDirection, setScrollDirection] = useState(null)
    const previousScrollY = useRef(0)

    useEffect(() => {
        const handleScroll = () => {
            const currentScrollY = window.scrollY

            if (currentScrollY > previousScrollY.current) {
                setScrollDirection('down')
            } else if (currentScrollY < previousScrollY.current) {
                setScrollDirection('up')
            }

            previousScrollY.current = currentScrollY
        }

        window.addEventListener('scroll', handleScroll, { passive: true })
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    return scrollDirection
}

/**
 * Hook for reduced motion preference
 * Returns true if user prefers reduced motion
 */
export function usePrefersReducedMotion() {
    const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

    useEffect(() => {
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
        setPrefersReducedMotion(mediaQuery.matches)

        const handleChange = (e) => {
            setPrefersReducedMotion(e.matches)
        }

        mediaQuery.addEventListener('change', handleChange)
        return () => mediaQuery.removeEventListener('change', handleChange)
    }, [])

    return prefersReducedMotion
}

/**
 * Hook for detecting if element is in viewport
 * More sophisticated than Intersection Observer
 */
export function useInViewport(ref, options = {}) {
    const { threshold = 0.1, rootMargin = '0px' } = options
    const [isInViewport, setIsInViewport] = useState(false)

    useEffect(() => {
        const element = ref.current
        if (!element) return

        const observer = new IntersectionObserver(
            ([entry]) => {
                setIsInViewport(entry.isIntersecting)
            },
            { threshold, rootMargin }
        )

        observer.observe(element)
        return () => observer.disconnect()
    }, [threshold, rootMargin])

    return isInViewport
}
