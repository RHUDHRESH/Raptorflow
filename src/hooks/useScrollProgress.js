import { useEffect, useState } from 'react'

/**
 * Hook to track scroll progress (0 to 1)
 * Useful for scroll progress indicators
 * @returns {number} - scroll progress from 0 to 1
 */
export function useScrollProgress() {
    const [scrollProgress, setScrollProgress] = useState(0)

    useEffect(() => {
        const handleScroll = () => {
            const windowHeight = window.innerHeight
            const documentHeight = document.documentElement.scrollHeight
            const scrollTop = window.scrollY

            const totalScrollable = documentHeight - windowHeight
            const progress = totalScrollable > 0 ? scrollTop / totalScrollable : 0

            setScrollProgress(Math.min(Math.max(progress, 0), 1))
        }

        // Set initial value
        handleScroll()

        window.addEventListener('scroll', handleScroll, { passive: true })
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    return scrollProgress
}

export default useScrollProgress
