import React from 'react'
import { motion } from 'framer-motion'
import { Crosshair, Lightning, Heart, Brain, ArrowRight, Quotes } from '@phosphor-icons/react'
import { Link } from 'react-router-dom'
import PremiumPageLayout, { GlassCard } from '../components/PremiumPageLayout'

// Import custom artwork
import clarityArt from '../assets/about_values_clarity_1765014804665.png'
import speedArt from '../assets/about_values_speed_1765014823102.png'
import founderArt from '../assets/about_values_founder_1765014837525.png'
import aiArt from '../assets/about_values_ai_1765014852354.png'

const fadeUp = {
    initial: { opacity: 0, y: 30 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.8 }
}

const stagger = {
    animate: {
        transition: {
            staggerChildren: 0.1
        }
    }
}

const values = [
    {
        icon: Crosshair,
        artwork: clarityArt,
        title: 'Clarity Over Complexity',
        description: 'We believe in removing noise, not adding features. Every element earns its place.'
    },
    {
        icon: Lightning,
        artwork: speedArt,
        title: 'Speed of Execution',
        description: 'Strategy without action is just daydreaming. We optimize for founder velocity.'
    },
    {
        icon: Heart,
        artwork: founderArt,
        title: 'Founder-First Design',
        description: 'Built by founders, for founders. We understand the loneliness of the journey.'
    },
    {
        icon: Brain,
        artwork: aiArt,
        title: 'AI as Copilot',
        description: "AI amplifies your instincts. It doesn't replace your vision—it accelerates it."
    }
]

// Value card with custom artwork background
const ValueCard = ({ value, index }) => {
    const Icon = value.icon

    return (
        <motion.div
            variants={fadeUp}
            className="group relative"
        >
            <GlassCard className="h-full p-8 overflow-hidden">
                {/* Custom artwork background */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-30 transition-opacity duration-700">
                    <img
                        src={value.artwork}
                        alt=""
                        className="absolute inset-0 w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a]/80 to-transparent" />
                </div>

                {/* Content */}
                <div className="relative z-10">
                    <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/10 border border-amber-500/20 flex items-center justify-center mb-6 group-hover:scale-110 group-hover:border-amber-500/40 transition-all duration-500">
                        <Icon className="w-7 h-7 text-amber-400" weight="duotone" />
                    </div>
                    <h3 className="text-xl font-medium text-white mb-3 group-hover:text-amber-300 transition-colors">
                        {value.title}
                    </h3>
                    <p className="text-white/50 leading-relaxed group-hover:text-white/70 transition-colors">
                        {value.description}
                    </p>
                </div>

                {/* Hover glow effect */}
                <div className="absolute -bottom-20 -right-20 w-60 h-60 bg-gradient-radial from-amber-500/20 to-transparent rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
            </GlassCard>
        </motion.div>
    )
}

const About = () => {
    return (
        <PremiumPageLayout>
            <div className="pt-32 pb-24">

                {/* Hero Section */}
                <section className="max-w-5xl mx-auto px-6 md:px-12 mb-32">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1 }}
                        className="text-center"
                    >
                        <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-amber-400 font-medium mb-8">
                            <span className="w-8 h-px bg-amber-400" />
                            About Raptorflow
                            <span className="w-8 h-px bg-amber-400" />
                        </span>
                        <h1 className="text-5xl md:text-7xl lg:text-8xl font-light text-white leading-[0.95] mb-8">
                            Marketing OS for
                            <br />
                            <span className="italic bg-gradient-to-r from-amber-300 via-amber-400 to-orange-400 text-transparent bg-clip-text">
                                ambitious founders
                            </span>
                        </h1>
                        <p className="text-xl text-white/50 max-w-2xl mx-auto leading-relaxed">
                            We're building the operating system that turns founder intuition into
                            strategic clarity—without the agency overhead or template fatigue.
                        </p>
                    </motion.div>
                </section>

                {/* Story Section */}
                <section className="max-w-4xl mx-auto px-6 md:px-12 mb-32">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                    >
                        <div className="flex items-center gap-4 mb-8">
                            <div className="w-12 h-px bg-gradient-to-r from-amber-500 to-transparent" />
                            <h2 className="text-sm uppercase tracking-[0.3em] text-amber-400 font-medium">
                                The Story
                            </h2>
                        </div>

                        <div className="space-y-8 text-lg text-white/60 leading-relaxed">
                            <p className="text-2xl text-white/80 font-light">
                                <span className="text-amber-400 font-medium">We've been where you are.</span>
                            </p>

                            <p>
                                Staring at a blank Google Doc, trying to figure out positioning.
                                Hiring agencies that deliver PDFs nobody opens. Reading the same "10 marketing
                                frameworks" blog posts that never quite fit your unique situation.
                            </p>

                            <p>
                                Traditional marketing advice assumes you have unlimited time, budget, and
                                a team of specialists. But you're a founder—you're doing everything. You
                                need clarity, not more complexity.
                            </p>

                            <GlassCard className="my-12 p-8">
                                <div className="flex gap-4">
                                    <Quotes weight="fill" className="w-8 h-8 text-amber-500/60 flex-shrink-0" />
                                    <p className="text-2xl text-white/70 italic font-light">
                                        "What if AI could help founders see their market the way a seasoned
                                        CMO does—but in minutes, not months?"
                                    </p>
                                </div>
                            </GlassCard>

                            <p>
                                That question sparked Raptorflow. We combined battle-tested marketing
                                frameworks with modern AI to create something new: an operating system
                                that thinks alongside you.
                            </p>

                            <p>
                                Not templates to fill. Not courses to complete. A living system that
                                evolves with your business and keeps you focused on the moves that matter.
                            </p>
                        </div>
                    </motion.div>
                </section>

                {/* Values Section */}
                <section className="max-w-6xl mx-auto px-6 md:px-12 mb-32">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                    >
                        <div className="text-center mb-16">
                            <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-amber-400 font-medium mb-6">
                                Our Principles
                            </span>
                            <h2 className="text-4xl md:text-5xl font-light text-white">
                                What We Believe
                            </h2>
                        </div>

                        <motion.div
                            className="grid md:grid-cols-2 gap-6"
                            variants={stagger}
                            initial="initial"
                            whileInView="animate"
                            viewport={{ once: true }}
                        >
                            {values.map((value, index) => (
                                <ValueCard key={value.title} value={value} index={index} />
                            ))}
                        </motion.div>
                    </motion.div>
                </section>

                {/* CTA Section */}
                <section className="max-w-4xl mx-auto px-6 md:px-12">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                        className="text-center"
                    >
                        <div className="pt-16 border-t border-white/5">
                            <h2 className="text-3xl md:text-4xl font-light text-white mb-6">
                                Ready to build your legend?
                            </h2>
                            <p className="text-white/50 mb-10 text-lg max-w-xl mx-auto">
                                Join founders who've traded guesswork for strategic clarity.
                            </p>
                            <Link
                                to="/start"
                                className="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-amber-500 to-amber-400 text-black font-medium rounded-full hover:shadow-[0_0_40px_rgba(245,158,11,0.3)] transition-all duration-300"
                            >
                                Get started free
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" weight="bold" />
                            </Link>
                        </div>
                    </motion.div>
                </section>
            </div>
        </PremiumPageLayout>
    )
}

export default About
