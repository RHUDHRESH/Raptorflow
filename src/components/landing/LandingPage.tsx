"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, CheckCircle } from "lucide-react";
import { RaptorLogo } from "@/components/ui/CompassLogo";

// Interactive Installations
import ParticleFlowCanvas from "@/components/landing/installations/ParticleFlowCanvas";
import ModuleConstellation from "@/components/landing/installations/ModuleConstellation";
import LiquidTestimonials from "@/components/landing/installations/LiquidTestimonials";
import InteractivePricing from "@/components/landing/installations/InteractivePricing";
import AnimatedTimeline from "@/components/landing/installations/AnimatedTimeline";
import MagneticBenefits from "@/components/landing/installations/MagneticBenefits";
import AnimatedFAQ from "@/components/landing/installations/AnimatedFAQ";
import ParallaxTransformation from "@/components/landing/installations/ParallaxTransformation";
import ScrollProgressCTA from "@/components/landing/installations/ScrollProgressCTA";

// New Installations (5 more)
import OrbitTestimonials from "@/components/landing/installations/OrbitTestimonials";
import TypewriterTerminal from "@/components/landing/installations/TypewriterTerminal";
import GravityFormFields from "@/components/landing/installations/GravityFormFields";
import StackedDeckCards from "@/components/landing/installations/StackedDeckCards";
import ScrollStoryTimeline from "@/components/landing/installations/ScrollStoryTimeline";

// Amazing Additions (3 more)
import LogoGlobe3D from "@/components/landing/installations/LogoGlobe3D";
import { SoundToggle } from "@/components/landing/installations/SoundSystem";
import AIDemoChat from "@/components/landing/installations/AIDemoChat";

// Personality Elements
import {
    AnimatedCounter,
    FloatingEmojis,
    WittyTooltip,
    MoodGreeting,
    SparkleText,
    WavingHand,
    ScrollEncouragement
} from "@/components/landing/installations/PersonalityElements";

// Extra Enhancements (10 more)
import {
    CursorSpotlight,
    GradientWaveDivider,
    FunFactsTicker,
    InteractiveLogo,
    BreathingDot,
    LiveActivityIndicator
} from "@/components/landing/installations/ExtraEnhancements";

// Micro-interactions & Personality CSS
import "@/components/landing/installations/micro-interactions.css";
import "@/components/landing/installations/personality-styles.css";

/**
 * LANDING PAGE - Grand Simplicity + Wow Factor
 * Clean, editorial, but with visual richness
 */
