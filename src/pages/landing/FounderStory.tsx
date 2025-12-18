import React from 'react'
import { motion } from 'framer-motion'
import { Quote, ArrowRight, Heart } from 'lucide-react'
import { Link } from 'react-router-dom'

// ═══════════════════════════════════════════════════════════════════════════════
// FOUNDER STORY - Since we can't show testimonials, our story IS the testimonial
// ═══════════════════════════════════════════════════════════════════════════════

export const FounderStory = () => {
    const painPoints = [
        "Endless tools that didn't connect",
        "AI that generated garbage without context",
        "Strategy docs that gathered dust",
        "'Accountability' apps that just added noise"
    ]

    return (
        <section className="relative py-24 md:py-32 overflow-hidden">
            {/* Background pattern */}
            <div className="absolute inset-0 bg-gradient-to-br from-zinc-100/50 via-background to-background" />
            <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.02)_1px,transparent_1px)] bg-[size:60px_60px] opacity-[0.4]" />

            <div className="container-editorial relative z-10">
                <div className="max-w-4xl mx-auto">
                    {/* Quote mark */}
                    <motion.div
                        className="flex justify-center mb-8"
                        initial={{ opacity: 0, scale: 0.5 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                    >
                        <div className="w-16 h-16 rounded-2xl bg-zinc-100 flex items-center justify-center">
                            <Quote className="w-8 h-8 text-zinc-700" />
                        </div>
                    </motion.div>

                    {/* Main statement */}
                    <motion.div
                        className="text-center mb-12"
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                    >
                        <h2 className="font-serif text-3xl md:text-5xl font-medium text-foreground leading-tight">
                            We built RaptorFlow because we were{' '}
                            <span className="text-zinc-900 italic underline underline-offset-4">tired</span> of...
                        </h2>
                    </motion.div>

                    {/* Pain points list */}
                    <motion.div
                        className="grid md:grid-cols-2 gap-4 mb-16"
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                    >
                        {painPoints.map((point, i) => (
                            <motion.div
                                key={point}
                                className="flex items-center gap-4 p-5 rounded-xl bg-zinc-900 border border-zinc-800"
                                initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: 0.3 + i * 0.1 }}
                                whileHover={{ scale: 1.02 }}
                            >
                                <span className="text-white text-xl font-bold">✕</span>
                                <span className="text-white font-medium">{point}</span>
                            </motion.div>
                        ))}
                    </motion.div>

                    {/* The solution philosophy */}
                    <motion.div
                        className="relative p-8 md:p-12 rounded-3xl bg-card border border-border"
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.4 }}
                    >
                        {/* Decorative gradient */}
                        <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

                        <div className="relative z-10">
                            <p className="text-xl md:text-2xl text-foreground leading-relaxed mb-8">
                                Most marketing software is built for managers. RaptorFlow is built for <span className="text-zinc-900 font-bold italic">owners.</span>
                                <br /><br />
                                We built something different. A system that gives you the same operating cadence that growth teams use—
                                <span className="text-zinc-900 font-bold">simplified for founders who don't have time for bullshit.</span>
                            </p>
                            <div className="mb-10 p-8 bg-zinc-900 text-white rounded-3xl border border-zinc-800 shadow-xl overflow-hidden relative">
                                <div className="absolute top-0 right-0 w-32 h-32 bg-white opacity-[0.03] -mr-16 -mt-16 rounded-full" />
                                <h4 className="text-sm font-bold uppercase tracking-widest text-white/50 mb-4 flex items-center gap-2">
                                    <span className="w-8 h-px bg-white/20" /> Our Mission
                                </h4>
                                <p className="text-white text-lg md:text-xl font-medium leading-relaxed">
                                    To turn every founder into a high-level strategic operator, replacing technical debt and chaos with a definitive, 90-day war plan that compounds every single day.
                                    <span className="block mt-4 text-zinc-400 text-base font-normal">No fluff, no "ghostwriting" garbage—just pure execution.</span>
                                </p>
                            </div>

                            <div className="flex flex-col md:flex-row items-center justify-between gap-6 pt-6 border-t border-border">
                                {/* Philosophy pillars */}
                                <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted">
                                        <span className="w-2 h-2 rounded-full bg-zinc-700" />
                                        Less, but better
                                    </span>
                                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted">
                                        <span className="w-2 h-2 rounded-full bg-zinc-700" />
                                        Ship daily
                                    </span>
                                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted">
                                        <span className="w-2 h-2 rounded-full bg-zinc-700" />
                                        Trust the data
                                    </span>
                                </div>

                                {/* Read more link */}
                                <motion.div whileHover={{ x: 4 }}>
                                    <Link
                                        to="/manifesto"
                                        className="group flex items-center gap-2 text-zinc-900 font-medium hover:underline"
                                    >
                                        Read our manifesto
                                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                    </Link>
                                </motion.div>
                            </div>
                        </div>
                    </motion.div>

                    {/* Bottom statement */}
                    <motion.div
                        className="mt-12 text-center"
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.5 }}
                    >
                        <p className="text-lg text-muted-foreground">
                            A good business shouldn't lose because marketing is confusing.{' '}
                            <span className="text-foreground font-medium">
                                We're here to change that.
                            </span>
                        </p>

                        <motion.div
                            className="mt-6 flex items-center justify-center gap-1 text-sm text-muted-foreground"
                            whileHover={{ scale: 1.05 }}
                        >
                            Built with
                            <motion.span
                                animate={{ scale: [1, 1.2, 1] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            >
                                <Heart className="w-4 h-4 text-red-500 fill-red-500 inline mx-1" />
                            </motion.span>
                            for founders who refuse to guess
                        </motion.div>
                    </motion.div>
                </div>
            </div>
        </section>
    )
}

export default FounderStory

