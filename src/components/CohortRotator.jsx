import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion'
import { Check, ChevronLeft, ChevronRight } from 'lucide-react'
import useReducedMotion from '../hooks/useReducedMotion'
import { ANIMATION } from '../lib/animations'

/**
 * Cohort Rotator Component
 * Auto-rotating cards showing ICP examples with typing effect and progress bar
 */
export default function CohortRotator() {
    const [currentIndex, setCurrentIndex] = useState(0)
    const [isPaused, setIsPaused] = useState(false)
    const prefersReducedMotion = useReducedMotion()
    const progress = useMotionValue(0)

    const cohorts = [
        {
            title: 'Overwhelmed Agency Owner',
            whoTheyAre: 'Runs a 5-15 person marketing agency. Drowning in client deliverables. Struggles to find time for their own marketing.',
            whatTheyNeed: 'A system that doesn\'t add more work. Clear priorities. Finishable tasks that fit between client calls.',
            howYouHelp: '"Marketing that fits your actual life. 1-3 moves per week. No guilt, just clarity."'
        },
        {
            title: 'Solo Founder Wearing All Hats',
            whoTheyAre: 'Building a product solo. Marketing feels like a distraction. Every hour counts. No team to delegate to.',
            whatTheyNeed: 'Marketing that doesn\'t require a full-time commitment. Clear next steps. No analysis paralysis.',
            howYouHelp: '"Ship marketing moves between product sprints. Stay visible without burning out."'
        },
        {
            title: 'Product Manager Launching New Feature',
            whoTheyAre: 'Responsible for adoption metrics. Needs users to actually try the new feature. Limited marketing budget.',
            whatTheyNeed: 'Targeted campaigns that reach the right users. Measurable results. Fast execution.',
            howYouHelp: '"Turn feature launches into focused campaigns. Track what matters. No vanity metrics."'
        }
    ]

    // Auto-rotation logic with progress bar
    useEffect(() => {
        if (isPaused) return

        const duration = 8000 // 8 seconds per slide
        const startTime = Date.now()

        const timer = setInterval(() => {
            const elapsed = Date.now() - startTime
            const p = Math.min(elapsed / duration, 1)
            progress.set(p * 100)

            if (elapsed >= duration) {
                handleNext()
            }
        }, 16)

        return () => clearInterval(timer)
    }, [currentIndex, isPaused])

    const handleNext = () => {
        setCurrentIndex((prev) => (prev + 1) % cohorts.length)
        progress.set(0)
    }

    const handlePrev = () => {
        setCurrentIndex((prev) => (prev - 1 + cohorts.length) % cohorts.length)
        progress.set(0)
    }

    const currentCohort = cohorts[currentIndex]

    return (
        <div
            className="relative max-w-4xl mx-auto"
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
        >
            <div className="mb-6 flex items-center gap-3 justify-center md:justify-start">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-100 text-green-600">
                    <Check className="h-5 w-5" strokeWidth={3} />
                </div>
                <span className="text-sm font-bold uppercase tracking-wider text-gray-500">With RaptorFlow cohorts</span>
            </div>

            <div className="relative overflow-hidden rounded-2xl bg-black shadow-2xl">
                {/* Progress Bar at Top */}
                <motion.div
                    className="absolute top-0 left-0 h-1 bg-white z-20"
                    style={{ width: isPaused ? `${progress.get()}%` : useTransform(progress, p => `${p}%`) }}
                />

                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentIndex}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.4, ease: ANIMATION.EASINGS.smooth }}
                        className="p-8 md:p-12 text-white min-h-[450px] flex flex-col"
                    >
                        {/* Shimmer Background */}
                        <motion.div
                            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent pointer-events-none"
                            animate={{ x: ['-200%', '200%'] }}
                            transition={{ duration: 3, repeat: Infinity, repeatDelay: 2 }}
                        />

                        <div className="relative z-10">
                            <h3 className="font-serif text-3xl md:text-4xl font-black mb-6 leading-tight">
                                ICP Cohort: <span className="text-white/70">"{currentCohort.title}"</span>
                            </h3>

                            <div className="space-y-8">
                                <div>
                                    <p className="text-xs uppercase tracking-wider text-white/50 mb-2 font-bold">Who They Are</p>
                                    <p className="text-lg leading-relaxed text-white/90">
                                        {currentCohort.whoTheyAre}
                                    </p>
                                </div>

                                <div className="grid md:grid-cols-2 gap-8">
                                    <div>
                                        <p className="text-xs uppercase tracking-wider text-white/50 mb-2 font-bold">What They Need</p>
                                        <p className="text-base leading-relaxed text-white/80">
                                            {currentCohort.whatTheyNeed}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-xs uppercase tracking-wider text-white/50 mb-2 font-bold">How You Help</p>
                                        <p className="text-base leading-relaxed text-white italic border-l-2 border-white/20 pl-4">
                                            {currentCohort.howYouHelp}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-auto pt-8 flex items-center justify-between border-t border-white/10 relative z-10">
                            <p className="text-sm text-white/60 font-medium">
                                ✓ Specific, actionable, real
                            </p>

                            {/* Navigation Controls */}
                            <div className="flex items-center gap-4">
                                <button
                                    onClick={handlePrev}
                                    className="p-2 rounded-full hover:bg-white/10 transition-colors"
                                    aria-label="Previous cohort"
                                >
                                    <ChevronLeft className="h-5 w-5" />
                                </button>
                                <div className="flex gap-2">
                                    {cohorts.map((_, i) => (
                                        <button
                                            key={i}
                                            onClick={() => { setCurrentIndex(i); progress.set(0); }}
                                            className={`h-1.5 rounded-full transition-all duration-300 ${i === currentIndex ? 'w-6 bg-white' : 'w-1.5 bg-white/30 hover:bg-white/50'}`}
                                            aria-label={`Go to cohort ${i + 1}`}
                                        />
                                    ))}
                                </div>
                                <button
                                    onClick={handleNext}
                                    className="p-2 rounded-full hover:bg-white/10 transition-colors"
                                    aria-label="Next cohort"
                                >
                                    <ChevronRight className="h-5 w-5" />
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    )
}
