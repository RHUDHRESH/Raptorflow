import { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import useReducedMotion from '../hooks/useReducedMotion'

/**
 * Magnetic Button Component
 * Buttons that subtly follow the mouse cursor when hovering nearby
 * Disabled when user prefers reduced motion
 */
export default function MagneticButton({
    to,
    children,
    className = '',
    strength = 0.3,
    radius = 80
}) {
    const buttonRef = useRef(null)
    const [position, setPosition] = useState({ x: 0, y: 0 })
    const [isNear, setIsNear] = useState(false)
    const prefersReducedMotion = useReducedMotion()

    const handleMouseMove = (e) => {
        if (!buttonRef.current || prefersReducedMotion) return

        const rect = buttonRef.current.getBoundingClientRect()
        const centerX = rect.left + rect.width / 2
        const centerY = rect.top + rect.height / 2

        // Calculate distance from center
        const deltaX = e.clientX - centerX
        const deltaY = e.clientY - centerY
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)

        // Check if cursor is within magnetic radius
        if (distance < radius) {
            setIsNear(true)
            // Apply magnetic effect (stronger when closer)
            const force = (radius - distance) / radius
            setPosition({
                x: deltaX * strength * force,
                y: deltaY * strength * force
            })
        } else {
            setIsNear(false)
            setPosition({ x: 0, y: 0 })
        }
    }

    const handleMouseLeave = () => {
        setIsNear(false)
        setPosition({ x: 0, y: 0 })
    }

    return (
        <Link
            to={to}
            ref={buttonRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            className={className}
            style={{
                transform: `translate(${position.x}px, ${position.y}px)`,
                transition: isNear ? 'transform 0.2s ease-out' : 'transform 0.4s ease-out'
            }}
        >
            {children}
        </Link>
    )
}