export default function LandingPage() {
    return (
        <main className="min-h-screen bg-[var(--canvas)] text-[var(--ink)] overflow-x-hidden">

            {/* Cursor Spotlight Effect */}
            <CursorSpotlight />

            {/* ═══════════════════════════════════════════════════════════════
                HEADER
            ═══════════════════════════════════════════════════════════════ */}
            <header className="fixed top-0 left-0 right-0 z-50 bg-[var(--canvas)]/90 backdrop-blur-md border-b border-[var(--border)]">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <InteractiveLogo>
                        <Link href="/" className="flex items-center gap-3 group">
                            <RaptorLogo size={28} className="text-[var(--ink)] micro-logo-spin" />
                            <span className="font-editorial text-xl font-bold tracking-tight micro-text-gradient">RaptorFlow</span>
                        </Link>
                    </InteractiveLogo>
                    <nav className="hidden md:flex items-center gap-8">
                        <Link href="#system" className="text-sm text-[var(--secondary)] hover:text-[var(--ink)] micro-nav-link">System</Link>
                        <Link href="#how" className="text-sm text-[var(--secondary)] hover:text-[var(--ink)] micro-nav-link">How it works</Link>
                        <Link href="#pricing" className="text-sm text-[var(--secondary)] hover:text-[var(--ink)] micro-nav-link">Pricing</Link>
                        <Link href="/login" className="text-sm text-[var(--ink)] micro-nav-link">Log in</Link>
                        <Link href="/signup" className="text-sm px-5 py-2.5 bg-[var(--ink)] text-[var(--canvas)] rounded-lg font-medium micro-button-press">
                            Start Now
                        </Link>
                    </nav>
                </div>
            </header>

            {/* ═══════════════════════════════════════════════════════════════
                HERO - Full viewport, dramatic
            ═══════════════════════════════════════════════════════════════ */}
            <section className="relative min-h-screen flex items-center justify-center px-6 pt-20 overflow-hidden">
                {/* Interactive Particle Flow Canvas */}
                <div className="absolute inset-0 overflow-hidden">
                    <ParticleFlowCanvas />
                </div>

                <div className="relative z-10 max-w-5xl mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--surface)] border border-[var(--border)] rounded-full mb-10 micro-card-lift personality-glow-pulse"
                    >
                        <span className="w-2 h-2 rounded-full bg-green-500 micro-badge-pulse" />
                        <WittyTooltip message="We're just getting started! 🎉">
                            <span className="text-sm text-[var(--secondary)] cursor-help">Now in public beta</span>
                        </WittyTooltip>
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-6xl md:text-7xl lg:text-8xl font-editorial font-medium leading-[0.95] tracking-tight mb-8"
                    >
                        <SparkleText>Stop posting.</SparkleText><br />
                        <span className="text-[var(--muted)] personality-shimmer-text">Start building.</span>
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
                            className="group inline-flex items-center justify-center gap-2 px-8 py-4 bg-[var(--ink)] text-[var(--canvas)] text-lg font-medium rounded-xl micro-button-press micro-arrow-slide"
                        >
                            Get Started
                            <ArrowRight className="w-5 h-5 arrow" />
                        </Link>
                        <Link
                            href="#how"
                            className="inline-flex items-center justify-center gap-2 px-8 py-4 border border-[var(--border)] text-[var(--ink)] text-lg font-medium rounded-xl micro-border-glow"
                        >
                            See how it works
                        </Link>
                    </motion.div>

                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="text-sm text-[var(--muted)] flex items-center justify-center gap-4 flex-wrap"
                    >
                        <span>No commitment required</span>
                        <span className="opacity-50">·</span>
                        <span className="personality-shake-hover cursor-default">Setup in 20 mins ⚡</span>
                        <span className="opacity-50">·</span>
                        <span>Cancel anytime</span>
                    </motion.p>
                </div>

                {/* Floating Emojis */}
                <FloatingEmojis emojis={["🚀", "✨", "💡", "🎯", "⚡"]} />

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
                    <p className="text-sm text-[var(--muted)] uppercase tracking-wider">
                        Trusted by <AnimatedCounter end={500} suffix="+" /> founders
                    </p>
                    <div className="flex items-center gap-10 micro-stagger-fade">
                        {["ProductHunt", "Indie Hackers", "YC", "Techstars", "500 Global"].map((name, i) => (
                            <span key={i} className="text-sm font-medium text-[var(--muted)] hover:text-[var(--ink)] transition-colors cursor-default micro-icon-bounce">{name}</span>
                        ))}
                    </div>
                </div>
            </section>

            {/* Fun Facts Ticker */}
            <FunFactsTicker />

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

                    {/* Interactive Module Constellation */}
                    <ModuleConstellation />
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

                    {/* Animated Interactive Timeline */}
                    <AnimatedTimeline />
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                SEE IT IN ACTION - Terminal Demo
            ═══════════════════════════════════════════════════════════════ */}
            <section className="py-32 bg-[var(--surface)] border-y border-[var(--border)]">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <p className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-4">See it in Action</p>
                        <h2 className="text-4xl md:text-5xl font-editorial">Watch the magic. <span className="text-[var(--muted)]">Live.</span></h2>
                    </div>

                    {/* Typewriter Terminal */}
                    <TypewriterTerminal />
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

                    {/* Parallax Before/After Transformation */}
                    <ParallaxTransformation />
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

                    {/* Magnetic Benefits Cards */}
                    <MagneticBenefits />
                </div>
            </section>

            <section className="py-32">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <p className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-4">Testimonials</p>
                        <h2 className="text-4xl md:text-5xl font-editorial">Founders who ship.</h2>
                    </div>

                    {/* Orbit Testimonials */}
                    <OrbitTestimonials />
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════
                EXPLORE FEATURES - Stacked Deck
            ═══════════════════════════════════════════════════════════════ */}
            <section className="py-32 bg-[var(--surface)] border-y border-[var(--border)]">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-20">
                        <p className="text-sm uppercase tracking-[0.3em] text-[var(--muted)] mb-4">Explore Features</p>
                        <h2 className="text-4xl md:text-5xl font-editorial">Deal through the deck.</h2>
                        <p className="text-xl text-[var(--secondary)] mt-4">Five modules that power your marketing OS.</p>
                    </div>

                    {/* Stacked Deck Cards */}
                    <StackedDeckCards />
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
                        <p className="text-xl text-[var(--secondary)]">Choose your plan and get started today.</p>
                    </div>

                    {/* Interactive 3D Pricing Cards */}
                    <InteractivePricing />
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

                    {/* Animated FAQ Accordion */}
                    <AnimatedFAQ />
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
                        Ready to stop guessing? <WavingHand />
                    </motion.h2>
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-xl text-[var(--canvas)]/70 mb-10"
                    >
                        Join <AnimatedCounter end={500} suffix="+" /> founders who replaced marketing chaos with a system that works.
                    </motion.p>
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                    >
                        <Link
                            href="/signup"
                            className="inline-flex items-center gap-2 px-10 py-5 bg-[var(--canvas)] text-[var(--ink)] text-lg font-semibold rounded-xl micro-button-press micro-arrow-slide"
                        >
                            Get Started
                            <ArrowRight className="w-5 h-5 arrow" />
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
                            <div className="flex items-center gap-3 mb-4 group">
                                <RaptorLogo size={28} className="text-[var(--ink)] micro-logo-spin" />
                                <span className="font-editorial font-bold text-xl micro-text-gradient">RaptorFlow</span>
                            </div>
                            <p className="text-[var(--secondary)] max-w-xs">The operating system for founder-led marketing.</p>
                        </div>
                        <div className="flex gap-16">
                            <div>
                                <h4 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)] mb-4">Product</h4>
                                <ul className="space-y-2 text-sm">
                                    <li><Link href="#system" className="text-[var(--secondary)] hover:text-[var(--ink)] micro-nav-link">Features</Link></li>
                                    <li><Link href="#pricing" className="text-[var(--secondary)] hover:text-[var(--ink)] micro-nav-link">Pricing</Link></li>
                                    <li><Link href="/login" className="text-[var(--secondary)] hover:text-[var(--ink)] micro-nav-link">Log in</Link></li>
                                </ul>
                            </div>
                            <div>
                                <h4 className="text-sm font-semibold uppercase tracking-wider text-[var(--muted)] mb-4">Legal</h4>
                                <ul className="space-y-2 text-sm">
                                    <li><Link href="/legal/privacy" className="text-[var(--secondary)] hover:text-[var(--ink)] micro-nav-link">Privacy</Link></li>
                                    <li><Link href="/legal/terms" className="text-[var(--secondary)] hover:text-[var(--ink)] micro-nav-link">Terms</Link></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div className="pt-8 border-t border-[var(--border)] flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-[var(--muted)]">
                        <p>© {new Date().getFullYear()} RaptorFlow Inc. • Built with ❤️ for founders</p>
                        <div className="flex items-center gap-4">
                            <SoundToggle />
                            <MoodGreeting />
                        </div>
                    </div>
                </div>
            </footer>

            {/* Floating Scroll Progress CTA */}
            <ScrollProgressCTA />

            {/* Scroll Encouragement */}
            <ScrollEncouragement />

            {/* Live Activity Indicator */}
            <LiveActivityIndicator />

            {/* AI Demo Chat */}
            <AIDemoChat />
        </main>
    );
}
