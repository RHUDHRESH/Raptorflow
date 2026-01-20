"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight01Icon, CheckmarkCircle02Icon } from "hugeicons-react";
import { RaptorLogo } from "@/components/ui/CompassLogo";

/**
 * LANDING PAGE - Grand Simplicity + Wow Factor
 * Clean, editorial, but with visual richness
 */
export default function LandingPage() {
    return (
        <main className="min-h-screen bg-[var(--canvas)] text-[var(--ink)] overflow-x-hidden">

            {/* ═══════════════════════════════════════════════════════════════
                HEADER
            ═══════════════════════════════════════════════════════════════ */}
            <header className="fixed top-0 left-0 right-0 z-50 bg-[var(--canvas)]/90 backdrop-blur-md border-b border-[var(--border)]">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-3">
                        <RaptorLogo size={28} className="text-[var(--ink)]" />
                        <span className="font-editorial text-xl font-bold tracking-tight">RaptorFlow</span>
                    </Link>
                    <nav className="hidden md:flex items-center gap-8">
                        <Link href="#system" className="text-sm text-[var(--secondary)] hover:text-[var(--ink)]">System</Link>
                        <Link href="#how" className="text-sm text-[var(--secondary)] hover:text-[var(--ink)]">How it works</Link>
                        <Link href="#pricing" className="text-sm text-[var(--secondary)] hover:text-[var(--ink)]">Pricing</Link>
                        <Link href="/login" className="text-sm text-[var(--ink)]">Log in</Link>
                        <Link href="/signup" className="text-sm px-5 py-2.5 bg-[var(--ink)] text-[var(--canvas)] rounded-lg font-medium hover:opacity-90 transition-opacity">
                            Start free
                        </Link>
                    </nav>
                </div>
            </header>

            {/* ═══════════════════════════════════════════════════════════════
                HERO - Full viewport, dramatic
            ═══════════════════════════════════════════════════════════════ */}
            <section className="relative min-h-screen flex items-center justify-center px-6 pt-20 overflow-hidden">
                {/* Subtle gradient orbs */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    <motion.div
                        animate={{
                            scale: [1, 1.1, 1],
                            opacity: [0.03, 0.06, 0.03]
                        }}
                        transition={{ duration: 8, repeat: Infinity }}
                        className="absolute top-1/4 -left-1/4 w-[800px] h-[800px] bg-[var(--accent)] rounded-full blur-[150px]"
                    />
                    <motion.div
                        animate={{
                            scale: [1.1, 1, 1.1],
                            opacity: [0.05, 0.08, 0.05]
                        }}
                        transition={{ duration: 10, repeat: Infinity }}
                        className="absolute bottom-1/4 -right-1/4 w-[600px] h-[600px] bg-[var(--ink)] rounded-full blur-[120px] opacity-5"
                    />
                </div>

                <div className="relative z-10 max-w-5xl mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--surface)] border border-[var(--border)] rounded-full mb-10"
                    >
                        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-sm text-[var(--secondary)]">Now in public beta</span>
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-6xl md:text-7xl lg:text-8xl font-editorial font-medium leading-[0.95] tracking-tight mb-8"
                    >
                        Stop posting.<br />
                        <span className="text-[var(--muted)]">Start building.</span>
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="text-xl md:text-2xl text-[var(--secondary)] max-w-2xl mx-auto mb-12 leading-relaxed"
                    >
                        The first operating system for founder-led marketing.
                        Strategy, content, and execution—unified at last.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="flex flex-col sm:flex-row gap-4 justify-center mb-8"
                    >
                        <Link
                            href="/signup"
                            className="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-[var(--ink)] text-[var(--canvas)] text-lg font-medium rounded-xl hover:opacity-90 transition-opacity"
                        >
                            Start your free trial
                            {React.createElement(ArrowRight01Icon as any, { className: "w-5 h-5 group-hover:translate-x-1 transition-transform" })}
                        </Link>
                        <Link
                            href="#how"
                            className="inline-flex items-center justify-center gap-2 px-8 py-4 border border-[var(--border)] text-[var(--ink)] text-lg font-medium rounded-xl hover:border-[var(--ink)] transition-colors"
                        >
                            See how it works
                        </Link>
                    </motion.div>

                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="text-sm text-[var(--muted)]"
                    >
                        No credit card required · 14 days free · Cancel anytime
                    </motion.p>
                </div>

                {/* Scroll indicator */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                    className="absolute bottom-8 left-1/2 -translate-x-1/2"
                >
                    <motion.div
                        animate={{ y: [0, 8, 0] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="w-6 h-10 border-2 border-[var(--border)] rounded-full flex justify-center pt-2"
                    >
                        <div className="w-1 h-2 bg-[var(--muted)] rounded-full" />
                    </motion.div>
                </motion.div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                SOCIAL PROOF BAR
            ═══════════════════════════════════════════════════════════════ */}
            <section className="py-12 border-y border-[var(--border)] bg-[var(--surface)]">
                <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16">
                    <p className="text-sm text-[var(--muted)] uppercase tracking-wider">Trusted by 500+ founders</p>
                    <div className="flex items-center gap-10">
                        {["ProductHunt", "Indie Hackers", "YC", "Techstars", "500 Global"].map((name, i) => (
                            <span key={i} className="text-sm font-medium text-[var(--muted)]">{name}</span>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                THE PROBLEM - Emotional, relatable
            ═══════════════════════════════════════════════════════════════ */}
            <section className="py-32">
                <div className="max-w-4xl mx-auto px-6">
                    <motion.p
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-3xl md:text-4xl lg:text-5xl font-editorial leading-[1.3] text-[var(--ink)]"
                    >
                        You didn't start a company to spend 15 hours a week fighting with generic AI prompts and social media schedulers.
                        <span className="text-[var(--muted)]"> Tool sprawl is the villain of your growth. Six months of posting. Zero pipeline.</span>
                    </motion.p>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="mt-8 text-xl text-[var(--secondary)]"
                    >
                        The problem isn’t your effort; it’s your architecture.
                    </motion.p>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                THE SYSTEM - Visual grid with hover
            ═══════════════════════════════════════════════════════════════ */}
            <section id="system" className="py-32 bg-[var(--surface)] border-y border-[var(--border)]">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="max-w-3xl mb-20">
                        <p className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-4">The Technical Spine</p>
                        <h2 className="text-4xl md:text-5xl lg:text-6xl font-editorial mb-6">Six modules.<br /><span className="text-[var(--muted)]">One unified engine.</span></h2>
                        <p className="text-xl text-[var(--secondary)]">Everything you need to go from business context to market domination. No more tool-switching. Marketing, finally under control.</p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[
                            { name: "Foundation", desc: "Our 22-step cognitive onboarding extracts your Precision Soundbites and builds your 90-day plan in minutes.", tag: "Strategy" },
                            { name: "Cohorts", desc: "Segment by behavioral science markers, not demographics. Know exactly who converts—and why.", tag: "Intelligence" },
                            { name: "Moves", desc: "Ready-to-ship execution packets delivered every Monday. Content drafted. Tasks clear. Just ship.", tag: "Execution" },
                            { name: "Muse", desc: "Generate content that sounds like your specific brand voice, not a generic robot. Scale your ideas.", tag: "Creation" },
                            { name: "Matrix", desc: "The Boardroom View. See what's actually driving pipeline. Cut what isn't. Decide in seconds.", tag: "Analytics" },
                            { name: "Blackbox", desc: "The Cognitive Spine. Every experiment, every outcome, and every insight preserved forever.", tag: "Memory" }
                        ].map((module, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className="group relative p-8 bg-[var(--canvas)] border border-[var(--border)] rounded-2xl hover:border-[var(--ink)] transition-all duration-300 cursor-pointer"
                            >
                                <span className="inline-block px-2 py-1 text-xs uppercase tracking-wider text-[var(--muted)] bg-[var(--surface)] rounded mb-4">{module.tag}</span>
                                <h3 className="text-2xl font-bold mb-3 group-hover:text-[var(--accent)] transition-colors">{module.name}</h3>
                                <p className="text-[var(--secondary)] leading-relaxed text-sm">{module.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                HOW IT WORKS - 3 Steps
            ═══════════════════════════════════════════════════════════════ */}
            <section id="how" className="py-32">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-20">
                        <p className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-4">The Implementation Plan</p>
                        <h2 className="text-4xl md:text-5xl font-editorial">Deploy your OS.<br /><span className="text-[var(--muted)]">In three steps.</span></h2>
                    </div>

                    <div className="grid md:grid-cols-3 gap-12">
                        {[
                            { step: "01", title: "Synchronize Context", desc: "Connect your specific business context. We build your RICP, positioning, and 90-day execution plan automatically." },
                            { step: "02", title: "Deploy Weekly Moves", desc: "Every Monday, get your ready-to-ship packet: assets, strategic tasks, and maneuvers. No more blank pages." },
                            { step: "03", title: "Execute & Track", desc: "The Matrix shows the signal. See what's driving pipeline. Double down on winners. Scale with absolute certainty." }
                        ].map((item, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.15 }}
                                className="text-center"
                            >
                                <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center">
                                    <span className="text-2xl font-mono font-bold text-[var(--blueprint)]">{item.step}</span>
                                </div>
                                <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                                <p className="text-[var(--secondary)] leading-relaxed">{item.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                THE TRANSFORMATION - Before vs After
            ═══════════════════════════════════════════════════════════════ */}
            <section className="py-32 bg-[var(--canvas)] border-t border-[var(--border)] overflow-hidden">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-20">
                        <h2 className="text-4xl md:text-5xl font-editorial">The Transformation.</h2>
                        <p className="text-xl text-[var(--secondary)] mt-4">From marketing chaos to surgical execution.</p>
                    </div>

                    <div className="grid md:grid-cols-2 gap-px bg-[var(--border)] border border-[var(--border)] rounded-3xl overflow-hidden shadow-2xl">
                        {/* Before */}
                        <div className="bg-[var(--surface)] p-12 space-y-8">
                            <h3 className="text-2xl font-bold text-[var(--muted)] flex items-center gap-3">
                                <span className="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-sm font-mono font-bold italic">×</span>
                                Before RaptorFlow
                            </h3>
                            <ul className="space-y-6">
                                {[
                                    "Staring at a blank cursor every Monday morning.",
                                    "Guessing which channels are actually driving growth.",
                                    "Switching between Buffer, Notion, and generic AI prompts.",
                                    "Spending 15+ hours a week on 'marketing activities'.",
                                    "Zero pipeline visibility and inconsistent messaging."
                                ].map((item, i) => (
                                    <li key={i} className="flex gap-4 text-lg text-[var(--secondary)] line-through decoration-[var(--muted)]/30">
                                        <span className="text-[var(--muted)]/50">—</span>
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* After */}
                        <div className="bg-[var(--canvas)] p-12 space-y-8 relative">
                            <div className="absolute top-0 right-0 p-4 opacity-5">
                                <RaptorLogo size={200} />
                            </div>
                            <h3 className="text-2xl font-bold text-[var(--ink)] flex items-center gap-3">
                                <span className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-sm font-mono font-bold">✓</span>
                                After RaptorFlow
                            </h3>
                            <ul className="space-y-6 relative z-10">
                                {[
                                    "Ready-to-ship Move packets delivered every Monday.",
                                    "Surgical precision in ICP and behavior targeting.",
                                    "A single, unified OS for strategy and execution.",
                                    "Save 10+ hours a week through technical automation.",
                                    "Full pipeline tracking and institutional memory."
                                ].map((item, i) => (
                                    <li key={i} className="flex gap-4 text-lg text-[var(--ink)] font-medium">
                                        {React.createElement(CheckmarkCircle02Icon as any, { className: "w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" })}
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                BENEFITS - Why RaptorFlow
            ═══════════════════════════════════════════════════════════════ */}
            <section className="py-32 bg-[var(--ink)] text-[var(--canvas)]">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="max-w-3xl mb-16">
                        <h2 className="text-4xl md:text-5xl font-editorial mb-6">Why founders switch.</h2>
                        <p className="text-xl text-[var(--canvas)]/70">RaptorFlow isn't another tool. It's the tool that replaces five others.</p>
                    </div>

                    <div className="grid md:grid-cols-2 gap-8">
                        {[
                            { title: "Save 10+ hours per week", desc: "Stop context-switching between tools. Everything lives in one place." },
                            { title: "Ship content that converts", desc: "No more guessing what to post. Every Move is backed by your strategy." },
                            { title: "Know what's working", desc: "Real attribution, not vanity metrics. See the full pipeline picture." },
                            { title: "Build institutional memory", desc: "Every experiment, every outcome. Never repeat the same mistakes." }
                        ].map((benefit, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                className="flex gap-4 p-6 rounded-xl bg-white/5 border border-white/10"
                            >
                                <div className="flex-shrink-0 mt-1">
                                    {React.createElement(CheckmarkCircle02Icon as any, { className: "w-6 h-6 text-[var(--accent)]" })}
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold mb-2">{benefit.title}</h3>
                                    <p className="text-[var(--canvas)]/70">{benefit.desc}</p>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                TESTIMONIALS - Multiple quotes
            ═══════════════════════════════════════════════════════════════ */}
            <section className="py-32">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <p className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-4">Testimonials</p>
                        <h2 className="text-4xl md:text-5xl font-editorial">Founders who ship.</h2>
                    </div>

                    <div className="grid md:grid-cols-3 gap-6">
                        {[
                            { quote: "I went from random posting to a real strategy in one afternoon. This is what founder marketing should feel like.", name: "Sarah Chen", role: "Founder, ProductLabs" },
                            { quote: "RaptorFlow replaced Notion, Buffer, and ChatGPT for me. The weekly Moves alone save me 5 hours.", name: "Marcus Rodriguez", role: "CEO, Clarity AI" },
                            { quote: "Finally understand what's driving pipeline vs. what's just vanity metrics. Game changer.", name: "Emma Thompson", role: "Founder, DesignPro" }
                        ].map((testimonial, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className="p-8 border border-[var(--border)] rounded-2xl"
                            >
                                <p className="text-lg leading-relaxed mb-6">"{testimonial.quote}"</p>
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-[var(--ink)] text-[var(--canvas)] flex items-center justify-center font-bold text-sm">
                                        {testimonial.name.split(' ').map(n => n[0]).join('')}
                                    </div>
                                    <div>
                                        <p className="font-semibold">{testimonial.name}</p>
                                        <p className="text-sm text-[var(--muted)]">{testimonial.role}</p>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                PRICING
            ═══════════════════════════════════════════════════════════════ */}
            <section id="pricing" className="py-32 bg-[var(--surface)] border-y border-[var(--border)]">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <p className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-4">Pricing</p>
                        <h2 className="text-4xl md:text-5xl font-editorial mb-4">Simple. Honest. <span className="text-[var(--muted)]">No surprises.</span></h2>
                        <p className="text-xl text-[var(--secondary)]">Start free. Upgrade when you're ready.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                        {[
                            { tier: "Ascent", price: "$29", desc: "For founders getting started", features: ["Foundation setup", "3 weekly Moves", "Basic Muse AI", "Matrix analytics", "Email support"] },
                            { tier: "Glide", price: "$79", desc: "For founders scaling up", features: ["Everything in Ascent", "Unlimited Moves", "Advanced Muse (voice training)", "Cohort segmentation", "Priority support", "Blackbox vault"], popular: true },
                            { tier: "Soar", price: "$199", desc: "For teams", features: ["Everything in Glide", "5 team seats", "Custom AI training", "API access", "Dedicated success manager"] }
                        ].map((plan, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.1 }}
                                className={`p-8 rounded-2xl border ${plan.popular ? 'border-[var(--ink)] bg-[var(--canvas)] shadow-xl' : 'border-[var(--border)] bg-[var(--canvas)]'}`}
                            >
                                {plan.popular && <p className="text-xs uppercase tracking-wider text-[var(--accent)] mb-4 font-semibold">Most popular</p>}
                                <h3 className="text-2xl font-bold mb-2">{plan.tier}</h3>
                                <p className="text-4xl font-mono font-bold mb-1">{plan.price}<span className="text-base text-[var(--muted)] font-normal">/mo</span></p>
                                <p className="text-sm text-[var(--muted)] mb-6">{plan.desc}</p>
                                <ul className="space-y-3 mb-8">
                                    {plan.features.map((f, j) => (
                                        <li key={j} className="flex items-start gap-2 text-sm">
                                            {React.createElement(CheckmarkCircle02Icon as any, { className: "w-4 h-4 text-[var(--accent)] flex-shrink-0 mt-0.5" })}
                                            <span>{f}</span>
                                        </li>
                                    ))}
                                </ul>
                                <Link
                                    href="/signup"
                                    className={`block w-full py-3 text-center font-semibold rounded-xl transition-colors ${plan.popular ? 'bg-[var(--ink)] text-[var(--canvas)]' : 'border border-[var(--border)] hover:border-[var(--ink)]'}`}
                                >
                                    Start free trial
                                </Link>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                FAQ
            ═══════════════════════════════════════════════════════════════ */}
            <section className="py-32">
                <div className="max-w-3xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <p className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-4">FAQ</p>
                        <h2 className="text-4xl md:text-5xl font-editorial">Questions? <span className="text-[var(--muted)]">Answered.</span></h2>
                    </div>

                    <div className="space-y-6">
                        {[
                            { q: "How is RaptorFlow different from other marketing tools?", a: "RaptorFlow isn't a tool—it's an operating system. Others give you features in isolation. We connect strategy to execution in one unified workflow." },
                            { q: "Do I need a marketing team?", a: "No. Built specifically for founders and lean teams. The system generates your weekly execution packets—no dedicated marketer needed." },
                            { q: "What if I don't know my positioning yet?", a: "That's what Foundation is for. Our onboarding synthesizes your ICP, positioning, and 90-day plan in under 20 minutes." },
                            { q: "How long until I see results?", a: "Most users ship their first Move within a week. Measurable pipeline impact typically shows within 4-6 weeks of consistent execution." }
                        ].map((faq, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 10 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                className="p-6 border border-[var(--border)] rounded-xl"
                            >
                                <h3 className="text-lg font-bold mb-3">{faq.q}</h3>
                                <p className="text-[var(--secondary)]">{faq.a}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                FINAL CTA
            ═══════════════════════════════════════════════════════════════ */}
            <section className="py-32 bg-[var(--ink)] text-[var(--canvas)]">
                <div className="max-w-4xl mx-auto px-6 text-center">
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-5xl md:text-6xl lg:text-7xl font-editorial mb-6"
                    >
                        Ready to stop guessing?
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-xl text-[var(--canvas)]/70 mb-10"
                    >
                        Join 500+ founders who replaced marketing chaos with a system that works.
                    </motion.p>
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                    >
                        <Link
                            href="/signup"
                            className="inline-flex items-center gap-2 px-10 py-5 bg-[var(--canvas)] text-[var(--ink)] text-lg font-semibold rounded-xl hover:opacity-90 transition-opacity"
                        >
                            Start your free trial
                            {React.createElement(ArrowRight01Icon as any, { className: "w-5 h-5" })}
                        </Link>
                    </motion.div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                FOOTER
            ═══════════════════════════════════════════════════════════════ */}
            <footer className="py-16 border-t border-[var(--border)]">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="flex flex-col md:flex-row justify-between items-start gap-12 mb-12">
                        <div>
                            <div className="flex items-center gap-3 mb-4">
                                <RaptorLogo size={28} className="text-[var(--ink)]" />
                                <span className="font-editorial font-bold text-xl">RaptorFlow</span>
                            </div>
                            <p className="text-[var(--secondary)] max-w-xs">The operating system for founder-led marketing.</p>
                        </div>
                        <div className="flex gap-16">
                            <div>
                                <h4 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)] mb-4">Product</h4>
                                <ul className="space-y-2 text-sm">
                                    <li><Link href="#system" className="text-[var(--secondary)] hover:text-[var(--ink)]">Features</Link></li>
                                    <li><Link href="#pricing" className="text-[var(--secondary)] hover:text-[var(--ink)]">Pricing</Link></li>
                                    <li><Link href="/login" className="text-[var(--secondary)] hover:text-[var(--ink)]">Log in</Link></li>
                                </ul>
                            </div>
                            <div>
                                <h4 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)] mb-4">Legal</h4>
                                <ul className="space-y-2 text-sm">
                                    <li><Link href="/legal/privacy" className="text-[var(--secondary)] hover:text-[var(--ink)]">Privacy</Link></li>
                                    <li><Link href="/legal/terms" className="text-[var(--secondary)] hover:text-[var(--ink)]">Terms</Link></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div className="pt-8 border-t border-[var(--border)] flex justify-between text-sm text-[var(--muted)]">
                        <p>© {new Date().getFullYear()} RaptorFlow Inc.</p>
                        <p>Marketing. Finally under control.</p>
                    </div>
                </div>
            </footer>
        </main>
    );
}
