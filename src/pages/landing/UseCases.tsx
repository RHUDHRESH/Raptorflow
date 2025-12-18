import React, { useRef, useState, useEffect } from 'react'
import { motion, useMotionTemplate, useMotionValue, useSpring } from 'framer-motion'
import { ArrowRight, Target, Zap, TrendingUp, CheckCircle2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { IconLaunch, IconAgency, IconGrowth } from '@/components/brand/BrandSystem'

// ═══════════════════════════════════════════════════════════════════════════════
// USE CASES - "WORLD CLASS" EDITION
// Interaction: Mouse-tracking spotlight "Reveal"
// Vibe: Tactical Noir / Lighting up the Dark
// ═══════════════════════════════════════════════════════════════════════════════

const PERSONAS = [
    {
        id: 'founder',
        Icon: IconLaunch,
        title: 'Solo Founder',
        subtitle: 'The Lone Wolf',
        challenge: 'No marketing team. No time. The clock is ticking.',
        solution: 'AI Execution Partner',
        quote: 'Strategy locked in 15 minutes.',
        benefits: [
            '20+ ready assets from day one',
            'Daily checklist = no overwhelm',
            'Focus on product, not posting'
        ],
        accent: 'from-zinc-500 to-gray-500',
        light: 'rgba(245, 158, 11, 0.15)' // zinc
    },
    {
        id: 'startup',
        Icon: IconGrowth,
        title: 'Startup',
        subtitle: 'The Sprinter',
        challenge: 'Limited runway. High burn. Need traction yesterday.',
        solution: 'Velocity Engine',
        quote: 'Launch campaigns in hours, not weeks.',
        benefits: [
            'A/B test everything automatically',
            'Kill losers, scale winners fast',
            'Investor-ready metrics'
        ],
        accent: 'from-emerald-500 to-teal-500',
        light: 'rgba(16, 185, 129, 0.15)' // Emerald
    },
    {
        id: 'business',
        Icon: IconAgency,
        title: 'Small Business',
        subtitle: 'The Empire Builder',
        challenge: 'Marketing is a black hole. High effort, low ROI.',
        solution: 'Predictability System',
        quote: 'Set it up once. Runs on autopilot.',
        benefits: [
            'Track every lead source',
            'Consistent output, zero burnout',
            'Real ROI, perfectly measured'
        ],
        accent: 'from-gray-500 to-gray-500',
        light: 'rgba(59, 130, 246, 0.15)' // Blue
    }
]

// "Spotlight" Card Component
const SpotlightCard = ({ persona, index }) => {
    const mouseX = useMotionValue(0)
    const mouseY = useMotionValue(0)

    function handleMouseMove({ currentTarget, clientX, clientY }) {
        let { left, top } = currentTarget.getBoundingClientRect()
        mouseX.set(clientX - left)
        mouseY.set(clientY - top)
    }

    const Icon = persona.Icon

    return (
        <div
            className="group relative border border-white/10 bg-zinc-900/60 overflow-hidden rounded-3xl"
            onMouseMove={handleMouseMove}
        >
            {/* The Spotlight Beam */}
            <motion.div
                className="pointer-events-none absolute -inset-px opacity-0 transition duration-300 group-hover:opacity-100"
                style={{
                    background: useMotionTemplate`
                        radial-gradient(
                            650px circle at ${mouseX}px ${mouseY}px,
                            ${persona.light},
                            transparent 80%
                        )
                    `
                }}
            />

            {/* Inner Content Container */}
            <div className="relative h-full p-8 md:p-10 flex flex-col z-10">
                {/* Header Section */}
                <div className="mb-8 flex items-start justify-between">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className={`h-1.5 w-1.5 rounded-full bg-gradient-to-r ${persona.accent} animate-pulse`} />
                            <span className="text-xs font-mono uppercase tracking-widest text-zinc-500">{persona.subtitle}</span>
                        </div>
                        <h3 className="text-3xl font-serif text-white">{persona.title}</h3>
                    </div>
                    <div className="relative group-hover:scale-110 transition-transform duration-500">
                        <div className={`absolute inset-0 bg-gradient-to-br ${persona.accent} blur-xl opacity-20`} />
                        <Icon size={40} className="text-white relative z-10" />
                    </div>
                </div>

                {/* The "Problem" (Darkness) */}
                <div className="mb-8 relative pl-4 border-l-2 border-zinc-800 group-hover:border-zinc-700 transition-colors">
                    <p className="text-zinc-500 text-sm leading-relaxed font-mono">
                        // OBSTACLE DETECTED
                    </p>
                    <p className="text-zinc-400 mt-1 italic">
                        "{persona.challenge}"
                    </p>
                </div>

                {/* The "Solution" (Light) - Only fully reveals on hover/focus */}
                <div className="mt-auto">
                    <div className="mb-6">
                        <h4 className={`text-transparent bg-clip-text bg-gradient-to-r ${persona.accent} font-bold uppercase tracking-wider text-sm mb-2`}>
                            {persona.solution}
                        </h4>
                        <p className="text-xl text-white font-medium leading-tight">
                            {persona.quote}
                        </p>
                    </div>

                    <ul className="space-y-3 pt-6 border-t border-white/5">
                        {persona.benefits.map((benefit, i) => (
                            <li key={i} className="flex items-center gap-3 text-zinc-400 group-hover:text-zinc-200 transition-colors">
                                <CheckCircle2 size={16} className={`flex-shrink-0 text-zinc-600 group-hover:text-white transition-colors`} />
                                <span className="text-sm">{benefit}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Grid Pattern overlay for texture */}
            <div className="pointer-events-none absolute inset-0 opacity-[0.03]"
                style={{ backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)', backgroundSize: '40px 40px' }}
            />
        </div>
    )
}

export const UseCases = () => {
    return (
        <section className="relative py-32 bg-[#FDFBF7] overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 pointer-events-none opacity-50">
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-black/5 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-black/5 to-transparent" />
            </div>

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                {/* Section Header */}
                <div className="max-w-3xl mx-auto text-center mb-20">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-zinc-600 mb-6"
                    >
                        <span className="w-8 h-px bg-zinc-400" />
                        Your Battle Station
                        <span className="w-8 h-px bg-zinc-400" />
                    </motion.div>
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-4xl md:text-6xl font-serif text-black mb-6"
                    >
                        Built for founders who <span className="bg-clip-text text-transparent bg-gradient-to-r from-zinc-500 to-gray-500 italic font-bold">execute</span>.
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="text-xl text-zinc-600"
                    >
                        No more excuses. No more "I'll figure it out later." Pick your path. Get your plan.
                    </motion.p>
                </div>

                {/* Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
                    {PERSONAS.map((persona, i) => (
                        <div key={persona.id} className="relative group">
                            <div className="h-full p-8 rounded-2xl bg-white border border-black/5 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                                <div className="flex items-start justify-between mb-8">
                                    <div>
                                        <h3 className="text-2xl font-serif text-black mb-1">{persona.title}</h3>
                                        <p className="text-xs uppercase tracking-widest text-zinc-500">{persona.subtitle}</p>
                                    </div>
                                    <div className={`p-3 rounded-xl bg-gradient-to-br ${persona.accent} text-white shadow-lg`}>
                                        <persona.Icon size={24} />
                                    </div>
                                </div>

                                <div className="mb-6">
                                    <p className="text-xs font-bold uppercase text-red-500 mb-1">Challenge</p>
                                    <p className="text-zinc-600 italic">"{persona.challenge}"</p>
                                </div>

                                <div className="mb-6">
                                    <p className="text-xs font-bold uppercase text-emerald-600 mb-1">Solution</p>
                                    <p className="text-black font-medium">{persona.quote}</p>
                                </div>

                                <ul className="space-y-2 pt-6 border-t border-black/5">
                                    {persona.benefits.map((benefit, j) => (
                                        <li key={j} className="flex items-center gap-2 text-sm text-zinc-600">
                                            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                                            {benefit}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ))}
                </div>

                {/* CTA */}
                <motion.div
                    className="mt-20 text-center"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.4 }}
                >
                    <p className="text-zinc-600 mb-8 font-medium">
                        Not sure if RaptorFlow fits your workflow?
                    </p>
                    <Link
                        to="/contact"
                        className="group inline-flex items-center gap-3 px-8 py-4 bg-black text-white rounded-full font-bold hover:bg-zinc-800 transition-all duration-300 shadow-xl"
                    >
                        Commence Briefing
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </Link>
                </motion.div>
            </div>
        </section>
    )
}

export default UseCases

