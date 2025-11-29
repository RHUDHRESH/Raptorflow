import { motion } from 'framer-motion'
import { Target, Zap, TrendingUp } from 'lucide-react'
import useReducedMotion from '../hooks/useReducedMotion'
import { ANIMATION } from '../lib/animations'

/**
 * Floating Dashboard Mockup
 * 3D perspective mockup of RaptorFlow dashboard
 * Uses CSS 3D transforms for depth effect
 */
export default function FloatingMockup() {
    const prefersReducedMotion = useReducedMotion()

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.8, rotateY: 20 }}
            animate={{ opacity: 1, scale: 1, rotateY: 0 }}
            transition={{
                duration: prefersReducedMotion ? 0 : ANIMATION.DURATIONS.dramatic,
                delay: 0.4,
                ease: ANIMATION.EASINGS.smooth
            }}
            className="relative"
            style={{
                perspective: '1000px',
                transformStyle: 'preserve-3d'
            }}
        >
            {/* Main dashboard card */}
            <motion.div
                animate={prefersReducedMotion ? {} : {
                    rotateX: [0, 2, 0, -2, 0],
                    rotateY: [0, -2, 0, 2, 0],
                }}
                transition={{
                    duration: 20,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
                className="relative rounded-lg border-2 border-white/20 bg-black/90 p-6 backdrop-blur-xl shadow-2xl"
                style={{
                    transformStyle: 'preserve-3d',
                    transform: 'translateZ(0px)'
                }}
            >
                {/* Subtle noise texture */}
                <div
                    className="absolute inset-0 opacity-5 rounded-lg"
                    style={{
                        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' /%3E%3C/svg%3E")`,
                    }}
                />

                {/* Top bar */}
                <div className="mb-4 flex items-center justify-between border-b border-white/10 pb-3">
                    <h3 className="font-serif text-sm font-bold tracking-tight text-white">RaptorFlow Dashboard</h3>
                    <div className="flex gap-1.5">
                        <div className="h-2 w-2 rounded-full bg-white/20" />
                        <div className="h-2 w-2 rounded-full bg-white/20" />
                        <div className="h-2 w-2 rounded-full bg-white/20" />
                    </div>
                </div>

                {/* Stats cards */}
                <div className="space-y-3">
                    {[
                        { icon: Target, label: 'Cohorts', value: '5 active', delay: 0.1 },
                        { icon: Zap, label: 'Moves', value: '3 this week', delay: 0.2 },
                        { icon: TrendingUp, label: 'Clarity', value: '100%', delay: 0.3 }
                    ].map((item, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{
                                duration: prefersReducedMotion ? 0 : ANIMATION.DURATIONS.normal,
                                delay: 0.6 + item.delay,
                                ease: ANIMATION.EASINGS.smooth
                            }}
                            className="group flex items-center gap-3 rounded-md border border-white/10 bg-white/5 p-3 backdrop-blur-sm transition-all duration-300 hover:border-white/30 hover:bg-white/10"
                            style={{
                                transform: `translateZ(${(i + 1) * 10}px)`
                            }}
                        >
                            <div className="rounded-md bg-white/10 p-2">
                                <item.icon className="h-4 w-4 text-white" strokeWidth={2} />
                            </div>
                            <div className="flex-1">
                                <div className="text-xs font-mono uppercase tracking-wider text-white/50">
                                    {item.label}
                                </div>
                                <div className="font-serif text-sm font-bold text-white">
                                    {item.value}
                                </div>
                            </div>
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ delay: 0.8 + item.delay }}
                                className="h-2 w-2 rounded-full bg-white"
                            />
                        </motion.div>
                    ))}
                </div>

                {/* Bottom indicator */}
                <motion.div
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: 1 }}
                    transition={{ duration: 1, delay: 1.2 }}
                    className="mt-4 h-1 rounded-full bg-gradient-to-r from-white/20 via-white/50 to-white/20"
                    style={{ transformOrigin: 'left' }}
                />
            </motion.div>

            {/* Floating decorative elements */}
            {[...Array(3)].map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute h-16 w-16 rounded-full border border-white/10"
                    style={{
                        left: `${-10 + i * 30}%`,
                        top: `${20 + i * 20}%`,
                        background: 'radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%)',
                    }}
                    animate={prefersReducedMotion ? {} : {
                        y: [0, -20, 0],
                        opacity: [0.2, 0.4, 0.2],
                        scale: [1, 1.1, 1],
                    }}
                    transition={{
                        duration: 4 + i,
                        repeat: Infinity,
                        delay: i * 0.5,
                    }}
                />
            ))}
        </motion.div>
    )
}
