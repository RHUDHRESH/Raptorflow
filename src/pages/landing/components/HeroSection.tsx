import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Check, Play, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { InteractiveArt } from './InteractiveArt'
import { KPIShowcase } from './KPIShowcase'
import { ROTATING_WORDS } from '@/data/landing-content'

// Dynamic morphing arrow component
const MorphingArrow = () => (
    <div className="relative w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24">
        {/* Outer rotating ring */}
        <motion.div
            className="absolute inset-0 rounded-full border-2 border-dashed border-amber-500/30"
            animate={{ rotate: 360 }}
            transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
        />

        {/* Inner pulsing glow */}
        <motion.div
            className="absolute inset-2 rounded-full bg-gradient-to-br from-amber-500/20 to-orange-500/20"
            animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0.8, 0.5] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />

        {/* Arrow icon */}
        <motion.svg
            viewBox="0 0 24 24"
            className="absolute inset-0 w-full h-full p-4 sm:p-5 text-amber-500"
            animate={{ x: [0, 4, 0] }}
            transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
        >
            <motion.path
                d="M5 12h14M13 5l7 7-7 7"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="none"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1, ease: "easeOut" }}
            />
        </motion.svg>

        {/* Particle sparks */}
        {[...Array(3)].map((_, i) => (
            <motion.div
                key={i}
                className="absolute right-0 top-1/2 w-1.5 h-1.5 rounded-full bg-amber-400"
                initial={{ x: 0, opacity: 0 }}
                animate={{
                    x: [0, 20, 30],
                    opacity: [0, 1, 0],
                    scale: [0.5, 1, 0.5]
                }}
                transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    delay: i * 0.3,
                    ease: "easeOut"
                }}
            />
        ))}
    </div>
)

const RotatingWord = () => {
    const [index, setIndex] = useState(0)

    useEffect(() => {
        const interval = setInterval(() => {
            setIndex(i => (i + 1) % ROTATING_WORDS.length)
        }, 4000)
        return () => clearInterval(interval)
    }, [])

    const currentWord = ROTATING_WORDS[index]

    return (
        <div className="relative flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 md:gap-8 py-6 sm:py-8">
            {/* FROM word - Faded out with destruction effect */}
            <div className="relative">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentWord.from}
                        className="relative"
                        initial={{ opacity: 0, x: -30, filter: 'blur(10px)' }}
                        animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
                        exit={{ opacity: 0, x: -20, filter: 'blur(10px)', scale: 0.9 }}
                        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
                    >
                        {/* Broken/shattered background effect */}
                        <motion.div
                            className="absolute -inset-3 rounded-xl bg-red-500/5 border border-red-500/10"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.3 }}
                        />

                        <span className="relative inline-block font-bold text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-red-400/70">
                            {currentWord.from}
                            {/* Animated strikethrough */}
                            <motion.span
                                className="absolute left-0 right-0 top-1/2 h-[4px] bg-gradient-to-r from-red-500/80 via-red-400 to-red-500/80 origin-left"
                                initial={{ scaleX: 0 }}
                                animate={{ scaleX: 1 }}
                                transition={{ delay: 0.5, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                            />
                        </span>
                    </motion.div>
                </AnimatePresence>
            </div>

            {/* Dynamic Morphing Arrow */}
            <MorphingArrow />

            {/* TO word - Vibrant and victorious */}
            <div className="relative">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentWord.to}
                        className="relative"
                        initial={{ opacity: 0, x: 30, filter: 'blur(10px)', scale: 0.9 }}
                        animate={{ opacity: 1, x: 0, filter: 'blur(0px)', scale: 1 }}
                        exit={{ opacity: 0, x: 20, filter: 'blur(10px)' }}
                        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
                    >
                        {/* Glowing background */}
                        <motion.div
                            className="absolute -inset-4 rounded-2xl bg-gradient-to-r from-amber-500/10 via-orange-500/15 to-amber-500/10 blur-xl"
                            animate={{ opacity: [0.5, 0.8, 0.5] }}
                            transition={{ duration: 3, repeat: Infinity }}
                        />

                        {/* Premium badge effect */}
                        <motion.div
                            className="absolute -inset-3 rounded-xl border border-amber-500/20 bg-gradient-to-br from-amber-500/5 to-transparent"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.4 }}
                        />

                        <span className="relative inline-block font-black text-4xl sm:text-5xl md:text-6xl lg:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-amber-400 via-orange-500 to-amber-500">
                            {currentWord.to}
                        </span>

                        {/* Sparkle effect */}
                        <motion.div
                            className="absolute -top-2 -right-2"
                            animate={{ rotate: [0, 15, -15, 0], scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        >
                            <Sparkles className="w-5 h-5 text-amber-400" />
                        </motion.div>
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    )
}

