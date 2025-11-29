import { motion } from 'framer-motion'
import { ANIMATION } from '../lib/animations'
import useReducedMotion from '../hooks/useReducedMotion'
import { useState, useEffect, useRef } from 'react'

/**
 * Constraint Card Component
 * Visualizes constraints (e.g., "7 cohorts max") with animated numbers
 * Features thick left border and hover lift effect
 */
export default function ConstraintCard({
    number,
    label,
    sublabel,
    delay = 0,
    className = ''
}) {
    const prefersReducedMotion = useReducedMotion()
    const [count, setCount] = useState(0)
    const nodeRef = useRef(null)

    // Simple intersection observer to trigger count animation
    const [isInView, setIsInView] = useState(false)

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsInView(true)
                    observer.disconnect()
                }
            },
            { threshold: 0.5 }
        )

        if (nodeRef.current) {
            observer.observe(nodeRef.current)
        }

        return () => observer.disconnect()
    }, [])

    // Count up animation
    useEffect(() => {
        if (!isInView || prefersReducedMotion) {
            if (prefersReducedMotion) setCount(number)
            return
        }

        let startTime
        const duration = 2000 // 2 seconds

        const animate = (timestamp) => {
            if (!startTime) startTime = timestamp
            const progress = Math.min((timestamp - startTime) / duration, 1)

            // Ease out quart
            const ease = 1 - Math.pow(1 - progress, 4)

            setCount(Math.floor(ease * number))

            if (progress < 1) {
                requestAnimationFrame(animate)
            } else {
                setCount(number)
            }
        }

        requestAnimationFrame(animate)
    }, [isInView, number, prefersReducedMotion])

    return (
        <motion.div
            ref={nodeRef}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{
                duration: prefersReducedMotion ? 0 : ANIMATION.DURATIONS.normal,
                delay: delay,
                ease: ANIMATION.EASINGS.smooth
            }}
            whileHover={{
                y: -8,
                boxShadow: '0 20px 40px -15px rgba(255, 255, 255, 0.1)',
                borderColor: 'rgba(255, 255, 255, 0.4)'
            }}
            className={`group relative flex flex-col justify-between overflow-hidden rounded-lg bg-white/5 p-6 backdrop-blur-sm transition-all duration-300 border border-white/10 ${className}`}
        >
            {/* Thick left border accent */}
            <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-white transition-all duration-300 group-hover:w-2 group-hover:bg-white" />

            {/* Subtle glow effect on hover */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

            <div className="relative z-10">
                <div className="font-serif text-5xl font-black tracking-tighter text-white mb-2">
                    {count}
                </div>
                <div className="font-mono text-xs uppercase tracking-widest text-white/60 mb-1">
                    {label}
                </div>
                <div className="text-sm text-white/40">
                    {sublabel}
                </div>
            </div>
        </motion.div>
    )
}
