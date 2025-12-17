import { motion } from 'framer-motion'
import { ArrowRight, Brain, Crosshair, Heart, Quote, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'

import { MarketingLayout } from '@/components/MarketingLayout'

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
        icon: Zap,
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
const ValueCard = ({ value }) => {
    const Icon = value.icon

    return (
        <motion.div
            variants={fadeUp}
            className="group relative"
        >
            <div className="relative overflow-hidden rounded-card border border-border bg-card p-8 shadow-editorial-sm transition-editorial hover:shadow-editorial">
                {/* Custom artwork background */}
                <div className="pointer-events-none absolute inset-0 opacity-0 transition-editorial group-hover:opacity-20">
                    <img
                        src={value.artwork}
                        alt=""
                        className="absolute inset-0 h-full w-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-background via-background/70 to-transparent" />
                </div>

                <div className="relative">
                    <div className="flex h-12 w-12 items-center justify-center rounded-card border border-border bg-muted text-muted-foreground transition-editorial group-hover:border-primary/30 group-hover:text-primary">
                        <Icon className="h-5 w-5" strokeWidth={1.5} />
                    </div>
                    <h3 className="mt-6 font-serif text-headline-sm text-foreground">{value.title}</h3>
                    <p className="mt-3 text-body-sm text-muted-foreground leading-relaxed">{value.description}</p>
                </div>
            </div>
        </motion.div>
    )
}

const About = () => {
    return (
        <MarketingLayout>
            <div className="container-editorial py-16 md:py-24">
                {/* Hero Section */}
                <section className="mb-16 md:mb-20">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="text-center"
                    >
                        <p className="text-editorial-caption mb-6">About</p>
                        <h1 className="font-serif text-headline-xl md:text-[4.25rem] leading-[1.06] text-foreground mb-6">
                            Marketing OS for
                            <br />
                            <span className="italic text-primary">ambitious founders</span>
                        </h1>
                        <p className="text-body-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                            We're building the operating system that turns founder intuition into
                            strategic clarity—without the agency overhead or template fatigue.
                        </p>
                    </motion.div>
                </section>

                {/* Story Section */}
                <section className="mb-16 md:mb-20">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                    >
                        <div className="flex items-center gap-4 mb-8">
                            <div className="h-px w-12 bg-border" />
                            <div className="text-editorial-caption">The Story</div>
                        </div>

                        <div className="space-y-6 text-body-md text-muted-foreground leading-relaxed">
                            <p className="text-body-lg text-foreground">We've been where you are.</p>

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

                            <div className="rounded-card border border-border bg-card p-8">
                                <div className="flex gap-4">
                                    <Quote className="h-6 w-6 text-primary/60 flex-shrink-0" />
                                    <p className="text-body-lg text-foreground italic leading-relaxed">
                                        "What if AI could help founders see their market the way a seasoned
                                        CMO does—but in minutes, not months?"
                                    </p>
                                </div>
                            </div>

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
                <section className="mb-16 md:mb-20">
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                    >
                        <div className="text-center mb-10">
                            <div className="text-editorial-caption">Our Principles</div>
                            <h2 className="mt-3 font-serif text-headline-lg">What We Believe</h2>
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
                <section>
                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                        className="text-center"
                    >
                        <div className="pt-10 border-t border-border">
                            <h2 className="font-serif text-headline-md text-foreground mb-4">
                                Ready to build your legend?
                            </h2>
                            <p className="text-muted-foreground mb-8 text-body-md max-w-xl mx-auto">
                                Join founders who've traded guesswork for strategic clarity.
                            </p>
                            <Link
                                to="/start"
                                className="inline-flex items-center justify-center rounded-md bg-foreground px-5 py-3 text-sm font-medium text-background transition-editorial hover:opacity-95"
                            >
                                Get started
                                <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </div>
                    </motion.div>
                </section>
            </div>
        </MarketingLayout>
    )
}

export default About
