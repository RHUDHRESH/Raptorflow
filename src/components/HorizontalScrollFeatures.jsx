import { useRef, useState, useEffect } from 'react'
import { motion, useScroll, useTransform, useSpring } from 'framer-motion'
import { ChevronLeft, ChevronRight, BarChart3, Users, Target, Zap, Layers, Clock } from 'lucide-react'
import useReducedMotion from '../hooks/useReducedMotion'
import { ANIMATION } from '../lib/animations'

/**
 * Horizontal Scroll Features Component
 * Scrollable card carousel with snap points and parallax effects
 */
export default function HorizontalScrollFeatures() {
    const scrollRef = useRef(null)
    const prefersReducedMotion = useReducedMotion()
    const [canScrollLeft, setCanScrollLeft] = useState(false)
    const [canScrollRight, setCanScrollRight] = useState(true)

    const features = [
        {
            id: '01',
            title: 'Cohort Builder',
            desc: 'Define your buyers not by demographics, but by their real-world context and problems.',
            icon: Users,
            color: 'bg-blue-500'
        },
        {
            id: '02',
            title: 'Campaign Matrix',
            desc: 'Map your marketing moves to specific cohorts. No more random acts of marketing.',
            icon: Layers,
            color: 'bg-purple-500'
        },
        {
            id: '03',
            title: 'Move Planner',
            desc: 'Plan finishable 1-3 hour tasks. Stop drowning in endless to-do lists.',
            icon: Clock,
            color: 'bg-green-500'
        },
        {
            id: '04',
            title: 'Impact Tracking',
            desc: 'Measure what actually matters. Revenue, conversations, and clarity.',
            icon: BarChart3,
            color: 'bg-orange-500'
        },
        {
            id: '05',
            title: 'Strategy Guardrails',
            desc: 'Built-in limits prevent burnout. 3 moves/week, 7 cohorts max.',
            icon: Target,
            color: 'bg-red-500'
        },
        {
            id: '06',
            title: 'Execution Velocity',
            desc: 'Ship faster by focusing only on what moves the needle today.',
            icon: Zap,
            color: 'bg-yellow-500'
        }
    ]

    const checkScroll = () => {
        if (scrollRef.current) {
            const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current
            setCanScrollLeft(scrollLeft > 0)
            setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10)
        }
    }

    useEffect(() => {
        checkScroll()
        window.addEventListener('resize', checkScroll)
        return () => window.removeEventListener('resize', checkScroll)
    }, [])

    const scroll = (direction) => {
        if (scrollRef.current) {
            const { clientWidth } = scrollRef.current
            const scrollAmount = direction === 'left' ? -clientWidth / 2 : clientWidth / 2
            scrollRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' })
        }
    }

    return (
        <div className="relative py-10">
            {/* Navigation Controls (Desktop) */}
            <div className="hidden md:flex justify-end gap-4 mb-8 px-6 max-w-7xl mx-auto">
                <button
                    onClick={() => scroll('left')}
                    disabled={!canScrollLeft}
                    className={`p-3 rounded-full border border-black/10 transition-all ${canScrollLeft ? 'hover:bg-black hover:text-white' : 'opacity-30 cursor-not-allowed'
                        }`}
                >
                    <ChevronLeft className="h-6 w-6" />
                </button>
                <button
                    onClick={() => scroll('right')}
                    disabled={!canScrollRight}
                    className={`p-3 rounded-full border border-black/10 transition-all ${canScrollRight ? 'hover:bg-black hover:text-white' : 'opacity-30 cursor-not-allowed'
                        }`}
                >
                    <ChevronRight className="h-6 w-6" />
                </button>
            </div>

            {/* Scroll Container */}
            <div
                ref={scrollRef}
                onScroll={checkScroll}
                className="flex overflow-x-auto snap-x snap-mandatory gap-6 px-6 pb-12 scrollbar-hide"
                style={{ scrollPaddingLeft: '1.5rem', scrollPaddingRight: '1.5rem' }}
            >
                {features.map((feature, i) => (
                    <motion.div
                        key={feature.id}
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: i * 0.1 }}
                        className="snap-center flex-shrink-0 w-[85vw] md:w-[400px] group"
                    >
                        <div className="h-full border-2 border-black/5 bg-white p-8 rounded-2xl transition-all duration-300 hover:border-black hover:shadow-2xl relative overflow-hidden">
                            {/* Number Badge */}
                            <div className="absolute top-6 right-6 font-mono text-4xl font-bold text-black/5 group-hover:text-black/10 transition-colors">
                                {feature.id}
                            </div>

                            {/* Icon */}
                            <div className={`mb-6 inline-flex h-14 w-14 items-center justify-center rounded-xl ${feature.color} text-white shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                                <feature.icon className="h-7 w-7" strokeWidth={2.5} />
                            </div>

                            <h3 className="font-serif text-2xl font-black mb-4 group-hover:translate-x-1 transition-transform">
                                {feature.title}
                            </h3>

                            <p className="text-gray-600 leading-relaxed text-lg">
                                {feature.desc}
                            </p>

                            {/* Hover Line */}
                            <div className="absolute bottom-0 left-0 h-1.5 bg-black w-0 group-hover:w-full transition-all duration-500 ease-out" />
                        </div>
                    </motion.div>
                ))}

                {/* Spacer for right padding */}
                <div className="w-6 flex-shrink-0" />
            </div>
        </div>
    )
}