export const HeroSection = () => {
    return (
        <section className="relative min-h-screen flex flex-col justify-center pt-20 pb-16 md:pt-24 md:pb-24 overflow-hidden">
            {/* Premium animated background */}
            <div className="absolute inset-0 pointer-events-none">
                {/* Warm cream base */}
                <div className="absolute inset-0 bg-gradient-to-br from-amber-50/80 via-background to-orange-50/50" />

                {/* Animated glow orbs - larger and more prominent */}
                <motion.div
                    className="absolute top-0 left-[10%] w-[800px] h-[800px] rounded-full"
                    style={{ background: 'radial-gradient(circle, rgba(245, 158, 11, 0.12) 0%, transparent 70%)' }}
                    animate={{ scale: [1, 1.15, 1], opacity: [0.6, 0.8, 0.6] }}
                    transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
                />
                <motion.div
                    className="absolute bottom-0 right-[5%] w-[600px] h-[600px] rounded-full"
                    style={{ background: 'radial-gradient(circle, rgba(251, 146, 60, 0.08) 0%, transparent 70%)' }}
                    animate={{ scale: [1.1, 1, 1.1], opacity: [0.4, 0.6, 0.4] }}
                    transition={{ duration: 12, repeat: Infinity, ease: "easeInOut", delay: 3 }}
                />

                {/* Subtle noise texture */}
                <div
                    className="absolute inset-0 opacity-[0.02]"
                    style={{
                        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`
                    }}
                />

                {/* Fine grid pattern */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.02)_1px,transparent_1px)] bg-[size:80px_80px]" />
            </div>

            {/* Interactive stencil art - Hero */}
            <InteractiveArt type="orbit" size={80} position={{ x: '5%', y: '15%' }} delay={0.3} />
            <InteractiveArt type="diamond" size={60} position={{ x: '92%', y: '20%' }} delay={0.5} />
            <InteractiveArt type="target" size={55} position={{ x: '88%', y: '70%' }} delay={0.7} />
            <InteractiveArt type="wave" size={65} position={{ x: '8%', y: '75%' }} delay={0.4} />

            <div className="container-editorial relative z-10 w-full">
                <div className="max-w-5xl mx-auto text-center">
                    {/* Premium label */}
                    <motion.div
                        className="mb-8"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-sm font-medium text-primary">
                            <Sparkles className="w-4 h-4" />
                            The War Room for Founders
                        </span>
                    </motion.div>

                    {/* Main transformation headline */}
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                    >
                        <h1 className="font-serif text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-medium tracking-tight text-foreground leading-tight mb-4">
                            Transform Your Marketing
                        </h1>
                    </motion.div>

                    {/* Rotating words transformation */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                    >
                        <RotatingWord />
                    </motion.div>

                    <motion.p
                        className="mt-6 text-lg md:text-xl lg:text-2xl text-muted-foreground/90 max-w-4xl mx-auto leading-relaxed"
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        Done playing guessing games with marketing? RaptorFlow turns chaos into clear{' '}
                        <span className="text-primary font-bold">campaigns</span>, daily execution, and{' '}
                        <span className="text-primary font-bold">revenue</span>.
                    </motion.p>

                    <motion.div
                        className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <Link
                            to="/signup"
                            className="group relative inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold text-lg shadow-lg shadow-amber-500/25 hover:shadow-xl hover:shadow-amber-500/30 transition-all hover:scale-[1.02]"
                        >
                            Build My War Plan
                            <span className="inline-block group-hover:rotate-12 transition-transform">⚔️</span>
                        </Link>
                        <Link
                            to="#demo"
                            className="inline-flex items-center gap-2 px-8 py-4 border-2 border-primary/30 bg-background/80 backdrop-blur-sm rounded-xl font-medium text-lg hover:border-primary/50 hover:bg-primary/5 transition-all"
                        >
                            <Play className="w-5 h-5 fill-primary text-primary" />
                            Try the Playground
                        </Link>
                    </motion.div>

                    <motion.div
                        className="mt-8 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm font-medium text-muted-foreground"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                    >
                        <span className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" />First campaign in 15 min</span>
                        <span className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" />14-day full refund</span>
                        <span className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-500" />No agency fees</span>
                    </motion.div>
                </div>

                <div className="mt-20 max-w-6xl mx-auto">
                    <KPIShowcase />
                </div>
            </div>
        </section>
    )
}
