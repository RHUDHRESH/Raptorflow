import React from 'react'
import { Link } from 'react-router-dom'
import { Check, Play, Zap, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'
import { KPIShowcase } from './KPIShowcase'

export const HeroSection = () => {
    return (
        <section className="relative min-h-screen flex flex-col justify-center pt-24 pb-20 overflow-hidden bg-background">

            {/* Background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute inset-0 bg-background" />

                {/* Floating geometric elements - X factor */}
                <motion.div
                    className="absolute top-[15%] left-[8%] w-16 h-16 border border-zinc-200 rotate-45"
                    animate={{ y: [0, -15, 0], rotate: [45, 50, 45] }}
                    transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
                />
                <motion.div
                    className="absolute top-[25%] right-[12%] w-8 h-8 bg-zinc-100 rounded-full"
                    animate={{ y: [0, 20, 0], scale: [1, 1.1, 1] }}
                    transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                />
                <motion.div
                    className="absolute bottom-[20%] left-[12%] w-24 h-1 bg-zinc-200"
                    animate={{ scaleX: [1, 1.5, 1], opacity: [0.5, 0.8, 0.5] }}
                    transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 2 }}
                />
                <motion.div
                    className="absolute bottom-[30%] right-[8%] w-12 h-12 border-2 border-zinc-300 rounded-full"
                    animate={{ y: [0, -10, 0], x: [0, 5, 0] }}
                    transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
                />

                {/* Subtle grid */}
                <div
                    className="absolute inset-0 opacity-[0.03]"
                    style={{
                        backgroundImage: 'linear-gradient(hsl(var(--foreground) / 0.15) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--foreground) / 0.15) 1px, transparent 1px)',
                        backgroundSize: '60px 60px'
                    }}
                />
            </div>

            <div className="container-editorial relative z-10 w-full">
                <div className="max-w-5xl mx-auto text-center">
                    {/* Badge with pulse effect */}
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{ duration: 0.6, type: "spring", stiffness: 100 }}
                        className="mb-8"
                    >
                        <motion.span
                            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-zinc-900 text-white text-sm font-semibold shadow-lg"
                            whileHover={{ scale: 1.05 }}
                            transition={{ type: "spring", stiffness: 400 }}
                        >
                            <motion.div
                                animate={{ rotate: [0, 360] }}
                                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                            >
                                <Zap className="w-4 h-4" />
                            </motion.div>
                            Marketing System for Founders
                        </motion.span>
                    </motion.div>

                    {/* Main Headline - Static, Bold, Direct */}
                    <motion.h1
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="font-serif text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-medium tracking-tight text-foreground leading-[1.05]"
                    >
                        Your Marketing.
                        <br />
                        <span className="text-zinc-900 italic">
                            Finally Under Control.
                        </span>
                    </motion.h1>

                    {/* Subheadline */}
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="mt-8 text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed"
                    >
                        RaptorFlow gives founders a complete marketing system—
                        <span className="font-semibold text-foreground"> strategy, content, and execution</span>—
                        in one place. No more chaos. No more guessing.
                    </motion.p>

                    {/* CTAs */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.3 }}
                        className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4"
                    >
                        <Link
                            to="/app"
                            className="group inline-flex items-center gap-3 px-10 py-5 bg-zinc-900 text-white rounded-2xl font-bold text-xl shadow-2xl hover:bg-black transition-all duration-300 hover:scale-[1.02]"
                        >
                            Build My Marketing System
                            <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                        </Link>
                        <Link
                            to="#demo"
                            className="group inline-flex items-center gap-3 px-10 py-5 bg-white border border-zinc-300 rounded-2xl font-semibold text-xl text-zinc-800 hover:border-zinc-400 hover:bg-zinc-50 transition-all duration-300"
                        >
                            <Play className="w-6 h-6 text-zinc-600 fill-zinc-600" />
                            Try the Playground
                        </Link>
                    </motion.div>

                    {/* Trust signals */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className="mt-10 flex flex-wrap items-center justify-center gap-x-10 gap-y-4 text-base font-medium text-muted-foreground"
                    >
                        <span className="flex items-center gap-2">
                            <Check className="w-5 h-5 text-zinc-600" />
                            First campaign in 15 min
                        </span>
                        <span className="flex items-center gap-2">
                            <Check className="w-5 h-5 text-zinc-600" />
                            14-day full refund
                        </span>
                        <span className="flex items-center gap-2">
                            <Check className="w-5 h-5 text-zinc-600" />
                            No agency fees
                        </span>
                    </motion.div>
                </div>

                {/* KPI Showcase */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5, duration: 0.6 }}
                    className="mt-24 max-w-5xl mx-auto"
                >
                    <KPIShowcase />
                </motion.div>
            </div>
        </section>
    )
}

