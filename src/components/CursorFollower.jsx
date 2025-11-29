import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import useReducedMotion from '../hooks/useReducedMotion'

/**
 * Cursor Follower Component
 * Subtle glowing effect that follows the mouse cursor
 * Only active in hero section, disabled with reduced motion
 */
export default function CursorFollower() {
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
    const [isVisible, setIsVisible] = useState(false)
    const prefersReducedMotion = useReducedMotion()

    useEffect(() => {
        if (prefersReducedMotion) return

        const handleMouseMove = (e) => {
            setMousePosition({ x: e.clientX, y: e.clientY })
            if (!isVisible) setIsVisible(true)
        }

        const handleMouseLeave = () => {
            setIsVisible(false)
        }

        window.addEventListener('mousemove', handleMouseMove)
        document.addEventListener('mouseleave', handleMouseLeave)

        return () => {
            window.removeEventListener('mousemove', handleMouseMove)
            document.removeEventListener('mouseleave', handleMouseLeave)
        }
    }, [isVisible, prefersReducedMotion])

    if (prefersReducedMotion || !isVisible) return null

    return (
        <motion.div
            className="pointer-events-none fixed z-40"
            style={{
                left: mousePosition.x,
                top: mousePosition.y,
                transform: 'translate(-50%, -50%)'
            }}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0 }}
            transition={{ duration: 0.2 }}
        >
            {/* Outer glow */}
            <div
                className="absolute inset-0 rounded-full"
                style={{
                    width: '200px',
                    height: '200px',
                    background: 'radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%)',
                    filter: 'blur(20px)'
                }}
            />

            {/* Inner glow */}
            <div
                className="absolute inset-0 rounded-full"
                style={{
                    width: '200px',
                    height: '200px',
                    background: 'radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 60%)',
                    filter: 'blur(10px)'
                }}
            />

            {/* Center dot */}
            <div
                className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/20"
                style={{
                    width: '4px',
                    height: '4px',
                    filter: 'blur(1px)'
                }}
            />
        </motion.div>
    )
}
