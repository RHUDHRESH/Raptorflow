import { motion } from 'framer-motion'
import useReducedMotion from '../hooks/useReducedMotion'
import { ANIMATION } from '../lib/animations'

/**
 * Animated Headline Component
 * Splits text into words and animates them in with stagger
 * Creates dramatic reveal effect for hero headlines
 */
export default function AnimatedHeadline({
    children,
    className = '',
    stagger = 'normal',
    delay = 0
}) {
    const prefersReducedMotion = useReducedMotion()

    // Split text into words
    const words = children.split(' ')

    if (prefersReducedMotion) {
        return <h1 className={className}>{children}</h1>
    }

    return (
        <h1 className={className}>
            {words.map((word, i) => (
                <motion.span
                    key={i}
                    className="inline-block"
                    initial={{ opacity: 0, y: 30, rotateX: -90 }}
                    animate={{ opacity: 1, y: 0, rotateX: 0 }}
                    transition={{
                        duration: ANIMATION.DURATIONS.slow,
                        delay: delay + i * ANIMATION.STAGGER[stagger],
                        ease: ANIMATION.EASINGS.smooth
                    }}
                >
                    {word}
                    {i < words.length - 1 && '\u00A0'}
                </motion.span>
            ))}
        </h1>
    )
}
