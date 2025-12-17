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
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-background" />
            <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.02)_1px,transparent_1px)] bg-[size:60px_60px]" />

            <div className="container-editorial relative z-10">
                <div className="max-w-4xl mx-auto">
                    {/* Quote mark */}
                    <motion.div
                        className="flex justify-center mb-8"
                        initial={{ opacity: 0, scale: 0.5 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                    >
                        <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center">
                            <Quote className="w-8 h-8 text-primary" />
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
                            <span className="text-primary italic">tired</span> of...
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
                                className="flex items-center gap-4 p-5 rounded-xl bg-red-500/5 border border-red-500/10"
                                initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: 0.3 + i * 0.1 }}
                                whileHover={{ x: 4, borderColor: 'rgba(239, 68, 68, 0.2)' }}
                            >
                                <span className="text-red-400 text-xl">✕</span>
                                <span className="text-foreground font-medium">{point}</span>
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
                                So we built something different. A system that gives you the same operating cadence that growth teams use—
                                <span className="text-primary font-medium">simplified for founders who don't have time for bullshit.</span>
                            </p>

                            <div className="flex flex-col md:flex-row items-center justify-between gap-6 pt-6 border-t border-border">
                                {/* Philosophy pillars */}
                                <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted">
                                        <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                                        Less, but better
                                    </span>
                                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted">
                                        <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                                        Ship daily
                                    </span>
                                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted">
                                        <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                                        Trust the data
                                    </span>
                                </div>

                                {/* Read more link */}
                                <motion.div whileHover={{ x: 4 }}>
                                    <Link
                                        to="/manifesto"
                                        className="group flex items-center gap-2 text-primary font-medium hover:underline"
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
