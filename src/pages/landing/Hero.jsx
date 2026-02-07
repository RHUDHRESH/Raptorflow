import React, { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useScroll, useTransform } from 'framer-motion'
import { Play, ChevronDown } from 'lucide-react'

const Hero = () => {
    const navigate = useNavigate()
    const containerRef = useRef(null)
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start start", "end start"]
    })

    const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
    const scale = useTransform(scrollYProgress, [0, 0.5], [1, 1.1])
    const y = useTransform(scrollYProgress, [0, 0.5], [0, 100])

    return (
        <section 
            ref={containerRef} 
            className="relative h-screen overflow-hidden bg-black"
        >
            {/* Background video/image overlay */}
            <motion.div 
                style={{ scale }}
                className="absolute inset-0"
            >
                {/* Cinematic gradient */}
                <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black" />
                <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-transparent to-black/80" />
                
                {/* Animated mesh */}
                <div className="absolute inset-0 opacity-30">
                    <div 
                        className="absolute inset-0"
                        style={{
                            backgroundImage: `radial-gradient(circle at 20% 50%, rgba(220, 180, 120, 0.15) 0%, transparent 50%),
                                            radial-gradient(circle at 80% 50%, rgba(180, 140, 100, 0.1) 0%, transparent 50%)`
                        }}
                    />
                </div>

                {/* Film grain */}
                <div 
                    className="absolute inset-0 opacity-[0.03] mix-blend-overlay"
                    style={{
                        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`
                    }}
                />
            </motion.div>

            {/* Content */}
            <motion.div 
                style={{ opacity, y }}
                className="relative z-10 h-full flex flex-col items-center justify-center px-6"
            >
                {/* Eyebrow */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1, delay: 0.5 }}
                    className="mb-8"
                >
                    <span className="text-[10px] uppercase tracking-[0.4em] text-white/40 font-light">
                        The Strategic Operating System
                    </span>
                </motion.div>

                {/* Main headline */}
                <div className="text-center max-w-5xl">
                    <motion.h1
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1.2, delay: 0.7 }}
                        className="font-light text-white text-5xl sm:text-6xl md:text-7xl lg:text-8xl leading-[0.9] tracking-tight"
                    >
                        Learn to build
                        <br />
                        <span className="italic font-normal bg-gradient-to-r from-amber-200 via-yellow-100 to-amber-200 bg-clip-text text-transparent">
                            strategy that ships
                        </span>
                    </motion.h1>
                </div>

                {/* Subtitle */}
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1, delay: 1.1 }}
                    className="mt-8 text-lg md:text-xl text-white/50 font-light text-center max-w-2xl leading-relaxed"
                >
                    Transform your scattered ideas into a precision 90-day execution plan. 
                    <span className="text-white/70"> The methodology trusted by 500+ founders.</span>
                </motion.p>

                {/* CTAs */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 1, delay: 1.3 }}
                    className="mt-12 flex flex-col sm:flex-row items-center gap-6"
                >
                    {/* Primary CTA */}
                    <button
                        onClick={() => navigate('/start')}
                        className="group relative px-10 py-5 bg-white text-black font-medium tracking-wide overflow-hidden transition-transform hover:scale-105"
                    >
                        <span className="relative z-10 flex items-center gap-3">
                            <Play className="w-4 h-4 fill-current" />
                            Get Started
                        </span>
                    </button>

                    {/* Secondary */}
                    <button className="flex items-center gap-3 text-white/60 hover:text-white transition-colors">
                        <span className="text-sm tracking-wide">View Curriculum</span>
                        <ChevronDown className="w-4 h-4" />
                    </button>
                </motion.div>

                {/* Bottom fade indicator */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 2 }}
                    className="absolute bottom-12 left-1/2 -translate-x-1/2"
                >
                    <motion.div
                        animate={{ y: [0, 8, 0] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="flex flex-col items-center gap-4"
                    >
                        <span className="text-[10px] uppercase tracking-[0.3em] text-white/30">
                            Scroll to discover
                        </span>
                        <div className="w-px h-12 bg-gradient-to-b from-white/30 to-transparent" />
                    </motion.div>
                </motion.div>
            </motion.div>

            {/* Vignette */}
            <div className="absolute inset-0 pointer-events-none shadow-[inset_0_0_200px_rgba(0,0,0,0.8)]" />
        </section>
    )
}

export default Hero
