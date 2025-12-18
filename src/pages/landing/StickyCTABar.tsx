import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowRight, Check, X } from 'lucide-react'
import { Link } from 'react-router-dom'

// ═══════════════════════════════════════════════════════════════════════════════
// STICKY CTA BAR - Appears after scrolling past hero
// ═══════════════════════════════════════════════════════════════════════════════

export const StickyCTABar = () => {
    const [isVisible, setIsVisible] = useState(false)
    const [isDismissed, setIsDismissed] = useState(false)

    useEffect(() => {
        const handleScroll = () => {
            // Don't show if dismissed
            if (isDismissed) {
                setIsVisible(false)
                return
            }

            // Show after scrolling 600px (past hero)
            const shouldShow = window.scrollY > 600

            // Hide near footer (last 500px of page)
            const nearFooter = window.scrollY > (document.documentElement.scrollHeight - window.innerHeight - 500)

            setIsVisible(shouldShow && !nearFooter)
        }

        window.addEventListener('scroll', handleScroll, { passive: true })
        // Run once on mount
        handleScroll()
        return () => window.removeEventListener('scroll', handleScroll)
    }, [isDismissed])

    const handleDismiss = () => {
        console.log('Dismiss clicked!') // Debug log
        setIsVisible(false) // Immediately hide
        setIsDismissed(true)
        // Reset after 60 seconds so it can appear again
        setTimeout(() => setIsDismissed(false), 60000)
    }

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ y: 100, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: 100, opacity: 0 }}
                    transition={{ type: "spring", damping: 20, stiffness: 300 }}
                    className="fixed bottom-0 left-0 right-0 z-50 p-4 pointer-events-none"
                >
                    <div className="max-w-4xl mx-auto pointer-events-auto">
                        <motion.div
                            className="relative flex flex-col sm:flex-row items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl bg-card/95 backdrop-blur-xl border border-border shadow-2xl shadow-black/20"
                            whileHover={{ y: -2 }}
                        >
                            {/* Dismiss button */}
                            <button
                                onClick={(e) => {
                                    e.preventDefault()
                                    e.stopPropagation()
                                    handleDismiss()
                                }}
                                className="absolute -top-2 -right-2 z-10 w-7 h-7 rounded-full bg-background border border-border flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors shadow-md cursor-pointer"
                                aria-label="Dismiss"
                                type="button"
                            >
                                <X className="w-3.5 h-3.5" />
                            </button>

                            {/* Left side - Trust indicators */}
                            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                                <span className="flex items-center gap-1.5">
                                    <Check className="w-4 h-4 text-zinc-600" />
                                    14-day money-back guarantee
                                </span>
                                <span className="hidden sm:flex items-center gap-1.5">
                                    <Check className="w-4 h-4 text-zinc-600" />
                                    Setup in 15 minutes
                                </span>
                                <span className="hidden md:flex items-center gap-1.5">
                                    <Check className="w-4 h-4 text-zinc-600" />
                                    No credit card required
                                </span>
                            </div>

                            {/* Right side - CTA */}
                            <motion.div
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                            >
                                <Link
                                    to="/signup"
                                    className="group flex items-center gap-2 px-6 py-3 bg-zinc-900 text-white rounded-xl font-medium shadow-lg whitespace-nowrap hover:bg-black transition-all"
                                >
                                    Get Started
                                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </Link>
                            </motion.div>
                        </motion.div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    )
}

export default StickyCTABar

