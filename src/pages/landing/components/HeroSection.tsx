import React from 'react'
import { Link } from 'react-router-dom'
import { Check, Play, Zap, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'
import { KPIShowcase } from './KPIShowcase'

export const HeroSection = () => {
    return (
        <section className="relative min-h-screen flex flex-col justify-center pt-24 pb-20 overflow-hidden" style={{ backgroundColor: '#FDFBF7' }}>
            {/* Background */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute inset-0" style={{ backgroundColor: '#FDFBF7' }} />

                {/* Warm gradient orbs */}
                <div
                    className="absolute top-[10%] left-[5%] w-[600px] h-[600px] rounded-full opacity-60"
                    style={{ background: 'radial-gradient(circle, rgba(251, 191, 36, 0.15) 0%, transparent 70%)' }}
                />
                <div
                    className="absolute bottom-[10%] right-[10%] w-[500px] h-[500px] rounded-full opacity-50"
                    style={{ background: 'radial-gradient(circle, rgba(249, 115, 22, 0.1) 0%, transparent 70%)' }}
                />

                {/* Subtle grid */}
                <div
                    className="absolute inset-0 opacity-[0.025]"
                    style={{
                        backgroundImage: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)',
                        backgroundSize: '80px 80px'
                    }}
                />
            </div>

            <div className="container-editorial relative z-10 w-full">
                <div className="max-w-5xl mx-auto text-center">
                    {/* Badge */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="mb-8"
                    >
                        <span className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-amber-100 border border-amber-200/60 text-sm font-semibold text-amber-700">
                            <Zap className="w-4 h-4" />
                            The War Room for Founders
                        </span>
                    </motion.div>

                    {/* Main Headline - Static, Bold, Direct */}
                    <motion.h1
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="font-serif text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-medium tracking-tight text-zinc-900 leading-[1.05]"
                    >
                        Your Marketing.
                        <br />
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600">
                            Finally Under Control.
                        </span>
                    </motion.h1>

                    {/* Subheadline */}
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="mt-8 text-xl md:text-2xl text-zinc-600 max-w-3xl mx-auto leading-relaxed"
                    >
                        RaptorFlow gives founders a complete marketing system—
                        <span className="font-semibold text-zinc-800"> strategy, content, and execution</span>—
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
                            to="/signup"
                            className="group inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-2xl font-bold text-xl shadow-2xl shadow-amber-500/25 hover:shadow-amber-500/40 transition-all duration-300 hover:scale-[1.02]"
                        >
                            Build My War Plan
                            <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                        </Link>
                        <Link
                            to="#demo"
                            className="group inline-flex items-center gap-3 px-10 py-5 bg-white border-2 border-zinc-200 rounded-2xl font-semibold text-xl text-zinc-700 hover:border-amber-300 hover:bg-amber-50/50 transition-all duration-300"
                        >
                            <Play className="w-6 h-6 text-amber-500 fill-amber-500" />
                            Try the Playground
                        </Link>
                    </motion.div>

                    {/* Trust signals */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className="mt-10 flex flex-wrap items-center justify-center gap-x-10 gap-y-4 text-base font-medium text-zinc-500"
                    >
                        <span className="flex items-center gap-2">
                            <Check className="w-5 h-5 text-emerald-500" />
                            First campaign in 15 min
                        </span>
                        <span className="flex items-center gap-2">
                            <Check className="w-5 h-5 text-emerald-500" />
                            14-day full refund
                        </span>
                        <span className="flex items-center gap-2">
                            <Check className="w-5 h-5 text-emerald-500" />
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
